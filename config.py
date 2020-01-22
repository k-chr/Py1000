# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 23:14:38 2020

@author: Kamil Chrustowski
"""
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

OPTIONS = {'Gondola full of stars':'bg1.png',
           'Gondola swimming in the lake of tears':'bg2.png',
           'Gondola on the Moon':'bg3.png',
           'Gondola 2077':'bg4.png'
           }

SHADOWS = {'bg1.png':'#8fd9ff',
           'bg2.png':'#386890',
           'bg3.png': '#f8f4dd',
           'bg4.png': '#617479'
           }

TEXT = {   'bg1.png':'#476677',
           'bg2.png':'#f0f8ff',
           'bg3.png': '#2c1b01',
           'bg4.png': '#fffff0'
        }
def getKey(value):
    for key, val in OPTIONS.items():
        if val == value:
            return key
    return None    
class Config:
    __instance = None
    __playingBackground = ""
    __name = ""
    @staticmethod
    def getInstance():
        """ Static access method. """
        if Config.__instance == None:
            Config()
        return Config.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Config.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.__playingBackground = os.path.join('images\\backgrounds', 'bg2.png')
            self.__name = 'bg2.png'
            self.__shadow = SHADOWS[self.__name]
            self.__text = TEXT[self.__name]
            Config.__instance = self
    def get_shadow_config(self):
        return self.__shadow
    def get_text_config(self):
        return self.__text
    def get_background_config(self):
        return self.__playingBackground
    def get_name(self):
        return self.__name
    def set_background_config(self, name):
        self.__name = name
        self.__shadow = SHADOWS[self.__name]
        self.__text = TEXT[self.__name]
        self.__playingBackground = os.path.join('images\\backgrounds',name)
        print(self.__playingBackground)
            
class ConfigDialog(QDialog):
    def closeEvent(self, event):
        event.ignore()
    def updatePreview(self, key):
        self.preview.setPixmap(QPixmap(os.path.join('images\\backgrounds',OPTIONS[key])))
    def accept(self):
        Config.getInstance().set_background_config(OPTIONS[self.combobox.currentText()])
        super(ConfigDialog, self).accept()
        
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setFixedSize(500, 400)
        self.combobox = QComboBox()
        for key in OPTIONS:
            self.combobox.addItem(key)
        self.combobox.setCurrentText(getKey(Config.getInstance().get_name()))
        self.preview = Background(QPixmap(Config.getInstance().get_background_config()), 270, 430)
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Choose background from comboBox'))
        self.layout.addWidget(self.combobox)
        self.layout.addWidget(QLabel('Preview: '))
        self.layout.addWidget(self.preview)
        self.combobox.currentTextChanged.connect(self.updatePreview)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                   Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)
        self.setLayout(self.layout)
    @staticmethod
    def getDialog(parent=None):
        dialog = ConfigDialog(parent)
        dialog.setWindowTitle("Customize application")
        result = dialog.exec_()
        return result == QDialog.Accepted
class Background(QWidget):
    def __init__(self, pixmap,height,width, parent=None):
        super(Background, self).__init__(parent)
        self.pixmap = pixmap
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setStyleSheet("background-color: transparent;background: none; background-repeat: none; border: 10px;")
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(0,0, self.pixmap.scaled(QSize(self.width(), self.height())))
    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        if pixmap is None:
            print("Invalid pixmap")
        self.update()