from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt

app = Flask(__name__)
api = Api(app)
bcrypt = Bcrypt(app)

from webserver.resources.users_collection import UsersCollection
from webserver.resources.users import Users
from webserver.resources.rooms_collection import RoomsCollection
from webserver.resources.rooms import Rooms
api.add_resource(UsersCollection, "/users")
api.add_resource(Users, "/users/<string:user_id>")
api.add_resource(RoomsCollection, "/rooms")
api.add_resource(Rooms, "/rooms/<string:room_id>")
