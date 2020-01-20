# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 01:03:49 2020

@author: Kamil Chrustowski
"""
from threading import Lock
from communicationhandler import CommunicationHandler
from functionalrunnable import FunctionalRunnable
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
from pickle import loads, dumps
from statusgame import StatusGame
class Peer(QObject):
    
    __lock = Lock()
    gameEnded = pyqtSignal()
    __socket = None
    __ip = ""
    __port = 7312
    __handler = None
    __curr_reconnection = 0
    __max_reconnection = 5
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
    def __rcvCmd(self, command):
        dictionary = loads(command)
        print(dictionary)
    def sendCmd(self, cmd):
        self.__handler.send_message(dumps(cmd))
    def initCommunication(self):
        self.__handler.send_message(dumps(self.prerpareClientMessage(eventType='STACK_CHANGED')))
    def on_connected(self):
        print("I\'m Connected")
        StatusGame.getInstance().set_status_name("GAME")
        self.__handler = CommunicationHandler(self.__socket)
        self.__handler.messageReceived.connect(self.__rcvCmd)
        
        QTimer.singleShot(1000, self.initCommunication)
    def prerpareClientMessage(self, eventType, **kwargs):
        def switch(x):
            return {
                'CARD_PLAYED': {'EVENT':'CARD_PLAYED', 'CARD':kwargs.get('CARD', ())},
                'NEW_BID':{'EVENT':'NEW_BID', 'BID_VALUE':kwargs.get('BID_VALUE', 0)},
                'STACK_CHANGED':{'EVENT':'STACK_CHANGED', 'CARDS':kwargs.get('CARDS', [(),()])},
                'VALUE_DECLARED':{'EVENT':'VALUE_DECLARED', 'GAME_VALUE':kwargs.get('GAME_VALUE',0)},
                'TRUMP_CHANGED':{'EVENT':'TRUMP_CHANGED','NEW_SUIT':kwargs.get('NEW_SUIT','')}
            }.get(x, {}) 
        return switch(eventType)