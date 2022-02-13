import requests
import json

class RoomHandler(object):
    def __init__(self):
        self.api_endpoint = "http://webserver:5000/rooms"

    def get_rooms(self) -> list:
        """
            Returns a list of room ids.
        """
        res = requests.get(self.api_endpoint)
        rooms = []
        if res.status_code == 200:
            for doc in res.json()["response"]:
                rooms.append(doc["_id"])

        return rooms

    def join_room(self, room_id: str, user_id: str) -> bool:
        """
            Lets a user into a room.
        """
        room_id = room_id.replace(" ", "%20")   # white spaces not allowed in a url
        user_id = user_id.replace(" ", "%20")
        request_url = self.api_endpoint + "/" + room_id + "?participant=" + user_id
        res = requests.patch(request_url)
        if (res.status_code == 200):
            return True
        if (res.status_code == 404):
            print(res.json()["response"])
        return False


if __name__ == "__main__":
    obj = RoomHandler()
    print(obj.get_rooms())

    if (obj.join_room("Room 1", "zarifmahfuz")):
        print("Joined room successfully")