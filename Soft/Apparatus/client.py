import socket
import threading
from time import sleep
from datetime import datetime
from configparser import ConfigParser
from ast import literal_eval 
import sys

class MainRov:
    def __init__(self):
        self.startTime = str(datetime.now())
        self.config = ConfigParser()
        try:
            self.config.read("Soft\Apparatus\settings-rov.ini")
            self.host = literal_eval(self.config["Client"]["host"])
        except:
            try:
                self.config.read("/home/proteus0/SoftProteus/Soft/Apparatus/settings-rov.ini")
                self.host = literal_eval(self.config["Client"]["host"])
            except:
                print('None settings file')
                sys.exit()
        
        self.port = literal_eval(self.config["Client"]["port"])
        self.log = literal_eval(self.config["Client"]["log"])
        self.logcmd = literal_eval(self.config["Client"]["logcmd"])
        self.ratelog = literal_eval(self.config['Client']['ratelog'])
        self.logOutput = literal_eval(self.config['Client']['logOutput'])
        self.logInput = literal_eval(self.config['Client']['logInput'])
        
        self.name = literal_eval(self.config["RovSettings"]["name"])
        self.motorpowervalue = literal_eval(
            self.config["RovSettings"]["MotorPowerValue"])
        
        
    def variablePrint(self):
        print('Start: ', self.startTime)
        print('host-', self.host)
        print("port-", self.port)
        print("log-", self.log)
        print("logcmd-", self.logcmd)
        print("Name-", self.name)
        print("MotorValue-", self.motorpowervalue)
        print("RateLog-", self.ratelog)
        print('logInput-', self.logInput)
        print('logOutput-', self.logOutput)
        
    # инициализация сервера
    def InitServer(self, *args):
        self.logger.WritelogSis('Init server')
        self.server = ServerMainPult(
            self,
            log=self.log,
            logcmd=self.logcmd,
            host=self.host,
            port=self.port,
            motorpowervalue=self.motorpowervalue,
            joystickrate=self.joystickrate,
            startTime=self.startTime
        )

        self.server.startservermain()   
        
        
class LogerTXT:
    '''
    класс для логирования 
    NameRov - названия аппарата 
    time - время начала логирования 
    ratelog - частота логирования

    Основной принцип заключается в том что мы вытягиваем атрибуты 
    класса сервера и переодически из логируем
    '''

    def __init__(self, rov: MainRov):
        self.rov = rov
        self.ratelog = self.rov.ratelog
        time = self.rov.startTime
        NameRov = self.rov.name
        time = '-'.join('-'.join('-'.join(time.split()).split('.')).split(':'))

        self.namefileSistem = "Soft/Apparatus/log/sistem/" + \
            f'{NameRov}-sis-{time}.txt'
        self.namefileInput = "Soft/Apparatus/log/input/" + \
            f'INPUT-{NameRov}-{time}.txt'
        self.namefileOutput = "Soft/Apparatus/log/output/" + \
            f'OUTPUT-{NameRov}-{time}.txt'

        # обработка ошибки с некорректным путем
        try:
            self.fileInput = open(self.namefileInput, "a+")
            self.fileOutput = open(self.namefileOutput, 'a+')
            self.fileSis = open(self.namefileSistem, 'a+')
        except:
            self.fileInput = open(f'INPUT-{NameRov}-{time}.txt', "a+")
            self.fileOutput = open(f'OUTPUT-{NameRov}-{time}.txt', "a+")
            self.fileSis = open(f'{NameRov}-sis-{time}.txt', "a+")

        # запись шапки
        self.fileInput.write(f"NameRov: {NameRov}\n")
        self.fileInput.write(f'Time: {time}\n')
        self.fileOutput.write(f"NameRov: {NameRov}\n")
        self.fileOutput.write(f'Time: {time}\n')
        self.fileSis.write(f"NameRov: {NameRov}\n")
        self.fileSis.write(f'Time: {time}\n')
        self.fileInput.close()
        self.fileOutput.close()
        self.fileSis.close()

    # логирование принятой информации раз в секунду
    # TODO переписать для того чтобы логер брал все из обьекта rov, а не тягал из сервера.
    def WritelogInput(self, *args):
        pult = self.rov.server
        print('logInput')
        while True:
            if pult.checkConnect:
                self.fileInput = open(self.namefileInput, "a+")
                inf = str(pult.DataInput)
                self.fileInput.write(inf+'\n')
                # Запись ошибок
                if pult.DataInput['error'] != None:
                    errorinf = pult.DataInput['error']
                    self.fileInput.write('ERROR :' + errorinf + '\n')

                sleep(self.ratelog)
                self.fileInput.close()

    # паралельное логирование отсылаемой информации
    def WritelogOutput(self, *args):
        pult = self.rov.server
        print('logWrite')
        while True:
            if pult.checkConnect:
                self.fileOutput = open(self.namefileOutput, "a+")
                inf = str(pult.DataOutput)
                self.fileOutput.write(inf+'\n')
                self.fileOutput.close()
                sleep(self.ratelog)

    # запись системных логов
    def WritelogSis(self, text):
        timelog = str(datetime.now())
        self.fileSis = open(self.namefileSistem, 'a+')
        self.fileSis.write(timelog + ' - ' + text + '\n')
        self.fileSis.close()


class ROVProteusClient:
    '''
    Класс ответсвенный за связь с постом управления 
    '''
    def __init__(self,main:MainRov):
        self.rov = main
        self.HOST = main.host
        self.PORT = main.port
        self.logcmd = main.logcmd
        self.ratesensor = main.r
        self.rate = 1а

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
            data = self.client.recv(512).decode('utf-8')
            # TODO считаем и отсылаем управляющие сигналы на моторы и прочую полезную нагрузку
            if self.logcmd:
                print(data)
            
class FrontCAM:
    def __init__(self):
        pass
    # TODO реализовать опрос камер 
    
# if __name__ == '__main__':
#     Proteus1 = ROVProteus()
