from database_manager import rooms_collection
import pymongo

class RoomManager(object):
    """
        Handles the creation of rooms.
    """
    def __init__(object):
        pass

    def create_room(self, room_id: str) -> str:
        """
            Creates a new room in the Rooms collection, if it does not already exist.

            Returns:
                room_id: indicates that the room was created or already exists.
        """
        doc = {"_id": room_id}
        try:
            room_id = rooms_collection.insert_one(doc).inserted_id
        except pymongo.errors.DuplicateKeyError:
            pass
        return room_id
