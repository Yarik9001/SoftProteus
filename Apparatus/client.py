import socket
import threading
from time import sleep
from datetime import datetime


class ROVProteus:
    '''
    Класс описывающий поведение подводного аппарата
    '''

    def __init__(self, logcmd=True):
        self.HOST = "127.0.0.1"
        self.PORT = 1234
        self.logcmd =logcmd
        self.ratesensor = 0.5
        self.rate = 1

        self.startclientmain()
        

    def settingServer(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.client.connect((self.HOST, self.PORT))  # подключение адресс  порт
        # обмен приветсвиями

    
    def startmultithreading(self):
        # инициализауия потоков приема и передачи
        dispatch = threading.Thread(
            target=ROVProteus.CheckSensor, args=(self,))

        receiver = threading.Thread(
            target=ROVProteus.ReceivingCommands, args=(self,))

        dispatch.start()
        receiver.start()

    def startclientmain(self):
        # запуск бекенда сервера
        self.settingServer()
        self.hello()
        self.startmultithreading()

    def CheckSensor(self):
        '''
        Функция сбора данных с дачиков и отправки на пульт 
        '''
        while True:
            timecontrol = str(datetime.now())
            MassCheckSensor = {'time': timecontrol,
                                'dept': 0,
                                'm1': 0,'m2': 0, 'm3': 0,
                                'm4': 0, 'm5': 0, 'm6': 0,
                                'Volt': 0,
                                'error': None,
                                'danger-error':False,
                                'x':0, 'y':0,'z':0}

            # TODO опрос датчиков тока, глубины, 

            MassSensor = str(MassCheckSensor).encode("utf-8")
            self.client.send(MassSensor)
            sleep(self.ratesensor)

    def ReceivingCommands(self):
        '''
        Прием информации 
        '''
        while True:
            data = self.client.recv(1024).decode('utf-8')
            # TODO считаем и отсылаем управляющие сигналы на моторы и прочую полезную нагрузку
            if self.logcmd:
                print(data)
            
class FrontCAM:
    def __init__(self):
        pass
    # TODO реализовать опрос камер 
    
if __name__ == '__main__':
    Proteus1 = ROVProteus()
