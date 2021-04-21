import socket  # модуль для взаимодействия по сети
import threading  # модуль для разделения на потоки
from datetime import datetime  # получение  времени
from time import sleep  # сон
from ast import literal_eval  # модуль для перевода строки в словарик
from configparser import  ConfigParser # мудуль для работы с конфиг файлами 
# модуль для работы с джойстиком ps2
from pyPS4Controller.controller import Controller
# часть связанная с графическим интерфейсом
import sys
from PyQt5 import QtCore, QtWidgets


class ServerMainPult:
    '''
    Класс описывающий систему бекенд пульта 
    '''

    def __init__(self, log=True, logcmd=False, host=None, port=None, motorpowervalue=500, joystickrate=0.01):
        # init variable
        self.HOST = host
        self.PORT = port
        self.JOYSTICKRATE = joystickrate
        self.MotorPowerValue = motorpowervalue
        self.massControl = {'time': 0,  # Текущее время
                            'motorpowervalue': 1,  # мощность моторов
                            'x': 0, 'y': 0, 'z': 0,  # по идее мощность моторов
                            'led': False,  # управление светом
                            'manipul': 0,  # Управление манипулятором
                            'servo-x1': 0, 'servo-y1': 0,  # управление подвесом курсовой камеры
                            'servo-x2': 0, 'servo-y2': 0}  # управление подвесом обзорной камеры
        # словарик для отправки на аппарат

        self.log = log  # флаг логирования
        self.logcmd = logcmd
        self.datainput = {}  # получаемая информация
        self.startservermain()  # поднимаем сервер

    def settingServer(self):
        # setting server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen()
        if self.logcmd:
            print("Server is start and listening")

    def hello(self):
        # обмен преветсвиями
        self.user_socket, self.address = self.server.accept()
        data = self.user_socket.recv(256)
        self.user_socket.send('Connect-Pult1-25'.encode("utf-8"))
        if self.logcmd:
            print(data.decode("utf-8"))

    def ReceiverProteus(self, *args):
        '''
        Прием информации с аппарата
        '''
        while True:
            self.datainput = dict(literal_eval(
                self.user_socket.recv(1024).decode('utf-8')))
            # TODO тут что то делаем с полученной информацией ( выводим на экран и прочее )
            if self.logcmd:
                print(self.datainput)

    def ControlProteus(self, *args):
        '''
        Отправка управляющей информации на аппарат 
        '''
        while True:
            timecontrol = str(datetime.now())
            self.massControl["time"] = timecontrol
            self.massControl["x"] = 0
            self.massControl["y"] = 0
            self.massControl["z"] = 0
            # TODO сделать опрос джойстика или других управляющих приблуд

            outmass = str(self.massControl).encode('utf-8')
            self.user_socket.send(outmass)
            sleep(self.JOYSTICKRATE)

    def startmultithreading(self):
        # инициализация логирования
        self.loger = LogerTXT('Prteus0')

        # инициализация потоков приема и передачи
        receiver = threading.Thread(
            target=self.ReceiverProteus, args=(self,))

        dispatch = threading.Thread(
            target=self.ControlProteus, args=(self,))

        logthread = threading.Thread(
            target=self.loger.writelogpult, args=(self,))

        dispatch.start()
        receiver.start()
        logthread.start()

    def startservermain(self):
        # запуск бекенда сервера
        self.settingServer()
        self.hello()
        self.startmultithreading()


class LogerTXT:
    '''
    класс для логирования 
    '''

    def __init__(self, name):
        self.RATELOG = 1
        time = '-'.join('-'.join('-'.join(str(datetime.now()
                                              ).split()).split('.')).split(':'))
        self.name = "ControlPost/log/" + f'{name}-{time}.txt'
        try:  # обработка ошибки с некорректным путем
            self.file = open(self.name, "a+")
        except:
            self.file = open(f'{name}-{time}.txt')
        # запись шапки
        self.file.write(f"Name: {name}\n")
        self.file.write(f'Time: {time}\n')
        self.file.close()

    def writelog(self, info):  # запись одной строчки в лог
        self.file.write(info + '\n')

    # паралельное логирование принятой информации раз в секунду
    def writelogpult(self, pult: ServerMainPult):
        while True:
            self.file = open(self.name, "a+")
            inf = str(pult.datainput)
            self.file.write(inf+'\n')
            if pult.datainput['error'] != None:
                errorinf = pult.datainput['error']
                self.file.write('ERROR :' + errorinf + '\n')
            sleep(self.RATELOG)
            self.file.close()

    def VisualizationLog(self):
        # TODO визуализация логов
        pass


class MyController(Controller):
    # TODO класс взаимодействия с джойстиком +-
    pass


