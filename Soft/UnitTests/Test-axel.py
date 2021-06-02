from mpu6050 import mpu6050
from time import sleep 

sensor = mpu6050(0x68)
while True:
    accelerometer_data = sensor.get_accel_data()
    print(accelerometer_data)
    sleep(0.25)