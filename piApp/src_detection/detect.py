import RPi.GPIO as GPIO
import time
import cv2
import piexif
from datetime import datetime
import src_detection.recognize_faces_image as recog

def run():
    # set the GPIO mode to Broadcom SOC channel
    GPIO.setmode(GPIO.BCM)
    # set the input pin number as 4 
    GPIO.setup(4, GPIO.IN)
    # start the video capture from the camera connected with the raspberry pi
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    count = 0

    while True:
        motion = GPIO.input(4)
        if motion == 1:
            print("true")
            for i in range(5):
                ret, frame = cap.read()
                frame = cv2.flip(frame, -1)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                print(f"[INFO] Picture {i+1} taken.")
                # check if the frame is successfully captured
                if ret:
                    # get the current date and time in the format "YYYY:MM:DD HH:MM:SS"
                    date_time = (datetime.now()).strftime("%d/%m/%Y %H:%M:%S")
                    # write the captured frame to the file "pics_taken/image_<count>.jpg"
                    cv2.imwrite(f"pics_taken/image_{count}.jpg", frame)
                    # load the exif data of the image
                    exif_dict = piexif.load(f"pics_taken/image_{count}.jpg")
                    # set the exif data "DateTimeOriginal" with the current date and time
                    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_time
                    # insert the modified exif data to the image
                    piexif.insert(piexif.dump(exif_dict), f"pics_taken/image_{count}.jpg")
                time.sleep(1)
                count += 1
            recog.run()
            time.sleep(5)
