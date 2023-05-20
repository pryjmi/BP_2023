import codecs
import contextlib
import json
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from .models import User
from . import db, mongo, grid_fs

views = Blueprint("views", __name__)

class Create_dict(dict):
    """Class full filled with multiple dictionaries.

    Args:
        dict (_type_): _description_
    """
    def __init__(self):
        self = {}
    def add(self, key, value):
        self[key] = value

def log(timedate, message, collection):
    """Saves log strings to database.

    Args:
        timedate (str): Date and time of the log.
        message (str): Message of the log.
        collection (str): Chooses in which database collection is log saved.
    """
    db[collection].insert_one({
        "timedate": timedate,
        "message": message
    })

def remove_user(username, password):
    """Removes user if user is not current_user and if theirs password was correct.
    Removes from database.

    Args:
        username (str): Username of the to-be-deleted user.
        password (str): Password of the to-be-deleted user.
    """
    if username == current_user.username:
        flash("Cannot delete current user.")
    elif check_password_hash(current_user.password, password):
        db["users"].delete_one({"username": username})
        log(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), f"User {username} deleted.", "user_logs")
    else:
        flash("Cannot delete user, incorrect password.")

def add_user(username, password):
    """Adds/creates user by calling functions from class User.

    Args:
        username (str): Inserted username.
        password (str): Inserted password.
    """
    if len(username) < 1:
        flash("Cannot create user, username field is empty.")
    elif len(password) < 1:
        flash("Cannot create user, password field is empty.")
    else:
        password = generate_password_hash(password, method="sha256")
        find_user = User.get_by_username(username)

        if find_user is None:
            User.sign_up(username, password, None)
            log(datetime.now().strftime('%d/%m/%Y %H:%M:%S'),\
                f"User {username} created.", "user_logs")
        else:
            flash("Cannot create user, user already exists.")

def display_users():
    """Finds all users usernames in database.

    Returns:
        list: List of MongoDB documents -> all users usernames.
    """
    cursor = db["users"].find({}, {"username":1, "_id":0})
    return [doc["username"] for doc in cursor]

def display_files():
    """Finds all images names in database.

    Returns:
        list: List of MongoDB documents -> all images names.
    """
    cursor = db["fs.files"].find({}, {"filename":1, "_id":0})
    return [doc["filename"] for doc in cursor]

def display_images(type):
    """Finds all images in database, puts them temporalily in folder on server.
    HTML view loads them up from there.

    Returns:
        list: List of images names with their path.
    """
    res_image = ""
    res_name = ""
    res_date = ""
    if type == "known":
        cursor = db["pi_files"].find({"name": {"$nin": ["unknown", "no_face"]}}).sort([("captured", -1)]).limit(1)
    elif type == "unknown":
        cursor = db["pi_files"].find({"name": "unknown"}).sort([("captured", -1)]).limit(1)
    elif type == "no":
        cursor = db["pi_files"].find({"name": "no_face"}).sort([("captured", -1)]).limit(1)
    else:
        print("Wrong argument.")
    for item in cursor:
        chunks = db["pi_chunks"].find({"files_id": item["_id"]}).sort("n")
        file_data = b"".join([chunk["data"] for chunk in chunks])
        filename = item["filename"]
        image_loc = f"/srv/www/html/app/images/{filename}"
        with open(image_loc, "wb") as output:
            output.write(file_data)
        res_image = f"images/{filename}"
        res_name = item["name"]
        res_date = item["captured"]
    return res_image, res_name, res_date

def load_files():
    files = []
    cursor = db["fs.files"].find({})
    for item in cursor:
        file = grid_fs.get(item["_id"])
        filename = item["filename"]
        file_bin = file.read()
        file_loc = f"/srv/www/html/app/images/{filename}"
        with open(file_loc, "wb") as output:
            output.write(file_bin)
        files.append(f"images/{filename}")
    return files


@views.route("/", methods=["GET", "POST"])
@login_required
def main():
    """Main page view, loads up after successful login. Redirects to Home page.

    Returns:
        function: Flask function, redirects to different view.
    """

    return redirect(url_for("views.home"))

