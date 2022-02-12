from webserver.database_manager import users_collection
from webserver.classes.exceptions.data_format import DataFormatError
from webserver.classes.exceptions.invalid_userid import InvalidUserException
from jsonschema import validate
from flask_bcrypt import Bcrypt
import pymongo

class User(object):
    """
        This class interacts with the database to perform database operations related to the
        Users collection.
    """
    def __init__(self):
        self.schema = {
            "type": "object",
            "properties": {
                "userId": {"type": "string"},
                "name": {"type": "string"},
                "email": {"type": "string"},
                "password": {"type": "string"}
            },
            "required": ["name", "userId", "password"],
            "additionalProperties": False
        }

    def user_exists(self, userId: str) -> bool:
        result = users_collection.find({"_id": userId})
        return result != None

    def add_user(self, data: dict, bcrypt: Bcrypt):
        """
            Adds a new user to the Users collection.
            Returns the inserted id if operation was successful. Returns None otherwise.
        """
        # raises exception is invalid data
        self.validate_data(data)
        data["_id"] = data["userId"]
        del data["userId"]

        unhashed_password = data["password"]
        data["password"] = bcrypt.generate_password_hash(unhashed_password).decode("utf-8")

        try:
            ret = users_collection.insert_one(data)
            return ret.inserted_id
        except pymongo.errors.DuplicateKeyError:
            pass
        return None

    def login_user(self, userId: str, password: str, bcrypt: Bcrypt):
        """
            Queries the database with the given userId and verifies the given password.

            Raises:
                InvalidUserException: if userId does not exist

            Returns:
                True, if password is valid. False otherwise.
        """
        doc = users_collection.find_one({"_id": userId})
        if (doc == None):
            raise InvalidUserException(f'{userId} does not exist')
        valid_password = bcrypt.check_password_hash(doc["password"], password)
        return valid_password

    def validate_data(self, data: dict) -> None:
        # validate the data
        if (isinstance(data, dict)):
            validate(instance=data, schema=self.schema)
        else:
            raise DataFormatError("Invalid data format")

