from flask import Flask
from flask_login import LoginManager
from ssh_pymongo import MongoSession
from flask_pymongo import PyMongo
import gridfs

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config["SECRET_KEY"] = "secretkey"
app.config["MONGO_URI"] = "mongo uri"
session = MongoSession("server",
    port="port",
    user="user",
    password="password",
    uri="uri"
)
db = session.connection["flask_db"]

mongo = PyMongo(app)
grid_fs = gridfs.GridFS(db)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


from .views import views
from .auth import auth

app.register_blueprint(views, url_prefix="/")
app.register_blueprint(auth, url_prefix="/")

from .models import User

@login_manager.user_loader
def load_user(user_id):
    user = db["users"].find_one({"_id": user_id})
    if user is not None:
        return User(user["username"], user["password"], user["_id"])
    else:
        return None
