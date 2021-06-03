from time import sleep
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.


class DrkMotor:
    def __init__(self):

        # инициализация моторов
        self.kit = ServoKit(channels=16)

        self.drk0 = self.kit.servo[0]
        self.drk0.set_pulse_width_range(1100, 1900)
        self.drk1 = self.kit.servo[1]
        self.drk1.set_pulse_width_range(1100, 1900)
        self.drk2 = self.kit.servo[2]
        self.drk2.set_pulse_width_range(1100, 1900)
        self.drk3 = self.kit.servo[3]
        self.drk3.set_pulse_width_range(1100, 1900)
        self.drk4 = self.kit.servo[4]
        self.drk4.set_pulse_width_range(1000, 1900)
        self.drk5 = self.kit.servo[5]
        self.drk5.set_pulse_width_range(1000, 1900)

        self.initMotor()

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
        self.drk0.angle = 87
        self.drk1.angle = 87
        self.drk2.angle = 87
        self.drk3.angle = 87
        self.drk4.angle = 87
        self.drk5.angle = 87
        print('motor center')
        sleep(6)
        print('motor good')

    def test_motor_value(self):
        for i in range(181):
            self.drk0.angle = i
            self.drk1.angle = i
            self.drk2.angle = i
            self.drk3.angle = i
            self.drk4.angle = i
            self.drk5.angle = i
            sleep(0.5)
        for i in range(180, 0, -1):
            self.drk0.angle = i
            self.drk1.angle = i
            self.drk2.angle = i
            self.drk3.angle = i
            self.drk4.angle = i
            self.drk5.angle = i
            sleep(0.5)
        for i in range(0,88):
            self.drk0.angle = i
            self.drk1.angle = i
            self.drk2.angle = i
            self.drk3.angle = i
            self.drk4.angle = i
            self.drk5.angle = i
            sleep(0.5)


if __name__ == '__main__':
    drk = DrkMotor()
