import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep
from datetime import datetime
###################################################
from time import sleep
from adafruit_servokit import ServoKit

class Acp:
    def __init__(self):
        '''
        Класс описывающий взаимодействие и опрос датчиков тока 
        '''
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads13 = ADS.ADS1115(self.i2c)
        self.ads13.gain = 0.6666666666666666

        a1 = AnalogIn(self.ads13, ADS.P0)
        
        self.CorNulA1 = a1.value


    def Read(self):
        '''
        Функция опроса датчиков тока и напряжения 
        '''
        a1 = AnalogIn(self.ads13, ADS.P0)
        
        MassOut = {}
        MassOut['amper'] = round((a1.value - self.CorNulA1) * 0.00057321919 * 8.24, 3)
        
        return MassOut

class DrkMotor:
    def __init__(self):

        # инициализация моторов
        self.kit = ServoKit(channels=16)

        self.drk0 = self.kit.servo[0]
        self.drk0.set_pulse_width_range(1100, 1900)
        
        self.initMotor()

        print('init-motor')

    def initMotor(self):
        self.drk0.angle = 180
        print('motor max')
        sleep(2)
        self.drk0.angle = 0
        print('motor min')
        sleep(2)
        self.drk0.angle = 87
        print('motor center')
        sleep(6)
        print('motor good')

def main():
    print('Stert main program')
    drk = DrkMotor()
    tester = Acp()

    StartTime = datetime.now()
    print('Start test')
    print(StartTime)
    name = str(StartTime) + '.txt'
    fileLog = open(name, "a+")
    massdata = {'value':0, 'amper':0}
    for i in range(87,181):
        massdata['amper'] = tester.Read()['amper']
        massdata['value'] = i 
        drk.drk0.angle = i
        print(massdata)
        data = '    '.join([str(massdata['value']), str(massdata['amper'])])
        fileLog.write(f'{data}\n')
        sleep(1)
    for i in range(180,-1,-1):
        massdata['amper'] = tester.Read()['amper']
        massdata['value'] = i 
        drk.drk0.angle = i
        print(massdata)
        data = '    '.join([str(massdata['value']), str(massdata['amper'])])
       
        fileLog.write(f'{data}\n')
        sleep(1)
    for i in range(0,88):
        massdata['amper'] = tester.Read()['amper']
        massdata['value'] = i 
        drk.drk0.angle = i
        print(massdata)

        data = '    '.join([str(massdata['value']), str(massdata['amper'])])
        fileLog.write(f'{data}\n')
        sleep(1)


if __name__ == '__main__':
    main()