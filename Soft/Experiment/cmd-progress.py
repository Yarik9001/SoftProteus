from progress.bar import IncrementalBar
from time import sleep
motor1 = IncrementalBar('motor-1', max=100)

for i in range(100):
    # Do some work
    sleep(0.01)
    motor1.next()


motor1.finish()

# работает адекватно только с 1 баром одновременно,
# паралельно запустить несколько не получилось.  
