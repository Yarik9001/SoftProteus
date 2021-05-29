import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

PORT = None  # TODO - Определить порт к которому подключен шилд
MINI = 900  # TODO - определить минимальную частоту 
MAXI = 1900  # TODO - определить максимальную частоту 
i2c = busio.I2C(SCL, SDA)

# Create a simple PCA9685 class instance.
pca = PCA9685(i2c, address=PORT)
pca.frequency = 50

servo7 = servo.Servo(pca.channels[7])
servo7.set_pulse_width_range(MINI, MAXI)

servo6 = servo.Servo(pca.channels[6])
servo6.set_pulse_width_range(MINI, MAXI)

def testOne():    
    # test-one управление дрк как сервоприводом 
    for i in range(180):
        servo7.angle = i
        time.sleep(0.03)
        
    for i in range(180):
        servo7.angle = 180 - i
        time.sleep(0.03)

