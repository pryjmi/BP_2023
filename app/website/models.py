import uuid
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from flask import session
from . import db

class User(UserMixin):
    """
    User class.

    Attributes:
            username (string): User's name.
            password (string, sha256): User's password, hashed using sha256.
            _id (uuid.hex): User's id.
    """
    def __init__(self, username, password, _id):
        """
        User constructor.

        Parameters:
            username (string): User's name.
            password (string, sha256): User's password, hashed using sha256.
            _id (uuid.hex): User's id.
        """
        self.username = username
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @property
    def is_authenticated(self):
        """
        Returns True if the user is logged in.
        """
        return True
    @property
    def is_active(self):
        """
        Returns True if the user is logged in.
        """
        return True
    @property
    def is_anonymous(self):
        """
        Returns False if the user is logged in.
        """
        return False
    def get_id(self):
        """
        Returns the id of the user.
        """
        return self._id

    @classmethod
    def get_by_username(cls, username):
        """
        Function that returns user data obtained from the database.

        The function finds user data using a PyMongo query with the username key.
        If the data is not None, the function returns the data.

        Attributes:
            data (MongoDB cursor): User data stored in the database.

        Parameters:
            username (string): User's name.

        Returns:
            data (MongoDB cursor): User data stored in the database.
        """
        data = db["users"].find_one({"username": username})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        """
        Function that returns user data obtained from the database.

        The function finds user data using a PyMongo query with the _id key.
        If the data is not None, the function returns the data.

        Attributes:
            data (MongoDB cursor): User data stored in the database.

        Parameters:
            _id (uuid.hex): User's id.

        Returns:
            data (MongoDB cursor): User data stored in the database.
        """
        data = db["users"].find_one({"_id": _id})
        if data is not None:
            return cls(**data)

    @classmethod
    def login_valid(cls, username, password):
        """
        Function that checks if the user exists and if the password is correct.

        The function checks if the user exists, then compares the entered password
        with the stored password.
        If they match, the function returns True, otherwise False.

        Parameters:
            username (string): User's name.
            password (string, sha256): User's password, hashed using sha256.

        Returns:
            True / False.
        """
        verify_user = User.get_by_username(username)
        if verify_user is not None:
            return check_password_hash(verify_user.password, password)
        return False

    @classmethod
    def sign_up(cls, username, password, _id):
        """
        Function that creates new users.

        The function checks if the given user exists, if it is None,
        it creates it and returns True, otherwise it returns False.

        Parameters:
            username (string): User's name.
            password (string, sha256): User's password, hashed using sha256.
            _id (uuid.hex): User's id.

        Returns:
            True / False.
        """
        user = cls.get_by_username(username)
        if user is None:
            new_user = cls(username, password, _id)
            new_user.save_to_mongo()
            session["user"] = username
            return True
        else:
            return False

    def json(self):
        """
        Function that saves data into JSON format.

        Returns:
            JSON format uof user data.
        """
        return {
            "_id": self._id,
            "username": self.username,
            "password": self.password
        }

    def save_to_mongo(self):
        """
        Function that saves user data in JSON format to the database.
        """
        db["users"].insert_one(self.json())