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
Test cases for Inventory Model
"""
# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Inventory, DataValidationError, db, Condition
from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  Inventory   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestInventoryModel(TestCase):
    """Test Cases for Inventory Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_inventory_item(self):
        """It should create an Inventory item and assert that it exists"""
        item = InventoryFactory()
        item.create()
        self.assertIsNotNone(item.id)
        found = Inventory.all()
        self.assertEqual(len(found), 1)
        data = Inventory.find(item.id)
        self.assertEqual(data.product_id, item.product_id)
        self.assertEqual(data.quantity, item.quantity)
        self.assertEqual(data.restock_level, item.restock_level)
        self.assertEqual(data.restock_amount, item.restock_amount)
        self.assertEqual(data.condition, item.condition)

    def test_read_an_inventory_item(self):
        """It should Read an Inventory Item"""
        item = InventoryFactory()
        logging.debug(item)
        item.id = None
        item.create()
        self.assertIsNotNone(item.id)
        # Fetch it back
        found_item = Inventory.find(item.id)
        self.assertEqual(found_item.id, item.id)
        self.assertEqual(found_item.product_id, item.product_id)
        self.assertEqual(found_item.quantity, item.quantity)
        self.assertEqual(found_item.restock_level, item.restock_level)
        self.assertEqual(found_item.restock_amount, item.restock_amount)
        self.assertEqual(found_item.condition, item.condition)

    def test_serialize_an_inventory_item(self):
        """It should serialize an Inventory item"""
        item = InventoryFactory()
        data = item.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], item.id)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertIn("restock_level", data)
        self.assertEqual(data["restock_level"], item.restock_level)
        self.assertIn("restock_amount", data)
        self.assertEqual(data["restock_amount"], item.restock_amount)
        self.assertIn("condition", data)
        self.assertEqual(data["condition"], item.condition.name)

    def test_deserialize_an_inventory_item(self):
        """It should deserialize an Inventory item"""
        item = InventoryFactory()
        item.create()
        new_item = Inventory()
        new_item.deserialize(item.serialize())
        self.assertEqual(new_item.product_id, item.product_id)
        self.assertEqual(new_item.quantity, item.quantity)
        self.assertEqual(new_item.restock_level, item.restock_level)
        self.assertEqual(new_item.restock_amount, item.restock_amount)
        self.assertEqual(new_item.condition, item.condition)

    def test_deserialize_with_missing_data(self):
        """It should not deserialize an Inventory item with missing data"""
        data = {"id": 1, "product_id": 123}
        item = Inventory()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_with_bad_data(self):
        """It should not deserialize an Inventory item with bad data"""
        data = "this is not a dictionary"
        item = Inventory()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_with_bad_condition(self):
        """It should not deserialize an Inventory item with a bad condition"""
        item = InventoryFactory()
        data = item.serialize()
        data["condition"] = "SOLD" # Invalid condition
        new_item = Inventory()
        self.assertRaises(DataValidationError, new_item.deserialize, data)