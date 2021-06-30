# Не обращайте внимания это просто свалка всякого потенцеально полезного (не точно)
'''
def logger_txt_print(tekst: str):  # запись логов в txt файл
    print(tekst)
    file = open('logi/log.txt', 'a+')
    t = datetime.now()
    file.write(f'{t}\t- {tekst}\n')
    file.close()


def color_print(tem: float):  # цветной вывод температуры
    if tem < 35:
        print("\033[34m {}" .format(tem), end='')  # синий
        print("\033[37m {}" .format(''))
    elif tem >= 35 and tem <= 36.8:
        print("\033[32m {}" .format(tem), end='')  # зеленый
        print("\033[37m {}" .format(''))
    elif tem >= 36.8 and tem <= 37:
        print("\033[33m {}" .format(tem), end='')  # желтый
        print("\033[37m {}" .format(''))
    elif tem >= 37:
        print("\033[31m {}" .format(tem), end='')  # красный
        print("\033[37m {}" .format(''))


def print_dikt():
    while True:
        t = datetime.now()
        print('-----')
        print(t)
        file = open('logi/log.txt', 'a+')
        file.write(f'\n-----\n{t}\n')
        if braslet_dikt.keys():
            for i in braslet_dikt.keys():
                te = braslet_dikt[i]
                print(i, end=' - ')
                color_print(te)
                file.write(f'{i} - {te}\n')
        else:
            print('None')
            file.write('None\n')
        file.close()
        sleep(2)



def listen_user(user):  # прослушивание браслетов
    print("Listening user")
    while True:
        data = user.recv(2048)
        t = datetime.now()
        adres = str(user)[130:143]
        tem = (str(data)[1:])[1:-1]
        braslet_dikt[adres] = float(tem)
        fil = open(f'logi/log-{adres}.txt', 'a+')
        fil.write(f'{t} - {adres} - {tem}\n')
        fil.close()
        # print(str(user)[130:143], end=' - ')
        # color_print(float(tem))


def start_server():
    while True:
        user_socket, address = server.accept()
        logger_txt_print(f"User <{address[0]}> connected!")
        braslet_list.append(user_socket)
        t = datetime.now()
        adres = str(user_socket)[130:143]
        braslet_dikt[adres] = 0
        fil = open(f'logi/log-{adres}.txt', 'a+')
        fil.write(f'{t} - {adres} - start\n')
        fil.close()
        listen_accepted_user = threading.Thread(  # многопоточный прием сообщений
            target=listen_user, args=(user_socket,))
        listen_accepted_user.start()


print_time = threading.Thread(target=print_dikt)
print_time.start()


if __name__ == '__main__':
    start_server()


Тип	Битрейт видео, стандартная частота кадров (24, 25, 30)	Битрейт видео, высокая частота кадров (48, 50, 60)
2160p (4К)             	 35–45 Мбит/с	                             53–68 Мбит/с
1440p (2К)	             16 Мбит/c                                   24 Мбит/c
1080p	                 8 Мбит/c                                    12 Мбит/c
720p	                 5 Мбит/                                     7,5 Мбит/c
'''
# print('hello world')

# получение ip adress
# # import socket
# # print(socket.gethostbyname(socket.getfqdn()))
# from configparser import  ConfigParser

# config = ConfigParser()  # создаём объекта парсера
# config.read("settings.ini")  # читаем конфиг

# print(config["Twitter"]["username"])  # обращаемся как к обычному словарю!
# # 'johndoe'

# from screeninfo import get_monitors
# for m in get_monitors():
#     print(m.width)
#     print(m.height)

# import keyboard

# a = None

# def print_pressed_keys(e):
#     global a
#     if e != a:
#         a = e
#         print(e.event_type, e.name)

# def up(key):
#     print('up')
    
# def down(key):
#     print('down')

# keyboard.on_press_key('w', up ,suppress=False)
# keyboard.on_release_key('w', down, suppress=False)
# keyboard.wait()
'''
вперед - down w
отпустить - up w

назад - down s
отмена -up s

вправо - down a
отмена - up a

влево - down d
отмена - up d

вверх - down  up
отмена - up up

вниз - down down 
отмена - up down 
'''
# from keyboard import hook, wait, on_press_key, on_release_key

# class MyControllerKeyboard:
#     def __init__(self):
#         on_press_key('w', self.forward, suppress= False)
#         on_release_key('w',self.forward_release, suppress=False)
#         on_press_key('s', self.back, suppress=False)
#         on_release_key('s', self.down_relaese, suppress=False)
#         on_press_key('a', self.left, suppress=False)
#         on_release_key('a', self.left_relaese, suppress=False)
#         on_press_key('d', self.right, suppress=False)
#         on_release_key('d', self.right_relaese, suppress=False)
#         on_press_key('up', self.up, suppress=False)
#         on_release_key('up', self.up_relaese, suppress=False)
#         on_press_key('down', self.down, suppress=False)
#         on_release_key('down', self.down_relaese, suppress=False)
#         wait()
        
#     def forward(self, key):
#         print('forward')
        
#     def forward_release(self, key):
#         print('forward-stop')
        
#     def back(self, key):
#         print('back')
        
#     def back_ralease(self, key):
#         print('back-relaese')
    
#     def left(self, key):
#         print('left')
        
#     def left_relaese(self, key):
#         print('left_relaese')
        
#     def right(self, key):
#         print('right')
        
#     def right_relaese(self, key):
#         print('right-relaese')
        
#     def up(self, key):
#         print('up')
    
#     def up_relaese(self, key):
#         print('up-relaese')
        
#     def down(self, key):
#         print('down')
        
#     def down_relaese(self, key):
#         print('down-relaese')
        
# a = MyControllerKeyboard()

print(0.00057321919 * 5.3)