import socket
import cv2
import zmq
import base64
import numpy as np

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,)
client.connect(("127.0.0.1", 1234))

