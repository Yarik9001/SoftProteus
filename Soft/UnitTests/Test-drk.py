from time import sleep
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
class DrkMotor:
    def __init__(self):
        self.kit = ServoKit(channels=16)
        
        self.drk0 = self.kit.servo[0]
        self.drk1 = self.kit.servo[1]
        self.drk2 = self.kit.servo[2]
        self.drk3 = self.kit.servo[3]
        self.drk4 = self.kit.servo[4]
        self.drk5 = self.kit.servo[5]
        
        print('init-motor')
        
    def initMotor(self):
        self.drk0.angle = 180
        self.drk1.angle = 180
        self.drk2.angle = 180
        self.drk3.angle = 180
        self.drk4.angle = 180
        self.drk5.angle = 180
        print('motor max')
        sleep(2)
        self.drk0.angle = 0
        self.drk1.angle = 0
        self.drk2.angle = 0
        self.drk3.angle = 0
        self.drk4.angle = 0
        self.drk5.angle = 0
        print('motor min')
        sleep(2)
        self.drk0.angle = 90
        self.drk1.angle = 90
        self.drk2.angle = 90
        self.drk3.angle = 90
        self.drk4.angle = 90
        self.drk5.angle = 90
        print('motor center')
        sleep(6)
        print('motor good')
        
    
        
    
        
    # for i in range(len(kit.servo)):
    #     kit.servo[i].angle = 180
    # time.sleep(1)
    # for i in range(len(kit.servo)):
    #     kit.servo[i].angle = 0
    # time.sleep(1)
    
if __name__ =='__main__': 
    drk = DrkMotor()
    drk.initMotor()