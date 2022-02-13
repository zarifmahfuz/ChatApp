import requests
import json

class LoginHandler(object):
    """
        Talks to the webserver to verify login information of a user.
    """
    def __init__(self):
        self.api_endpoint = "http://webserver:5000/users"

    def verify_user(self, user_id: str, password: str) -> bool:
        """
            Verfies user credentials.
        """
        user_id = user_id.replace(" ", "%20")
        password = password.replace(" ", "%20")
        request_url = self.api_endpoint + "/" + user_id + "?password=" + password
        res = requests.get(request_url)
        if (res.status_code == 200):
            return True
        elif (res.status_code == 404):
            print("Invalid userid")
            return False
        elif (res.status_code == 401):
            print("Invalid password")
            return False
        return False

    def register_user(self, user_id: str, password: str, name: str, email: str = "") -> bool:
        """
            Registers a new user.
        """
        payload = {
            "userId": user_id,
            "password": password,
            "name": name,
            "email": email
        }
        headers = {"Content-Type": "application/json"}
        res = requests.post(self.api_endpoint, headers=headers, data=json.dumps(payload))
        if (res.status_code == 201):
            return True
        elif (res.status_code == 409):
            print(f'A user with userid {user_id} already exists.')
            return False
        print(res.json())
        return False

if __name__ == "__main__":
    obj = LoginHandler()
    if (obj.verify_user("zrifmahfuz", "passord") is True):
        print("login successful")

    if obj.register_user("helloworld", "password", "Hello World") is True:
        print("registration successful")