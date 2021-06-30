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
        for i in range(5):
            masscor1init[0].append(a1.value)
            masscor1init[1].append(a2.value)
            masscor1init[2].append(a3.value)
            masscor1init[3].append(a4.value)
            masscor1init[4].append(a5.value)
            masscor1init[5].append(a6.value)
            sleep(0.1)
            
        self.CorNulA1 = sum(masscor1init[0]) / 5
        self.CorNulA2 = sum(masscor1init[1]) / 5
        self.CorNulA3 = sum(masscor1init[2]) / 5
        self.CorNulA4 = sum(masscor1init[3]) / 5
        self.CorNulA5 = sum(masscor1init[4]) / 5
        self.CorNulA6 = sum(masscor1init[5]) / 5

            

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
        MassOut['a1'] = round((a1.value - self.CorNulA1) * 0.00057321919 * 3, 3)
        MassOut['a2'] = round((a2.value - self.CorNulA2) * 0.00057321919, 3)
        MassOut['a3'] = round((a3.value - self.CorNulA3) * 0.00057321919, 3)
        MassOut['a4'] = round((a4.value - self.CorNulA4) * 0.00057321919, 3)
        MassOut['a5'] = round((a5.value - self.CorNulA5) * 0.00057321919, 3)
        MassOut['a6'] = round((a6.value - self.CorNulA6) * 0.00057321919, 3)

        return MassOut
    
if __name__ == '__main__':
    testacp = Acp()
    while True:
        mass = {}
        mass = testacp.ReadAmperemeter(mass)
        print(mass['a1'])
        sleep(0.5)