import socket  # библиотека для связи
import threading  # библиотека для потоков
import sys
import cv2
import board
import busio
import base64
import zmq
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit
from time import sleep  # библиотека длязадержек
from datetime import datetime  # получение текущего времени
from configparser import ConfigParser  # чтание конфигов
from ast import literal_eval
from adafruit_mpu6050 import MPU6050

class MainRov:
    def __init__(self):
        #  дефолтное время старта программы
        self.startTime = str(datetime.now())
        # чтение конфигов из файлика,  если файлик не найден то прорамма откажеться работать.
        self.config = ConfigParser()
        try:
            self.config.read("/home/pi/Desktop/SoftProteus/Soft/Apparatus/settings-rov.ini")
            self.host = literal_eval(self.config["Client"]["host"])
        except:
            try:
                self.config.read(
                    "/home/proteus0/SoftProteus/Soft/Apparatus/settings-rov.ini")
                self.host = literal_eval(self.config["Client"]["host"])
            except:
                print('None settings file')
                sys.exit()
        # чтение конфигов отвечающих за клиентскую часть
        self.port = literal_eval(self.config["Client"]["port"])
        self.portcam = literal_eval(self.config["Client"]["portcam"])
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
        '''
        Инициализация клиент серверной связи для управления и сбора телеметрии
        '''
        self.logger.WritelogSis('Init Client')
        self.client = ROVProteusClient(self)
        self.client.startclientmain()
        
    def InitCam(self, *args):
        self.camera = SocketCameraOut(self)
        self.logger.WritelogSis('Init Camera')
        self.camera.mainCameraOut()

    def InitLogger(self, *args):
        '''
        Инициализация логирования 
        '''
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

    def InitDRK(self, *args):
        '''
        Инициализация движителей 
        '''
        self.logger.WritelogSis('Init DRK')
        self.drk = DrkMotor(self)
        self.drk.main_motor()
        
    # def InitAmpermert(self,*args):
    #     '''
    #     Инициализация датчиков тока для отслеживания нагрузки на движители 
    #     '''
    #     self.Amper = Amperemeter()
    #     self.logger.WritelogSis('Init Ampermert')
    #     self.Amper.mainAmperemeter()
        
    def InitOrientation(self,*args):
        '''
        Инициализация сбора телеметрии о положении робота 
        '''
        self.orientation = SensorOrientation()
        self.logger.WritelogSis('Init Orientation')
        self.orientation.MainAccelerometer()

    def main(self):
        '''
        функция для запука всех систем аппарата, в нее необходимо добавлять инициализацию потоков и их запуск
        '''
        self.logger.WritelogSis('Starting threading')
        # создание потока для системной информации и телеметрии
        self.mainClient = threading.Thread(
            target=self.InitClient, args=(self,))
        # создание потока для камеры 
        self.mainCamera = threading.Thread(
            target=self.InitCam, args=(self,))
        # создание потока для логирования 
        self.mainlogger = threading.Thread(
            target=self.InitLogger, args=(self,))
        # создание потока для управления движителями
        self.mainDrk = threading.Thread(
            target=self.InitDRK, args=(self,))
        # создание потока для сбора телеметрии с датчиков тока 
        # self.mainAmpermetr = threading.Thread(
        #     target=self.InitAmpermert(), args=(self,))
        # # создание потока для сбора показаний с датчиков ориентации 
        self.mainOrientations = threading.Thread(
            target=self.InitOrientation, args=(self,))
        # запуск всех потоков с небольшой задержкой чтобы ве успевало стартануть 
        self.mainClient.start()
        sleep(0.25)
        self.mainlogger.start()
        sleep(0.25)
        self.mainDrk.start()
        sleep(0.25)
        self.mainCamera.start()
        sleep(0.25)
        # self.mainAmpermetr.start()
        # sleep(0.25)
        self.mainOrientations.start()
        

    def variablePrint(self):
        '''
        Вывод всех атрибутов класса
        '''
        print('Start: ', self.startTime)  # вывод стартового времени
        print('host-', self.host)  # вывод хоста к которому будет подключаться аппарат
        print("port-", self.port) # вывод порта для подключения и получения системной информации
        print("log-", self.log)  # вывод флага логирования логируем\не логируем
        print("logcmd-", self.logcmd)  # выводим ли логи в консоль
        print("Name-", self.name)  # вывод имени аппарата
        print("MotorValue-", self.motorpowervalue) # вывод коофицента мощности на моторах
        print("RateLog-", self.ratelog)  # частота логировани
        print('logInput-', self.logInput)  # логирование получаемой информации
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
        pult = self.rov.client
        print('logInput')
        while True:
            if pult.checkConnect:
                self.fileInput = open(self.namefileInput, "a+")
                inf = str(pult.MassInput)
                self.fileInput.write(inf+'\n')
                sleep(self.ratelog)
                self.fileInput.close()

    # паралельное логирование отсылаемой информации
    def WritelogOutput(self, *args):
        pult = self.rov.client
        print('logWrite')
        while True:
            if pult.checkConnect:
                self.fileOutput = open(self.namefileOutput, "a+")
                inf = str(pult.MassOut)
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
    def __init__(self, rov: MainRov):
        self.rov = rov
        self.debag = False
        self.pwmMin = 1000
        self.pwmMax = 1950
        
        # инициализация моторов
        self.kit = ServoKit(channels=16)

        self.drk0 = self.kit.servo[0]
        self.drk0.set_pulse_width_range(self.pwmMin, self.pwmMax)
        self.drk1 = self.kit.servo[1]
        self.drk1.set_pulse_width_range(self.pwmMin, self.pwmMax)
        self.drk2 = self.kit.servo[2]
        self.drk2.set_pulse_width_range(self.pwmMin, self.pwmMax)
        self.drk3 = self.kit.servo[3]
        self.drk3.set_pulse_width_range(self.pwmMin, self.pwmMax)
        self.drk4 = self.kit.servo[4]
        self.drk4.set_pulse_width_range(self.pwmMin, self.pwmMax)
        self.drk5 = self.kit.servo[5]
        self.drk5.set_pulse_width_range(self.pwmMin, self.pwmMax)

        self.initMotor()

        print('init-motor')

    def initMotor(self):
        '''
        Функция для калибровки драйверов моторов
        '''
        self.drk0.angle = 180
        self.drk1.angle = 180
        self.drk2.angle = 180
        self.drk3.angle = 180
        self.drk4.angle = 180
        self.drk5.angle = 180
        if self.rov.logcmd:
            print('motor max')
        sleep(2)
        self.drk0.angle = 0
        self.drk1.angle = 0
        self.drk2.angle = 0
        self.drk3.angle = 0
        self.drk4.angle = 0
        self.drk5.angle = 0
        if self.rov.logcmd:
            print('motor min')
        sleep(2)
        self.drk0.angle = 87
        self.drk1.angle = 87
        self.drk2.angle = 87
        self.drk3.angle = 87
        self.drk4.angle = 87
        self.drk5.angle = 87
        if self.rov.logcmd:
            print('motor center')
        sleep(3)
        if self.rov.logcmd:
            print('motor good')

    def test_motor_value(self):
        '''
        Функция для плавной проверки роботоспособности всех движителей 
        '''
        for i in range(181):
            self.drk0.angle = i
            self.drk1.angle = i
            self.drk2.angle = i
            self.drk3.angle = i
            self.drk4.angle = i
            self.drk5.angle = i
            sleep(0.25)
        for i in range(180, 0, -1):
            self.drk0.angle = i
            self.drk1.angle = i
            self.drk2.angle = i
            self.drk3.angle = i
            self.drk4.angle = i
            self.drk5.angle = i
            sleep(0.25)
        for i in range(0, 88):
            self.drk0.angle = i
            self.drk1.angle = i
            self.drk2.angle = i
            self.drk3.angle = i
            self.drk4.angle = i
            self.drk5.angle = i
            sleep(0.25)

    def main_motor(self):
        '''
        Основная функция которая опрашивает массив примимаемой информации и рапределяет нагрузку на движители 
        '''
        while True:
            # считывание принятых показаний с джойстика 
            J1_Val_Y = self.rov.client.MassInput["y"]
            J1_Val_X = self.J1_Val_Y = self.rov.client.MassInput["x"]
            J2_Val_X = self.J1_Val_Y = self.rov.client.MassInput["z"]
            J2_Val_Y = self.J1_Val_Y = self.rov.client.MassInput["r"]
            # расчет нагрузки на каждый движитель 
            motor1 = J1_Val_Y + J1_Val_X + J2_Val_X 
            motor2 = J1_Val_Y - J1_Val_X - J2_Val_X 
            motor3 = (-1 * J1_Val_Y) - J1_Val_X + J2_Val_X 
            motor4 = (-1 * J1_Val_Y) + J1_Val_X - J2_Val_X 
            motor5 = J2_Val_Y
            motor6 = J2_Val_Y
            # Преобразование рассчитанной нагрузки в градусы 
            motor1 = 90 - int(motor1 * 0.9)
            motor2 = 90 - int(motor2 * 0.9)
            motor3 = 90 - int(motor3 * 0.9)
            motor4 = 90 - int(motor4 * 0.9)
            motor5 = 90 - int(motor5 * 0.9)
            motor6 = 90 - int(motor6 * 0.9)
            
            if self.rov.logcmd:
                print(motor1, motor2, motor3, motor4, motor5, motor6)
                
            # отправка расчитанной нагрузки на движители
            if not self.debag:
                self.drk0.angle = motor1
                self.drk1.angle = motor2
                self.drk2.angle = motor3
                self.drk3.angle = motor4
                self.drk4.angle = motor5
                self.drk5.angle = motor6
            else:
                #print(motor1, motor2, motor3, motor4, motor5, motor6)
                print(self.rov.client.MassInput)
            sleep(0.1)


