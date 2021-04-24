from threading import Thread
from time import sleep

class Check():
    def __init__(self):
        self.name = 'Proteus0'
        self.n = 0

def one(a:Check, name):
    while True:
        sleep(0.001)
        a.n += 1

def two(a:Check, name):
    while True:
        sleep(0.2)
        print(a.n)

def thee(a:Check,name):
    while True:
        sleep(1)
        a.n = 0



ch = Check()
a = Thread(target=one, name='one',args=(ch,'one'))
b = Thread(target=two, name='tho',args=(ch, 'tho'))
c = Thread(target=thee, name='three',args=(ch,'three'))
a.start()
b.start()
c.start()

#  в целом цель была в том чтобы показать что мы можем
#  из нескольких потоков читать и записывать без каких либо конфликтов 