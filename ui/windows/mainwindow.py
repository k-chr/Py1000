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
        #if(self.gameLayout is None and self.player is not None): #jak już ustawi playera to wtedy dopiero ma ustawić game layout
        self.gameLayout = GameLayout(self.player, WINDOW_SIZE)
        return self.gameLayout
    def closeEvent(self,event):
        if(self.player is not None):
            self.player.cleanUp()
        event.accept()
    def create_welcome_game_layout(self):
        self.welcomeLayout = None
        banner = QPixmap(os.path.join('images', 'banner.png'))
        w_bg = QPixmap(os.path.join('images', 'main.jpg'))
        self.welcomeLayout = WelcomeLayout(WINDOW_SIZE, 350, banner, ['host', 'peer', 'settings', 'help', 'quit'],w_bg, self.player)
        return self.welcomeLayout

    def handle_menu(self, button):
        print(button.name)
    def __init__(self):
        super(MainWindow, self).__init__()
        self.welcomeLayout = None
        self.gameLayout = None
        self.resize(1500, 1100)
        self.showMaximized()
        self.showFullScreen()
        #PLAYER CONTENT
        self.player = None
        self.setWindowIcon(QIcon(QPixmap(os.path.join('images', 'ico.png'))))
        
        #IZA DO TESTÓW:
        if DEBUG == False:
            self.initPlayer()
        self.cursor_pix = QPixmap(os.path.join('images', 'gondola_coursor.png'))
        self.cursor_scaled_pix = self.cursor_pix.scaled(QSize(25, 25), Qt.KeepAspectRatio)
        self.current_cursor = QCursor(self.cursor_scaled_pix, -1, -1)

        # print(self.bgSound.isPlaying())
        # MERGING GUI ELEMENTS
        self.w = QWidget()
        self.w.setCursor(self.current_cursor)
        self.setCentralWidget(self.w)
        self.w.setLayout(self.create_welcome_game_layout())
        

        #STATUS HELP STATUS GAME
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("color: blue;")
        self.setStatusBar(self.statusBar)
        StatusGame.getInstance().signals.statusChanged.connect(lambda: self.set_status(StatusGame.getInstance().get_status_name()))
        if DEBUG == False:
            StatusGame.getInstance().signals.statusChanged.connect(lambda: self.player.on_status_changed(StatusGame.getInstance().get_status_name()))
        self.set_status(StatusGame.getInstance().get_status_name())
        self.initUI()
        self.setFixedSize(self.size())
    def set_status(self, status_name):
        self.statusBar.showMessage(STATUS_GAME[status_name])
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