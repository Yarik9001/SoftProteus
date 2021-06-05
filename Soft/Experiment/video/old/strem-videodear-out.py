# import required libraries
from vidgear.gears import NetGear
import cv2

stream = cv2.VideoCapture(0)

options = {"flag": 0, "copy": False, "track": False}

server = NetGear(
    address="127.0.0.1",
    port="5454",
    protocol="tcp",
    pattern=0,
    logging=False,
    **options
)

while True:

    try:
        (grabbed, frame) = stream.read()
        if not grabbed:
            break
        server.send(frame)

    except KeyboardInterrupt:
        break

stream.release()
server.close()