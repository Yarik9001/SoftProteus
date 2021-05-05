from os import system
import socket
import sys
import threading



class ServerMainPult:
    '''
    минимальная реализация сервера для отладки 
    DataOutput - славарик для отправки на аппарат 
    logcmd - флаг отвечающий за логирование в командную строку 
    Матиматика считается при отправке на аппарат 
    '''
    def __init__(self):
        self.startTime = 0
        self.MotorPowerValue = 500
        self.logcmd = False
        self.DataPult = {'j1-val-y':0, 'j1-val-x':0, 'j2-val-y':0, 'j2-val-x':0}
        self.DataOutput = {'time': self.startTime,  # Текущее время
                            'motorpowervalue': self.MotorPowerValue,  # мощность моторов
                            'motor-1': 0, 'motor-2': 0,
                            'motor-3': 0, 'motor-4': 0,
                            'motor-5':0, 'motor-6': 0, # по идее мощность моторов
                            'led': False,  # управление светом
                            'manipul': 0,  # Управление манипулятором
                            'servo-x1': 0, 'servo-y1': 0,  # управление подвесом курсовой камеры
                            'servo-x2': 0, 'servo-y2': 0  # управление подвесом обзорной камеры
                            }

class Inspection():
    def __init__(self):
        self.checkConnect = False
        self.HOST = host
        self.PORT = port
        
#TODO
