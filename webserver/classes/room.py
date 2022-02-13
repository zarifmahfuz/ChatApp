from webserver.classes.exceptions.invalid_userid import InvalidUserException
from webserver.classes.user import User
from webserver.database_manager import users_collection, rooms_collection
from jsonschema import validate
from webserver.classes.exceptions.data_format import DataFormatError
from webserver.classes.exceptions.invalid_room import InvalidRoomException
import json
from bson import json_util

class Room(object):
    """
        Handles the backend service for creation of rooms and managing users in the rooms.
    """
    def __init__(self, user: User):
        self.schema = {
            "type": "object",
            "properties": {
                "roomId": {"type": "string"},
                "name": {"type": "string"},
                "participants": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["roomId"],
            "additionalProperties": False
        }
        self.user = user

    def add_room(self, data: dict):
        """
            Adds a new room into the database. If "participants" field is specified, all participants must be valid
            userIds.
            Returns:
                roomId (str): if operation was successful
                None, otherwise 
        """
        self.validate_data(data)
        data["_id"] = data["roomId"]
        del data["roomId"]

        if ("participants" in data):
            for participant in data["participants"]:
                if (self.user.user_exists(participant) is False):
                    raise InvalidUserException(f'userId {participant} does not exist')

        try:
            ret = rooms_collection.insert_one(data)
            return ret.inserted_id
        except:
            pass
        return None

    def get_all_rooms(self):
        """
            Gets all the room documents in the Rooms collection.

            Returns:
                rooms (list(dict)): json object
        """
        result = rooms_collection.find({})
        return json.loads(json_util.dumps(result))

    def add_participant(self, room_id: str, user_id: str):
        """
            Adds a new participant to a room with the given room id.

            Raises:
                InvalidUserException: if the given user_id does not exist.
                InvalidRoomException: if the given room_id does not exist.

            Returns:
                pymongo.results.UpdateResult
        """
        if self.user.user_exists(user_id) is False:
            raise InvalidUserException(f'{user_id} is not a valid user')

        # i need to insert user_id into the "participants" field of the specific room document
        # IF the user_id does not already exist.
        update_result = rooms_collection.update_one({"_id": room_id}, {"$addToSet": {"participants": user_id}})

        if (update_result.matched_count < 1):
            # the given room_id does not exist
            raise InvalidRoomException(f'{room_id} is not a valid roomId')

        return update_result.raw_result

    def validate_data(self, data: dict) -> None:
        # validate the data
        if (isinstance(data, dict)):
            validate(instance=data, schema=self.schema)
        else:
            raise DataFormatError("Invalid data format")