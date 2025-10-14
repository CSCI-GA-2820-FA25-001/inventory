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
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Inventory
from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/inventory"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create inventory items
    ############################################################
    def _create_inventory_items(self, count: int = 1) -> list:
        """Factory method to create inventory items in bulk"""
        items = []
        for _ in range(count):
            test_item = InventoryFactory()
            response = self.client.post(BASE_URL, json=test_item.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test inventory item",
            )
            new_item = response.get_json()
            test_item.id = new_item["id"]
            items.append(test_item)
        return items

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # Todo: Add your test cases here...

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_inventory_item(self):
        """It should Get a single Inventory Item"""
        # Create an inventory item and get its id
        test_item = self._create_inventory_items(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_item.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["product_id"], test_item.product_id)
        self.assertEqual(data["quantity"], test_item.quantity)
        self.assertEqual(data["restock_level"], test_item.restock_level)
        self.assertEqual(data["restock_amount"], test_item.restock_amount)
        self.assertEqual(data["condition"], test_item.condition.name)

    def test_get_inventory_item_not_found(self):
        """It should not Get an Inventory Item that is not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_create_inventory_conflict(self):
        """It should not allow creating a duplicate inventory item (409 Conflict)"""
        # Create an initial item
        test_item = self._create_inventory_items(1)[0]

        # Try creating another item with the same product_id
        duplicate_data = test_item.serialize()
        duplicate_data["id"] = None  # remove id for creation

        response = self.client.post(BASE_URL, json=duplicate_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        data = response.get_json()
        self.assertIn("already exists", data["message"])

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_inventory_item(self):
        """It should Update an existing Inventory item"""
        test_item = self._create_inventory_items(1)[0]
        self.assertIsNotNone(test_item.id)

        new_data = test_item.serialize()
        new_data["quantity"] = test_item.quantity + 10
        new_data["condition"] = "USED"

        response = self.client.put(f"{BASE_URL}/{test_item.id}", json=new_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated = response.get_json()
        self.assertEqual(updated["id"], test_item.id)
        self.assertEqual(updated["quantity"], new_data["quantity"])
        self.assertEqual(updated["condition"], new_data["condition"])

        check_item = Inventory.find(test_item.id)
        self.assertEqual(check_item.quantity, new_data["quantity"])
        self.assertEqual(check_item.condition.name, new_data["condition"])

    def test_update_inventory_item_with_invalid_content_type(self):
        """It should fail to update an Inventory item with invalid Content-Type"""
        test_item = self._create_inventory_items(1)[0]

        # wrong Content-Type (is_json=False)
        response = self.client.put(
            f"{BASE_URL}/{test_item.id}",
            data="not a json",  # raw data, not JSON
            content_type="text/plain",
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = response.get_json()
        self.assertIn("Content-Type must be application/json", data["message"])

    def test_update_inventory_item_not_found(self):
        """It should return 404 when updating a non-existing Inventory item"""
        # looking for non exist item
        response = self.client.put(
            f"{BASE_URL}/0", json={"quantity": 10, "condition": "USED"}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_inventory_list(self):
        """It should Get a list of Inventory item"""
        self._create_inventory_items(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
