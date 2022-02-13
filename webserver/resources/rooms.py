from flask_restful import Resource
from flask import request
from webserver.classes.exceptions.invalid_userid import InvalidUserException
from webserver.classes.exceptions.invalid_room import InvalidRoomException
from webserver.classes.exceptions.data_format import DataFormatError
from webserver.classes.user import User
from webserver.classes.room import Room

user = User()
room = Room(user)

class Rooms(Resource):
    def patch(self, room_id):
        """
            Handles a PATCH request. Adds a user to a room if they are not already present in the room.

            Returns:
                status code 200: successful
                status code 404: either the given room_id is invalid OR the user_id is invalid
        """
        try:
            print(f'Received ROOM ID: {room_id}')
            participant = request.args.get("participant", default=None, type=str)
            if participant is None:
                return {"response": "participant parameter was not given in the request URL"}, 400

            ret = room.add_participant(room_id, participant)
            return {"response": ret}, 200
        except (InvalidUserException, InvalidRoomException) as e:
            return {"response": str(e)}, 404
        except Exception as e:
            return {"response": str(e)}, 500