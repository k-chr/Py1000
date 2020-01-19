from initdialog import *
from player import *
from statusgame import *
from PyQt5.QtCore import *
from welcomelayout import WelcomeLayout
from gamelayout import GameLayout

#window constants
WINDOW_SIZE = 1000, 700
OFFSET_X = 5
OFFSET_Y = 500

class MainWindow(QMainWindow):
    def create_game_layout(self):
        if(self.gameLayout is None and self.player is not None): #jak już ustawi playera to wtedy dopiero ma ustawić game layout
            self.gameLayout = GameLayout(self.player, WINDOW_SIZE)
            return self.gameLayout

    def create_welcome_game_layout(self):
        if(self.welcomeLayout is None):
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

        #PLAYER CONTENT
        self.player = None
        self.setWindowIcon(QIcon(QPixmap(os.path.join('images', 'ico.png'))))

        ##BACKGROUND + PLAYSCENE
        #self.view = QGraphicsView()
        #self.playscene = QGraphicsScene()
        #self.view.setScene(self.playscene)
        #self.playscene.setSceneRect(QRectF(0, 0, *PLAY_SCENE_SIZE))
        #bg = QPixmap(os.path.join('images\\backgrounds', 'bg2.png'))
        #bg = bg.scaled(self.playscene.width(), self.playscene.height())
        #brushBg = QBrush(bg)
        #self.playscene.setBackgroundBrush(brushBg)

        #IZA DO TESTÓW:
        self.initPlayer()

        # MERGING GUI ELEMENTS
        self.w = QWidget()
        self.setCentralWidget(self.w)
        self.w.setLayout(self.create_game_layout())

        #HAND
        temp_cards = []
        temp_cards2 = []
        for _ in range(0, 10):
            card = Card('C', '12', "HAND")
            self.player.add_card_to_hand(card)
            temp_cards2.append(Card('C', '12'))
        #above is temporary
        self.gameLayout.init_hand_cards(self.player.hand_cards, CARD_DIMENSIONS)
        self.gameLayout.init_opponent_cards(temp_cards2, CARD_DIMENSIONS)

        #DECKS
        self.gameLayout.init_card_decks(CARD_DIMENSIONS)

        #STACKS
        # temporary
        c1 = []
        c2 = []
        for x in range(0, 2):
            card = Card('C', '9', "STACK")
            c1.append(card)
        for x in range(0, 2):
            card = Card('C', '11', "STACK")
            c2.append(card)

        self.gameLayout.init_card_stacks(c1, c2, CARD_DIMENSIONS)

        #IZA KONIEC TESTÓW

        #self.w.setLayout(self.create_welcome_game_layout())

        #STATUS HELP STATUS GAME
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("color: blue;")
        self.setStatusBar(self.statusBar)
        StatusGame.getInstance().signals.statusChanged.connect(lambda: self.set_status(StatusGame.getInstance().get_status_name()))
        self.set_status(StatusGame.getInstance().get_status_name())
        self.initUI()

    def set_status(self, status_name):
        self.statusBar.showMessage(STATUS_GAME[status_name])

    def initPlayer(self):
        self.player = Player()
    def initUI(self):
        self.setGeometry(100, 100, *WINDOW_SIZE)
        self.setWindowTitle("Py1000 - THE CARD GAME ")
        self.setFixedSize(WINDOW_SIZE[0]+ 2 , WINDOW_SIZE[1] + 2)
        self.show()

        
    def toggle_declare_value_dialog(self):
        value, ok = InitDialog.getDialog(self, "Declare value")

        if ok is True:
            self.declared.setText(value.__str__())
            self.player.declared_value = value
            self.declared.setReadOnly(True)
        else:
            if self.declared.text() == "":
                self.declared.setText("100")

