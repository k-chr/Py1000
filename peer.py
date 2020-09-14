# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 01:03:49 2020

@author: Kamil Chrustowski
"""
from threading import Lock
from net.communicationhandler import CommunicationHandler
from fun_threading.functionalrunnable import FunctionalRunnable
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
from pickle import loads, dumps
from statusgame import StatusGame
class Peer(QObject):
    
    __lock = Lock()
    gameEnded = pyqtSignal(str)
    __socket = None
    __ip = ""
    __port = 7312
    __handler = None
    __curr_reconnection = 0
    __max_reconnection = 5
    opponentScoreChanged = pyqtSignal(int)
    who_takes = pyqtSignal(str)
    gotCards = pyqtSignal(list,list,list,list)
    trumpChanged = pyqtSignal(str)
    cardPlayed = pyqtSignal(tuple)
    stackChanged = pyqtSignal(list, int)
    new_bid = pyqtSignal(int)
    who_starts = pyqtSignal(str)
    value_declared = pyqtSignal(int)
    def __init__(self, ip):
        super(Peer, self).__init__()
        self.__ip = ip
        self.__socket = QTcpSocket()
        self.__socket.connected.connect(self.on_connected)
        self.__socket.error.connect(self.on_error)
    def on_error(self, error):
        self.__curr_reconnection += 1
        if(self.__curr_reconnection >= self.__max_reconnection):
            StatusGame.getInstance().set_status_name("CONNECTION_FAILED")
            QTimer.singleShot(3000, lambda:StatusGame.getInstance().set_status_name("APP_START") )
            self.__curr_reconnection = 0
            return
        if error == QAbstractSocket.ConnectionRefusedError:
            print(
                'Unable to send data to port: "{}"'.format(
                    self.__port
                )
            )
            print("trying to reconnect")
            QTimer.singleShot(1000, self.tryToConnect)
    def tryToConnect(self):
        self.__socket.connectToHost(self.__ip, self.__port)
    def cleanUp(self):
        try:
            self.gotCards.disconnect()
        except:
            pass
        try:
            self.who_starts.disconnect()
        except:
            pass
        try:
            self.who_takes.disconnect()
        except:
            pass
        try:
            self.opponentScoreChanged.disconnect()
        except:
            pass
        try:
            self.gameEnded.disconnect()
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
        self.__handler.cleanUp()
    def __rcvCmd(self, command):
        dictionary = loads(command)
        print(dictionary)
        event = dictionary.get('EVENT',"")
        if (event == 'WHO_STARTS'):
            self.who_starts.emit(dictionary['WHO'])
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
        elif (event == 'CARDS_HANDIN'):
            self.gotCards.emit(dictionary['SERVER_CARDS'],
                               dictionary['PLAYER_CARDS'],
                               dictionary['FIRST_STACK'],
                               dictionary["SECOND_STACK"])
        elif (event == 'WHO_TAKES'):
            self.who_takes.emit(dictionary['WHO'])
        elif(event == 'SCORE'):
            self.opponentScoreChanged.emit(dictionary['VALUE'])
        elif(event == 'RESULT'):
            self.gameEnded.emit(dictionary['WHO'])
    def sendCmd(self, cmd):
        self.__handler.send_message(dumps(cmd))
    def initCommunication(self):
        self.__handler.send_message(dumps(self.prepareClientMessage(eventType='INIT')))
    def on_connected(self):
        print("I\'m Connected")
        StatusGame.getInstance().set_status_name("GAME")
        self.__handler = CommunicationHandler(self.__socket)
        self.__socket.readyRead.connect(self.__get_message)
        self.__handler.messageReceived.connect(self.__rcvCmd)
        
        QTimer.singleShot(10, self.initCommunication)
    def __get_message(self):
        self.__handler.get_message()
    def prepareClientMessage(self, eventType, **kwargs):
        def switch(x):
            return {
                'READY':{'EVENT':'READY'},
                'SCORE':{'EVENT':'SCORE', 'VALUE':kwargs.get('VALUE',0)},
                'CARD_PLAYED': {'EVENT':'CARD_PLAYED', 'CARD':kwargs.get('CARD', ())},
                'NEW_BID':{'EVENT':'NEW_BID', 'BID_VALUE':kwargs.get('BID_VALUE', 0)},
                'STACK_CHANGED':{'EVENT':'STACK_CHANGED', 'STACK_INDEX':kwargs.get('STACK_INDEX', 0),
                                 'CARDS':kwargs.get('CARDS', [(),()])},
                'VALUE_DECLARED':{'EVENT':'VALUE_DECLARED', 'GAME_VALUE':kwargs.get('GAME_VALUE',0)},
                'INIT':{'EVENT':'INIT'},
                'DECK_TAKEN':{'EVENT':'DECK_TAKEN'},
                'MULTI_EVENT':{"EVENT":'MULTI_EVENT',
                               'FIRST':kwargs.get('FIRST',''), 
                               'SECOND':kwargs.get('SECOND',''),
                               'FIRST_ARG':kwargs.get('FIRST_ARG',None), 
                               'SECOND_ARG':kwargs.get('SECOND_ARG',None)}
            }.get(x, {}) 
        return switch(eventType)