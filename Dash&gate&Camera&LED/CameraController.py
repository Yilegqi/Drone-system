import cv2 as cv
import numpy as np
import paho.mqtt.client as mqtt
import base64
import time
import threading



local_broker_address =  "127.0.0.1"
local_broker_port = 1883
sendingVideoStream = False

def SendVideoStream ():
    global sendingVideoStream
    cap = cv.VideoCapture(0)
    while sendingVideoStream:
        # Read Frame
        _, frame = cap.read()
        # Encoding the Frame
        _, buffer = cv.imencode('.jpg', frame)
        # Converting into encoded bytes
        jpg_as_text = base64.b64encode(buffer)
        # Publishig the Frame on the Topic home/server
        client.publish('cameraControllerAnswer/videoFrame', jpg_as_text)
    cap.release()

def takepic():
    cap = cv.VideoCapture(0)  # video capture source camera (Here webcam of laptop)
    for n in range(10):
        # this loop is required to discard first frames
        ret, frame = cap.read()
        _, buffer = cv.imencode('.jpg', frame)
        # Converting into encoded bytes
        jpg_as_text = base64.b64encode(buffer)
        client.publish('cameraControllerAnswer/picture', jpg_as_text)

def takepicwithfr():
    cap = cv.VideoCapture(0)
    for n in range(10):
        ret, frame = cap.read()
        image = frame
        faceCascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.1, minNeighbors = 5, minSize = (30, 30))

        for (x, y, w, h) in faces:
            cv.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv.imwrite('aaa.jpg', image)
        _, buffer = cv.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer)
        client.publish('cameraControllerAnswer/picturewithFaceRecognition', jpg_as_text)



def on_message(client, userdata, message):
    global sendingVideoStream
    if message.topic == 'connectPlatform':
        print('Camera controller connected')
        client.subscribe('cameraControllerCommand/+')

    if message.topic == 'cameraControllerCommand/takePicture':
        print('Take picture')
        takepic()
        client.publish('LEDsControllerCommand/LEDsSequenceWhenRecognizePicture')

    if message.topic == 'cameraControllerCommand/takePicturewithFaceRecognition':
        print('Take picture with face recognition')
        takepicwithfr()
        client.publish('LEDsControllerCommand/LEDsSequenceWhenRecognizePicture')

    if message.topic == 'cameraControllerCommand/startVideoStream':
        sendingVideoStream = True
        w = threading.Thread(target=SendVideoStream)
        w.start()

    if message.topic == 'cameraControllerCommand/stopVideoStream':
        sendingVideoStream = False




client = mqtt.Client("Camera controller")
client.on_message = on_message
client.connect(local_broker_address, local_broker_port)
client.loop_start()
print ('Waiting connection from DASH...')
client.subscribe('connectPlatform')
