"""
Created on Sun Sep  13 02:42:16 2020

@author: Kamil Chrustowski
"""

from PyQt5.QtWidgets import QApplication
from ui.windows.mainwindow import MainWindow
from sounds.soundmanager import SoundManager

class App(QApplication):

    def __init__(self, args):
        super(App, self).__init__(args)
        self.main_window = MainWindow()
        self.sound_manager = SoundManager(self.main_window)
        self.exec_()
