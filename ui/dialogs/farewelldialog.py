# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 00:25:20 2020

@author: Kamil Chrustowski
"""
from PyQt5.QtGui import QFont, QPainter
import os
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSizePolicy
from ui.widgets.configbutton import ConfigButton
from PyQt5.QtMultimedia import QSound
class FarewellDialog(QDialog):
    
    def closeEvent(self, event):
        event.ignore()  
        
    def __init__(self, txt, parent=None):
        super(FarewellDialog, self).__init__(parent)
        self.setFixedSize(600, 200)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.pixmap = QPixmap(os.path.join('images\\backgrounds', 'blank4.png'))
        self.setAttribute(Qt.WA_TranslucentBackground)
        lab = QLabel(txt)
        lab.setStyleSheet("QLabel{padding-left: 2px; padding-right: 2px; padding-top: 2px; padding-bottom: 2px;}")
        lab.setFont(QFont('KBREINDEERGAMES', 80))
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lab)
        lab.setAlignment(Qt.AlignCenter)
        self.button = ConfigButton(text="Go back to Main Menu")
        vbox.addWidget(self.button, 0, Qt.AlignBottom|Qt.AlignCenter)
        self.setLayout(vbox)
        self.button.clicked.connect(lambda: self.accept())
        
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.save()
        painter.drawPixmap(0,0, self.pixmap.scaled(QSize(self.width(), self.height())))
        painter.restore()
        
    @staticmethod
    def getDialog(parent=None, title="Bidding"):
        dialog = FarewellDialog(title, parent)
        dialog.setWindowTitle("It\'s the end of the game")
        result = dialog.exec_()
        return result == QDialog.Accepted