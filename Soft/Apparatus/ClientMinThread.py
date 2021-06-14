import socket  # библиотека для связи
import sys
import board
import busio
import base64
import zmq
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit
from adafruit_mpu6050 import MPU6050
from time import sleep  # библиотека длязадержек
from datetime import datetime  # получение текущего времени
from configparser import ConfigParser  # чтание конфигов
from multiprocessing import Process
from ast import literal_eval


class MainRov:
    def __init__(self):
        self.startTime = str(datetime.now())  # времы старта программы
        # чтение конфигов из файлика,  если файлик не найден то прорамма откажеться работать.
        self.config = ConfigParser()
        try:
            self.config.read(
                "/home/pi/Desktop/SoftProteus/Soft/Apparatus/settings-rov.ini")
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
        self.logger.WritelogSis('Init logger')
        
        self.client = ROVProteusClient(host=self.host, port=self.port)
        self.logger.WritelogSis('Init client sockets')
        
        self.drk = DrkMotor()
        self.logger.WritelogSis('Init drk-motor')
        
        self.acp = Acp()
        self.logger.WritelogSis('Init acp')
        
        self.sensor = SensorOrientation()
        self.logger.WritelogSis('Init sensor')
        
        # массив отсылаемой информации
        self.MassOut = {'time': None,
                        'dept': 0,
                        'a1': 0, 'a2': 0, 'a3': 0,
                        'a4': 0, 'a5': 0, 'a6': 0,
                        'Volt': 0,
                        'error': None,
                        'danger-error': False,
                        'x': 0, 'y': 0, 'z': 0}
        # массив принимаемый с пота управления
        self.MassInput = {'time': None,  # Текущее время
                          'motorpowervalue': 0.5,  # мощность моторов
                          'x': 0, 'y': 0, 'z': 0, 'r': 0,  # по идее мощность моторов
                          'led': False,  # управление светом
                          'manipul': 0,  # Управление манипулятором
                          'servo-x1': 0, 'servo-y1': 0,  # управление подвесом курсовой камеры
                          'servo-x2': 0, 'servo-y2': 0,  # управление подвесом обзорной камеры
                          'ly-cor': 0, 'lx-cor': 0, 'ry-cor': 0, 'rx-cor': 0
                          }
    
    def RunClientReceivin(self, *args):
        while True:
            self.MassInput = self.client.ClientReceivin()
            self.logger.WritelogInput(self.data)
            self.drk.main_motor(self.data)
            
    
    def RunClientDispatch(self, *args):
        while True:
            self.MassOut = self.acp.ReadAmperemeter(self.MassOut)
            self.MassOut = self.sensor.ReadAccelerometer(self.MassOut)
            self.MassOut = self.MassOut['time'] = datetime.now()
            self.logger.WritelogOutput(self.MassOut)
            self.client.ClientDispatch(self.MassOut)
            sleep(0.25)
            
    def main(self):
        ProcessRunClientReceivin = Process(target=self.RunClientReceivin, args=(self,))
        ProcessRunClientDispatc = Process(target=self.RunClientDispatch, args=(self,))
        
        ProcessRunClientReceivin.start()
        ProcessRunClientDispatc.start()


