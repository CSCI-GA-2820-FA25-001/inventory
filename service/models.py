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
    """Used for an data validation errors when deserializing"""


class Condition(Enum):
    """Enumeration of valid Inventory conditions"""
    NEW = 0
    OPEN_BOX = 1
    USED = 2


class Inventory(db.Model):
    """
    Class that represents an Inventory item
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    restock_level = db.Column(db.Integer, nullable=False, default=0)
    condition = db.Column(db.Enum(Condition), nullable=False, server_default=(Condition.NEW.name))

    def __repr__(self):
        return f"<Inventory for product id='{self.product_id}'>"

    def create(self):
        """
        Creates an Inventory record in the database
        """
        logger.info("Creating inventory record for product id: %s", self.product_id)
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
        Updates an Inventory record in the database
        """
        logger.info("Saving inventory record for product id: %s", self.product_id)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes an Inventory record from the data store"""
        logger.info("Deleting inventory record for product id: %s", self.product_id)
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
            "condition": self.condition.name,  # return the name of the enum
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
            # Get the enum from the name
            self.condition = getattr(Condition, data["condition"])
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError("Invalid Inventory: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Inventory: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the YourResourceModels in the database"""
        logger.info("Processing all YourResourceModels")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a YourResourceModel by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all YourResourceModels with the given name

        Args:
            name (string): the name of the YourResourceModels you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
