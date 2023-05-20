import face_recognition
import pickle
import cv2
import imutils
import os
import piexif
import numpy as np

# Function to set up files and directories the algorithm works with
def set_up():
    # Load the embeddings from the pickle file.
    encodings_file = "./src_sync_data/datasets/encodings.pkl"
    # Get the list of images from the image directory.
    image_dir = "pics_taken"
    images = [f"{image_dir}/{image}" for image in os.listdir(image_dir) if not image.startswith(".")]
    # Set destination directory.
    final_dir = "data_store"
    return encodings_file, images, final_dir

# Function to load face encodings from a pickled file
def load_embeddings(encodings_file):
    print("[INFO] Loading embeddings.")
    data = {}
    # Open the pickled file and unpack the encodings and names
    with open(encodings_file, "rb") as f:
        while True:
            try:
                # Load the data from the file
                dictionary = pickle.load(f)
                # Add the data to the data dictionary
                for k, v in dictionary.items():
                    data.setdefault(k, []).extend(v)
            except EOFError:
                # End the loop when the end of the file is reached
                break
    # Return the data dictionary
    return data

# Function to write exif information to an image file
def write_exif(file, date_time, user_comment):
    # Encode the user comment in utf-8
    name_bytes = user_comment.encode("utf-8") + b'\x00'
    # Load the exif information from the file
    exif_dict = piexif.load(file)
    # Update the date time original and user comment fields
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_time
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = name_bytes
    # Write the updated exif information back to the file
    piexif.insert(piexif.dump(exif_dict), file)

# Function to save the recognized faces to a file
def save_file(file, dir, date_time, image, final_dir):
    # If a file with the same name already exists
    if f"{file}.jpg" in dir:
        i = 1
        # Add a suffix to the file name to make it unique
        while True:
            file_new = f"{file}_{str(i)}"
            if f"{file_new}.jpg" not in dir:
                cv2.imwrite(f"{final_dir}/{file_new}.jpg", image)
                write_exif(f"{final_dir}/{file_new}.jpg", date_time, file)
                break
            i += 1
    # If the file does not already exist
    else:
        cv2.imwrite(f"{final_dir}/{file}.jpg", image)
        write_exif(f"{final_dir}/{file}.jpg", date_time, file)

# Function to recognize the faces in an image
def recognize(image_name, data, final_dir, count):
    # Load the input image and convert it from BGR to RGB.
    image = cv2.imread(image_name)
    #image = imutils.resize(image, width=600)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Extract the original date and time of the image using the piexif library.
    date_time = (piexif.load(image_name))["Exif"][piexif.ExifIFD.DateTimeOriginal]

    # Detect the (x, y) coordinates of the bounding boxes corresponding to each face in the input image
    # and then compute embeddings for each face.
    boxes = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, boxes)
    recognized = [x for x in os.listdir(final_dir) if not x.startswith(".")]
    
    # If there are no faces in the image, save the image with the label "no_face".
    if not boxes:
        no_face = "no_face"
        save_file(no_face, recognized, date_time, image, final_dir)
        os.remove(image_name)
        print(f"[INFO] Recognized: {no_face}")
        return

    # Initialize the list of names for each detected face.
    names = []

    # Loop over the embeddings.
    for encoding in encodings:
        # Attempt to match each face in the input image to a known encoding.
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "unknown"

        # If there is a match, find the index of all matching faces
        # and initialize a dictionary to count the total number of times the face was matched.
        if np.any(matches):
            matchedIdxs = np.argwhere(matches)
            counts = {}

            # Loop over the matched indices and count the number of occurrences.
            for i in matchedIdxs:
                name = data["names"][i[0]]
                counts[name] = counts.get(name, 0) + 1

            # Determine the recognized face with the highest count.
            # In case of a tie, the first face from the dictionary is selected.
            name = max(counts, key=counts.get)

        # Update the list of names.
        names.append(name)

    # Loop over the recognized faces.
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # Crop the image to the bounding box of the recognized face.
        rect_img = image[top:bottom, left:right]
        save_file(name, recognized, date_time, rect_img, final_dir)

    os.remove(image_name)
    print(f"[INFO] Recognized: {name}")
    print("[INFO] Image processed.")

# Run the algorithm.
def run():
    encodings_file, images, final_dir = set_up()
    data = load_embeddings(encodings_file)
    for count, image in enumerate(images, start=1):
        recognize(image, data, final_dir, count)
