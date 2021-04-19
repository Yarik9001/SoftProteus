import socket  # модуль для взаимодействия по сети
import threading  # модуль для разделения на потоки
from datetime import datetime  # получение  времени
from time import sleep  # сон
from ast import literal_eval  # модуль для перевода строки в словарик
from pyPS4Controller.controller import Controller # модуль для работы с джойстиком ps2



class ServerMainPult:
    '''
    Класс описывающий систему бекенд пульта 
    '''

    def __init__(self, log=True, logcmd=True):
        # init variable
        self.HOST = "127.0.0.1"
        self.PORT = 1234
        self.JOYSTICKRATE = 0.1
        self.MotorPowerValue = 1
        self.massControl = {'time': 0, # Текущее время 
                            'motorpowervalue': 1, # мощность моторов
                            'x': 0, 'y': 0, 'z': 0, # по идее мощность моторов  
                            'led': False, # управление светом 
                            'manipul': 0, # Управление манипулятором 
                            'servo-x1': 0, 'servo-y1': 0, # управление подвесом курсовой камеры
                            'servo-x2': 0, 'servo-y2': 0} # управление подвесом обзорной камеры 
                            # словарик для отправки на аппарат

        self.log = log  # флаг логирования
        self.logcmd = logcmd
        self.datainput = {}  # получаемая информация
        self.startservermain()  # поднимаем сервер

    def settingServer(self):
        # setting server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen()
        if self.logcmd:
            print("Server is start and listening")

    def hello(self):
        # обмен преветсвиями
        self.user_socket, self.address = self.server.accept()
        data = self.user_socket.recv(256)
        self.user_socket.send('Connect-Pult1-25'.encode("utf-8"))
        if self.logcmd:
            print(data.decode("utf-8"))

    def ReceiverProteus(self, *args):
        '''
        Прием информации с аппарата
        '''
        while True:
            self.datainput = dict(literal_eval(
                self.user_socket.recv(1024).decode('utf-8')))
            # TODO тут что то делаем с полученной информацией ( выводим на экран и прочее )
            if self.logcmd:
                print(self.datainput)

    def ControlProteus(self, *args):
        '''
        Отправка управляющей информации на аппарат 
        '''
        while True:
            timecontrol = str(datetime.now())
            self.massControl["time"] = timecontrol
            self.massControl["x"] = 0
            self.massControl["y"] = 0
            self.massControl["z"] = 0
            # TODO сделать опрос джойстика или других управляющих приблуд

            outmass = str(self.massControl).encode('utf-8')
            self.user_socket.send(outmass)
            sleep(self.JOYSTICKRATE)

    def startmultithreading(self):
        # инициализация логирования
        self.loger = LogerTXT('Prteus0')

        # инициализация потоков приема и передачи
        receiver = threading.Thread(
            target=self.ReceiverProteus, args=(self,))

        dispatch = threading.Thread(
            target=self.ControlProteus, args=(self,))

        logthread = threading.Thread(
            target=self.loger.writelogpult, args=(self,))

        dispatch.start()
        receiver.start()
        logthread.start()

    def startservermain(self):
        # запуск бекенда сервера
        self.settingServer()
        self.hello()
        self.startmultithreading()


class LogerTXT:
    '''
    класс для логирования 
    '''

    def __init__(self, name):
        self.RATELOG = 1
        time = '-'.join('-'.join('-'.join(str(datetime.now()
                                              ).split()).split('.')).split(':'))
        self.name = "ControlPost/log/" + f'{name}-{time}.txt'
        self.file = open(self.name, "a+")
        # запись шапки
        self.file.write(f"Name: {name}\n")
        self.file.write(f'Time: {time}\n')
        self.file.close()

    def writelog(self, info):  # запись одной строчки в лог
        self.file.write(info + '\n')

    # паралельное логирование принятой информации раз в секунду
    def writelogpult(self, pult: ServerMainPult):
        while True:
            self.file = open(self.name, "a+")
            inf = str(pult.datainput)
            self.file.write(inf+'\n')
            sleep(self.RATELOG)
            self.file.close()
    
    def VisualizationLog():
        # TODO визуализация логов 
        pass

class MyController(Controller):
    # TODO класс взаимодействия с джойстиком 
    pass


if __name__ == '__main__':
    Proteus = ServerMainPult(log=True, logcmd=True)
