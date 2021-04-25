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
        self.motorpowervalue = literal_eval(self.config["RovSettings"]["MotorPowerValue"])
        self.joystickrate = literal_eval(self.config["RovSettings"]["joystickrate"])

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
    def InitServer(self,*args):
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
    def InitLogger(self,*args):
        if self.log and (self.logOutput or self.logInput):
            self.logger = LogerTXT(self.server)
            if self.logInput:
                self.logger.WritelogInput()
            if self.logOutput:
                self.logger.WritelogOutput()


    # инициализация приложения 
    def InitApp(self, *args):
        self.QuiROV = APPGui()
        self.QuiROV.main()

    def InitJoystick(self, *args):
        # TODO Сделать опрос джойстика и инициализацию обьекта класса джойстик 
        pass
    
    # инициализация основного цикла 
    def MAIN(self):
        self.mainserver = threading.Thread(
            target=self.InitServer, args=(self,))

        self.mainJoistik = threading.Thread(
            target=self.InitJoystick, args=(self,))


        self.mainserver.start()
        self.mainJoistik.start()

        # self.InitApp()


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

    def __init__(self,name =None, log=True, logcmd=False, host=None, port=None, motorpowervalue=500, joystickrate=0.01, startTime=None):
        # инициализация атрибутов 
        self.HOST = host
        self.PORT = port
        self.JOYSTICKRATE = joystickrate 
        self.MotorPowerValue = motorpowervalue
        self.log = log 
        self.logcmd = logcmd
        self.DataInput = {}
        self.startTime = startTime

        # словарик для отправки на аппарат
        self.DataOutput = {'time': self.startTime,  # Текущее время
                            'motorpowervalue': self.MotorPowerValue,  # мощность моторов
                            'x': 0, 'y': 0, 'z': 0,  # по идее мощность моторов
                            'led': False,  # управление светом
                            'manipul': 0,  # Управление манипулятором
                            'servo-x1': 0, 'servo-y1': 0,  # управление подвесом курсовой камеры
                            'servo-x2': 0, 'servo-y2': 0}  # управление подвесом обзорной камеры

        # self.startservermain()  # поднимаем сервер

    def settingServer(self):
        # настройка сервера 
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen()
        self.user_socket, self.address = self.server.accept()
        return "ROV-Connected"
            

    def ReceiverProteus(self,*args):
        '''
        Прием информации с аппарата запись в атрибуты класса 
        (работает в фотонов режиме в отдельном потоке)
        '''
        while True:
            self.DataInput = dict(literal_eval(
                self.user_socket.recv(1024).decode('utf-8')))
            if self.logcmd:
                print(self.DataInput)


    def ControlProteus(self,*args):
        '''
        Отправка управляющей информации на аппарат через равные промежутки времени.
        Значения для отправки беруться из атрибутов класса, а изменяются в паралельных потоках.
        (работает в фоновом режиме в отдельном потоке) 
        '''
        while True:
            timecontrol = str(datetime.now())
            self.DataOutput["time"] = timecontrol
            self.user_socket.send(str(self.DataOutput).encode('utf-8'))
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
        self.RATELOG = self.rov.ratelog
        time = self.rov.startTime
        NameRov = self.rov.name
        time = '-'.join('-'.join('-'.join(time.split()).split('.')).split(':'))

        self.namefileInput = "ControlPost/log/" + f'INPUT-{NameRov}-{time}.txt'
        self.namefileOutput = "ControlPost/log/" + f'OUTPUT-{NameRov}-{time}.txt'

        # обработка ошибки с некорректным путем
        try: 
            self.fileInput = open(self.namefileInput, "a+")
            self.fileOutput = open(self.namefileOutput, 'a+')
        except:
            self.fileInput = open(f'INPUT-{NameRov}-{time}.txt')
            self.fileOutput = open(f'OUTPUT-{NameRov}-{time}.txt')

        # запись шапки
        self.fileInput.write(f"NameRov: {NameRov}\n")
        self.fileInput.write(f'Time: {time}\n')
        self.fileOutput.write(f"NameRov: {NameRov}\n")
        self.fileOutput.write(f'Time: {time}\n')
        self.fileInput.close()
        self.fileOutput.close()

    # логирование принятой информации раз в секунду
    def WritelogInput(self): # TODO переписать для того чтобы логер брал все из обьекта rov, а не тягал из сервера.
        pult = self.rov.server
        while True:
            self.fileInput = open(self.namefileInput, "a+")
            inf = str(pult.DataInput)
            self.fileInput.write(inf+'\n')
            # Запись ошибок 
            if pult.DataInput['error'] != None:
                errorinf = pult.DataInput['error']
                self.fileInput.write('ERROR :' + errorinf + '\n')
                
            sleep(self.RATELOG)
            self.fileInput.close()

    # паралельное логирование отсылаемой информации 
    def WritelogOutput(self):
        pult = self.rov.server
        while True:
            self.fileOutput = open(self.namefileOutput, "a+")
            inf = str(pult.DataOutput)
            self.fileOutput.write(inf+'\n')
            # Запись ошибок 
            if pult.DataOutput['error'] != None:
                errorinf = pult.DataOutput['error']
                self.fileOutput.write('ERROR :' + errorinf + '\n')

            sleep(self.RATELOG)
            self.fileOutput.close()



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

    # функция проверки прогресс баров 
    def checkprogress(self, *args):
        speed = 0.01
        for i in range(101):
            sleep(speed)
            self.progressBar.setValue(i)

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
        # проверка прогресс баров в отдельном потоке 
        # check = threading.Thread(
        #     target=self.ui.checkprogress, args=(self.ui,))
        # check.start()
        # показ окна и обработка закрытия 
        self.MainWindow.show() 
        sys.exit(self.app.exec_())



if __name__ == '__main__': # основной запуск 
    # Proteus = ServerMainPult(log=True, logcmd=True) # вызов сервера
    Proteus = MainRovPult()
    Proteus.MAIN()