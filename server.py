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
from PyQt5.Qt import *
from pickle import loads, dumps
class Server(QObject):
    __lock = Lock()
    opponnentConnected = pyqtSignal()
    gameEnded = pyqtSignal()
    __server = None
    __ip = None
    __socket = None
    __port = 7312
    __serverService = QThreadPool()
    __serverService.setMaxThreadCount(1)
    __listeningService = QThreadPool()
    __listeningService.setMaxThreadCount(1)
    __client = None
    def __init__(self):
        super(Server, self).__init__()
        self.__server = QTcpServer()
        self.__server.setMaxPendingConnections(1)
        self.__server.newConnection.connect(self.on_newConnection)
    def receiveIp(self, ip):
        self.__ip = QHostAddress(ip)
        print(self.__ip.toString())
        self.startListen()
    def on_newConnection(self):
        #def wrapper():
            while self.__server.hasPendingConnections() and self.__client is None:
                print("Incoming Connection...")
                with self.__lock:
                    print("I'm into lock")
                    self.__socket = self.__server.nextPendingConnection()
                    handler = CommunicationHandler(self.__socket)
                    self.__client = handler
                    self.__socket.readyRead.connect(self.__client.get_message)
                    self.__client.messageReceived.connect(self.__rcvCmd)
                    self.opponnentConnected.emit()
            print("There is no connection dude")
        #self.__serverService.start(FunctionalRunnable(wrapper))
    def __rcvCmd(self, command):
        dictionary = loads(command)
        print(dictionary)
    def cleanUp(self):
        print("closing connection")
        self.__serverService.waitForDone()
        self.__listeningService.waitForDone()
        self.__client.cleanUp()
        self.__server.close()
        self.__client = None
        self.__ip = None
    def prerpareServerMessage(self, playerPoints, serverPoints, eventType, card=None):
        if eventType == 'cardPlacedByOpponent':
            return {'playerPoints':playerPoints, 'serverPoints':serverPoints, 'eventType':eventType, 'card':card}
        else:
            return {'playerPoints':playerPoints, 'serverPoints':serverPoints, 'eventType':eventType}
    def startListen(self):
        #def listen():
            if self.__server.listen(
                    self.__ip, self.__port
                    ):
                print(
                    "Server is listening on port: {}".format(
                        self.__port
                        )
                    )
            else:
                print("Server couldn't start")
        #self.__listeningService.start(FunctionalRunnable(listen))
    def getHostingClient(self):
        print("I'm reached this fucking method")
        