class ROVProteusClient:
    '''
    Класс ответсвенный за связь с постом управления 
    '''
    def __init__(self, main: MainRov):
        self.rov = main
        self.HOST = main.host
        self.PORT = main.port
        self.logcmd = main.logcmd
        self.checkConnect = True
        self.ratesensor = main.ratesensor
        # массив отсылаемый с аппарата на пост управления 
        self.MassOut = {'time': main.startTime,
                        'dept': 0,
                        'a1': 0, 'a2': 0, 'a3': 0,
                        'a4': 0, 'a5': 0, 'a6': 0,
                        'Volt': 0,
                        'error': None,
                        'danger-error': False,
                        'x': 0, 'y': 0, 'z': 0}
        # массив принимаемый с пота управления 
        self.MassInput = {'time': main.startTime,  # Текущее время
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
            target=self.ClientDispatch, args=(self,))

        receiver = threading.Thread(
            target=self.ClientReceivin, args=(self,))

        dispatch.start()
        receiver.start()

    def startclientmain(self, *args):
        # запуск бекенда сервера
        self.settingClient()
        self.startmultithreading()

    def ClientDispatch(self, *args):
        '''
        Функция для  отправки пакетов на пульт 
        '''
        while True:
            self.MassOut['time'] = str(datetime.now())
            DataOutput = str(self.MassOut).encode("utf-8")
            self.client.send(DataOutput)
            sleep(self.ratesensor)

    def ClientReceivin(self, *args):
        '''
        Прием информации с поста управления 
        '''
        while True:
            data = self.client.recv(512).decode('utf-8')
            self.MassInput = dict(literal_eval(str(data)))
            if self.logcmd:
                print(data)


