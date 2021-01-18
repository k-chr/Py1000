# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:27:21 2020

@author: Kamil Chrustowski
"""
from fun_threading.functionalrunnable import FunctionalRunnable
from . import loads, QObject, pyqtSignal, QThreadPool, QTcpSocket

class CommunicationHandler(QObject):
    messageReceived = pyqtSignal(bytes)
    __socket = None
    __should_exit = False
    __receiving_service = QThreadPool()
    __sending_service = QThreadPool()
    __receiving_service.setMaxThreadCount(1)
    __sending_service.setMaxThreadCount(1)

    def __init__(self, socket:QTcpSocket):
        print("into constructor {self}")
        super(CommunicationHandler, self).__init__()
        self.__socket = socket
        
    def cleanUp(self):
        print("cleaning up")
        self.__should_exit = True
        self.__sending_service.waitForDone()
        self.__receiving_service.waitForDone()
        self.__socket.disconnectFromHost()

    def get_message(self):
        print("I\'m before wrapper")
        def wrapper():
            print("I'm into wrapper")
            if self.__should_exit == False:
                if self.__socket.bytesAvailable()>0:
                    msg = self.__socket.readAll()
                    print("Message length: ", msg.count())
                    message = msg.data()
                    print(f"Received message: {loads(message)}")
                    self.messageReceived.emit(message)       
        self.__receiving_service.start(FunctionalRunnable(wrapper))

    def send_message(self,message):
        print(f"message to send {message}")
        def wrapper(cmd):
            while(self.__socket.bytesAvailable() > 0):
                a = 1
            self.__socket.write(cmd)
            self.__socket.flush()
            print("I'm outta the sending")
        self.__sending_service.start(FunctionalRunnable(wrapper, message))
                