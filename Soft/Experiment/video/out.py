import base64
import cv2
import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect('tcp://192.168.1.102:7777')

camera = cv2.VideoCapture(0)

while True:
    try:
        ret, frame = camera.read()
        frame = cv2.resize(frame, (640, 480))
        encoded, buf = cv2.imencode('.jpg', frame)
        image = base64.b64encode(buf)
        socket.send(image)
    except KeyboardInterrupt:
        camera.release()
        cv2.destroyAllWindows()
        break