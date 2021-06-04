import socket
import cv2
import pickle
import struct
import threading
import pyshine as ps
import imutils
import cv2


class SocketCameraOut:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_name = socket.gethostname()
        self.host_ip = '127.0.0.1'
        print('HOST IP:', self.host_ip)
        self.port = 9999
        self.socket_address = (self.host_ip, self.port)
        self.server_socket.bind(self.socket_address)
        self.server_socket.listen()
        print("Listening at", self.socket_address)

    def show_client(self, addr, client_socket):
        try:
            print('CLIENT {} CONNECTED!'.format(addr))
            if client_socket:  # if a client socket exists
                data = b""
                payload_size = struct.calcsize("Q")
                while True:
                    while len(data) < payload_size:
                        packet = client_socket.recv(4*1024)  # 4K
                        if not packet:
                            break
                        data += packet
                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    msg_size = struct.unpack("Q", packed_msg_size)[0]

                    while len(data) < msg_size:
                        data += client_socket.recv(4*1024)
                    frame_data = data[:msg_size]
                    data = data[msg_size:]
                    frame = pickle.loads(frame_data)
                    text = f"CLIENT: {addr}"
                    frame = ps.putBText(frame, text, 10, 10, vspace=10, hspace=1, font_scale=0.7, 						background_RGB=(
                        255, 0, 0), text_RGB=(255, 250, 250))
                    cv2.imshow(f"FROM {addr}", frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                client_socket.close()
        except Exception as e:
            print(f"CLINET {addr} DISCONNECTED")
            pass

    def mainCamera(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            thread = threading.Thread(
                target=self.show_client, args=(addr, client_socket))
            thread.start()
            print("TOTAL CLIENTS ", threading.activeCount() - 1)


class SocketCameraInput:
    def __init__(self):
        self.vid = cv2.VideoCapture(0)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_ip = '192.168.1.102'
        self.port = 9999
        self.client_socket.connect((self.host_ip, self.port))

    def mainCameraIn(self):
        if self.client_socket:
            while (self.vid.isOpened()):
                try:
                    self.img, self.frame = self.vid.read()
                    self.frame = imutils.resize(
                        self.frame, width=640, height=480)
                    self.a = pickle.dumps(self.frame)
                    self.message = struct.pack("Q", len(self.a))+self.a
                    self.client_socket.sendall(self.message)
                    host_ip = self.host_ip
                    cv2.imshow(f"TO: {host_ip}", self.frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        self.client_socket.close()
                except:
                    print('VIDEO FINISHED!')
                    break


if __name__ == '__main__':
    cam = SocketCameraInput()
    cam.mainCameraIn()
