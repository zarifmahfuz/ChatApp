from flask import Flask
from flask_restful import Api
from webserver.resources.users_collection import UsersCollection

app = Flask(__name__)
api = Api(app)
api.add_resource(UsersCollection, "/users")
