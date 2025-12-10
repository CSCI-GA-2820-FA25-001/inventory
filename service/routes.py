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
Inventory Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Inventory items
"""

from flask import jsonify, request
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
    description=(
        "A RESTful inventory management service for tracking "
        "product stock levels, conditions, and automated restocking"
    ),
    default="inventory",
    default_label="Inventory Operations",
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

    # Seed at least one inventory item if the database is empty.
    # Use a product_id that is never used in the Behave scenarios,
    # so we don't collide with test data like 12345, 88888, etc.
    if Inventory.query.count() == 0:
        app.logger.info(
            "No inventory items found in database; "
            "creating a sample item for the UI listing scenario."
        )
        sample_item = Inventory(
            product_id=10101,
            quantity=10,
            restock_level=5,
            restock_amount=5,
            condition=Condition.NEW,
            description="Sample inventory item",
        )
        sample_item.create()

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
        "product_id": fields.Integer(
            required=True, description="Unique product identifier", example=12345
        ),
        "condition": fields.String(
            required=True,
            enum=[c.name for c in Condition],  # NEW, USED, OPEN_BOX only
            description=(
                "The condition of the Inventory item (e.g., NEW, USED, OPEN_BOX)"
            ),
            example="NEW",
        ),
        "quantity": fields.Integer(
            required=True, description="Current stock quantity", example=100, min=0
        ),
        "restock_amount": fields.Integer(
            required=True,
            description="Quantity to add during restock operations",
            example=50,
            min=0,
        ),
        "restock_level": fields.Integer(
            required=True,
            description="Minimum quantity threshold before restocking is recommended",
            example=20,
            min=0,
        ),
        "description": fields.String(
            required=False,
            description="Product description",
            example="Premium wireless headphones with active noise cancellation",
        ),
    },
)

inventory_model = api.inherit(
    "InventoryModel",
    create_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="Unique inventory record identifier (auto-generated)",
        ),
    },
)

# query string arguments
inventory_args = reqparse.RequestParser()
inventory_args.add_argument(
    "product_id", type=int, location="args", required=False, help="Filter by product ID"
)
inventory_args.add_argument(
    "condition",
    type=str,
    location="args",
    required=False,
    help="Filter by condition (NEW, USED, OPEN_BOX)",
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
    help="Filter by quantity less than specified value",
)
inventory_args.add_argument(
    "quantity_gt",
    type=int,
    location="args",
    required=False,
    help="Filter by quantity greater than specified value",
)
inventory_args.add_argument(
    "restock_level",
    type=int,
    location="args",
    required=False,
    help="Filter by exact restock level",
)
inventory_args.add_argument(
    "restock_lt",
    type=int,
    location="args",
    required=False,
    help="Filter by restock level less than specified value",
)
inventory_args.add_argument(
    "restock_gt",
    type=int,
    location="args",
    required=False,
    help="Filter by restock level greater than specified value",
)
inventory_args.add_argument(
    "query",
    type=str,
    location="args",
    required=False,
    help="Search descriptions (case-insensitive partial match)",
)


######################################################################
#  H E L P E R S
######################################################################
def build_inventory_query(args):
    """Build an Inventory query from parsed request arguments."""
    q = Inventory.query
    condition = args["condition"]
    product_id = args["product_id"]
    quantity = args["quantity"]
    quantity_lt = args["quantity_lt"]
    quantity_gt = args["quantity_gt"]
    restock_level = args["restock_level"]
    restock_lt = args["restock_lt"]
    restock_gt = args["restock_gt"]
    query = args["query"]

    if condition:
        # May raise KeyError if condition is invalid; caller will handle
        q = q.filter(Inventory.condition == Condition[condition.upper()])

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
    return q

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  PATH: /inventory/{id}
######################################################################
@api.route("/inventory/<int:item_id>")
@api.param("item_id", "The inventory item identifier")
class InventoryResource(Resource):
    """
    InventoryResource class

    Manages individual inventory items
    Allows the manipulation of a single Inventory item
    GET /inventory{id} - Returns an Inventory with the id
    PUT /inventory{id} - Update an Inventory with the id
    DELETE /inventory{id} -  Deletes an Inventory with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN INVENTORY ITEM
    # ------------------------------------------------------------------
    @api.doc("get_inventory_item")
    @api.response(200, "Success")
    @api.response(404, "Inventory item not found")
    @api.marshal_with(inventory_model)
    def get(self, item_id):
        """
        Retrieve an inventory item

        Returns detailed information for a single inventory item
        including stock levels and restock parameters.
        """
        app.logger.info("Request to Retrieve an inventory item with id [%s]", item_id)

        item = Inventory.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory item with id '{item_id}' was not found.",
            )

        app.logger.info("Returning inventory item: %s", item.product_id)
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING INVENTORY ITEM
    # ------------------------------------------------------------------
    @api.doc("update_inventory_item")
    @api.response(200, "Inventory item updated successfully")
    @api.response(404, "Inventory item not found")
    @api.response(400, "Invalid request data")
    @api.response(415, "Unsupported media type")
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model)
    def put(self, item_id):
        """
        Update an inventory item

        Updates all fields of an existing inventory item.
        All required fields must be included in the request body.
        """
        app.logger.info("Request to update Inventory item with id [%s]", item_id)

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
        item.deserialize(data)
        item.id = item_id
        item.update()

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN INVENTORY ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_inventory_item")
    @api.response(204, "Inventory item deleted successfully")
    def delete(self, item_id):
        """
        Delete an inventory item

        Permanently removes an inventory item from the system.
        This operation is idempotent.
        """
        app.logger.info("Request to Delete an inventory item with id [%s]", item_id)

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
    """
    Inventory Collection

    Manages the collection of all inventory items
    """

    # ------------------------------------------------------------------
    # LIST ALL INVENTORY ITEMS
    # ------------------------------------------------------------------
    @api.doc("list_inventory_items")
    @api.expect(inventory_args, validate=True)
    @api.response(200, "Success")
    @api.marshal_list_with(inventory_model)
    def get(self):
        """
        List inventory items

        Returns all inventory items. Supports filtering by product_id,
        condition, quantity ranges, restock levels, and description search.
        Multiple filters can be combined.
        """
        app.logger.info("Request for inventory list")

        # Parse query parameters
        args = inventory_args.parse_args()

        # Build query using helper, handling invalid condition values gracefully
        try:
            q = build_inventory_query(args)
        except KeyError:
            condition = args.get("condition")
            app.logger.warning("Invalid condition: %s", condition)
            return [], status.HTTP_200_OK

        items = q.all()
        results = [item.serialize() for item in items]

        app.logger.info("Returning %d filtered inventory items", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW INVENTORY ITEM
    # ------------------------------------------------------------------
    @api.doc("create_inventory_item")
    @api.response(201, "Inventory item created successfully")
    @api.response(400, "Invalid request data")
    @api.response(409, "Inventory item already exists")
    @api.expect(create_model)
    @api.marshal_with(inventory_model, code=201)
    def post(self):
        """
        Create an inventory item

        Creates a new inventory item. The product_id must be unique.
        Returns the created item with an auto-generated id.
        """
        app.logger.info("Request to create an Inventory item")
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload

        item = Inventory()

        # condition upper() for consistency with query
        if "condition" in data:
            data["condition"] = data["condition"].upper()
        item.deserialize(data)

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


######################################################################
# RESTOCK AN INVENTORY ITEM
# PATH: /inventory/{id}/restock
######################################################################
@api.route("/inventory/<int:item_id>/restock")
@api.param("item_id", "The inventory item identifier")
class RestockResource(Resource):  # pylint: disable=too-few-public-methods
    """
    Restock Operations

    Performs restocking actions on inventory items
    """

    @api.doc("restock_inventory_item")
    @api.response(200, "Inventory item restocked successfully")
    @api.response(404, "Inventory item not found")
    @api.marshal_with(inventory_model)
    def put(self, item_id):
        """
        Restock an inventory item

        Increases the inventory quantity by the predefined restock_amount.
        No request body required - the restock_amount is retrieved from
        the existing inventory record.
        """
        app.logger.info("Request to restock Inventory item with id [%s]", item_id)

        item = Inventory.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory item with id '{item_id}' was not found.",
            )

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
