# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 23:14:38 2020

@author: Kamil Chrustowski
"""
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from configbutton import ConfigButton
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
class ConfigComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ConfigComboBox, self).__init__(parent)
        self.setFont(QFont('KBREINDEERGAMES', 14))
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("QComboBox {border: 1px solid gray; border-radius: 3px; padding: 1px 18px 1px 3px;    min-width: 6em;}"+
                        "QComboBox:editable { image: url(/images/backgrounds/blank2.png);}"+
                        "QComboBox:!editable, QComboBox::drop-down:editable { image: url(/images/backgrounds/blank.png);}"+
                        "QComboBox:!editable:on, QComboBox::drop-down:editable:on { image: url(/images/backgrounds/blank.png); }"+
                        "QComboBox:on {  padding-top: 3px;  padding-left: 4px;}"+
                        "QComboBox::drop-down { subcontrol-origin: padding;    subcontrol-position: top right;    width: 15px;    border-left-width: 1px;    border-left-color: darkgray; border-left-style: solid;border-top-right-radius: 3px; border-bottom-right-radius: 3px;}"+
                        "QComboBox QAbstractItemView {border: 2px solid darkgray; outline: 0;selection-background-color: lightgray;}")
        self.pixmap = QPixmap(os.path.join('images\\backgrounds', 'blank2.png'))
    # def paintEvent(self, event):
    #     painter = QPainter()
    #     painter.begin(self)
    #     painter.save()
    #     painter.drawPixmap(0,0, self.pixmap.scaled(QSize(self.width(), self.height())))
    #     painter.setFont(QFont('KBREINDEERGAMES', 14))
    #     painter.setPen(QColor("white"))
    #     painter.drawText(self.rect(), Qt.AlignCenter, self.currentText())
    #     painter.restore()
        
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
            
class ConfigDialog(QDialog):
    def closeEvent(self, event):
        event.ignore()
    def updatePreview(self, key):
        self.preview.setPixmap(QPixmap(os.path.join('images\\backgrounds',OPTIONS[key])))
    def accept(self):
        Config.getInstance().set_background_config(OPTIONS[self.combobox.currentText()])
        super(ConfigDialog, self).accept()
    def handle_buttons(self, button):
        print(button)
        if(button.text() == "OK"):
            self.accept()
        elif(button.text() == "CANCEL"):
            self.done(QDialog.Rejected)
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setFixedSize(700, 600)
        self.combobox = ConfigComboBox()
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        for key in OPTIONS:
            self.combobox.addItem(key)
        self.setWindowFlags(Qt.FramelessWindowHint)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor("Black"))
        shadow.setOffset(0,0)
        self.setGraphicsEffect(shadow)
        self.combobox.setCurrentText(getKey(Config.getInstance().get_name()))
        self.preview = Background(QPixmap(Config.getInstance().get_background_config()), 340, 530)
        self.layout = QVBoxLayout()
        lab = QLabel('Choose background from comboBox')
        lab.setFixedHeight(30)
        lab.setStyleSheet("QLabel{padding-left: 2px; padding-right: 2px; padding-top: 2px; padding-bottom: 2px;}")
        lab.setFont(QFont('KBREINDEERGAMES', 18))
        lab.setAutoFillBackground(True)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QColor(255,255,255,128)))
        lab.setPalette(palette)
        lab.setContentsMargins(2,2,2,2)
        self.layout.addWidget(lab)
        self.layout.addWidget(self.combobox)
        lab2 = QLabel('Preview: ')
        lab2.setFixedHeight(30)
        lab2.setStyleSheet("QLabel{padding-left: 2px; padding-right: 2px; padding-top: 2px; padding-bottom: 2px;}")
        lab2.setAutoFillBackground(True)
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(255,255,255,128))
        lab2.setPalette(pal)
        lab2.setContentsMargins(2,2,2,2)
        lab2.setFont(QFont('KBREINDEERGAMES', 18))
        self.layout.addWidget(lab2)
        self.layout.addWidget(self.preview, 0, Qt.AlignCenter)
        self.combobox.currentTextChanged.connect(self.updatePreview)
        self.pixmap = QPixmap(os.path.join('images\\backgrounds', 'blank1.png'))
        self.buttons = QButtonGroup()
        self.ok_button = ConfigButton(text="OK")
        group = QGroupBox()
        group.setContentsMargins(0,0,0,0)
        group.setFlat(True)
        group.setStyleSheet("border:0;")
        self.cancel_button = ConfigButton(text="CANCEL")
        self.buttons.addButton(self.ok_button)
        self.buttons.addButton(self.cancel_button)
        self.buttons.buttonPressed.connect(self.handle_buttons)
        hb = QHBoxLayout()
        hb.addWidget(self.ok_button)
        hb.addWidget(self.cancel_button)
        group.setLayout(hb)
        group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setLayout(self.layout)
        self.layout.addWidget(group,0, Qt.AlignBottom|Qt.AlignRight)
        self.cursor_pix = QPixmap(os.path.join('images', 'gondola_coursor.png'))
        self.cursor_scaled_pix = self.cursor_pix.scaled(QSize(25, 25), Qt.KeepAspectRatio)
        self.current_cursor = QCursor(self.cursor_scaled_pix, -1, -1)
        self.setCursor(self.current_cursor)
        self.combobox.setCursor(self.current_cursor)
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.save()
        painter.drawPixmap(0,0, self.pixmap.scaled(QSize(self.width(), self.height())))
        painter.restore()
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