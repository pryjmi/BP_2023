from imutils import paths
import face_recognition
import pickle
import cv2
import os

def setup():
    # setup paths for directiories and pickle file (dataset)
    dataset = "./data_fetch"
    dataset_old = "./src_sync_data/datasets/dataset_old"
    pkl_file = "./src_sync_data/datasets/encodings.pkl"
    return dataset, dataset_old, pkl_file

def encode(dataset, dataset_old, pkl_file):
    # get input image paths from dataset
    print("[INFO] Quantifying faces...")
    imagePaths = list(paths.list_images(dataset))

    # initialize list of known necodings and known names
    knownEncodings = []
    knownNames = []

    # iterate over image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extract name from image file
        print(f"[INFO] Processing image {i+1}/{len(imagePaths)}", end="\r")
        name = ((imagePath.split(os.path.sep)[-1]).split(".")[0]).split("_")[0]

        # load input image and convert from BGR to RGB
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect (x, y) coordiantes of bounding boxes corresponding to each face
        boxes = face_recognition.face_locations(rgb, model="hog")

        # compute facial embeddings for the face
        encodings = face_recognition.face_encodings(rgb, boxes)

        # iterate over the encodings
        for encoding in encodings:
            # add each encoding + name to the set of known names and encodings
            knownEncodings.append(encoding)
            knownNames.append(name)

    # save facial encodings + names
    print("[INFO] Serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}

    # if the binary file exists, append new data to it
    if os.path.exists(pkl_file):
        print("[INFO] Appending to existing file")
        with open(pkl_file, "ab") as f:
            f.write(pickle.dumps(data))
    else:
        # else, create a new file
        print("[INFO] Writing to new file")
        with open(pkl_file, "wb") as f:
            f.write(pickle.dumps(data))

    images = list(os.listdir(dataset))
    num = 0
    # go through all image in the folder, rename them appropriately and move them to the dataset_old folder
    for image in images:
        # continually update the list of old images
        images_old = list(os.listdir(dataset_old))
        if not image.startswith("."):
            # name the next images according to the number of old images: 80 images -> next image will be 81.png, then 82.png, etc.
            count = len(images_old)
            ext = image.split(".")[-1]
            count += 1
            image_new = image
            while image_new in images_old:
                num += 1
                image_new = (image.split("_"))[0]
                image_new = f"{image_new}_{num}.{ext}"
            os.rename(f"{dataset}/{image}", f"{dataset_old}/{image_new}")

def run():
    dataset, dataset_old, pkl_file = setup()
    encode(dataset, dataset_old, pkl_file)