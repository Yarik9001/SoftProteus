import socket  # модуль для взаимодействия по сети
import threading  # модуль для разделения на потоки
from datetime import datetime  # получение  времени
from time import sleep  # сон
from ast import literal_eval  # модуль для перевода строки в словарик
from configparser import ConfigParser  # мудуль для работы с конфиг файлами
from os import system


# модуль для работы с джойстиком ps2
try:
    from pyPS4Controller.controller import Controller
except:
    try:
        system('pip install pyPS4Controller')
    except:
        system('sudo pip install pyPS4Controller')

# модуль для управления с клавиатуры
try:
    from keyboard import wait, on_release_key, on_press_key
except:
    try:
        system('pip install keyboard')
    except:
        system('sudo pip install keyboard')

# часть связанная с графическим интерфейсом
import sys
from PyQt5 import QtCore, QtWidgets


class MainRovPult:
    def __init__(self):
        self.startTime = str(datetime.now())

        # считывание конфиг файлов
        self.config = ConfigParser()
        self.config.read("ControlPost/settings.ini")
        self.host = literal_eval(self.config["Server"]["host"])
        self.port = literal_eval(self.config["Server"]["port"])
        self.log = literal_eval(self.config["Server"]["log"])
        self.logcmd = literal_eval(self.config["Server"]["logcmd"])
        self.ratelog = literal_eval(self.config['Server']['ratelog'])
        self.logOutput = literal_eval(self.config['Server']['logOutput'])
        self.logInput = literal_eval(self.config['Server']['logInput'])

        self.name = literal_eval(self.config["RovSettings"]["name"])
        self.motorpowervalue = literal_eval(
            self.config["RovSettings"]["MotorPowerValue"])
        self.joystickrate = literal_eval(
            self.config["RovSettings"]["joystickrate"])

        self.P = literal_eval(self.config["RovSettings"]["P"])
        self.I = literal_eval(self.config["RovSettings"]["I"])
        self.D = literal_eval(self.config["RovSettings"]["D"])

        if self.logcmd:
            self.variablePrint()

    # вывод показаний конфигов
    def variablePrint(self):
        print('Start: ', self.startTime)
        print('host-', self.host)
        print("port-", self.port)
        print("log-", self.log)
        print("logcmd-", self.logcmd)
        print("Name-", self.name)
        print("MotorValue-", self.motorpowervalue)
        print("JoystikRate-", self.joystickrate)
        print("RateLog-", self.ratelog)
        print('logInput-', self.logInput)
        print('logOutput-', self.logOutput)

    # инициализация сервера
    def InitServer(self, *args):
        self.server = ServerMainPult(
            log=self.log,
            logcmd=self.logcmd,
            host=self.host,
            port=self.port,
            motorpowervalue=self.motorpowervalue,
            joystickrate=self.joystickrate,
            startTime=self.startTime
        )

        self.server.startservermain()

    # инициализация логирования
    def InitLogger(self, *args):
        if self.log and (self.logOutput or self.logInput):
            self.logger = LogerTXT(self)
            if self.logInput:
                loginp = threading.Thread(
                    target=self.logger.WritelogInput, args=(self.logger,))
                loginp.start()
            if self.logOutput:
                logout = threading.Thread(
                    target=self.logger.WritelogOutput, args=(self.logger,))
                logout.start()

    # инициализация приложения

    def InitApp(self, *args):
        self.QuiROV = APPGui()
        self.QuiROV.main()

    def InitJoystick(self, *args):
        # TODO Сделать опрос джойстика и инициализацию обьекта класса джойстик
        pass

    def InitKeyboardPult(self, *args):
        self.keyboardPult = MyControllerKeyboard(self.server)
        self.keyboardPult.mainKeyboard()

    # инициализация основного цикла
    def MAIN(self):
        self.mainserver = threading.Thread(
            target=self.InitServer, args=(self,))

        self.mainJoistik = threading.Thread(
            target=self.InitJoystick, args=(self,))

        self.mainLogger = threading.Thread(
            target=self.InitLogger, args=(self,))

        self.mainKeyboard = threading.Thread(
            target=self.InitKeyboardPult, args=(self,))

        self.mainserver.start()
        self.mainJoistik.start()
        self.mainLogger.start()
        self.mainKeyboard.start()

        self.InitApp()


