# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 18:55:15 2020

@author: Kamil Chrustowski
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class GameButton(QPushButton):
    def __init__(self, pixmap, name, parent=None):
        super(GameButton, self).__init__(parent)
        self.name = name
        self.pixmap = pixmap
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setStyleSheet("background-color: transparent;background: none; background-repeat: none; border: 10px;")
        self.setAttribute(Qt.WA_Hover)
        self.setContentsMargins(0,0,0,0)
        self.setAutoFillBackground(True)
    def paintEvent(self, event):
         painter = QPainter()
         painter.begin(self)
         painter.drawPixmap(0,0, self.pixmap.scaled(self.size()))
    
    def enterEvent(self, event):
        if event.type() == QEvent.Enter:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(60)
            shadow.setXOffset(-1)
            shadow.setYOffset(-1)
            self.pixmap = self.pixmap.transformed(QTransform().scale(-1, 1))
            shadow.setColor(QColor("brown"))
            self.setGraphicsEffect(shadow)
        else:
            super(GameButton, self).enterEvent(event)
            
    def leaveEvent(self, event):
        if event.type() == QEvent.Leave:
            self.setGraphicsEffect(None)
            self.pixmap = self.pixmap.transformed(QTransform().scale(-1, 1))
        else:
            super(GameButton, self).leaveEvent(event)