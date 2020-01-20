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
from random import randint
from statusgame import StatusGame
class Server(QObject):
    __lock = Lock()
    opponnentConnected = pyqtSignal()
    gameEnded = pyqtSignal()
    connectionFailed = pyqtSignal()
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
    def __rcvCmd(self, command):
        dictionary = loads(command)
        print(dictionary)
    def randomizeStartingPlayer(self):
        val = randint(0,1)
        self.startingPlayer = val
    def sendCmd(self, cmd):
        self.__client.send_message(dumps(cmd))
    def cleanUp(self):
        print("closing connection")
        self.__serverService.waitForDone()
        self.__listeningService.waitForDone()
        self.__client.cleanUp()
        self.__server.close()
        self.__client = None
        self.__ip = None
    def prerpareServerMessage(self, eventType, **kwargs):
        def switch(x):
            return {
                'CARD_PLAYED': {'EVENT':'CARD_PLAYED', 'CARD':kwargs.get('CARD', ())},
                'NEW_BID':{'EVENT':'NEW_BID', 'BID_VALUE':kwargs.get('BID_VALUE', 0)},
                'STACK_CHANGED':{'EVENT':'STACK_CHANGED', 'CARDS':kwargs.get('CARDS', [(),()])},
                'VALUE_DECLARED':{'EVENT':'VALUE_DECLARED', 'GAME_VALUE':kwargs.get('GAME_VALUE',0)},
                'TRUMP_CHANGED':{'EVENT':'TRUMP_CHANGED','NEW_SUIT':kwargs.get('NEW_SUIT','')},
                'CARDS_HANDIN':{'EVENT':'CARDS_HANDIN','SERVER_CARDS':reversed(kwargs.get('SERVER_CARDS', [])),
                                'PLAYER_CARDS':reversed(kwargs.get('PLAYER_CARDS', [])),
                                'FIRST_STACK':kwargs.get('STACKS',[[],[]])[1],
                                'SECOND_STACK':kwargs.get('STACKS',[[],[]])[0] },
                'WHO_STARTS':{'EVENT':'WHO_STARTS', 'WHO':kwargs['WHO']}
            }.get(x, {}) 
        return switch(eventType)
    def startListen(self):
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
            StatusGame.getInstance().set_status_name("CONNECTION_FAILED")
            QTimer.singleShot(3000, lambda:StatusGame.getInstance().set_status_name("APP_START") )    
            self.connectionFailed.emit()