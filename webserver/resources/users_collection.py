from flask_restful import Resource
from flask import request
from webserver.database_manager import users_collection
from webserver.app import bcrypt
from webserver.classes.user import User
import jsonschema
from webserver.classes.exceptions.data_format import DataFormatError

user = User()

class UsersCollection(Resource):
    def post(self):
        """
            Handles a POST request. Inserts a new user into the Users collection.
            Returns:
                status code 201 if the user was successfully created.
                status code 409 if the given userId already exists.
        """
        try:
            data = request.get_json()
            ret = user.add_user(data, bcrypt)
            status = 201
            if (ret == None):
                status = 409
            return {"userId": ret}, status
        except (jsonschema.exceptions.ValidationError, DataFormatError) as e:
            return {"response": str(e)}, 400
        except Exception as e:
            return {"response": str(e)}, 500
