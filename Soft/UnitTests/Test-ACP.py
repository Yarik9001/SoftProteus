import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from time import sleep

i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)
while True:
    a1 = AnalogIn(ads, ADS.P0)
    a2 = AnalogIn(ads, ADS.P1)
    a3 = AnalogIn(ads, ADS.P2)
    a4 = AnalogIn(ads, ADS.P3)
    print('a1', a1.value, a1.voltage)
    print('a2', a2.value, a2.voltage)
    print('a3', a3.value, a3.voltage)
    print('a4', a4.value, a4.voltage)
    sleep(0.5)