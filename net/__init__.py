from __future__ import annotations
from pickle import loads
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool
from PyQt5.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket, QNetworkInterface
from enum import Enum

class HeaderType(Enum):
    DISCOVER = 0xDEAD
    
