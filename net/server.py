# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 12:02:26 2020

@author: Kamil Chrustowski
"""
from threading import Lock
from .communicationhandler import CommunicationHandler
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
from PyQt5.Qt import *
from pickle import loads, dumps
from random import randint
from statusgame import StatusGame

class Server(QObject):
    __lock = Lock()
    peerReady = pyqtSignal()
    deckTaken = pyqtSignal()
    opponentScoreChanged = pyqtSignal(int)
    opponentConnected = pyqtSignal()
    gameEnded = pyqtSignal()
    initPlayerChoosen = pyqtSignal(int)
    connectionFailed = pyqtSignal()
    trumpChanged = pyqtSignal(str)
    cardPlayed = pyqtSignal(tuple)
    stackChanged = pyqtSignal(list, int)
    new_bid = pyqtSignal(int)
    value_declared = pyqtSignal(int)
    __server = None
    __ip = None
    __socket = None
    __port = 7312
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
        while self.__server.hasPendingConnections():
            print("Incoming Connection...")
            with self.__lock:
                print("I'm into lock")
                self.__socket = self.__server.nextPendingConnection()
                handler = CommunicationHandler(self.__socket)
                self.__client = handler
                self.__socket.readyRead.connect(self.__client.get_message)
                self.__client.messageReceived.connect(self.__rcvCmd)
        print("There is no connection dude")
    def __rcvCmd(self, command):
        dictionary = loads(command)
        print(dictionary)
        event = dictionary.get('EVENT',"")
        if (event == 'INIT'):
            self.opponentConnected.emit()
        elif (event == 'NEW_BID'):
            self.new_bid.emit(dictionary['BID_VALUE'])
        elif (event== 'STACK_CHANGED'):
            self.stackChanged.emit(dictionary['CARDS'], dictionary['STACK_INDEX'])
        elif (event == 'MULTI_EVENT'):
            if(dictionary['FIRST'] == 'TRUMP_CHANGED'):    
                self.trumpChanged.emit(dictionary['FIRST_ARG'])
            if(dictionary["SECOND"] == 'CARD_PLAYED'):
                self.cardPlayed.emit(dictionary['SECOND_ARG'])
        elif (event == 'VALUE_DECLARED'):
            self.value_declared.emit(dictionary['GAME_VALUE'])
        elif (event == 'CARD_PLAYED'):
            self.cardPlayed.emit(dictionary['CARD'])
        elif(event == 'SCORE'):
            self.opponentScoreChanged.emit(dictionary['VALUE'])
        elif(event == 'DECK_TAKEN'):
            self.deckTaken.emit()
        elif(event == 'READY'):
            self.peerReady.emit()
    def randomizeStartingPlayer(self):
        val = randint(0,1)
        self.startingPlayer = val
        self.initPlayerChoosen.emit(self.startingPlayer)
    def setNewPlayer(self):
        self.startingPlayer = 1 if self.startingPlayer == 0 else 0
        self.initPlayerChoosen.emit(self.startingPlayer)
    def sendCmd(self, cmd):
        self.__client.send_message(dumps(cmd))
    def cleanUp(self):
        print("closing connection")
        try:
            self.deckTaken.disconnect()
        except:
            pass
        try:
            self.opponentScoreChanged.disconnect()
        except:
            pass
        try:
            self.opponentConnected.disconnect()
        except:
            pass
        try:
            self.gameEnded.disconnect()
        except:
            pass
        try:
            self.initPlayerChoosen.disconnect()
        except:
            pass
        try:
            self.connectionFailed.disconnect()
        except:
            pass
        try:
            self.trumpChanged.disconnect()
        except:
            pass
        try:
            self.cardPlayed.disconnect()
        except:
            pass
        try:
            self.stackChanged.disconnect()
        except:
            pass
        try:
            self.new_bid.disconnect()
        except:
            pass
        try:
            self.value_declared.disconnect()
        except:
            pass
        try:
            self.peerReady.disconnect()
        except:
            pass
        if self.__client is not None:
            self.__client.cleanUp()
        self.__server.close()
        self.__client = None
        self.__ip = None
    def prepareServerMessage(self, eventType, **kwargs):
        def switch(x):
            return {
                'RESULT':{'EVENT':'RESULT', 'WHO':kwargs.get('WHO', '')},
                'SCORE':{'EVENT':'SCORE', 'VALUE':kwargs.get('VALUE',0)},
                'CARD_PLAYED': {'EVENT':'CARD_PLAYED', 'CARD':kwargs.get('CARD', ())},
                'NEW_BID':{'EVENT':'NEW_BID', 'BID_VALUE':kwargs.get('BID_VALUE', 0)},
                'STACK_CHANGED':{'EVENT':'STACK_CHANGED', 'CARDS':kwargs.get('CARDS', [(),()]), 'STACK_INDEX':kwargs.get('STACK_INDEX', 0)},
                'VALUE_DECLARED':{'EVENT':'VALUE_DECLARED', 'GAME_VALUE':kwargs.get('GAME_VALUE',0)},
                'MULTI_EVENT':{"EVENT":'MULTI_EVENT',
                               'FIRST':kwargs.get('FIRST',''), 
                               'SECOND':kwargs.get('SECOND',''),
                               'FIRST_ARG':kwargs.get('FIRST_ARG',None), 
                               'SECOND_ARG':kwargs.get('SECOND_ARG',None)},
                'CARDS_HANDIN':{'EVENT':'CARDS_HANDIN','SERVER_CARDS':kwargs.get('SERVER_CARDS', []),
                                'PLAYER_CARDS':kwargs.get('PLAYER_CARDS', []),
                                'FIRST_STACK':kwargs.get('STACKS',[[],[]])[1],
                                'SECOND_STACK':kwargs.get('STACKS',[[],[]])[0]},
                'WHO_STARTS':{'EVENT':'WHO_STARTS', 'WHO':kwargs.get('WHO', 'NONE')},
                'WHO_TAKES':{"EVENT":"WHO_TAKES", "WHO":kwargs.get('WHO', 'NONE')}
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
            print("ERROR EMIT")
            self.connectionFailed.emit()