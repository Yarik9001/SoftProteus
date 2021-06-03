import socket # библиотека для связи 
import threading # библиотека для потоков 
from time import sleep # библиотека длязадержек
from datetime import datetime # получение текущего времени
from configparser import ConfigParser # чтание конфигов
from ast import literal_eval  # парсер для получаемых покетов 
from adafruit_servokit import ServoKit # библиотека для работы с дрк и сервоприводами 
import sys # системные штуки 

class MainRov:
    def __init__(self):
        #  дефолтное время старта программы 
        self.startTime = str(datetime.now())
        # чтение конфигов из файлика,  если файлик не найден то прорамма откажеться работать.
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
        # чтение конфигов отвечающих за клиентскую часть 
        self.port = literal_eval(self.config["Client"]["port"])
        self.log = literal_eval(self.config["Client"]["log"])
        self.logcmd = literal_eval(self.config["Client"]["logcmd"])
        self.ratelog = literal_eval(self.config['Client']['ratelog'])
        self.ratesensor = literal_eval(self.config['Client']['ratesensor'])
        self.logOutput = literal_eval(self.config['Client']['logOutput'])
        self.logInput = literal_eval(self.config['Client']['logInput'])
        # чтение и здание дефолтного имени и дефолтного значения коофицента усилия на моторы 
        self.name = literal_eval(self.config["RovSettings"]["name"])
        self.motorpowervalue = literal_eval(
            self.config["RovSettings"]["MotorPowerValue"])
        self.checkConnect = True
        
        self.logger = LogerTXT(self)
        self.logger.WritelogSis('Start the MainRovPult')
        self.logger.WritelogSis('Init config')
        
        if self.logcmd:
            self.variablePrint()
        
        self.CheckConfig = True
            
    def InitClient(self, args):
        self.logger.WritelogSis('Init server')
        self.client = ROVProteusClient(self)
        self.client.startclientmain()
            
    def  InitLogger(self, *args):
        if self.log and (self.logOutput or self.logInput):
            self.logger.WritelogSis('Init logger')
            if self.logInput:
                loginp = threading.Thread(
                    target=self.logger.WritelogInput, args=(self.logger,))
                loginp.start()
            if self.logOutput:
                logout = threading.Thread(
                    target=self.logger.WritelogOutput, args=(self.logger,))
                logout.start()
            
                
    def InitDRK(self, args):
        self.logger.WritelogSis('Init DRK')
        self.drk = DrkMotor(self)
        self.drk.main_motor()        
    
    
    def main(self):
        self.logger.WritelogSis('Starting threading')
        
        self.mainClient = threading.Thread(
            target=self.InitClient, args=(self,))
        
        self.mainlogger = threading.Thread(
            target=self.InitLogger, args=(self,))
        
        self.mainDrk = threading.Thread(
            target=self.InitDrk, args=(self,))
        
        self.mainClient.start()
        sleep(0.25)
        self.mainlogger.start()
        sleep(0.25)
        self.mainDrk.start()
        sleep(0.25)
        
        
    def variablePrint(self):
        '''
        Вывод всех атрибутов класса
        '''
        print('Start: ', self.startTime) # вывод стартового времени 
        print('host-', self.host) # вывод хоста к которому будет подключаться аппарат
        print("port-", self.port) # вывод порта для подключения и получения системной информации 
        print("log-", self.log) # вывод флага логирования логируем\не логируем
        print("logcmd-", self.logcmd) # выводим ли логи в консоль 
        print("Name-", self.name) # вывод имени аппарата 
        print("MotorValue-", self.motorpowervalue) # вывод коофицента мощности на моторах 
        print("RateLog-", self.ratelog) # частота логировани 
        print('logInput-', self.logInput) # логирование получаемой информации 
        print('logOutput-', self.logOutput) # логирование отправляемой информации 
        
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
        pult = self.rov
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

