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
        self.ads13.gain = 0.6666666666666666

        a1 = AnalogIn(self.ads13, ADS.P0)
        a2 = AnalogIn(self.ads13, ADS.P1)
        
       
        self.CorNulA1 = a1.value
        self.CorNulA2 = a2.value
       

    def ReadAmperemeter(self, MassOut: dict):
        '''
        Функция опроса датчиков тока 
        '''
        a1 = AnalogIn(self.ads13, ADS.P0)
        a2 = AnalogIn(self.ads13, ADS.P1)
        
        # Потенциально кривой матан
        MassOut['a1'] = a1.voltage / (10000/110000) * 0.988
        MassOut['a2'] = round((a2.value - self.CorNulA2) * 0.00057321919 * 8.24, 2)
        

        return MassOut
    
if __name__ == '__main__':
    testacp = Acp()
    while True:
        mass = testacp.ReadAmperemeter({})
        print(mass['a1'], mass['a2'])
        sleep(0.5)