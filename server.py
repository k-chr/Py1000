# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 12:02:26 2020

@author: Kamil Chrustowski
"""
from threading import Lock
from communicationhandler import CommunicationHandler
from functionalrunnable import FunctionalRunnable
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
from pickle import loads, dumps
class Server:
    __lock = Lock()
    gameEnded = pyqtSignal()
    __server = None
    __ip = ""
    __port = 7312
    __serverService = QThreadPool()
    __serverService.setMaxThreadCount(1)
    __client = None
    def __init__(self, ip):
        self.__server = QTcpServer()
        self.__server.setMaxPendingConnections(1)
        self.__ip = ip
        self.__server.newConnection.connect(self.__on_newConnection)
    def __on_newConnection(self):
        def wrapper():
            while self.__server.hasPendingConnections() and self.__client is None:
                print("Incoming Connection...")
                with self.__lock:
                    handler = CommunicationHandler(self.__server.nextPendingConnection())
                    self.__client = handler
                    self.__client.messageReceived.connect(self.__rcvCmd)
        self.__serverService.start(FunctionalRunnable(wrapper))
    def __rcvCmd(self, command):
        dictionary = loads(command)
        print(dictionary)
    def cleanUp(self):
        print("closing connection")
        self.__serverService.waitForDone()
        self.__client.cleanUp()
        self.__server.close()
        self.__client = None
        self.__ip = ""
    def prerpareServerMessage(self, playerPoints, serverPoints, eventType, *,card):
        if eventType == 'cardPlacedByOpponent':
            return {'playerPoints':playerPoints, 'serverPoints':serverPoints, 'eventType':eventType, 'card':card}
        else:
            return {'playerPoints':playerPoints, 'serverPoints':serverPoints, 'eventType':eventType}
    def startListen(self):
        if self.server.listen(
            self.__ip, self.__port
        ):
            print(
                "Server is listening on port: {}".format(
                    self.__port
                )
            )
        else:
            print("Server couldn't start")
    def getHostingClient(self):
        print("I'm reached this fucking method")
        