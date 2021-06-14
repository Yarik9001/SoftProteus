from time import sleep
from multiprocessing import Process

def one():
    while True:
        print(1)
        sleep(1)

def two():
    while True:
        print(2)
        sleep(0.5)
        
if __name__ == '__main__':  
    a = Process(target=one)
    b= Process(target=two)
    a.start()
    b.start()

