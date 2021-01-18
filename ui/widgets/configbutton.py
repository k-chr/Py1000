# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 18:39:22 2020

@author: Kamil Chrustowski
"""

from . import (QPushButton, QPixmap, QWidget,
               Qt, QEvent, path, QFont, QSizePolicy,
               QPainter, QSize)

class ConfigButton(QPushButton):

    def __init__(self, parent: QWidget =None, text: str =None):
        super(ConfigButton, self).__init__(parent)
        self.setText(text)
        self.setAttribute(Qt.WA_Hover)
        self.pixmap = QPixmap(path.join('images/backgrounds', 'blank2.png'))
        self.disbledPixmap = QPixmap(path.join('images/backgrounds', 'blank3.png'))
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def enterEvent(self, event):
        if event.type() == QEvent.Enter:
            if self.isEnabled():
                self.pixmap = QPixmap(path.join('images/backgrounds', 'blank.png'))
                self.update()
        else:
            super(ConfigButton, self).enterEvent(event)

    def paintEvent(self, event):
        painter = QPainter()
        
        painter.begin(self)
        if self.isEnabled():
            painter.drawPixmap(0,0, self.pixmap.scaled(QSize(self.width(), self.height())))
        else:
            painter.drawPixmap(0,0, self.disbledPixmap.scaled(QSize(self.width(), self.height()))) 
        if self.isEnabled():
            painter.setPen(Qt.white)
        else:
            painter.setPen(Qt.gray)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())
        
        painter.end()

    def leaveEvent(self, event):
        if event.type() == QEvent.Leave:
            if self.isEnabled():
                self.pixmap = QPixmap(path.join('images/backgrounds', 'blank2.png'))
                self.update()
        else:
            super(ConfigButton, self).leaveEvent(event)
