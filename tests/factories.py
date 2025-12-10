"""
Test Factory to make fake objects for testing
"""

import random
import factory
from factory.fuzzy import FuzzyInteger
from service.models import Inventory, Condition
# pylint: disable=too-few-public-methodsg


class InventoryFactory(factory.Factory):
    """Creates fake inventory items"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Inventory

    id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n + 1000)  # Ensure unique product IDs
    quantity = FuzzyInteger(0, 50)
    restock_level = FuzzyInteger(5, 15)
    restock_amount = FuzzyInteger(20, 30)
    condition = factory.LazyFunction(lambda: random.choice(list(Condition)))
