import pymongo
import time

def get_db():
    retries = 5
    while True:
        try:
            client = pymongo.MongoClient(host="datastore", port=27017)
            db = client["chat_db"]
            return db
        except pymongo.errors.ConnectionFailure as e:
            if retries == 0:
                raise e
            retries -= 1
            time.sleep(0.5)

db = get_db()
users_collection = db["Users"]
rooms_collection = db["Rooms"]
messages_collection = db["Messages"]
