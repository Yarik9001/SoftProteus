import socket
import threading  # модуль для разделения на потоки
from multiprocessing import Process
from datetime import datetime  # получение  времени
import pyshine as ps
import cv2
import zmq
import base64
import numpy as np
from time import sleep  # сон
from ast import literal_eval  # модуль для перевода строки в словарик
from configparser import ConfigParser  # мудуль для работы с конфиг файлами
from os import system
import sys
from pyPS4Controller.controller import Controller
from keyboard import wait, on_release_key, on_press_key

from PyQt5 import QtCore, QtGui, QtWidgets

class MainRovPult:
    def __init__(self):
        self.startTime = str(datetime.now())

        # считывание конфиг файлов
        self.config = ConfigParser()
        # костыльный способ обработки запуска в разных операционках
        try:
            self.config.read("Soft\ControlPost\settings.ini")
            self.host = literal_eval(self.config["Server"]["host"])
        except:
            try:
                self.config.read(
                    "/home/proteus0/SoftProteus/Soft/ControlPost/settings.ini")
                self.host = literal_eval(self.config["Server"]["host"])
            except:
                print('None settings file')
                sys.exit()

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
        self.checkControllerPS4 = literal_eval(
            self.config["RovSettings"]["ControllerPS4"])

        self.P = literal_eval(self.config["RovSettings"]["P"])
        self.I = literal_eval(self.config["RovSettings"]["I"])
        self.D = literal_eval(self.config["RovSettings"]["D"])

        self.logger = LogerTXT(self)
        self.logger.WritelogSis('Start the MainRovPult')
        self.logger.WritelogSis('Init config')
        self.logger.WritelogSis('Init logger')
        
        self.server = ROVProteusServer(logcmd=self.logcmd, host=self.host, port=self.port) 
        self.logger.WritelogSis('Init client sockets')
        
        self.MassInput = {'time': None,
                        'dept': 0,
                        'a1': 0, 'a2': 0, 'a3': 0,
                        'a4': 0, 'a5': 0, 'a6': 0,
                        'Volt': 0,
                        'error': None,
                        'danger-error': False,
                        'x': 0, 'y': 0, 'z': 0}
        # массив принимаемый с пота управления
        self.MassOut = {'time': None,  
                          'motorpowervalue': 0.5,  
                          'x': 0, 'y': 0, 'z': 0, 'r': 0, 
                          'led': False,  
                          'manipul': 0,  
                          'servo-x1': 0, 'servo-y1': 0,  
                          'servo-x2': 0, 'servo-y2': 0,  
                          'ly-cor': 0, 'lx-cor': 0, 'ry-cor': 0, 'rx-cor': 0
                          }

    def RunServerReceivin(self, *args):
        '''Базовая функция для приема информации с аппарата '''
        while True:
            self.MassInput = self.server.ServerReceiver() # Прием 
            self.logger.WritelogInput(self.MassInput) # Запись в лог файл

    def RunServerDispatch(self, *args):
        '''Базовая функция для отправки информации на аппарат '''
        while True:
            # опрос джойстика или еще какой либо управляющей шляпы
            #######################################################
            #######################################################
            self.logger.WritelogOutput(self.MassOut)
            self.server.ServerDispatch(self.MassOut)
            sleep(0.1)

    def main(self):
        ProcessRunServerReceivin = Process(target=self.RunServerReceivin, args=(self,))
        ProcessRunServerDispatch = Process(target=self.RunServerDispatch, args=(self,))
        
        ProcessRunServerReceivin.start()
        ProcessRunServerDispatch.start()

class ROVProteusServer:
    '''
    Класс описывающий систему связи 
    logcmd - флаг вывода логов с cmd 
    host - хост на котором будет крутиться сервер 
    port- порт для подключения 
    '''
    def __init__(self, logcmd=False, host=None, port=None):
        self.HOST = host
        self.PORT = port
        self.logcmd = logcmd
        self.checkConnect = False

    def settingServer(self):
        # настройка сервера
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(1)
        self.user_socket, self.address = self.server.accept()
        self.checkConnect = True
        if self.logcmd:
            print("ROV-Connected", self.user_socket)

    def ServerReceiver(self):
        '''Функция для приема информации с аппарата'''
        data = self.user_socket.recv(512)
        if len(data) == 0:
            self.server.close()
            self.checkConnect = False
            if self.logcmd:
                print('ROV-disconnection', self.user_socket)
                return None
        MassInput = dict(literal_eval(str(data.decode('utf-8'))))
        if self.logcmd:
            print("DataInput-", MassInput)
        return MassInput

    def ServerDispatch(self, MassOut: dict):
        '''Функция для отправки на аппарат информации''' 
        MassOut["time"] = str(datetime.now())
        if self.logcmd:
            print('DataOutput-',MassOut)
        self.user_socket.send(str(MassOut).encode('utf-8'))


class LogerTXT:
    '''
    класс для логирования 
    NameRov - названия аппарата 
    time - время начала логирования 
    ratelog - частота логирования

    Основной принцип заключается в том что мы вытягиваем атрибуты 
    класса сервера и переодически из логируем
    '''

    def __init__(self, namerov='proteus0', starttime='2021-06-12 11:52:33.801128'):
        
        time = starttime
        NameRov = namerov
        time = '-'.join('-'.join('-'.join(time.split()).split('.')).split(':'))

        self.namefileSistem = "Soft/ControlPost/log/sistem/" + \
            f'{NameRov}-sis-{time}.txt'
        self.namefileInput = "Soft/ControlPost/log/input/" + \
            f'INPUT-{NameRov}-{time}.txt'
        self.namefileOutput = "Soft/ControlPost/log/output/" + \
            f'OUTPUT-{NameRov}-{time}.txt'

        # обработка ошибки с некорректным путем
        try:
            self.fileInput = open(self.namefileInput, "a+")
            self.fileOutput = open(self.namefileOutput, 'a+')
            self.fileSis = open(self.namefileSistem, 'a+')
        except:
            self.fileInput = open(f'INPUT-{NameRov}-{time}.txt', "a+")
            self.fileOutput = open(f'OUTPUT-{NameRov}-{time}.txt', "a+")
            self.fileSis = open(f'{NameRov}-sis-{time}.txt', "a+")

        # запись шапки
        self.fileInput.write(f"NameRov: {NameRov}\n")
        self.fileInput.write(f'Time: {time}\n')
        self.fileOutput.write(f"NameRov: {NameRov}\n")
        self.fileOutput.write(f'Time: {time}\n')
        self.fileSis.write(f"NameRov: {NameRov}\n")
        self.fileSis.write(f'Time: {time}\n')
        self.fileInput.close()
        self.fileOutput.close()
        self.fileSis.close()

    def WritelogInput(self, data: dict):
        self.fileInput = open(self.namefileInput, "a+")
        self.fileInput.write(str(data)+'\n')
        self.fileInput.close()

    def WritelogOutput(self, data: dict):
        self.fileOutput = open(self.namefileOutput, "a+")
        self.fileOutput.write(str(data)+'\n')
        self.fileOutput.close()

    # запись системных логов
    def WritelogSis(self, text):
        timelog = str(datetime.now())
        self.fileSis = open(self.namefileSistem, 'a+')
        self.fileSis.write(timelog + ' - ' + text + '\n')
        self.fileSis.close()

