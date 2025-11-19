######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse
from service.models import Inventory
from service.common import status  # HTTP Status Codes
from service.models import Condition

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Inventory REST API Service",
    description="This is a sample server Inventory service.",
    default="inventory",
    default_label="Inventory operations",
    doc="/apidocs",  # default also could use doc='/apidocs/'
    prefix="/api",
)


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return app.send_static_file("index.html")


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "InventoryCreate",
    {
        "product_id": fields.Integer(required=True, description="The product ID"),
        "condition": fields.String(
            required=True,
            enum=[c.name for c in Condition],  # NEW, USED, OPEN_BOX only
            description="The condition of the Inventory item (e.g., NEW, USED, OPEN_BOX)",
        ),
        "quantity": fields.Integer(required=True, description="Current quantity"),
        "restock_amount": fields.Integer(
            required=True, description="Amount to restock by"
        ),
        "restock_level": fields.Integer(required=True, description="Restock threshold"),
        "description": fields.String(
            required=False, description="Item description"
        ),  # nullable=True
    },
)

inventory_model = api.inherit(
    "InventoryModel",
    create_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

# query string arguments
inventory_args = reqparse.RequestParser()
inventory_args.add_argument(
    "product_id", type=int, location="args", required=False, help="Filter by product_id"
)
inventory_args.add_argument(
    "condition", type=str, location="args", required=False, help="Filter by condition"
)
inventory_args.add_argument(
    "quantity",
    type=int,
    location="args",
    required=False,
    help="Filter by exact quantity",
)
inventory_args.add_argument(
    "quantity_lt",
    type=int,
    location="args",
    required=False,
    help="Filter by quantity less than",
)
inventory_args.add_argument(
    "quantity_gt",
    type=int,
    location="args",
    required=False,
    help="Filter by quantity greater than",
)
inventory_args.add_argument(
    "restock_level",
    type=int,
    location="args",
    required=False,
    help="Filter by exact restock_level",
)
inventory_args.add_argument(
    "restock_lt",
    type=int,
    location="args",
    required=False,
    help="Filter by restock_level less than",
)
inventory_args.add_argument(
    "restock_gt",
    type=int,
    location="args",
    required=False,
    help="Filter by restock_level greater than",
)
inventory_args.add_argument(
    "query",
    type=str,
    location="args",
    required=False,
    help="Free-text search in description",
)

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  PATH: /inventory/{id}
######################################################################
@api.route("/inventory/<int:item_id>")
@api.param("item_id", "The Inventory identifier")
class InventoryResource(Resource):
    """
    InventoryResource class

    Allows the manipulation of a single Inventory item
    GET /inventory{id} - Returns an Inventory with the id
    PUT /inventory{id} - Update an Inventory with the id
    DELETE /inventory{id} -  Deletes an Inventory with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN INVENTORY ITEM
    # ------------------------------------------------------------------
    @api.doc("get_inventory")
    @api.response(404, "Inventory item not found")
    @api.marshal_with(inventory_model)
    def get(self, item_id):
        """
        Retrieve a single Inventory Item

        This endpoint will return an Inventory Item based on its id
        """
        app.logger.info("Request to Retrieve an inventory item with id [%s]", item_id)

        # Attempt to find the Inventory Item and abort if not found
        item = Inventory.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory item with id '{item_id}' was not found.",
            )

        app.logger.info("Returning inventory item: %s", item.product_id)
        return item.serialize(), status.HTTP_200_OK  # serialize()로 일관성

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING INVENTORY ITEM
    # ------------------------------------------------------------------
    @api.doc("update_inventory")
    @api.response(404, "Inventory item not found")
    @api.response(400, "The posted Inventory data was not valid")
    @api.response(415, "Content-Type must be application/json")
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model)
    def put(self, item_id):
        """
        Update an Inventory Item

        This endpoint will update an Inventory item based the body that is posted
        """
        app.logger.info("Request to update Inventory item with id [%s]", item_id)

        # Find item FIRST before validation
        item = Inventory.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory item with id '{item_id}' was not found.",
            )

        if not request.is_json:
            abort(
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                "Content-Type must be application/json",
            )

        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        item.deserialize(
            data
        )  # deserialize에서 condition upper() 처리 추가 필요 (아래 클래스 메서드 참고)
        item.id = item_id
        item.update()

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN INVENTORY ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_inventory")
    @api.response(204, "Inventory item deleted")
    def delete(self, item_id):
        """
        Delete an Inventory Item

        This endpoint will delete an Inventory item based the id specified in the path
        """
        app.logger.info("Request to Delete an inventory item with id [%s]", item_id)

        # Delete the Inventory item if it exists
        item = Inventory.find(item_id)
        if item:
            app.logger.info("Inventory item with ID: %d found.", item.id)
            item.delete()

        app.logger.info("Inventory item with ID: %d delete complete.", item_id)
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /inventory
######################################################################
@api.route("/inventory", strict_slashes=False)
class InventoryCollection(Resource):
    """Handles all interactions with collections of Inventory items"""

    # ------------------------------------------------------------------
    # LIST ALL INVENTORY ITEMS
    # ------------------------------------------------------------------
    @api.doc("list_inventory")
    @api.expect(inventory_args, validate=True)
    @api.marshal_list_with(inventory_model)
    def get(self):
        """Returns all of the Inventory Items, supporting multi-filter queries."""

        app.logger.info("Request for inventory list")

        # Query parameters
        args = inventory_args.parse_args()
        product_id = args["product_id"]
        condition = args["condition"]
        quantity = args["quantity"]
        quantity_lt = args["quantity_lt"]
        quantity_gt = args["quantity_gt"]
        restock_level = args["restock_level"]
        restock_lt = args["restock_lt"]
        restock_gt = args["restock_gt"]
        query = args["query"]

        # Start query
        q = Inventory.query

        if condition:
            try:
                q = q.filter(
                    Inventory.condition == Condition[condition.upper()]
                )  # upper() 유지
            except KeyError:
                app.logger.warning("Invalid condition: %s", condition)
                return [], status.HTTP_200_OK

        # Apply filters dynamically
        if product_id is not None:
            q = q.filter(Inventory.product_id == product_id)
        if quantity is not None:
            q = q.filter(Inventory.quantity == quantity)
        if quantity_lt is not None:
            q = q.filter(Inventory.quantity < quantity_lt)
        if quantity_gt is not None:
            q = q.filter(Inventory.quantity > quantity_gt)
        if restock_level is not None:
            q = q.filter(Inventory.restock_level == restock_level)
        if restock_lt is not None:
            q = q.filter(Inventory.restock_level < restock_lt)
        if restock_gt is not None:
            q = q.filter(Inventory.restock_level > restock_gt)
        if query:
            q = q.filter(Inventory.description.ilike(f"%{query}%"))

        # Execute final query
        items = q.all()
        results = [
            item.serialize() for item in items
        ]  # marshal 전에 serialize 호출로 일관성

        app.logger.info("Returning %d filtered inventory items", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW INVENTORY ITEM
    # ------------------------------------------------------------------
    @api.doc("create_inventory")
    @api.response(400, "The posted data was not valid")
    @api.response(409, "Inventory item already exists")
    @api.expect(create_model)
    @api.marshal_with(inventory_model, code=201)
    def post(self):
        """
        Creates an Inventory Item
        This endpoint will create an Inventory item based the data in the body that is posted
        """
        app.logger.info("Request to create an Inventory item")
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload

        item = Inventory()
        # condition upper() for consistency with query
        if "condition" in data:
            data["condition"] = data["condition"].upper()
        item.deserialize(data)

        # Check for duplicate product_id
        existing_item = Inventory.query.filter_by(product_id=item.product_id).first()
        if existing_item:
            app.logger.warning("Duplicate product_id [%s] found", item.product_id)
            abort(
                status.HTTP_409_CONFLICT,
                f"Inventory item with product_id '{item.product_id}' already exists.",
            )

        item.create()

        location_url = api.url_for(InventoryResource, item_id=item.id, _external=True)
        app.logger.info("Inventory item with ID [%s] created.", item.id)
        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    # ------------------------------------------------------------------
    # DELETE ALL INVENTORY ITEMS (for testing only)
    # ------------------------------------------------------------------
    @api.doc("delete_all_inventory")
    @api.response(204, "All Inventory deleted")
    def delete(self):
        """
        Delete all Inventory

        This endpoint will delete all Inventory only if the system is under test
        """
        app.logger.info("Request to Delete all inventory...")
        if "TESTING" in app.config and app.config["TESTING"]:
            num_deleted = Inventory.query.delete()
            db.session.commit()
            app.logger.info("Removed %d Inventory items from the database", num_deleted)
        else:
            app.logger.warning("Request to clear database while system not under test")

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# RESTOCK AN INVENTORY ITEM
# PATH: /inventory/{id}/restock
######################################################################
@api.route("/inventory/<int:item_id>/restock")
@api.param("item_id", "The Inventory identifier")
class RestockResource(Resource):
    """Restock actions on an Inventory item"""

    @api.doc("restock_inventory")
    @api.response(404, "Inventory item not found")
    @api.marshal_with(inventory_model)
    def put(self, item_id):
        """
        Restock an Inventory Item

        This endpoint will increase the quantity of an Inventory item by its restock_amount
        """
        app.logger.info("Request to restock Inventory item with id [%s]", item_id)

        # Find the inventory item
        item = Inventory.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory item with id '{item_id}' was not found.",
            )

        # Increase quantity by restock_amount
        item.quantity += item.restock_amount
        item.update()

        app.logger.info(
            "Inventory item with ID [%s] restocked. New quantity: %s",
            item_id,
            item.quantity,
        )
        return item.serialize(), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
