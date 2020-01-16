# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 00:10:57 2020

@author: Kamil Chrustowski
"""
from concurrent.futures import *
from threading import Thread
from PyQt5.Qt import *
from PyQt5.QtWidgets import * 
class HostDialog(QDialog):
    def closeEvent(self, event):
        event.ignore()

    def __init__(self, parent=None):
        super(HostDialog, self).__init__(parent)
        self.setFixedSize(300, 80)
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel('Waiting for the peers'), 0, 0)
        buttons = QDialogButtonBox(Qt.Horizontal, self)
        self.button = buttons.addButton("Start", QDialogButtonBox.AcceptRole)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons, 1, 0, 1, 2)
        self.button.setDisable(True)
        