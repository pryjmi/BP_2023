import os
import glob
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, current_user
from website import db
from . import app
from .models import User

auth = Blueprint("auth", __name__)

def log(timedate, message):
    """
    Function that writes a user log in JSON format to the database.
    """
    db["user_logs"].insert_one({
        "timedate": timedate,
        "message": message
    })

@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    View displaying the login page.
    
    Allows logging into application by entering a username
    and password (if they are correct).
    
    Returns:
        render_template (HTML): Login page with form.
    """
    if request.method == "POST":
        session["last_active"] = datetime.now().astimezone()
        session.permanent = True
        username = request.form["username"]
        password = request.form["password"]
        find_user = db["users"].find_one({"username": username})

        if find_user:

            if User.login_valid(username, password):
                loguser = User(find_user["username"], find_user["password"], find_user["_id"])
                login_user(loguser, remember=False)
                log(datetime.now().strftime('%d/%m/%Y %H:%M:%S'),\
                    f"User {username} logged in successfully.")
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password", "error")
        else:
            flash("User doesn't exist", "error")

    return render_template("login.html", user=current_user)

@auth.route("/logout")
def logout():
    """
    View displaying the login page.

    Allows the user to log out.

    Returns:
        redirect (HTML): Login page with a form.
    """
    session.pop("user", None)

    try:
        user = current_user.username
    except AttributeError:
        user = ""

    log(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), f"User {user} logged out.")
    logout_user()
    images_dir = glob.glob("/srv/www/html/app/images/*")

    for file in images_dir:
        os.remove(file)

    return redirect(url_for("auth.login"))

@auth.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    """
    View displaying the sign up page.

    Allows new user to register if they do not already exist.
    After registration, they are redirected to the home view.

    Returns:
        render_template (HTML): Sign up page with a form.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"], method="sha256")
        find_user = User.get_by_username(username)

        if find_user is None:
            User.sign_up(username, password, None)
            log(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), f"User {username} created.")
            return redirect(url_for("views.home"))

    return render_template("sign_up.html")

@app.before_request
def before_request():
    """
    Function that checks user activity.

    If the user has been inactive for the last 60 minutes (POST / GET requests),
    they will be logged out.

    Returns:
        logout() (funkce): Userl logout (Flask function).
    """
    try:
        last_active = session["last_active"]
        delta = datetime.now().astimezone() - last_active

        if delta.seconds > 3600:
            session["last_active"] = datetime.now().astimezone()
            return logout()

    except KeyError:
        print("User is using Chrome.")