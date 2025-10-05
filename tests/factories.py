"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from service.models import Inventory, Condition


class InventoryFactory(factory.Factory):
    """Creates fake Inventory items that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""
        model = Inventory

    # id is created automatically by the database
    product_id = factory.Sequence(lambda n: n)
    quantity = FuzzyInteger(0, 100)
    restock_level = FuzzyInteger(10, 50)
    condition = FuzzyChoice(choices=[Condition.NEW, Condition.OPEN_BOX, Condition.USED])