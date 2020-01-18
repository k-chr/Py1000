# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:27:21 2020

@author: Kamil Chrustowski
"""
import sys
from functionalrunnable import FunctionalRunnable
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from PyQt5.QtWidgets import *
class CommunicationHandler:
    messageReceived = pyqtSignal(str)
    __socket = None
    __should_exit = False
    __receiving_service = QThreadPool()
    __sending_service = QThreadPool()
    __receiving_service.setMaxThreadCount(1)
    __sending_service.setMaxThreadCount(1)
    def __init__(self, socket):
        self.__socket = socket
        self.__socket.readyread.connect(self.get_message)
    def cleanUp(self):
        print("cleaning up")
        self.__should_exit = True
        self.__sending_service.waitForDone()
        self.__receiving_service.waitForDone()
        self.__socket.disconnectFromHost()
    def get_message(self):
        def wrapper():
            if self.__should_exit == False:
                if self.__socket.bytesAvailable()>0:
                    msg = self.__socket.readAll()
                    print(type(msg), msg.count())
                    message = msg.data()
                    print(f"Received message: {message}")
                    self.messageReceived.emit(message)       
        self.__receiving_service.start(FunctionalRunnable(wrapper))
    def send_message(self,message):
        def wrapper(cmd):
            self.__socket.write(cmd)
            self.__socket.flush()
        self.__sending_service.start(FunctionalRunnable(wrapper, message))
                