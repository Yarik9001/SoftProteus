import socket
import threading
from time import sleep
from datetime import datetime


class ROVProteus:
    '''
    Класс описывающий поведение подводного аппарата
    '''

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.client.connect(("127.0.0.1", 1234))  # подключение адресс  порт
        # обмен приветсвиями
        self.client.send('Connect-Proteus1-25'.encode("utf-8"))
        data = self.client.recv(256)
        print(data.decode("utf-8"))
        # инициализауия потоков приема и передачи
        dispatch = threading.Thread(
            target=ROVProteus.CheckSensor, args=(self,))
        receiver = threading.Thread(
            target=ROVProteus.ControlMotorServo, args=(self,))
        dispatch.start()
        receiver.start()

    def CheckSensor(self):
        '''
        Функция сбора данных с дачиков и отправки на пульт 
        '''
        while True:
            timecontrol = str(datetime.now())
            MassCheckSensor = {'time': timecontrol, 'dept': 0, 'm1': 0,
                                'm2': 0, 'm3': 0, 'm4': 0, 'm5': 0, 'm6': 0, 'Volt': 0}

            # TODO опрос датчиков

            MassSensor = str(MassCheckSensor).encode("utf-8")
            self.client.send(MassSensor)
            sleep(0.5)

    def ControlMotorServo(self):
        '''
        Управление моторами и сервомашинками 
        '''
        while True:
            data = self.client.recv(1024).decode('utf-8')
            print(data)
            # TODO считаем и отсылаем управляющие сигналы на моторы и прочую полезную нагрузку


if __name__ == '__main__':
    Proteus1 = ROVProteus()