class Ui_MainWindow(object):  # класс описывающий внешний вид приложения
    def setupUi(self, MainWindow):
        self.initprogress = 0
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 480)
        MainWindow.setStyleSheet("background-color: rgb(40, 40, 40);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(270, 380, 20, 71))
        self.progressBar.setProperty("value", self.initprogress)
        self.progressBar.setOrientation(QtCore.Qt.Vertical)
        self.progressBar.setObjectName("progressBar")

        self.progressBar_2 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_2.setGeometry(QtCore.QRect(300, 380, 20, 71))
        self.progressBar_2.setProperty("value", self.initprogress)
        self.progressBar_2.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_2.setObjectName("progressBar_2")

        self.progressBar_3 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_3.setGeometry(QtCore.QRect(330, 380, 20, 71))
        self.progressBar_3.setProperty("value", self.initprogress)
        self.progressBar_3.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_3.setObjectName("progressBar_3")

        self.progressBar_4 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_4.setGeometry(QtCore.QRect(360, 380, 20, 71))
        self.progressBar_4.setProperty("value", self.initprogress)
        self.progressBar_4.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_4.setObjectName("progressBar_4")

        self.progressBar_5 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_5.setGeometry(QtCore.QRect(390, 380, 20, 71))
        self.progressBar_5.setProperty("value", self.initprogress)
        self.progressBar_5.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_5.setObjectName("progressBar_5")

        self.progressBar_6 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_6.setGeometry(QtCore.QRect(420, 380, 20, 71))
        self.progressBar_6.setProperty("value", self.initprogress)
        self.progressBar_6.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_6.setObjectName("progressBar_6")

        self.dial = QtWidgets.QDial(self.centralwidget)
        self.dial.setGeometry(QtCore.QRect(100, 350, 100, 100))
        self.dial.setTracking(True)
        self.dial.setObjectName("dial")
        self.dial.setMinimum(0)
        self.dial.setMaximum(1000)
        self.dial.setValue(0)
        self.dial.valueChanged.connect(self.sliderMoved)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 659, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def sliderMoved(self):
        print("Dial value = %i" % (self.dial.value()))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def checkprogress(self, *args):
        speed = 0.01
        for i in range(101):
            sleep(speed)
            self.progressBar.setValue(i)
            self.dial.setValue(i * 10)

        for i in range(101):
            sleep(speed)
            self.progressBar_2.setValue(i)

        for i in range(101):
            sleep(speed)
            self.progressBar_3.setValue(i)

        for i in range(101):
            sleep(speed)
            self.progressBar_4.setValue(i)

        for i in range(101):
            sleep(speed)
            self.progressBar_5.setValue(i)

        for i in range(101):
            sleep(speed)
            self.progressBar_6.setValue(i)


class APPGui():  # класс описывающий работу приложение
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)

    def main(self):
        check = threading.Thread(
            target=self.ui.checkprogress, args=(self.ui,))
        check.start()

        self.MainWindow.show()
        sys.exit(self.app.exec_())

class MainRovPult:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("ControlPost/settings.ini")
        self.host = literal_eval(self.config["Server"]["host"]) 
        self.port = literal_eval(self.config["Server"]["port"])
        self.log = literal_eval(self.config["Server"]["log"])
        self.logcmd = literal_eval(self.config["Server"]["logcmd"])

        self.name = literal_eval(self.config["RovSettings"]["name"])
        self.motorpowervalue = literal_eval(self.config["RovSettings"]["MotorPowerValue"])
        self.joystickrate = literal_eval(self.config["RovSettings"]["joystickrate"])

        self.P = literal_eval(self.config["RovSettings"]["P"])
        self.I = literal_eval(self.config["RovSettings"]["I"])
        self.D = literal_eval(self.config["RovSettings"]["D"])

    def variablePrint(self):
        print(self.host)
        print(self.port)
        print(self.log)
        print(self.logcmd)
        print(self.name)
        print(self.motorpowervalue)
        print(self.joystickrate)

    def TypeVariablePrint(self):
        print(type(self.host))
        print(type(self.port))
        print(type(self.log))
        print(type(self.logcmd))
        print(type(self.name))
        print(type(self.motorpowervalue))
        print(type(self.joystickrate))     
        
    
    def InitServer(self):
        self.server = ServerMainPult(log=self.log, logcmd=self.logcmd,
                                    host=self.host, port=self.port,
                                    motorpowervalue=self.motorpowervalue,
                                    joystickrate=self.joystickrate)
        self.server.startservermain()

    def InitApp(self):
        self.QuiROV = APPGui()
        self.QuiROV.main()

    def MAIN(self):
        self.InitServer()
        self.InitApp()


if __name__ == '__main__': # основной запуск 
    # Proteus = ServerMainPult(log=True, logcmd=True) # вызов сервера
    Proteus = MainRovPult()
    Proteus.MAIN()