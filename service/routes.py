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

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Inventory
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...


######################################################################
# CREATE AN INVENTORY ITEM
# created by Jason, should be replaced by @Sichen Zhong's code
######################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Creates an Inventory item
    This endpoint will create an Inventory item based on the posted data
    """
    app.logger.info("Request to create an Inventory item")
    data = request.get_json()

    try:
        item = Inventory()
        item.deserialize(data)
        item.create()
    except Exception as e:
        app.logger.error("Error creating inventory: %s", str(e))
        abort(status.HTTP_400_BAD_REQUEST, f"Invalid data: {str(e)}")

    location_url = url_for("get_inventory_item", item_id=item.id, _external=False)
    app.logger.info("Inventory item with ID [%s] created.", item.id)
    return (
        jsonify(item.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# READ AN INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
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
    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:item_id>", methods=["PUT"])
def update_inventory_item(item_id):
    """
    Update an existing Inventory item
    This endpoint will update an Inventory item based on the posted data
    """
    app.logger.info("Request to update Inventory item with id [%s]", item_id)

    if not request.is_json:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Content-Type must be application/json",
        )

    data = request.get_json()

    item = Inventory.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Inventory item with id '{item_id}' was not found.",
        )

    try:
        item.deserialize(data)
        item.id = item_id
        item.update()
    except Exception as e:
        app.logger.error("Error updating inventory: %s", str(e))
        abort(status.HTTP_400_BAD_REQUEST, f"Invalid data: {str(e)}")

    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# LIST ALL INVENTORY ITEMS
######################################################################
@app.route("/inventory", methods=["GET"])
def list_inventory_items():
    """Returns all of the Inventory Items"""
    app.logger.info("Request for inventory list")

    items = []

    # Parse any arguments from the query string
    category = request.args.get("category")
    name = request.args.get("name")
    available = request.args.get("available")
    gender = request.args.get("gender")

    if category:
        app.logger.info("Find by category: %s", category)
        items = Inventory.find_by_category(category)
    elif name:
        app.logger.info("Find by name: %s", name)
        items = Inventory.find_by_name(name)
    elif available:
        app.logger.info("Find by available: %s", available)
        # create bool from string
        available_value = available.lower() in ["true", "yes", "1"]
        items = Inventory.find_by_availability(available_value)
    elif gender:
        app.logger.info("Find by gender: %s", gender)
        # create enum from string
        items = Inventory.find_by_gender(gender[gender.upper()])
    else:
        app.logger.info("Find all")
        items = Inventory.all()

    results = [item.serialize() for item in items]
    app.logger.info("Returning %d inventory items", len(results))
    return jsonify(results), status.HTTP_200_OK
