import cv2
import numpy as np
import sys
import time
import urllib
import signal
import random
from keras.models import load_model
from statistics import mode
from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input

# parameters for loading data and images
emotion_model_path = './models/emotion_model.hdf5'

# hyper-parameters for bounding boxes shape
frame_window = 10
emotion_offsets = (20, 40)

# loading models
face_cascade = cv2.CascadeClassifier(
    './models/haarcascade_frontalface_default.xml')
emotion_classifier = load_model(emotion_model_path)
emotion_labels = get_labels('fer2013')

# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]

emotion_text = "noClue"
color = (128, 128, 128)


def getImg(host, color, emotion):
    print(emotion)
    print(color)

    (r, g, b) = color
    req = urllib.request.urlopen(
        url="{0}/sendcolor?r={1}&g={2}&b={3}&emotion={4}".format(host, r, g, b, emotion))
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    return img

try:
    hostWithPort = sys.argv[1]
    hostWithPort = "http://{0}".format(hostWithPort)
    if ":" not in hostWithPort:
        print("Please include the IP and port, and nothing more")
        exit()

except:
    hostWithPort = "http://172.20.10.2:8001"

count = 0

while True:
    time.sleep(1)
    try:
        bgr_image = getImg(hostWithPort, tuple(color), emotion_text.lower())
        if bgr_image.any() == None:
            print("Bad image from the Pi...")
            continue
    except:
        print("No image from Pi...")
        time.sleep(.1)
        continue

    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5,
                                          minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

    faces = sorted(faces, reverse=True, key=lambda x: x[3])

    if len(faces) == 0:
        if count == 3:
            emotion_text = "noClue"
            count = 0

            color = np.random.rand(3)

            color = color * 255

            color = color.astype(int)
            color = color.tolist()

        count += 1
        continue

    x1, x2, y1, y2 = apply_offsets(faces[0], emotion_offsets)
    gray_face = gray_image[y1:y2, x1:x2]

    try:
        gray_face = cv2.resize(gray_face, (emotion_target_size))
        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_prediction = emotion_classifier.predict(gray_face)
        emotion_probability = np.max(emotion_prediction)
        emotion_label_arg = np.argmax(emotion_prediction)
        emotion_text = emotion_labels[emotion_label_arg]
    except:
        continue

    if emotion_text == "angry":
        # Angry
        color = emotion_probability * np.asarray((255, 0, 0))
    elif emotion_text == "happy":
        # Happy
        color = emotion_probability * np.asarray((0, 255, 0))
    elif emotion_text == "sad":
        # Sad
        color = emotion_probability * np.asarray((0, 0, 255))
    else:
        # Neutral or others
        emotion_text = "noClue"
        color = emotion_probability * np.asarray((255, 255, 255))

    color = color.astype(int)
    color = color.tolist()