class ServerMainPult:
    '''
    Класс описывающий систему бекенд пульта
    log - флаг логирования 
    log cmd - флаг вывода логов с cmd 
    host - хост на котором будет крутиться сервер 
    port- порт для подключения 
    motorpowervalue=500 - программное ограничение мощности моторов 
    joystickrate - частота опроса джойстика 

    '''

    def __init__(self, name=None, log=True, logcmd=False, host=None, port=None, motorpowervalue=500, joystickrate=0.01, startTime=None):
        # инициализация атрибутов
        self.HOST = host
        self.PORT = port
        self.JOYSTICKRATE = joystickrate
        self.MotorPowerValue = motorpowervalue
        self.log = log
        self.logcmd = logcmd
        self.startTime = startTime
        self.checkConnect = False

        # словарик для отправки на аппарат
        self.DataOutput = {'time': self.startTime,  # Текущее время
                           'motorpowervalue': self.MotorPowerValue,  # мощность моторов
                           'x': 0, 'y': 0, 'z': 0, 'r': 0,  # по идее мощность моторов
                           'led': False,  # управление светом
                           'manipul': 0,  # Управление манипулятором
                           'servo-x1': 0, 'servo-y1': 0,  # управление подвесом курсовой камеры
                           'servo-x2': 0, 'servo-y2': 0  # управление подвесом обзорной камеры
                           }
        self.DataInput = {
            'time': None,
            'dept': 0,
            'm1': 0, 'm2': 0, 'm3': 0,
            'm4': 0, 'm5': 0, 'm6': 0,
            'Volt': 0,
            'error': None,
            'danger-error': False,
            'x': 0, 'y': 0, 'z': 0
        }

        # self.startservermain()  # поднимаем сервер

    def settingServer(self):
        # настройка сервера
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen()
        self.user_socket, self.address = self.server.accept()
        self.checkConnect = True
        if self.logcmd:
            print("ROV-Connected", self.user_socket)

    def ReceiverProteus(self, *args):
        '''
        Прием информации с аппарата запись в атрибуты класса 
        (работает в фотонов режиме в отдельном потоке)
        '''
        while self.checkConnect:
            data = self.user_socket.recv(176)
            if len(data) == 0:
                self.server.close()
                self.checkConnect = False
                if self.logcmd:
                    print('ROV-disconnection', self.user_socket)
                break

            self.DataInput = dict(literal_eval(str(data.decode('utf-8'))))
            if self.logcmd:
                print("DataInput-", self.DataInput)

    def ControlProteus(self, *args):
        '''
        Отправка управляющей информации на аппарат через равные промежутки времени.
        Значения для отправки беруться из атрибутов класса, а изменяются в паралельных потоках.
        (работает в фоновом режиме в отдельном потоке) 
        '''
        while self.checkConnect:
            timecontrol = str(datetime.now())
            self.DataOutput["time"] = timecontrol
            self.user_socket.send(str(self.DataOutput).encode('utf-8'))
            if self.logcmd:
                print('DataOutput-', self.DataOutput)
            sleep(self.JOYSTICKRATE)

    def startmultithreading(self):
        # инициализация потоков приема и передачи
        receiver = threading.Thread(
            target=self.ReceiverProteus, args=(self,))

        dispatch = threading.Thread(
            target=self.ControlProteus, args=(self,))

        dispatch.start()
        receiver.start()

    # Для отладки
    def startservermain(self):
        self.settingServer()
        self.startmultithreading()


