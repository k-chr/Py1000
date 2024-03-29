"""
Created on Tue Jan 14 18:55:15 2020

@author: Kamil Chrustowski
"""

from . import (QPushButton, Qt, QEvent, QFont, QWidget,
              QFontMetrics, QPainter, QTransform, QColor,
              QGraphicsDropShadowEffect, QPixmap)

class GameButton(QPushButton):

    def __init__(self, pixmap: QPixmap, name: str, parent: QWidget =None, text: str =None):
        super(GameButton, self).__init__(text if text is not None else "",parent)
        self.name = name
        self.__text = text
        self.pixmap = pixmap
        #self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setStyleSheet("color: white;background-color:"+
                           " transparent;background: none; background-repeat: none; border: 10px;")
        self.setAttribute(Qt.WA_Hover)
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.save()  
        painter.drawPixmap(0, 0, self.pixmap.scaled(self.size()))
        painter.restore()
        painter.save()
        f = QFontMetrics(QFont('KBREINDEERGAMES', 18))
        b = f.boundingRect(self.__text)
        painter.setFont(QFont('KBREINDEERGAMES', 18))
        painter.setPen(Qt.red)
        painter.drawText(b, Qt.AlignCenter, self.__text)
        painter.restore()
        painter.end()

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