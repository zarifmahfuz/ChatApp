# from websocket.database_manager import rooms_collection, messages_collection
from this import d
from database_manager import rooms_collection, messages_collection
from datetime import datetime
from utils import get_date_repr
from itertools import cycle
import pymongo
import pprint

class ChatMessage(object):
    """
        Object that holds the chat message.
    """
    def __init__(self, msg_idx: int, timestamp: datetime, content: str, sender: str, room_id: str, written_to_db = False):
        self.msg_idx = msg_idx
        self.timestamp = timestamp
        self.content = content
        self.sender = sender
        self.room_id = room_id
        self.written_to_db = written_to_db      # message is not written to db when it is first created

    def get_data_for_db(self):
        """
            Returns a dictionary representing a document in the Messages collection.
        """
        return {"timestamp": self.timestamp, "sender": self.sender, "content": self.content, "room_id": self.room_id}

    def gata_data_for_pres(self) -> str:
        """
            Returns a string representation of a chat message.
        """
        return get_date_repr(self.timestamp) + ", " + self.sender +  ": " + self.content

    def __str__(self):
        ret = "{\n\t" + "timestamp: " + get_date_repr(self.timestamp) + ",\n\t" + "content: " + self.content + ",\n\t"\
            + "sender: " + self.sender + ",\n\t" + "room_id: " + self.room_id + ",\n\t" + "written_to_db: " \
            + str(self.written_to_db) + "\r\n}"
        return ret


class MessageHandler(object):
    def __init__(self):
        pass

    def write_to_db(self, data):
        """
            Writes given data into the Messages collection.

            Parameters:
                data (ChatMessage or list(ChatMessage)): messages to be inserted
        """
        # executing write operations in batches reduces the number of network round trips, increasing write throughput
        if (isinstance(data, list)):
            # assuming that the list contains ChatMessage objects
            req = []
            for chat_message in data:
                if (chat_message.written_to_db is False):
                    req.append(chat_message.get_data_for_db())
                    chat_message.written_to_db = True
            
            if (not len(req)):
                return

            result = messages_collection.insert_many(req).inserted_ids
            print(f'# message write requests: {len(req)}')
            print(f'# actual writes = {len(result)}')
        elif (isinstance(data, ChatMessage)):
            if (data.written_to_db is False):
                data = data.get_data_for_db()
                result = messages_collection.insert_one(data)
                data.written_to_db = True

    def get_most_recent_messages(self, room_id: str, count: int, cyclic_count: cycle):
        """
            Gets the most recent messages in a particular chat room.
        """
        # the _id field in MongoDB has a timestamp component to it, so the collection should be sorted by
        # insertion order
        # if we have a timestamps [1,2,3,4,5,6,7,8,9] and we want to get the 5 most recent messages
        # the first sort returns [9,8,7,6,5] and the second sort will return [5,6,7,8,9]
        result_cursor = messages_collection.aggregate([
            {"$match": {
                "room_id": room_id
            }},
            {"$sort": {
                "_id": -1
            }},
            {"$limit": count},
            {"$sort": {
                "_id": 1
            }}
        ])
        # build a list of chat message objects
        chat_messages = []
        i = 0
        for doc in result_cursor:
            chat_message = ChatMessage(next(cyclic_count), doc["timestamp"], doc["content"], doc["sender"],
                                       doc["room_id"], True)
            chat_messages.append(chat_message)
            i += 1
        return chat_messages


if __name__ == "__main__":
    # TEST CODE
    message_handler = MessageHandler()
    content = ["hello", "hi", "hey", "good morning", "afternoon", "evening", "night", "summer", "winter", "rain",
               "autumn", "i love summer"]
    data = []
    for msg in content:
        chat_msg = ChatMessage(0, datetime.utcnow(), msg, "zarifmahfuz", "Room 1")
        data.append(chat_msg)
    
    # post the data
    # message_handler.write_to_db(data)

    messages = message_handler.get_most_recent_messages("Room 4", 10, cycle(range(0, 100)))
    for m in messages:
        print(m)
    # messages_collection.delete_many({})
