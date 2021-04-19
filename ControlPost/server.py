import socket
import threading
from datetime import datetime
from time import sleep


class ServerMainPult:
    '''
    Класс описывающий систему управления роботом 
    '''
    def __init__(self, log=True):
        # init variable
        self.massControl = {'time': 0, 'x': 0, 'y': 0, 'z': 0, 'led': False,
                            'manipul': 0, 'servo-x1': 0, 'servo-y1': 0, 'servo-x2': 0, 'servo-y2': 0}
        self.log = log
        self.startservermain()

    def settingServer(self):
        # setting server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.server.bind(("127.0.0.1", 1234))
        self.server.listen()
        print("Server is start and listening")

    def hello(self):
        # обмен преветсвиями
        self.user_socket, self.address = self.server.accept()
        data = self.user_socket.recv(256)
        self.user_socket.send('Connect-Pult1-25'.encode("utf-8"))
        print(data.decode("utf-8"))

    def ReceiverProteus(self,*args):
        '''
        Прием информации с аппарата
        '''
        while True:
            self.datainput = self.user_socket.recv(1024).decode('utf-8')
            self.loger.writelog(self.datainput)
            print(self.datainput)

    def ControlProteus(self,*args):
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
            sleep(0.1)


    def startmultithreading(self):
        # инициализация логирования
        self.loger = LogerTXT('Prteus0')
        # инициализация потоков приема и передачи
        receiver = threading.Thread(
            target=self.ReceiverProteus, args=(self,))

        dispatch = threading.Thread(
            target=self.ControlProteus, args=(self,))

        # self.loging = threading.Thread(target=self.loger)
        dispatch.start()
        receiver.start()

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
        time = '-'.join('-'.join('-'.join(str(datetime.now()).split()).split('.')).split(':'))
        name = "ControlPost/log/" + f'Protrus0-{time}.txt'
        self.file = open(name, "a+")
        # запись шапки
        self.file.write(f"Name: {name}\n")
        self.file.write(f'Time: {time}\n')

    def writelog(self, info):
        self.file.write(info + '\n')

    def writelogpult(self):
        pass 


if __name__ == '__main__':
    Proteus = ServerMainPult(log=True)
