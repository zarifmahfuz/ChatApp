from flask_restful import Resource
from webserver.database_manager import users_collection


class UsersCollection(Resource):
    def post(self):
        return {"response": "hello world"}, 200