class DrkMotor:
    def __init__(self):

        # инициализация моторов
        self.kit = ServoKit(channels=16)

        self.drk0 = self.kit.servo[0]
        self.drk0.set_pulse_width_range(1100, 1900)
        self.drk1 = self.kit.servo[1]
        self.drk1.set_pulse_width_range(1100, 1900)
        self.drk2 = self.kit.servo[2]
        self.drk2.set_pulse_width_range(1100, 1900)
        self.drk3 = self.kit.servo[3]
        self.drk3.set_pulse_width_range(1100, 1900)
        self.drk4 = self.kit.servo[4]
        self.drk4.set_pulse_width_range(1000, 1900)
        self.drk5 = self.kit.servo[5]
        self.drk5.set_pulse_width_range(1000, 1900)

        self.initMotor()

        print('init-motor')

    def initMotor(self):
        self.drk0.angle = 180
        self.drk1.angle = 180
        self.drk2.angle = 180
        self.drk3.angle = 180
        self.drk4.angle = 180
        self.drk5.angle = 180
        print('motor max')
        sleep(2)
        self.drk0.angle = 0
        self.drk1.angle = 0
        self.drk2.angle = 0
        self.drk3.angle = 0
        self.drk4.angle = 0
        self.drk5.angle = 0
        print('motor min')
        sleep(2)
        self.drk0.angle = 87
        self.drk1.angle = 87
        self.drk2.angle = 87
        self.drk3.angle = 87
        self.drk4.angle = 87
        self.drk5.angle = 87
        print('motor center')
        sleep(6)
        print('motor good')

    def test_motor_value(self):
        for i in range(181):
            self.drk0.angle = i
            self.drk1.angle = i
            self.drk2.angle = i
            self.drk3.angle = i
            self.drk4.angle = i
            self.drk5.angle = i
            sleep(0.5)
        for i in range(180, 0, -1):
            self.drk0.angle = i
            self.drk1.angle = i
            self.drk2.angle = i
            self.drk3.angle = i
            self.drk4.angle = i
            self.drk5.angle = i
            sleep(0.5)
        for i in range(0,88):
            self.drk0.angle = i
            self.drk1.angle = i
            self.drk2.angle = i
            self.drk3.angle = i
            self.drk4.angle = i
            self.drk5.angle = i
            sleep(0.5)

    def main_motor(self):
        # TODO прописать систему взаимодействия с моторам (будет работать в отдельном потоке)
        pass 
    
class ROVProteusClient:
    '''
    Класс ответсвенный за связь с постом управления 
    '''
    def __init__(self, main:MainRov):
        self.rov = main
        self.HOST = main.host
        self.PORT = main.port
        self.logcmd = main.logcmd
        self.checkConnect = True
        self.ratesensor = main.ratesensor
        
        self.MassOut = {'time': main.startTime,
                                'dept': 0,
                                'm1': 0,'m2': 0, 'm3': 0,
                                'm4': 0, 'm5': 0, 'm6': 0,
                                'Volt': 0,
                                'error': None,
                                'danger-error':False,
                                'x':0, 'y':0,'z':0}
        
        self.MassInput =  {'time': main.startTime,  # Текущее время
                            'motorpowervalue': 0.5,  # мощность моторов
                            'x': 0, 'y': 0, 'z': 0, 'r': 0,  # по идее мощность моторов
                            'led': False,  # управление светом
                            'manipul': 0,  # Управление манипулятором
                            'servo-x1': 0, 'servo-y1': 0,  # управление подвесом курсовой камеры
                            'servo-x2': 0, 'servo-y2': 0  # управление подвесом обзорной камеры
                            }
        
    def settingClient(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.client.connect((self.HOST, self.PORT))  # подключение адресс  порт
        # обмен приветсвиями

    def startmultithreading(self):
        # создние отдельных асинхронных потоков для отправки и приема 
        dispatch = threading.Thread(
            target= self.ClientDispatch, args=(self,))

        receiver = threading.Thread(
            target=self.ClientReceivin, args=(self,))

        dispatch.start()
        receiver.start()

    def startclientmain(self):
        # запуск бекенда сервера
        self.settingClient()
        self.startmultithreading()

    def ClientDispatch(self):
        '''
        Функция для  отправки на пульт телеметрии
        '''
        while True:
            self.MassOut['time'] = str(datetime.now())
            DataOutput = str(self.MassOut).encode("utf-8")
            self.client.send(DataOutput)
            sleep(self.ratesensor)

    def ClientReceivin(self):
        '''
        Прием информации 
        '''
        while True:
            data = self.client.recv(512).decode('utf-8')
            self.MassInput = data
            if self.logcmd:
                print(data)
            
class FrontCAM:
    def __init__(self):
        pass
    # TODO реализовать опрос камер 
    
# if __name__ == '__main__':
#     Proteus1 = ROVProteus()