class MyControllerKeyboard:
    '''
    Класс для резервного управления ROV с помощью клавиатуры ноутбука 
    вперед - w
    назад - s
    вправо - a
    влево - d
    вверх - up
    вниз - down  
    поворот влево - left
    поворот направо - right
    '''

    def __init__(self, pult: ServerMainPult):
        self.pult = pult

    def mainKeyboard(self):
        on_press_key('w', self.forward, suppress=False)
        on_release_key('w', self.forward_release, suppress=False)
        on_press_key('s', self.back, suppress=False)
        on_release_key('s', self.back_release, suppress=False)
        on_press_key('a', self.left, suppress=False)
        on_release_key('a', self.left_relaese, suppress=False)
        on_press_key('d', self.right, suppress=False)
        on_release_key('d', self.right_relaese, suppress=False)
        on_press_key('up', self.up, suppress=False)
        on_release_key('up', self.up_relaese, suppress=False)
        on_press_key('down', self.down, suppress=False)
        on_release_key('down', self.down_relaese, suppress=False)
        on_press_key('left', self.turn_left, suppress=False)
        on_release_key('left', self.turn_left_relaese, suppress=False)
        on_press_key('right', self.turn_right, suppress=False)
        on_release_key('right', self.turn_right_relaese, suppress=False)
        wait()

    def forward(self, key):
        self.pult.DataOutput['y'] = 32767
        if self.pult.logcmd:
            print('forward')

    def forward_release(self, key):
        self.pult.DataOutput['y'] = 0
        if self.pult.logcmd:
            print('forward-stop')

    def back(self, key):
        self.pult.DataOutput['y'] = -32767
        if self.pult.logcmd:
            print('back')

    def back_release(self, key):
        self.pult.DataOutput['y'] = 0
        if self.pult.logcmd:
            print('back-relaese')

    def left(self, key):
        self.pult.DataOutput['x'] = -32767
        if self.pult.logcmd:
            print('left')

    def left_relaese(self, key):
        self.pult.DataOutput['x'] = 0
        if self.pult.logcmd:
            print('left_relaese')

    def right(self, key):
        self.pult.DataOutput['x'] = 32767
        if self.pult.logcmd:
            print('right')

    def right_relaese(self, key):
        self.pult.DataOutput['x'] = 0
        if self.pult.logcmd:
            print('right-relaese')

    def up(self, key):
        self.pult.DataOutput['z'] = 32767
        if self.pult.logcmd:
            print('up')

    def up_relaese(self, key):
        self.pult.DataOutput['z'] = 0
        if self.pult.logcmd:
            print('up-relaese')

    def down(self, key):
        self.pult.DataOutput['z'] = -32767
        if self.pult.logcmd:
            print('down')

    def down_relaese(self, key):
        self.pult.DataOutput['z'] = 0
        if self.pult.logcmd:
            print('down-relaese')

    def turn_left(self, key):
        self.pult.DataOutput['r'] = -32767
        if self.pult.logcmd:
            print('turn-left')

    def turn_left_relaese(self, key):
        self.pult.DataOutput['r'] = 0
        if self.pult.logcmd:
            print('turn-stop')

    def turn_right(self, key):
        self.pult.DataOutput['r'] = 32767
        if self.pult.logcmd:
            print('turn-right')

    def turn_right_relaese(self, key):
        self.pult.DataOutput['r'] = 0
        if self.pult.logcmd:
            print('turn-stop')


class LogerTXT:
    '''
    класс для логирования 
    NameRov - названия аппарата 
    time - время начала логирования 
    ratelog - частота логирования

    Основной принцип заключается в том что мы вытягиваем атрибуты 
    класса сервера и переодически из логируем
    '''

    def __init__(self, rov: MainRovPult):
        self.rov = rov
        self.ratelog = self.rov.ratelog
        time = self.rov.startTime
        NameRov = self.rov.name
        time = '-'.join('-'.join('-'.join(time.split()).split('.')).split(':'))

        self.namefileInput = "ControlPost/log/" + f'INPUT-{NameRov}-{time}.txt'
        self.namefileOutput = "ControlPost/log/" + \
            f'OUTPUT-{NameRov}-{time}.txt'

        # обработка ошибки с некорректным путем
        try:
            self.fileInput = open(self.namefileInput, "a+")
            self.fileOutput = open(self.namefileOutput, 'a+')
        except:
            self.fileInput = open(f'INPUT-{NameRov}-{time}.txt', "a+")
            self.fileOutput = open(f'OUTPUT-{NameRov}-{time}.txt', "a+")

        # запись шапки
        self.fileInput.write(f"NameRov: {NameRov}\n")
        self.fileInput.write(f'Time: {time}\n')
        self.fileOutput.write(f"NameRov: {NameRov}\n")
        self.fileOutput.write(f'Time: {time}\n')
        self.fileInput.close()
        self.fileOutput.close()

    # логирование принятой информации раз в секунду
    # TODO переписать для того чтобы логер брал все из обьекта rov, а не тягал из сервера.
    def WritelogInput(self, *args):
        pult = self.rov.server
        print('logInput')
        while True:
            if pult.checkConnect:
                self.fileInput = open(self.namefileInput, "a+")
                inf = str(pult.DataInput)
                self.fileInput.write(inf+'\n')
                # Запись ошибок
                if pult.DataInput['error'] != None:
                    errorinf = pult.DataInput['error']
                    self.fileInput.write('ERROR :' + errorinf + '\n')

                sleep(self.ratelog)
                self.fileInput.close()

    # паралельное логирование отсылаемой информации
    def WritelogOutput(self, *args):
        pult = self.rov.server
        print('logWrite')
        while True:
            if pult.checkConnect:
                self.fileOutput = open(self.namefileOutput, "a+")
                inf = str(pult.DataOutput)
                self.fileOutput.write(inf+'\n')
                self.fileOutput.close()
                sleep(self.ratelog)


