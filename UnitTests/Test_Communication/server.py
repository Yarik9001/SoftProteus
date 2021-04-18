import socket
import threading
from datetime import datetime
from time import sleep


class ServerMainPult:
    '''
    Класс описывающий систему управления роботом 
    '''

    def __init__(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        server.bind(("127.0.0.1", 1234))
        server.listen()
        print("Server is start and listening")
        # обмен преветсвиями
        self.user_socket, self.address = server.accept()
        data = self.user_socket.recv(256)
        self.user_socket.send('Connect-Pult1-25'.encode("utf-8"))
        print(data.decode("utf-8"))
        # инициализация потоков приема и передачи
        receiver = threading.Thread(
            target=ServerMainPult.ReceiverProteus, args=(self,))
        dispatch = threading.Thread(
            target=ServerMainPult.ControlProteus, args=(self,))
        dispatch.start()
        receiver.start()

    def ReceiverProteus(self):
        '''
        Прием информации с аппарата
        '''
        while True:
            data = self.user_socket.recv(1024).decode('utf-8')
            print(data)

    def ControlProteus(self):
        '''
        Отправка управляющей информации на аппарат 
        '''
        while True:
            timecontrol = str(datetime.now())
            massControl = {'time': timecontrol, 'x': 0, 'y': 0, 'z': 0, 'led': False,
                            'manipul': 0, 'servo-x1': 0, 'servo-y1': 0, 'servo-x2': 0, 'servo-y2': 0}
            # TODO сделать опрос джойстика или других управляющих приблуд

            outmass = str(massControl).encode('utf-8')
            self.user_socket.send(outmass)
            sleep(0.1)


if __name__ == '__main__':
    Proteus = ServerMainPult()
