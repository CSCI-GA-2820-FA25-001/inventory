"""
Models for Inventory

All of the models are stored in this module
"""

import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for data validation errors when deserializing"""


class Condition(Enum):
    """Enumeration for the condition of an Inventory item"""

    NEW = 1
    USED = 2
    OPEN_BOX = 3


class Inventory(db.Model):
    """
    Class that represents an Inventory item
    """

    __tablename__ = "inventory"

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    restock_level = db.Column(db.Integer, nullable=False, default=0)
    restock_amount = db.Column(
        db.Integer, nullable=False, default=0
    )  # As per spec, no default but good practice
    condition = db.Column(
        db.Enum(Condition), nullable=False, server_default=(Condition.NEW.name)
    )
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Inventory product_id={self.product_id} id=[{self.id}]>"

    def create(self):
        """
        Creates an Inventory item to the database
        """
        logger.info("Creating inventory for product_id: %s", self.product_id)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates an Inventory item in the database
        """
        logger.info("Saving inventory for product_id: %s", self.product_id)

        # Must have an id to update
        if self.id is None:
            raise DataValidationError("Update called with empty ID")

        # Explicitly validate condition: must be a Condition enum
        if not isinstance(self.condition, Condition):
            raise DataValidationError(f"Invalid condition: {self.condition!r}")

        try:
            db.session.commit()
        except Exception as e:  # You can narrow this later if you want
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e


    def delete(self):
        """Removes an Inventory item from the data store"""
        logger.info("Deleting inventory for product_id: %s", self.product_id)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes an Inventory item into a dictionary"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "restock_level": self.restock_level,
            "restock_amount": self.restock_amount,
            "condition": self.condition.name,  # Return the name of the enum
            "description": self.description,
        }

    def deserialize(self, data):
        """
        Deserializes an Inventory item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            self.quantity = data["quantity"]
            self.restock_level = data["restock_level"]
            self.restock_amount = data["restock_amount"]
            # Look up the enum from the string
            self.condition = getattr(Condition, data["condition"])
            self.description = data.get("description", None)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Inventory: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Inventory: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Inventory items in the database"""
        logger.info("Processing all Inventory items")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds an Inventory item by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_condition(cls, condition):
        """Returns all Inventory items with the given condition

        Args:
            condition (Condition): the condition of the Inventory items you want to match
        """
        logger.info("Processing condition query for %s ...", condition)
        return cls.query.filter(cls.condition == condition)
