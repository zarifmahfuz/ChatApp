from email.policy import default
from flask_restful import Resource
from flask import request
from webserver.app import bcrypt
from webserver.classes.user import User
from webserver.classes.exceptions.invalid_userid import InvalidUserException

user = User()

class Users(Resource):
    def get(self, user_id):
        """
            Handles a GET request.

            Expects a "password" key in the request body.

            Returns:
                status code 404: if the given user_id does not exist
                status code 401: if invalid password was given
                status code 200: if login was successful
        """
        try:
            password = request.args.get("password", default=None, type=str)
            if password is None:
                return {"response": "password field was not given"}, 400
            
            if (user.login_user(user_id, password, bcrypt)):
                return {"response": "login successful"}, 200
            else:
                return {"response": "invalid password"}, 401
        except InvalidUserException:
            return {"response": "invalid user_id"}, 404
        except Exception as e:
            return {"response": str(e)}, 500
