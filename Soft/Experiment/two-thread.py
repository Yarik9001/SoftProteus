from time import sleep
from threading import Thread

t = 0.25

massT = [0, 0.25, 0.5, 0.75, 1]

# типа основной процесс в ход которого мы пытаемся вмешаться и все испортить :)
def main():
    global t
    while  True:
        print(f'test-time-sleep{t}')
        sleep(t)

# тот неходоший процесс который вмешивается в работу основного и его корректирует как ему благорассудеться 
def corrector(*args):
    global t, massT
    while True:
        for i in massT:
            sleep(1)
            t = i 

threadCor = Thread(target=corrector)
threadCor.start()

main()

#  в целом тема работает и на выполнение функции можно влиять из драгого потока не к чему смертельному это не приводи,
#  но если будут проблемы надо будит курить этот момент.