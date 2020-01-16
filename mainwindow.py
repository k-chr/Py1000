from initdialog import *
from player import *
from statusgame import *
from PyQt5.QtCore import *
from welcomelayout import WelcomeLayout
STTACK_CHOICE = -1

#window constants
PLAY_SCENE_SIZE = 1200, 800
WINDOW_SIZE = 1500, 1000
OFFSET_X = 5
OFFSET_Y = 500

class MainWindow(QMainWindow):
    def add_to_left(self):
        for carddeck in self.carddecks:
            card = carddeck.remove_card()
            self.playscene.removeItem(card)
            card.location = "PLAYED_LEFT"
            self.player.add_card_to_left(card)

    def setScore(self):
        self.score.setText(self.player.calculate_score().__str__())

    def init_hand_cards(self, cards):
        temp = OFFSET_X
        for card in cards:
            card.setOffset(temp, OFFSET_Y)
            card.turn_face_up()
            self.player.hand_cards.append(card)
            self.playscene.addItem(card)
            temp += CARD_DIMENSIONS.width() + CARD_SPACING_X
            card.signals.clicked.connect(lambda card=card: self.change_card_location(card))

    def change_card_location(self, card):
        if card.location == "HAND" and StatusGame.getInstance().get_status_name() == "GAME":
            self.drop_card_from_hand(card)
        elif card.location == "HAND" and StatusGame.getInstance().get_status_name() == "STACK_CARD_TAKING":
            self.change_card_with_stack(card)

    def drop_card_from_hand(self, card):
        if self.carddecks[0].card is None:
            self.player.remove_card_from_hand(card)
            anime = QVariantAnimation(self)
            anime.valueChanged.connect(card.setOffset)
            anime.setDuration(500)
            anime.setStartValue(card.offset())
            anime.setEndValue(self.carddecks[0].pos())
            anime.start()
            self.carddecks[0].add_card(card)

    def change_card_with_stack(self, card):
        if self.stack_index < 0:
            print('olabogacosiestaloxd')
            return

        anime1 = QVariantAnimation(self)
        anime2 = QVariantAnimation(self)
        self.player.remove_card_from_hand(card)

        stack_card = self.cardstacks[self.stack_choice].get_one_card()
        self.cardstacks[self.stack_choice].remove_card(stack_card, "HAND")
        temp_pos_stack = stack_card.offset()
        temp_pos_card = card.offset()

        anime1.valueChanged.connect(stack_card.setOffset)
        anime1.setDuration(500)
        anime1.setStartValue(stack_card.offset())
        anime1.setEndValue(temp_pos_card)
        anime1.start()

        self.player.add_card_to_hand(stack_card)

        anime2.valueChanged.connect(card.setOffset)
        anime2.setDuration(500)
        anime2.setStartValue(card.offset())
        anime2.setEndValue(temp_pos_stack)
        anime2.start()

        self.cardstacks[self.stack_choice].add_card(card)

        self.stack_index -= 1


    def player_info(self):
        self.player_info_wg = QWidget()
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        vbox.addWidget(QLabel('Score:'))
        objValidator = QIntValidator(self)
        objValidator.setRange(-1000, 1000)
        self.score = QLineEdit()
        self.score.setValidator(objValidator)
        self.score.setText(self.player.score.__str__())
        self.score.setReadOnly(True)
        vbox.addWidget(self.score)

        vbox.addWidget(QLabel('Your declared value:'))
        self.declared = QLineEdit()
        vbox.addWidget(self.declared)

        #tutaj coś pokombinować
        vbox.addWidget(QLabel('Current reported color:'))
        reported = QLineEdit()
        reported.setReadOnly(True)
        reported.setText("red")
        reported.setStyleSheet("background: red")
        vbox.addWidget(reported)

        self.player_info_wg.setLayout(vbox)
        return self.player_info_wg
    def create_game_layout(self):
        self.view = QGraphicsView()
        self.playscene = QGraphicsScene()
        self.view.setScene(self.playscene)
        self.playscene.setSceneRect(QRectF(0, 0, *PLAY_SCENE_SIZE))
        bg = QPixmap(os.path.join('images\\backgrounds', 'bg2.png'))
        bg = bg.scaled(self.playscene.width(), self.playscene.height())
        brushBg = QBrush(bg)
        self.playscene.setBackgroundBrush(brushBg)
        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        hbox.addWidget(self.view)
        hbox.addWidget(self.player_info())
        return hbox
    def create_welcome_game_layout(self):
        if(self.welcomeLayout is None):
            banner = QPixmap(os.path.join('images', 'banner.png'))
            w_bg = QPixmap(os.path.join('images', 'main.jpg'))
            self.welcomeLayout = WelcomeLayout(WINDOW_SIZE, 350, banner, ['host', 'peer', 'settings', 'help', 'quit'],w_bg)
        return self.welcomeLayout
    def set_stack_choice(self, value):
        self.stack_choice = value
    def handle_menu(self, button):
        print(button.name)
    def __init__(self):
        super(MainWindow, self).__init__()
        self.welcomeLayout = None
        #PLAYER CONTENT
        self.player = None
        self.stack_choice = 0
        self.stack_index = 1

        ##BACKGROUND + PLAYSCENE
        #self.view = QGraphicsView()
        #self.playscene = QGraphicsScene()
        #self.view.setScene(self.playscene)
        #self.playscene.setSceneRect(QRectF(0, 0, *PLAY_SCENE_SIZE))
        #bg = QPixmap(os.path.join('images\\backgrounds', 'bg2.png'))
        #bg = bg.scaled(self.playscene.width(), self.playscene.height())
        #brushBg = QBrush(bg)
        #self.playscene.setBackgroundBrush(brushBg)

        #HAND
        temp_cards = []
        for _ in range(0, 10): temp_cards.append(Card('C', '12', "HAND"))
        #above is temporary
        #self.init_hand_cards(temp_cards)

        #DECKS
        #self.init_card_decks()

        #STACKS
        #self.init_card_stacks()

        #MERGING GUI ELEMENTS
        self.w = QWidget()
        self.setCentralWidget(self.w)
        #hbox = QHBoxLayout()
        self.w.setLayout(self.create_welcome_game_layout())
        #hbox.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        #hbox.addWidget(self.view)
        #hbox.addWidget(self.player_info())

        #STATUS HELP STATUS GAME
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("color: blue;")
        self.setStatusBar(self.statusBar)
        #TODO: ustawić tak, by po przesłaniu od serwera informacji o stanie tutaj też to się zmieniało
        self.statusBar.showMessage(STATUS_GAME[StatusGame.getInstance().get_status_name()])
        self.initUI()

    def initPlayer(self):
        self.player = Player()
    def initUI(self):
        self.setGeometry(100, 100, *WINDOW_SIZE)
        self.setWindowTitle("Py1000 - THE CARD GAME ")
        self.setFixedSize(WINDOW_SIZE[0]+ 2 , WINDOW_SIZE[1] + 2)
        self.show()
    def init_card_decks(self):
        self.carddecks = [] #0 - my carddeck, 1 - player cardeck
        y = 175
        for i in range (0, 2):
            carddeck = CardDeck()
            carddeck.setPos(350, y)
            y -= 125
            self.carddecks.append(carddeck)
            self.playscene.addItem(carddeck)

    def init_card_stacks(self):
        self.cardstacks = []
        x = 50
        for i in range(0, 2):
            cardstack = CardStack(i+1) # 1 - 1, 2 - 2
            cardstack.setPos(QPoint(x, 50))
            x += 500
            self.cardstacks.append(cardstack)
            self.playscene.addItem(cardstack)

        #temporary
        numberCards = []
        for x in range(0, 2):
            card = Card('C', '9', "STACK")
            card.signals.clicked.connect(lambda card=card: self.change_card_location(card))
            numberCards.append(card)
            self.playscene.addItem(card)

        self.cardstacks[0].addCards(numberCards)
        
    def run_networking_dialog(self):
        result = PeerDialog.getDialog(self, "Welcome player!")
        
    def toggle_declare_value_dialog(self):
        value, ok = InitDialog.getDialog(self, "Declare value")

        if ok is True:
            self.declared.setText(value.__str__())
            self.player.declared_value = value
            self.declared.setReadOnly(True)
        else:
            if self.declared.text() == "":
                self.declared.setText("100")



