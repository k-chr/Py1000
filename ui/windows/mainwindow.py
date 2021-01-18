from config import Config
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import QMainWindow, QStatusBar
from ui.dialogs.biddialog import *
from player import *
from statusgame import *
from PyQt5.QtMultimedia import QSound, QSoundEffect
from PyQt5.QtCore import *
from ui.layouts.welcomelayout import WelcomeLayout
from ui.layouts.gamelayout import GameLayout
#from ui.layouts.testlayout import TestLayout
# from ui.game import CARD_DIMENSIONS
import os
#window constants
WINDOW_SIZE = 1000, 700
OFFSET_X = 5
OFFSET_Y = 500
DEBUG = False


class MainWindow(QMainWindow):
    def create_game_layout(self):
        if(self.player is None):
            return None
        self.gameLayout = GameLayout(self.player, WINDOW_SIZE)
        return self.gameLayout

    def closeEvent(self,event):
        if(self.player is not None):
            self.player.cleanUp()
        event.accept()

    def create_welcome_game_layout(self):
        self.welcomeLayout = None
        w_bg = QPixmap(os.path.join('images', 'main.jpg'))
        self.welcomeLayout = WelcomeLayout(350,  ['host', 'peer', 'settings', 'help', 'quit'])
        return self.welcomeLayout

    def handle_menu(self, button):
        print(button.name)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.welcomeLayout = None
        self.gameLayout = None
        
        self.showMaximized()
        self.showFullScreen()
        #PLAYER CONTENT
        self.player = None
        
        #IZA DO TESTÓW:
        if DEBUG == False:
            self.initPlayer()
        # MERGING GUI ELEMENTS
        self.w = QWidget()
        self.setCentralWidget(self.w)
        self.w.setLayout(self.create_welcome_game_layout())
    
        #STATUS HELP STATUS GAME
        statusBar = QStatusBar()
        statusBar.setAttribute(Qt.WA_TranslucentBackground)
        statusBar.setStyleSheet("color: blue; background-color: rgba(255, 255, 255, 128)")
        self.setStatusBar(statusBar)
        StatusGame.getInstance().signals.statusChanged.connect(lambda: self.set_status(StatusGame.getInstance().get_status_name()))
        if DEBUG == False:
            StatusGame.getInstance().signals.statusChanged.connect(lambda: self.player.on_status_changed(StatusGame.getInstance().get_status_name()))
        self.set_status(StatusGame.getInstance().get_status_name())
        self.initUI()

    def set_status(self, status_name):
        self.statusBar().showMessage(STATUS_GAME[status_name])
        if(status_name == "GAME") and DEBUG == False:
            QWidget().setLayout(self.w.layout())
            self.w.setLayout(self.create_game_layout())
        elif(status_name == "BACK_TO_MENU" and DEBUG == False):
            QWidget().setLayout(self.w.layout())
            self.w.setLayout(self.create_welcome_game_layout())

    def initPlayer(self):
        self.player = Player()

    def initUI(self):
        self.setWindowTitle("Py1000 - THE CARD GAME ")
        self.show()