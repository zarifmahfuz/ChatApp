from flask_restful import Resource
from flask import request
import jsonschema
from webserver.classes.exceptions.invalid_userid import InvalidUserException
from webserver.classes.exceptions.data_format import DataFormatError
from webserver.classes.user import User
from webserver.classes.room import Room

user = User()
room = Room(user)

class RoomsCollection(Resource):
    def get(self):
        """
            Handles a GET request.
        """
        try:
            return {"response": room.get_all_rooms()}, 200
        except Exception as e:
            return {"response": str(e)}, 500

    def post(self):
        """
            Handles a POST request for a new room creation.

            Returns:
                status code 201: room was successfully created
                status code 409: given roomId already exists
                status code 404: a given userId does not exist
        """
        try:
            data = request.get_json()
            print("Received data:")
            print(data)
            ret = room.add_room(data)
            status = 201
            if (ret == None):
                status = 409
            return {"roomId": ret}, status
        except (InvalidUserException) as e:
            return {"response": str(e)}, 404
        except (jsonschema.exceptions.ValidationError, DataFormatError) as e:
            return {"response": str(e)}, 400
        except Exception as e:
            return {"response": str(e)}, 500