class ROVProteusClient:


    def __init__(self, host='127.0.0.1', port=1234, logcmd=False):
        '''
        Класс ответсвенный за связь с постом управления
        host - ip  адрес поста управления 
        port - порт на котором запущена программа для управления аппаратом 
        '''
        self.HOST = host
        self.PORT = port
        self.logcmd = logcmd

        

    def settingClient(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.client.connect((self.HOST, self.PORT))  # подключение адресс  порт

    def ClientDispatch(self, MassOut: dict):
        '''
        Функция для  отправки пакетов на пульт 
        '''
        if self.logcmd:
            print(MassOut)
        MassOut['time'] = str(datetime.now())
        DataOutput = str(MassOut).encode("utf-8")
        self.client.send(DataOutput)
        
    def ClientReceivin(self):
        '''
        Прием информации с поста управления 
        '''
        data = self.client.recv(512).decode('utf-8')
        MassInput = dict(literal_eval(str(data)))
        if self.logcmd:
            print(data)
        return MassInput


class LogerTXT:
    '''
    класс для логирования
    NameRov - названия аппарата
    '''

    def __init__(self, namerov='proteus0', starttime='2021-06-12 11:52:33.801128'):
        time = '-'.join('-'.join('-'.join(starttime.split()
                                          ).split('.')).split(':'))

        self.namefileSistem = "Soft/Apparatus/log/sistem/" + \
            f'{namerov}-sis-{time}.txt'
        self.namefileInput = "Soft/Apparatus/log/input/" + \
            f'INPUT-{namerov}-{time}.txt'
        self.namefileOutput = "Soft/Apparatus/log/output/" + \
            f'OUTPUT-{namerov}-{time}.txt'

        # обработка ошибки с некорректным путем
        try:
            self.fileInput = open(self.namefileInput, "a+")
            self.fileOutput = open(self.namefileOutput, 'a+')
            self.fileSis = open(self.namefileSistem, 'a+')
        except:
            self.fileInput = open(f'INPUT-{namerov}-{time}.txt', "a+")
            self.fileOutput = open(f'OUTPUT-{namerov}-{time}.txt', "a+")
            self.fileSis = open(f'{namerov}-sis-{time}.txt', "a+")

        # запись шапки
        self.fileInput.write(f"NameRov: {namerov}\n")
        self.fileInput.write(f'Time: {time}\n')
        self.fileOutput.write(f"NameRov: {namerov}\n")
        self.fileOutput.write(f'Time: {time}\n')
        self.fileSis.write(f"NameRov: {namerov}\n")
        self.fileSis.write(f'Time: {time}\n')
        self.fileInput.close()
        self.fileOutput.close()
        self.fileSis.close()

    # логирование принимаемой информации
    def WritelogInput(self, data: dict):
        self.fileInput = open(self.namefileInput, "a+")
        self.fileInput.write(str(data)+'\n')
        self.fileInput.close()

    # логирование отсылаемой информации
    def WritelogOutput(self, data: dict):
        self.fileOutput = open(self.namefileOutput, "a+")
        self.fileOutput.write(str(data)+'\n')
        self.fileOutput.close()

    # запись системных логов
    def WritelogSis(self, text):
        timelog = str(datetime.now())
        self.fileSis = open(self.namefileSistem, 'a+')
        self.fileSis.write(timelog + ' - ' + text + '\n')
        self.fileSis.close()


class DrkMotor:
    def __init__(self, debag=False, logcmd=False, pwmMin=1000, pwmMax=1900):
        self.logcmd = logcmd
        self.debag = debag
        self.pwmMin = pwmMin
        self.pwmMax = pwmMax

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

        # коофиценты корректировки на каждый мотор
        self.CorDrk0 = 1
        self.CorDrk1 = 1
        self.CorDrk2 = 1
        self.CorDrk3 = 1
        self.CorDrk4 = 1
        self.CorDrk5 = 1

        self.initMotor()
        if self.logcmd:
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
        if self.logcmd:
            print('motor max')
        sleep(2)
        self.drk0.angle = 0
        self.drk1.angle = 0
        self.drk2.angle = 0
        self.drk3.angle = 0
        self.drk4.angle = 0
        self.drk5.angle = 0
        if self.logcmd:
            print('motor min')
        sleep(2)
        self.drk0.angle = 87
        self.drk1.angle = 87
        self.drk2.angle = 87
        self.drk3.angle = 87
        self.drk4.angle = 87
        self.drk5.angle = 87
        if self.logcmd:
            print('motor center')
        sleep(3)
        if self.logcmd:
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

    def main_motor(self, MassInput: dict):
        '''
        Основная функция которая опрашивает массив примимаемой информации и рапределяет нагрузку на движители
        '''
        J1_Val_Y = MassInput["y"] + MassInput["ly-cor"]
        J1_Val_X = MassInput["x"] + MassInput["lx-cor"]
        J2_Val_X = MassInput["z"] + MassInput["ry-cor"]
        J2_Val_Y = MassInput["r"] + MassInput["rx-cor"]
        # расчет нагрузки на каждый движитель
        motor1 = J1_Val_Y + J1_Val_X + J2_Val_X
        motor2 = J1_Val_Y - J1_Val_X - J2_Val_X
        motor3 = (-1 * J1_Val_Y) - J1_Val_X + J2_Val_X
        motor4 = (-1 * J1_Val_Y) + J1_Val_X - J2_Val_X
        motor5 = J2_Val_Y
        motor6 = J2_Val_Y
        # Преобразование рассчитанной нагрузки в градусы (моторы управляются как сервоприводы)
        motor1 = 90 - int(motor1 * 0.9 * self.CorDrk0)
        motor2 = 90 - int(motor2 * 0.9 * self.CorDrk1)
        motor3 = 90 - int(motor3 * 0.9 * self.CorDrk2)
        motor4 = 90 - int(motor4 * 0.9 * self.CorDrk3)
        motor5 = 90 - int(motor5 * 0.9 * self.CorDrk4)
        motor6 = 90 - int(motor6 * 0.9 * self.CorDrk5)
        # отправка расчитанной нагрузки на движители
        if not self.debag:
            self.drk0.angle = motor1
            self.drk1.angle = motor2
            self.drk2.angle = motor3
            self.drk3.angle = motor4
            self.drk4.angle = motor5
            self.drk5.angle = motor6
        else:
            print(motor1, motor2, motor3, motor4, motor5, motor6)


class Acp:
    def __init__(self):
        '''
        Класс описывающий взаимодействие и опрос датчиков тока 
        '''
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads13 = ADS.ADS1115(self.i2c)
        self.adc46 = ADS.ADS1115(self.i2c, address=0x49)

        a1 = AnalogIn(self.ads13, ADS.P0)
        a2 = AnalogIn(self.ads13, ADS.P1)
        a3 = AnalogIn(self.ads13, ADS.P2)
        a4 = AnalogIn(self.adc46, ADS.P0)
        a5 = AnalogIn(self.adc46, ADS.P1)
        a6 = AnalogIn(self.adc46, ADS.P2)

        self.CorNulA1 = a1.value
        self.CorNulA2 = a2.value
        self.CorNulA3 = a3.value
        self.CorNulA4 = a4.value
        self.CorNulA5 = a5.value
        self.CorNulA6 = a6.value

    def ReadAmperemeter(self, MassOut: dict):
        '''
        Функция опроса датчиков тока 
        '''
        a1 = AnalogIn(self.ads13, ADS.P0)
        a2 = AnalogIn(self.ads13, ADS.P1)
        a3 = AnalogIn(self.ads13, ADS.P2)
        a4 = AnalogIn(self.adc46, ADS.P0)
        a5 = AnalogIn(self.adc46, ADS.P1)
        a6 = AnalogIn(self.adc46, ADS.P2)
        # Потенциально кривой матан
        MassOut['a1'] = round((a1.value - self.CorNulA1) * 0.00057321919, 3)
        MassOut['a2'] = round((a2.value - self.CorNulA2) * 0.00057321919, 3)
        MassOut['a3'] = round((a3.value - self.CorNulA3) * 0.00057321919, 3)
        MassOut['a4'] = round((a4.value - self.CorNulA4) * 0.00057321919, 3)
        MassOut['a5'] = round((a5.value - self.CorNulA5) * 0.00057321919, 3)
        MassOut['a6'] = round((a6.value - self.CorNulA6) * 0.00057321919, 3)

        return MassOut


class SensorOrientation:
    '''
    Класс описывающий опрос акселерометра по осям x, y, z, а так же датчика температуры
    '''

    def __init__(self):
        self.i2c = board.I2C()
        self.mpu = MPU6050(self.i2c)

    def ReadAccelerometer(self, MassOut: dict):
        # математика для перевода показаний дачиков в градусы с точностью до 3 знаков после запятой
        # потенциально кривой матан
        MassOut['x'] = round(self.mpu.acceleration[0] * 18, 3)
        MassOut['y'] = round(self.mpu.acceleration[1] * 18, 3)
        MassOut['z'] = round(self.mpu.acceleration[2] * 18, 3)
        MassOut['temp'] = round(self.mpu.temperature, 3)

        return MassOut


class Magnetrometr:
    def __init__(self):
        pass
        # TODO прописать класс для считывания показаний с мегнетрометра (возможно так же и с акслерометра)


if __name__ == '__main__':
    rov = MainRov()
    rov.main()
