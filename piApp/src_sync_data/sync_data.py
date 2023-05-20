import gridfs
import pickle
import os
import time
import datetime
import mimetypes
import piexif
import pymongo
from sshtunnel import SSHTunnelForwarder
import src_sync_data.datasets.encode_faces as encode

# load the password from binary file
def load_password(password_file):
    with open(password_file, "rb") as f:
        return pickle.load(f)

# connect to a server and MongoDB databse
def connect(password):
    connected = False
    while not connected:
        try:
            # make a SSH bridge and mount the server as localhost
            server = SSHTunnelForwarder(
                ssh_address_or_host=("server", "port"),
                ssh_username="username",
                ssh_password="password",
                remote_bind_address=("address", "port")
            )
            server.start()
            # connect to the database on localhost (mounted server)
            client = pymongo.MongoClient(
                "mongo_uri", 
                server.local_bind_port,
                socketTimeoutMS=5000
                )
            # connect to the database and collections, using GridFS for file storage
            db = client["flask_db"]
            grid_fs = gridfs.GridFS(db)
            files_col = db["pi_files"]
            chunks_col = db["pi_chunks"]
            print("[INFO] Connected successfully.")
            connected = True
            return client, db, grid_fs, files_col, chunks_col
        except Exception as e:
            print("[ERROR] Cannot connect to the database.", e)
            print("[INFO] Trying again in 10 seconds.")
            time.sleep(10)

# fetching data (images of faces) from the database
def fetch_data(db, grid_fs, data_fetch):
    try:
        cursor = db["fs.files"].find({})
    except Exception as e:
        print("[ERROR] Could not load the cursor.", e)
    try:
        # if there are files in the database, fetch them
        files = False
        for item in cursor:
            files = True
            file = grid_fs.get(item["_id"])
            filename = item["filename"]
            file_bin = file.read()
            file_loc = f"{data_fetch}/{filename}"
            with open(file_loc, "wb") as f:
                f.write(file_bin)
        if (files):
            print("[INFO] Data fetched successfully.")
            db["fs.files"].delete_many({})
            encode.run()
        else:
            print("[INFO] No data to fetch.")
    except Exception as e:
        print("[ERROR] Could not fetch the data.", e)

# storing data (detected / recognized faces, results) in the database
def store_data(files_col, chunks_col, data_store):
    files = [x for x in os.listdir(data_store) if not x.startswith(".")]
    if files:
        try:
            # if there are files in the data_store folder, upload them
            for file in files:
                file_loc = f"{data_store}/{file}"
                # get the date and time of the image capture and the name of the person
                date_time = (piexif.load(file_loc))["Exif"][piexif.ExifIFD.DateTimeOriginal]
                user_comment = (piexif.load(file_loc))["Exif"][piexif.ExifIFD.UserComment]
                date_time = date_time.decode('utf-8').strip("'")
                name = user_comment.decode("utf-8").rstrip('\x00')
                # data is split into chunks and each chunk is stored as a document in the chunks collection.
                # additional metadata such as filename, contentType, chunkSize, length, uploadDate, captured, and name is stored in the files collection.
                # works the same way as GridFS
                with open(file_loc, "rb") as f:
                    f_data = f.read()
                    content_type = mimetypes.guess_type(f.name)[0]
                    chunk_size = 255 * 1024
                    chunks = [f_data[i:i + chunk_size] for i in range(0, len(f_data), chunk_size)]
                    file_id = files_col.insert_one({
                        "filename": file,
                        "contentType": content_type,
                        "chunkSize": chunk_size,
                        "length": len(f_data),
                        "uploadDate": datetime.datetime.now(),
                        "captured": date_time,
                        "name": name
                    }).inserted_id
                    for n, chunk in enumerate(chunks):
                        chunks_col.insert_one({
                            "files_id": file_id,
                            "n": n,
                            "data": chunk
                            }).inserted_id
                # remove the file from the data_store folder, so it doesn't get uploaded again
                os.remove(file_loc)
                print(f"[INFO] File {file} uploaded successfully.")
        except Exception as e:
            print("[ERROR] Could not upload file to database.", e)
    else:
        print("[INFO] No files to upload.")

# check if the connection to the database is still active
def check_connection(client):
    try:
        # ping the database
        client.admin.command("ping")
        print("---ping---")
        return True
    except pymongo.errors.ConnectionFailure as e:
        # if the connection is lost, return False
        print("[ERROR] Connection lost.", e)
        client.close()
        return False

def run():
    # main loop
    password = load_password("src_sync_data/server_password")
    data_store = "data_store"
    data_fetch = "data_fetch"
    client, db, grid_fs, files_col, chunks_col = connect(password)
    # check the connection every 5 minutes
    while True:
        # if the connection is lost, reconnect
        if not check_connection(client):
            client, db, grid_fs, files_col, chunks_col = connect(password)
        # fetch and store data
        fetch_data(db, grid_fs, data_fetch)
        store_data(files_col, chunks_col, data_store)
        print("[INFO] End of cycle.")
        time.sleep(300)
