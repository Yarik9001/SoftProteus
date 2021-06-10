import socket
import cv2
import zmq
import base64
import numpy as np


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
server.bind(("192.168.1.102", 1234))
server.listen()
print("Server is start and listening")

capture  = cv2.VideoCapture(0)

while True:
    ret, im = capture.read()
    im = cv2.resize(im, (640, 480))
    im = cv2.flip(im, 1)
    encoded, buf = cv2.imencode('.jpg', im)
    image = base64.b64encode(im)
    server.send(image)
    