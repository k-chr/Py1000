"""
Created on Tue Jan 14 18:55:15 2020

@author: Kamil Chrustowski
"""

from . import (QPushButton, Qt, QEvent, QFont, QWidget,
              QFontMetrics, QPainter, QTransform, QColor,
              QGraphicsDropShadowEffect, QPixmap)

class MenuButton(QPushButton):

    def __init__(self, pixmap: QPixmap, name: str, parent: QWidget =None, text: str =None):
        super(MenuButton, self).__init__(text if text is not None else "",parent)
        self.name = name
        self.__text = text
        self.__entered = False
        self.pixmap = pixmap
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_Hover)
        self.setContentsMargins(0, 0, 0, 0)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        
        p = self.pixmap.scaled(self.size())  
        painter.drawPixmap(0, 0, p)
        if self.__entered:
            painter.scale(-1,1)
            painter.translate(-self.width(), 0)
        flag = Qt.AlignLeft if self.__entered else Qt.AlignRight
        f = QFontMetrics(QFont('KBREINDEERGAMES', 90), self)
        b = f.boundingRect(p.rect(), Qt.AlignBaseline, self.name.upper())
        print(f"bounding rect: {b.getCoords()}")
        painter.setFont(QFont('KBREINDEERGAMES', 90))
        painter.setPen(Qt.red)
        painter.drawText(b, Qt.AlignRight, self.name.upper())

        painter.end()

    def enterEvent(self, event):
        if event.type() == QEvent.Enter:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(60)
            shadow.setXOffset(-1)
            shadow.setYOffset(-1)
            shadow.setColor(QColor("brown")) 
            self.setGraphicsEffect(shadow)
            self.__entered = True
        else:
            super(MenuButton, self).enterEvent(event)
            
    def leaveEvent(self, event):
        if event.type() == QEvent.Leave:
            self.setGraphicsEffect(None)
            self.__entered = False
        else:
            super(MenuButton, self).leaveEvent(event)