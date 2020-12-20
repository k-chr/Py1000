"""
Created on Sun Sep  13 02:42:16 2020

@author: Kamil Chrustowski
"""

from config import Config
from PyQt5.QtWidgets import QApplication
from ui.windows.mainwindow import MainWindow
from sounds.soundmanager import SoundManager
import os


class App(QApplication):

    def __init__(self, args):
        super(App, self).__init__(args)
        
        with open(os.path.abspath('ui/py1000.qss'), 'r') as f:
            self.setStyleSheet(f.read())

        self.setWindowIcon(Config.get_instance().window_icon)
        self.setOverrideCursor(Config.get_instance().cursor)
        self.main_window = MainWindow()
        self.sound_manager = SoundManager(self.main_window)
        self.exec_()
