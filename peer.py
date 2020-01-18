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
class Peer(QObject):
    
    __lock = Lock()
    gameEnded = pyqtSignal()
    __socket = None
    __ip = ""
    __port = 7312
    __handler = None
    
    def __init__(self, ip):
        super(Peer, self).__init__()
        self.__ip = ip
        self.__socket = QTcpSocket()
        self.__socket.connected.connect(self.on_connected)
        self.__socket.error.connect(self.on_error)
    def on_error(self, error):
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
    def initCommunication(self):
        self.__handler.send_message(dumps(self.prerpareClientMessage(100, 200, 'startGame')))
    def on_connected(self):
        print("I\'m Connected")
        self.__handler = CommunicationHandler(self.__socket)
        self.__handler.messageReceived.connect(self.__rcvCmd)
        
        QTimer.singleShot(1000, self.initCommunication)
        
    def prerpareClientMessage(self, playerPoints, serverPoints, eventType, card=None):
        if eventType == 'cardPlacedByOpponent':
            return {'playerPoints':playerPoints, 'serverPoints':serverPoints, 'eventType':eventType, 'card':card}
        else:
            return {'playerPoints':playerPoints, 'serverPoints':serverPoints, 'eventType':eventType}
    