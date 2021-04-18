# Не обращайте внимания это просто свалка всякого потенцеально полезного (не точно)
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