class MyController(Controller):
    # TODO класс взаимодействия с джойстиком +-
    pass


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1366, 700)
        font = QtGui.QFont()
        font.setPointSize(12)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet("background-color: rgb(40, 40, 40);")
        MainWindow.setIconSize(QtCore.QSize(25, 25))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(625, 600, 6, 60))
        self.progressBar.setStyleSheet("QProgressBar {\n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: rgb(0, 170, 255);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar.setProperty("value", 24)
        self.progressBar.setTextVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Vertical)
        self.progressBar.setObjectName("progressBar")
        self.progressBar_2 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_2.setGeometry(QtCore.QRect(635, 600, 6, 60))
        self.progressBar_2.setAutoFillBackground(False)
        self.progressBar_2.setStyleSheet("QProgressBar {\n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"background-color: rgb(0, 255, 127);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar_2.setProperty("value", 24)
        self.progressBar_2.setTextVisible(False)
        self.progressBar_2.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_2.setInvertedAppearance(False)
        self.progressBar_2.setObjectName("progressBar_2")
        self.progressBar_3 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_3.setGeometry(QtCore.QRect(657, 600, 6, 60))
        self.progressBar_3.setStyleSheet("QProgressBar {\n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: rgb(0, 170, 255);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar_3.setProperty("value", 24)
        self.progressBar_3.setTextVisible(False)
        self.progressBar_3.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_3.setObjectName("progressBar_3")
        self.progressBar_4 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_4.setGeometry(QtCore.QRect(667, 600, 6, 60))
        self.progressBar_4.setStyleSheet("QProgressBar {\n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"background-color: rgb(0, 255, 127);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar_4.setProperty("value", 24)
        self.progressBar_4.setTextVisible(False)
        self.progressBar_4.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_4.setObjectName("progressBar_4")
        self.progressBar_5 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_5.setGeometry(QtCore.QRect(687, 600, 6, 60))
        self.progressBar_5.setStyleSheet("QProgressBar {\n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: rgb(0, 170, 255);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar_5.setProperty("value", 24)
        self.progressBar_5.setTextVisible(False)
        self.progressBar_5.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_5.setObjectName("progressBar_5")
        self.progressBar_6 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_6.setGeometry(QtCore.QRect(697, 600, 6, 60))
        self.progressBar_6.setStyleSheet("QProgressBar {\n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"background-color: rgb(0, 255, 127);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar_6.setProperty("value", 24)
        self.progressBar_6.setTextVisible(False)
        self.progressBar_6.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_6.setObjectName("progressBar_6")
        self.progressBar_7 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_7.setGeometry(QtCore.QRect(720, 600, 6, 60))
        self.progressBar_7.setStyleSheet("QProgressBar {\n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: rgb(0, 170, 255);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar_7.setProperty("value", 24)
        self.progressBar_7.setTextVisible(False)
        self.progressBar_7.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_7.setObjectName("progressBar_7")
        self.progressBar_8 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_8.setGeometry(QtCore.QRect(730, 600, 6, 60))
        self.progressBar_8.setStyleSheet("QProgressBar {\n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"background-color: rgb(0, 255, 127);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar_8.setProperty("value", 24)
        self.progressBar_8.setTextVisible(False)
        self.progressBar_8.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_8.setObjectName("progressBar_8")
        self.progressBar_9 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_9.setGeometry(QtCore.QRect(750, 600, 6, 60))
        self.progressBar_9.setStyleSheet("QProgressBar {\n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: rgb(0, 170, 255);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar_9.setProperty("value", 24)
        self.progressBar_9.setTextVisible(False)
        self.progressBar_9.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_9.setObjectName("progressBar_9")
        self.progressBar_10 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_10.setGeometry(QtCore.QRect(760, 600, 6, 60))
        self.progressBar_10.setStyleSheet("QProgressBar {\n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"background-color: rgb(0, 255, 127);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar_10.setProperty("value", 24)
        self.progressBar_10.setTextVisible(False)
        self.progressBar_10.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_10.setObjectName("progressBar_10")
        self.progressBar_11 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_11.setGeometry(QtCore.QRect(780, 600, 6, 60))
        self.progressBar_11.setStyleSheet("QProgressBar {\n"
"    \n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    \n"
"    background-color: rgb(0, 170, 255);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar_11.setProperty("value", 24)
        self.progressBar_11.setTextVisible(False)
        self.progressBar_11.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_11.setObjectName("progressBar_11")
        self.progressBar_12 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_12.setGeometry(QtCore.QRect(790, 600, 6, 60))
        self.progressBar_12.setStyleSheet("QProgressBar {\n"
"    background-color: rgb(100, 100, 100);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"background-color: rgb(0, 255, 127);\n"
"    border-radius: 3px\n"
"}")
        self.progressBar_12.setProperty("value", 24)
        self.progressBar_12.setTextVisible(False)
        self.progressBar_12.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_12.setObjectName("progressBar_12")
        self.dial = QtWidgets.QDial(self.centralwidget)
        self.dial.setGeometry(QtCore.QRect(530, 580, 75, 75))
        self.dial.setStyleSheet("background-color: rgb(120, 120, 120);")
        self.dial.setPageStep(100)
        self.dial.setTracking(True)
        self.dial.setOrientation(QtCore.Qt.Vertical)
        self.dial.setInvertedAppearance(False)
        self.dial.setInvertedControls(False)
        self.dial.setWrapping(False)
        self.dial.setNotchTarget(3.7)
        self.dial.setNotchesVisible(True)
        self.dial.setObjectName("dial")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(625, 660, 191, 17))
        self.label.setStyleSheet("font: 10pt \"Lato\";\n"
"font: 75 10pt \"Cantarell\";\n"
"font: 75 oblique 10pt \"DejaVu Sans\";\n"
"color: rgb(85, 170, 255);")
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(550, 650, 41, 31))
        font = QtGui.QFont()
        font.setFamily("Cantarell Extra Bold")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(10)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("\n"
"font: 81 10pt \"Cantarell Extra Bold\";\n"
"color: rgb(0, 170, 255);")
        self.label_2.setObjectName("label_2")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(30, 599, 61, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet("color: rgb(0, 170, 255);")
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(10, 619, 71, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_5.setFont(font)
        self.label_5.setStyleSheet("color: rgb(0, 170, 255);")
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(30, 639, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_6.setFont(font)
        self.label_6.setStyleSheet("color: rgb(0, 170, 255);")
        self.label_6.setObjectName("label_6")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(90, 599, 62, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(90, 619, 62, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(90, 640, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(850, 590, 501, 81))
        self.textEdit.setObjectName("textEdit")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(0, 0, 1361, 561))
        self.label_7.setText("")
        self.label_7.setObjectName("label_7")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(1270, 10, 81, 81))
        self.label_10.setObjectName("label_10")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(0, 570, 1361, 10))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(220, 600, 61, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(170, 600, 41, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_12.setFont(font)
        self.label_12.setStyleSheet("color: rgb(0, 170, 255);")
        self.label_12.setObjectName("label_12")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ROV-0.1"))
        self.label.setText(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'DejaVu Sans\'; font-size:10pt; font-weight:72; font-style:italic;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600; font-style:normal;\">M1   M2   M3   M4   M5   M6</span></p></body></html>"))
        self.label_2.setText(_translate("MainWindow", "Power"))
        self.label_4.setText(_translate("MainWindow", "Dept:"))
        self.label_5.setText(_translate("MainWindow", "Azimut:"))
        self.label_6.setText(_translate("MainWindow", "Time:"))
        self.label_3.setText(_translate("MainWindow", "None"))
        self.label_8.setText(_translate("MainWindow", "None"))
        self.label_9.setText(_translate("MainWindow", "None"))
        self.label_10.setText(_translate("MainWindow", "TextLabel"))
        self.label_11.setText(_translate("MainWindow", "None"))
        self.label_12.setText(_translate("MainWindow", "Volt:"))


class APPGui():  # класс описывающий работу приложение
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)

    def main(self):
        # проверка прогресс баров в отдельном потоке
        # check = threading.Thread(
        #     target=self.ui.checkprogress, args=(self.ui,))
        # check.start()
        # показ окна и обработка закрытия
        self.MainWindow.show()
        sys.exit(self.app.exec_())


if __name__ == '__main__':  # основной запуск
    # Proteus = ServerMainPult(log=True, logcmd=True) # вызов сервера
    Proteus = MainRovPult()
    Proteus.MAIN()
