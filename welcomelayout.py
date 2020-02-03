# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 18:55:35 2020

@author: Kamil Chrustowski
"""
from os import path
from PyQt5.QtCore import pyqtSignal, Qt, QCoreApplication 
from PyQt5.QtGui import QBrush, QPalette, QPixmap
from PyQt5.QtWidgets import QHBoxLayout,QVBoxLayout, QButtonGroup,QWidget, QApplication, QSizePolicy
from banner import Banner
from gamebutton import GameButton
from statusgame import StatusGame
from config import ConfigDialog
class WelcomeLayout(QHBoxLayout):
    quitSignal = pyqtSignal()
    def __init__(self,windowSize,bannerHeight, bannerPixmap,buttonNames,backgroundPixmap,player, parent=None):
        super(WelcomeLayout, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.banner = Banner(bannerPixmap, bannerHeight)
        self.buttonList = [GameButton(QPixmap(path.join('images/buttons', name+'.png')), name) for name in buttonNames]
        self.buttonGroup = QButtonGroup()
        self.menu = QVBoxLayout()
        self.menu.addWidget(self.banner)
        for button in self.buttonList:
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.buttonGroup.addButton(button)
            self.menu.addWidget(button)
        self.menu.setContentsMargins(200, 3, 200, 50)
        self.widget = QWidget()
        geometry = QApplication.desktop().geometry()
        self.bg = backgroundPixmap.scaled(geometry.width(),geometry.height())
        self.bgPalette = QPalette()
        self.bgPalette.setBrush(QPalette.Background,QBrush(self.bg))
        self.widget.setPalette(self.bgPalette)
        self.widget.setAutoFillBackground(True)
        self.widget.setLayout(self.menu)
        self.addWidget(self.widget)
        self.setContentsMargins(0,0,0,0)
        self.buttonGroup.buttonClicked.connect(self.handleMenu)
        self.playerInstance = player
    def handleMenu(self, button):
        if button.name == 'host':
            print('I\'m a host button')
            StatusGame.getInstance().set_status_name("WAITING_FOR_OPPONENT")
            self.playerInstance.playAsHost()
        elif button.name == 'peer':
            print('I\'m a peer button')
            StatusGame.getInstance().set_status_name("TYPE_IP")
            self.playerInstance.playAsPeer()
        elif button.name == 'settings':
            print('I\'m a settings button')
            value = ConfigDialog.getDialog()
            print(value)
        elif button.name == 'help':
            print('I\'m a help button')
            
        elif button.name == 'quit':
            print('I\'m a quit button')
            QCoreApplication.quit()