class SocketCameraOut:
    '''
    Класс описывающий прием видео потока с камеры аппарата 
    '''
    def __init__(self, rov: MainRov):
        self.rov = rov
        # порт поста управления 
        self.HOST = self.rov.host 
        self.PORT = self.rov.portcam
        self.ScreenResolution = ((640, 480))
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect('tcp://192.168.1.102:7777')
        self.camera = cv2.VideoCapture(0)        

    def mainCameraOut(self):
        # отправка изображения на пост управления 
        while True:
            try:
                self.ret, self.frame = self.camera.read()
                self.frame = cv2.resize(self.frame, self.ScreenResolution)
                self.encoded, self.buf = cv2.imencode('.jpg', self.frame)
                self.image = base64.b64encode(self.buf)
                self.socket.send(self.image)
            except KeyboardInterrupt:
                self.camera.release()
                cv2.destroyAllWindows()
                break


# class Amperemeter:
#     def __init__(self, rov: MainRov):
#         '''
#         Класс описывающий взаимодействие и опрос датчиков тока 
#         '''
#         self.rov = rov
#         self.i2c = busio.I2C(board.SCL, board.SDA)
#         self.ads13 = ADS.ADS1115(self.i2c)
#         self.adc46 = ADS.ADS1115(self.i2c, address=0x49)

#     def mainAmperemeter(self):
#         '''
#         Функция опроса датчиков тока 
#         '''
#         while True:
#             a1 = AnalogIn(self.ads13, ADS.P0)
#             a2 = AnalogIn(self.ads13, ADS.P1)
#             a3 = AnalogIn(self.ads13, ADS.P2)
#             a4 = AnalogIn(self.adc46, ADS.P0)
#             a5 = AnalogIn(self.adc46, ADS.P1)
#             a6 = AnalogIn(self.adc46, ADS.P2)
#             self.rov.client.MassOut['a1'] = a1.value
#             self.rov.client.MassOut['a2'] = a2.value
#             self.rov.client.MassOut['a3'] = a3.value
#             self.rov.client.MassOut['a4'] = a4.value
#             self.rov.client.MassOut['a5'] = a5.value
#             self.rov.client.MassOut['a6'] = a6.value
#             sleep(0.1)


class SensorOrientation:
    '''
    Класс описывающий опрос акселерометра по осям x, y, z, а так же датчика температуры
    '''
    def __init__(self, rov: MainRov):
        self.rov = rov
        self.i2c = board.I2C()  
        self.mpu = MPU6050(self.i2c)

    def MainAccelerometer(self):
        while True:
            self.rov.client.MassOut['x'] = self.mpu.acceleration[0]
            self.rov.client.MassOut['y'] = self.mpu.acceleration[1]
            self.rov.client.MassOut['z'] = self.mpu.acceleration[2]
            self.rov.client.MassOut['temp'] = self.mpu.temperature[0]
            sleep(0.1)

if __name__ == '__main__':
    rov = MainRov()
    rov.main()