@views.route("/home", methods=["GET", "POST"])
@login_required
def home():
    """Home page view, substitute to main page.

    Returns:
        function: Flask function, renders template with parameters needed for Jinja.
    """
    user_list = display_users()
    file_list = display_files()
    #files = load_files()
    known_face, known_name, known_date = display_images("known")
    unknown_face, unknown_name, unknown_date = display_images("unknown")
    no_face, no_name, no_date = display_images("no")

    if request.method in ["GET", "POST"]:
        session["last_active"] = datetime.now().astimezone()

    if request.method == "POST":
        if request.form.get("btn-create-usr") == "   Add user    ":
            username = request.form.get("username-input-create")
            password = request.form.get("password-input-create")
            add_user(username, password)

        if request.form.get("btn-remove-usr") == "Remove user":
            username = request.form.get("username-input")
            password = request.form.get("password-input")
            remove_user(username, password)

        if request.form.get("btn-dw-known") == "Download":
            with contextlib.suppress(Exception):
                known_face = known_face.split("/")[1]
                return download(known_face)

        if request.form.get("btn-dw-unknown") == "Download":
            with contextlib.suppress(Exception):
                unknown_face = unknown_face.split("/")[1]
                return download(unknown_face)

        if request.form.get("btn-dw-no") == "Download":
            with contextlib.suppress(Exception):
                no_face = no_face.split("/")[1]
                return download(no_face)

        """
        if request.form.get("file-btn-dw"):
            filename = request.form.get("file-btn-dw")
            return download(filename)
            """

        if request.form.get("file-btn-del"):
            filename = request.form.get("file-btn-del")
            item = db["fs.files"].find_one({"filename": filename})
            db["fs.chunks"].delete_many({"files_id": item["_id"]})
            db["fs.files"].delete_one({"_id": item["_id"]})
            log(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), \
                f"User {current_user.username} deleted file {filename}.", "user_logs")
            log(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), \
                f"File {filename} was removed from database.", "db_logs")

    return render_template("home.html", user=current_user, user_list=user_list, file_list=file_list, known_face=known_face,\
        unknown_face=unknown_face, no_face=no_face, known_name=known_name, known_date=known_date, unknown_name=unknown_name,\
            unknown_date=unknown_date, no_name=no_name, no_date=no_date)

@views.route("/dat_logs", methods=["GET", "POST"])
@login_required
def dat_logs():

    """Database page view, loads Database page.

    Returns:
        function: Flask function, renders template with parameters needed for Jinja.
    """
    user_list = display_users()
    file_list = display_files()

    image = ""

    if request.method in ["GET", "POST"]:
        session["last_active"] = datetime.now().astimezone()

    if request.method == "POST":
        if request.form.get("btn-create-usr") == "   Add user    ":
            username = request.form.get("username-input-create")
            password = request.form.get("password-input-create")
            add_user(username, password)

        if request.form.get("btn-remove-usr") == "Remove user":
            username = request.form.get("username-input")
            password = request.form.get("password-input")
            remove_user(username, password)

    """Logs page view, loads Logs page.

    Returns:
        function: Flask function, renders template with parameters needed for Jinja.
    """
    user_list = display_users()
    user_logs = []
    db_logs = []
    detection_logs = []

    if request.form.get("btn-show-logs") == "Show logs":
        number = request.form.get("log-number-input")
        logs_ = []

        if number in ["", "0"]:
            cursor = []
        else:
            cursor = db["user_logs"].find().sort("_id", -1).limit(int(number))
            logs_ = []
            for doc in cursor:
                time = doc["timedate"]
                message = doc["message"]
                logs_.append(f"{time} | {message}")
        user_logs = logs_
    else: user_logs = []

    if request.form.get("btn-log-all") == "Show all logs":
        return redirect(url_for("views.logs_all", logs="user_logs"))

    if request.form.get("btn-show-logs-db") == "Show logs":
        number = request.form.get("log-number-input-db")
        logs_ = []
        if number in ["", "0"]:
            cursor = []
        else:
            cursor = db["db_logs"].find().sort("_id", -1).limit(int(number))
            logs_ = []
            for doc in cursor:
                time = doc["timedate"]
                message = doc["message"]
                logs_.append(f"{time} | {message}")
        db_logs = logs_
    else: db_logs = []

    if request.form.get("btn-log-all-db") == "Show all logs":
        return redirect(url_for("views.logs_all", logs="db_logs"))

    if request.form.get("btn-show-logs-det") == "Show logs":
        number = request.form.get("log-number-input-det")
        logs_ = []

        if number in ["", "0"]:
            cursor = []
        else:
            cursor = db["pi_files"].find().sort("captured", -1).limit(int(number))
            logs_ = []
            for doc in cursor:
                time = doc["captured"]
                name = doc["name"]
                logs_.append(f"{time} | System captured: {name}")
        detection_logs = logs_
    else: detection_logs = []

    if request.form.get("btn-log-all-det") == "Show all logs":
        return redirect(url_for("views.logs_all", logs="detection_logs"))

    return render_template("dat_logs.html", \
        user=current_user, user_logs=user_logs, user_list=user_list, db_logs=db_logs, file_list=file_list, detection_logs=detection_logs)

