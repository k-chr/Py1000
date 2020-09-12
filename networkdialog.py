# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 00:10:57 2020

@author: Kamil Chrustowski
"""
import os
from concurrent.futures import *
from PyQt5.Qt import *
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
from PyQt5.QtGui import *
class PulsingProgressBar(QProgressBar):
    def __init__(self,width, height, parent = None):
        super(PulsingProgressBar, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(0)
        self.setValue(0)
        self.setFixedSize(QSize(width, height))
        self.setStyle(QStyleFactory.create('WindowsVista'))
        self.setStyleSheet("QProgressBar:horizontal {border: 1px solid gray;border-radius: 3px;background: white;padding: 1px;}QProgressBar::chunk {background: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #05B8CC, stop: 1 white);}")
        self.setTextVisible(False)
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(0)
        self.setGraphicsEffect(self.glow)
        self.glow.setXOffset(0)
        self.glow.setYOffset(0)
        self.glow.setColor(QColor("#05B8CC"))
        self.animu = QPropertyAnimation(self.glow, b"blurRadius")
        self.animu.setStartValue(0)
        self.animu.setEndValue(100)
        self.animu.setDuration(1000)
        self.animu.setLoopCount(-1)
        self.animu.start()
    def end(self):
        self.setMaximum(100)
        self.setValue(100)
        self.animu.stop()
class NetworkDialog(QDialog):
    ipFound = pyqtSignal(str)
    __ip = ""
    progressBar = None
    ipGroup = None
    button = None
    toClose = False
    interf = ["Network Bridge","Ethernet","Wi-Fi"]
    def closeEvent(self, event):
        if(self.toClose == True):
            print("CLOSE THIS SHIT")
            event.accept()    
        else:    
            event.ignore()

    def __init__(self, who, parent=None):
        super(NetworkDialog, self).__init__(parent)
        self.setFixedSize(300, 100)
        
        layout = self.getHostLayout() if who == 'Host' else self.getPeerLayout()
        self.setLayout(layout)
        
    def getHostLayout(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Waiting for opponents...'))
        def getIPv4Address():
            localhost = QHostAddress(QHostAddress.LocalHost)
            for interface in QNetworkInterface.allInterfaces():
                print(interface.humanReadableName())
                if(interface.humanReadableName() in self.interf and interface.flags() & QNetworkInterface.IsUp):
                    for entry in interface.addressEntries():
                        ip = entry.ip()
                        if ip.protocol() == QAbstractSocket.IPv4Protocol and ip != localhost:
                            print(ip.toString())
                            
                            return ip
    
        self.__ip = getIPv4Address().toString()
        print(self.__ip)
        self.progressBar = PulsingProgressBar(250, 20)
        layout.addWidget(self.progressBar)
        layout.addWidget(QLabel('Your IPv4 address to provide to your peers: '))
        label = QLabel(self.__ip)
        label.setObjectName('ip_label')
        newfont = QFont(label.font().family(), pointSize=15,weight=QFont.Bold) 
        label.setStyleSheet("QLabel#ip_label {color: #328930}")
        label.setFont(newfont)
        layout.addWidget(label)
        return layout
    def error(self):
        #self.toClose=True
        print("HERE")
        QTimer.singleShot(3000,lambda: self.done(QDialog.Rejected))
        print("HERE2")
    def finishHostDialog(self):
        print("ajm hir")
        self.done(QDialog.Accepted)
    def endDialog(self):
        if self.progressBar != None:
            self.progressBar.end()
            self.progressBar = None
        if self.__ip != "":
            self.__ip = ""
        if self.button != None:
            self.button = None
        if self.ipGroup != None:
            self.Group = None
    def getIp(self):
        return self.__ip
    def getPeerLayout(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Provide ip address of host: '))
        ipGrid = QGridLayout()
        ipGrid.setHorizontalSpacing(1)
        self.ipGroup = {}
        gridindex = 0
        for i in range (0,4):
            num = QLineEdit()
            num.setValidator(QIntValidator(0,255))
            num.textChanged.connect(self.checkIp)
            self.ipGroup = { **self.ipGroup, i:num}
            ipGrid.addWidget(num, 0, gridindex)
            gridindex = gridindex+1
            if(i < 3):
                ipGrid.addWidget(QLabel('.'), 0, gridindex)
                gridindex = gridindex + 1
        layout.addLayout(ipGrid)
        buttons = QDialogButtonBox(Qt.Horizontal, self)
        self.button = buttons.addButton("Start", QDialogButtonBox.AcceptRole)
        buttons.addButton("Cancel", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.peerAccept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.button.setEnabled(False)
        return layout
    def peerAccept(self):
        self.__ip = '.'.join(self.ipGroup[idx].text() for idx in sorted(self.ipGroup))
        super(NetworkDialog, self).accept()
    def checkIp(self, string):
        value = True
        for key, val in self.ipGroup.items():
            if val.text() == "":
                value = False
        self.button.setEnabled(value)
    @staticmethod
    def getDialog(who,receiver=None, parent = None):
        dialog = NetworkDialog(who, parent)
        
        print(receiver)
        if receiver != None:
            print("HERES")
            receiver.connectionFailed.connect(dialog.error)
            receiver.opponentConnected.connect(dialog.finishHostDialog)
            dialog.ipFound.connect(receiver.receiveIp)
            dialog.ipFound.emit(dialog.getIp())

        dialog.setWindowTitle("Py1000 - network dialog")
        dialog.setWindowIcon(QIcon(QPixmap(os.path.join('images', 'ico.png'))))
        result = dialog.exec_()
        
        value = dialog.getIp()
        print(result, value)
        
        return (value, result == QDialog.Accepted)