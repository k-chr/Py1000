# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 18:00:21 2020

@author: Kamil Chrustowski
"""

from . import (QWidget, QPixmap, Qt, QPainter, QSize)

class Banner(QWidget):

    def __init__(self, pixmap: QPixmap, height: int, parent: QWidget =None):
        super(Banner, self).__init__(parent)
        self.pixmap = pixmap
        self.setFixedHeight(height)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.ratio = pixmap.width() / pixmap.height()
        self.setStyleSheet("background-color: transparent;background: none;" +
                           " background-repeat: none; border: 10px;")

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap((self.width() - self.height() * self.ratio) // 2 ,0, 
                            self.pixmap.scaled(QSize(self.height() * self.ratio , self.height())))
