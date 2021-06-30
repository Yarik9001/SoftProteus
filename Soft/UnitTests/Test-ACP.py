import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep
###################################################
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
        
        masscor1init = [[],[],[],[],[],[]]
        for i in range(10):
            masscor1init[0].append(a1.value)
            masscor1init[1].append(a2.value)
            masscor1init[2].append(a3.value)
            masscor1init[3].append(a4.value)
            masscor1init[4].append(a5.value)
            masscor1init[5].append(a6.value)
            sleep(0.25)
            
        self.CorNulA1 = int(sum(masscor1init[0]) / 10)
        self.CorNulA2 = int(sum(masscor1init[1]) / 10)
        self.CorNulA3 = int(sum(masscor1init[2]) / 10)
        self.CorNulA4 = int(sum(masscor1init[3]) / 10)
        self.CorNulA5 = int(sum(masscor1init[4]) / 10)
        self.CorNulA6 = int(sum(masscor1init[5]) / 10)

            

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
        # получена точность 0.1
        MassOut['a1'] = abs(round((a1.value - self.CorNulA1) * -0.003038061707, 2))
        MassOut['a2'] = abs(round((a2.value - self.CorNulA2) * -0.003038061707, 2))
        MassOut['a3'] = abs(round((a3.value - self.CorNulA3) * -0.003038061707, 2))
        MassOut['a4'] = abs(round((a6.value - self.CorNulA6) * -0.003038061707, 2))
        MassOut['a5'] = abs(round((a5.value - self.CorNulA5) * -0.003038061707, 2))
        MassOut['a6'] = abs(round((a4.value - self.CorNulA4) * -0.003038061707, 2))

        return MassOut
    
if __name__ == '__main__':
    testacp = Acp()
    while True:
        mass = {}
        mass = testacp.ReadAmperemeter(mass)
        print(mass['a1'])
        print(mass['a2'])
        print(mass['a3'])
        print(mass['a4'])
        print(mass['a5'])
        print(mass['a6'])
        print('###############')
        sleep(0.5)