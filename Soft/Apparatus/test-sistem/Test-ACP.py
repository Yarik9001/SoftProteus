import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep
from datetime import datetime
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

    def Read(self):
        '''
        Функция опроса датчиков тока и напряжения 
        '''
        a1 = AnalogIn(self.ads13, ADS.P0)
        a2 = AnalogIn(self.ads13, ADS.P1)
        
        MassOut = {}
        MassOut['voltage'] = round((a1.voltage / (10000/110000) * 0.988), 3)
        MassOut['amper'] = round((a2.value - self.CorNulA2) * 0.00057321919 * 8.24, 3)
        
        return MassOut
    
def main():
    print('Start main program')
    tester = Acp()
    check = True
    while check:
        if tester.Read()['voltage'] <= 7:
            continue
        StartTime = datetime.now
        print('Start test')
        print(StartTime)
        fileLog = open(str(StartTime), "a+")
        massdata = {'I':0, 'time':0}
        while tester.Read()['voltage'] >= 9 or tester.Read['amper'] >= 0.5:
            
            v = tester.Read()['voltage']
            a = tester.Read()['amper']
            massdata['I'] += round(a * 0.28, 2)
            massdata['time'] += 1
            
            data = '    '.join(str(massdata['time']), str(v), str(a), str(massdata['I']))
            print(data) 
            fileLog.write(f'{data}\n')
            
            sleep(1)
        else:
            print('Final:  ', massdata)
            check = False
            break



if __name__ == '__main__':
    main()