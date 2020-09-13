"""
Created on Sun Sep  13 02:42:16 2020

@author: Kamil Chrustowski
"""

from PyQt5.QtWidgets import QApplication
from ui.windows.mainwindow import MainWindow

class App(QApplication):
    def __init__(self, args):
        super(App, self).__init__(args)
        self.mainWindow = MainWindow()
        self.exec_()    

