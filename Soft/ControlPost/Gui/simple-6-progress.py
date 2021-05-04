from PyQt5 import QtCore, QtGui, QtWidgets
from keyboard import wait, on_release_key, on_press_key
from threading import Thread
from time import sleep
import sys

class ServerMainPult:
    '''
    минимальная реализация сервера для отладки 
    DataOutput - славарик для отправки на аппарат 
    logcmd - флаг отвечающий за логирование в командную строку 
    '''
    def __init__(self):
        self.startTime = 0
        self.MotorPowerValue = 500
        self.logcmd = False
        self.DataOutput = {'time': self.startTime,  # Текущее время
                            'motorpowervalue': self.MotorPowerValue,  # мощность моторов
                            'x': 0, 'y': 0, 'z': 0, 'r': 0,  # по идее мощность моторов
                            'led': False,  # управление светом
                            'manipul': 0,  # Управление манипулятором
                            'servo-x1': 0, 'servo-y1': 0,  # управление подвесом курсовой камеры
                            'servo-x2': 0, 'servo-y2': 0  # управление подвесом обзорной камеры
                            }

class MyThread(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(dict)
    def  __init__(self, pult:ServerMainPult, parent=None):
        self.pult = pult
        QtCore.QThread.__init__(self, parent)
        
    def run(self):
        while True:
            print(self.pult.DataOutput)
            self.mysignal.emit(self.pult.DataOutput) # Передача данных из потока через сигнал
            sleep(0.1)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, pult:ServerMainPult):
        self.pult = pult
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(260, 323)
        MainWindow.setStyleSheet("background-color: rgb(62, 62, 62);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(20, 20, 20, 221))
        self.progressBar.setStyleSheet("QProgressBar {\n"
                                       "    background-color: rgb(161, 161, 161);\n"
                                       "    border-radius: 10px;\n"
                                       "}\n"
                                       "\n"
                                       "QProgressBar::chunk {\n"
                                       "    background-color: rgb(0, 170, 255);\n"
                                       "    border-radius: 10px\n"
                                       "}")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setOrientation(QtCore.Qt.Vertical)
        self.progressBar.setObjectName("progressBar")


        self.progressBar_2 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_2.setGeometry(QtCore.QRect(60, 20, 20, 221))
        self.progressBar_2.setStyleSheet("QProgressBar {\n"
                                         "    background-color: rgb(161, 161, 161);\n"
                                         "    border-radius: 10px;\n"
                                         "}\n"
                                         "\n"
                                         "QProgressBar::chunk {\n"
                                         "    background-color: rgb(0, 170, 255);\n"
                                         "    border-radius: 10px\n"
                                         "}")
        self.progressBar_2.setProperty("value", 0)
        self.progressBar_2.setTextVisible(True)
        self.progressBar_2.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_2.setObjectName("progressBar_2")
        
        
        self.progressBar_3 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_3.setGeometry(QtCore.QRect(100, 20, 20, 221))
        self.progressBar_3.setStyleSheet("QProgressBar {\n"
                                         "    background-color: rgb(161, 161, 161);\n"
                                         "    border-radius: 10px;\n"
                                         "}\n"
                                         "\n"
                                         "QProgressBar::chunk {\n"
                                         "    background-color: rgb(0, 170, 255);\n"
                                         "    border-radius: 10px\n"
                                         "}")
        self.progressBar_3.setProperty("value", 0)
        self.progressBar_3.setTextVisible(True)
        self.progressBar_3.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_3.setObjectName("progressBar_3")
        
        
        self.progressBar_4 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_4.setGeometry(QtCore.QRect(140, 20, 20, 221))
        self.progressBar_4.setStyleSheet("QProgressBar {\n"
                                         "    background-color: rgb(161, 161, 161);\n"
                                         "    border-radius: 10px;\n"
                                         "}\n"
                                         "\n"
                                         "QProgressBar::chunk {\n"
                                         "    background-color: rgb(0, 170, 255);\n"
                                         "    border-radius: 10px\n"
                                         "}")
        self.progressBar_4.setProperty("value", 0)
        self.progressBar_4.setTextVisible(True)
        self.progressBar_4.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_4.setObjectName("progressBar_4")
        
        
        self.progressBar_5 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_5.setGeometry(QtCore.QRect(180, 20, 20, 221))
        self.progressBar_5.setStyleSheet("QProgressBar {\n"
                                         "    background-color: rgb(161, 161, 161);\n"
                                         "    border-radius: 10px;\n"
                                         "}\n"
                                         "\n"
                                         "QProgressBar::chunk {\n"
                                         "    background-color: rgb(0, 170, 255);\n"
                                         "    border-radius: 10px\n"
                                         "}")
        self.progressBar_5.setProperty("value", 0)
        self.progressBar_5.setTextVisible(True)
        self.progressBar_5.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_5.setObjectName("progressBar_5")
        
        
        self.progressBar_6 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_6.setGeometry(QtCore.QRect(220, 20, 20, 221))
        self.progressBar_6.setStyleSheet("QProgressBar {\n"
                                         "    background-color: rgb(161, 161, 161);\n"
                                         "    border-radius: 10px;\n"
                                         "}\n"
                                         "\n"
                                         "QProgressBar::chunk {\n"
                                         "    background-color: rgb(0, 170, 255);\n"
                                         "    border-radius: 10px\n"
                                         "}")
        self.progressBar_6.setProperty("value", 0)
        self.progressBar_6.setTextVisible(True)
        self.progressBar_6.setOrientation(QtCore.Qt.Vertical)
        self.progressBar_6.setObjectName("progressBar_6")
        
        
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 270, 200, 14))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setStyleSheet("color: rgb(85, 170, 255);")
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.mythread = MyThread(self.pult) 
        self.mythread.started.connect(self.on_started)
        self.mythread.mysignal.connect(self.on_change, QtCore.Qt.QueuedConnection)
        self.mythread.start()
        self.label.setText("Value: None")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        
        
    def on_started(self): # Вызывается при запуске потока
        print('start thread')
        
    def on_change(self, data):
        '''
        Движение вперед - (1 вперед 2 вперед 3 назад 4 назад) 
        Движение назад - (1 назад 2 назад 3 вперед 4 вперед)
        Движение лагом вправо - (1 назад 2 вперед 3 вперед 4 назад)
        Движение лагом влево - (1 вперед 2 назад 3 назад 4 вперед)
        Движение вверх - (5 вниз 6 вниз)
        Движение вниз - (5 вверх 6 вверх)
        Поворот направо 
        Поворот налево 
        '''
        
        def transformation(value:int):
            '''
            Функция перевода значений АЦП с джойстика в проценты, где 50 процентов
            дефолтное значение
            '''
            value = (32768 - value) // 655
            return value
        
        self.label.setText("Value: ")
        
        self.progressBar.setValue()
        self.progressBar_2.setValue()
        # self.progressBar_3.setValue()
        # self.progressBar_4.setValue()
        self.progressBar_5.setValue()
        self.progressBar_6.setValue()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Main", "Main"))
        MainWindow.setStyleSheet("background-color: rgb(66, 66, 66);")
        



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


if __name__ == '__main__':
    servpass = ServerMainPult()
    keyboardPult = MyControllerKeyboard(servpass)
    
    def InitKeyboardPult():
        keyboardPult.mainKeyboard()
            
    mainKeyboard = Thread(target=InitKeyboardPult)
    mainKeyboard.start()
    
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, servpass)
    MainWindow.show()
    sys.exit(app.exec_())