@views.route("/logs_all")
@login_required
def logs_all():
    """Displays all logs from specific collection in HTML page. Converted to true JSON format.

    Returns:
        function: Flask function, renders template with parameters needed for Jinja.
    """
    dictionary = Create_dict()
    logs_ = request.args["logs"]
    cursor = db[logs_].find({},).sort("_id", -1)
    list_json = [
        {
            "_id": str(doc["_id"]),
            "timedate": doc["timedate"],
            "message": doc["message"],
        }
        for i, doc in enumerate(cursor, start=1)
    ]
    json_ = json.dumps(list_json, indent=2, sort_keys=True)

    return render_template("logs_all.html", user=current_user, logs=json_)

@views.route("/database", methods=["GET", "POST"])
@login_required
def database():
    """Database page view, loads Database page.

    Returns:
        function: Flask function, renders template with parameters needed for Jinja.
    """
    user_list = display_users()

    image = ""

    if request.method in ["GET", "POST"]:
        session["last_active"] = datetime.now().astimezone()

    if request.method == "POST":
        if request.form.get("btn-create-usr") == "   Add user    ":
            username = request.form.get("username-input-create")
            password = request.form.get("password-input-create")
            add_user(username, password)

        if request.form.get("btn-remove-usr") == "Remove user":
            username = request.form.get("username-input")
            password = request.form.get("password-input")
            remove_user(username, password)

        """if request.form.get("file-btn"):
            filename = request.form.get("file-btn")
            item = db["fs.files"].find_one({"filename": filename})
            image = grid_fs.get(item["_id"])
            base64_data = codecs.encode(image.read(), "base64")
            image = base64_data.decode("utf-8")"""

        if request.form.get("file-btn-dw"):
            filename = request.form.get("file-btn-dw")
            return download(filename)

        if request.form.get("file-btn-del"):
            filename = request.form.get("file-btn-del")
            item = db["fs.files"].find_one({"filename": filename})
            db["fs.chunks"].delete_many({"files_id": item["_id"]})
            db["fs.files"].delete_one({"_id": item["_id"]})
            log(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), \
                f"User {current_user.username} deleted file {filename}.", "user_logs")
            log(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), \
                f"File {filename} was removed from database.", "db_logs")

    return render_template("database.html", \
        user=current_user, user_list=user_list)

@views.route("/upload", methods=["POST"])
@login_required
def upload():
    """Uploads image files from users computer and saves them to database.

    Returns:
        function: Flask function redirect -> redirects back to Database view.
    """
    if "image" in request.files:
        #image = request.files["image"]
        images = request.files.getlist("image")
        suffix = (".jpg", ".jpeg", ".gif", ".png", ".svg")

        for image in images:
            if image.filename.endswith(suffix):
                grid_fs.put(image, filename=image.filename)
                log(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), \
                    f"User {current_user.username} uploaded file {image.filename}.", "user_logs")
                log(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), \
                    f"File {image.filename} was added to database.", "db_logs")
            else:
                flash("You can upload only images (JPEG, GIF, PNG, SVG)")

    return redirect(url_for("views.home"))

@views.route("/download/<filename>")
@login_required
def download(filename):
    """Downloads image through nginx from server's temporary folder.

    Args:
        filename (str): Image name (with suffix).

    Returns:
        function: redirect -> redirects to Download view with image name -> image is downloading.
    """
    return redirect(url_for("views.download", filename=filename))
