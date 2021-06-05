import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep

i2c = busio.I2C(board.SCL, board.SDA)

ads13 = ADS.ADS1115(i2c)
adc46 = ADS.ADS1115(i2c, address=0x49)

while True:
    a1 = AnalogIn(ads13, ADS.P0)
    a2 = AnalogIn(ads13, ADS.P1)
    a3 = AnalogIn(ads13, ADS.P2)
    a4 = AnalogIn(adc46, ADS.P0)
    a5 = AnalogIn(adc46, ADS.P1)
    a6 = AnalogIn(adc46, ADS.P2)
    print('##########################')
    print('a1', a1.value, a1.voltage)
    print('a2', a2.value, a2.voltage)
    print('a3', a3.value, a3.voltage)
    print('a4', a4.value, a4.voltage)
    print('a5', a5.value, a5.voltage)
    print('a6', a6.value, a6.voltage)
    sleep(0.5)
