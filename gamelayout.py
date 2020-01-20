import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from card import *
from initdialog import InitDialog
from config import Config
PLAY_SCENE_SIZE = 1200, 900

class Suit(QWidget):
    __size =[50,50]
    __suit = ""
    __pixmap = None
    __pixmaps = {'C':'club.png','H':'heart.png', 'S':'spade.png', 'D':'diamond.png'}
    def __init__(self, suit=""):
        super(Suit, self).__init__()
        self.setFixedHeight(self.__size[1])
        self.setFixedWidth(self.__size[0])
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setStyleSheet("background-color: transparent;background: none; background-repeat: none; border: 10px;")
        self.__suit = suit
        self.__pixmap = None if suit == "" else QPixmap(os.path.join('images', self.__pixmaps[self.__suit]))
    def changeSuit(self, suit):
        name = self.__pixmaps.get(suit, '')
        if(name != ''):
            self.__suit = suit
            self.__pixmap = QPixmap(os.path.join('images', self.__pixmaps[self.__suit]))
            self.update()
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(0,0, self.__pixmap.scaled(QSize(self.width(), self.height())))
class GameLayout(QHBoxLayout):
    def __init__(self, player, windowSize=None, parent=None):
        super(GameLayout, self).__init__(parent)
        self.setAlignment(Qt.AlignAbsolute)
        self.player = player
        self.player.cardsToHandInReady.connect(self.initCards)
        self.setContentsMargins(0,0,0,0)
        self.stack_choice = None
        self.stack_index = 1     
        self.addWidget(self.create_playscene(windowSize))
        self.addWidget(self.create_player_info(player))
    def runBiddingDialog(self):
        value, result = InitDialog.getDialog(min=140, max = 230)
        print(value, result)
    def create_playscene(self, WINDOW_SIZE):
        self.view = QGraphicsView()
        self.view.setAlignment(Qt.AlignAbsolute)
        self.playscene = QGraphicsScene()
        self.view.setScene(self.playscene)
        self.view.setStyleSheet("background-color: transparent;background: none; background-repeat: none;")
        self.playscene.setSceneRect(QRectF(0, 0, *PLAY_SCENE_SIZE))
        self.bg = QPixmap(Config.getInstance().get_background_config())
        geometry = QApplication.desktop().geometry()
        self.bg = self.bg.scaled(geometry.width(), geometry.height())
        brushBg = QBrush()
        brushBg.setColor(QColor(255,255,255,255) )
        self.playscene.setBackgroundBrush(brushBg)
        return self.view
    def paintEvent(self, event):
         painter = QPainter()
         painter.begin(self)
         painter.drawPixmap(0,0, self.bg)
    def initCards(self,server, player, stacks):
        self.init_hand_cards(server, CARD_DIMENSIONS)
        self.init_opponent_cards(player, CARD_DIMENSIONS)
        self.init_card_stacks(stacks[0], stacks[1], CARD_DIMENSIONS)
    def create_player_info(self, player):
        self.player_info_wg = QWidget()
        self.player_info_wg.setFixedWidth(200)
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignVCenter | Qt.AlignTop)

        vbox.addWidget(QLabel('Score:'))
        objValidator = QIntValidator(self)
        objValidator.setRange(-1000, 1000)
        self.score = QLineEdit()
        self.score.setValidator(objValidator)
        self.score.setText(player.score.__str__())
        self.score.setReadOnly(True)
        vbox.addWidget(self.score)

        vbox.addWidget(QLabel('Your declared value:'))
        self.declared = QLineEdit()
        vbox.addWidget(self.declared)

        # tutaj coś pokombinować
        vbox.addWidget(QLabel('Current reported suit:'))
        reported = Suit('C')
        vbox.addWidget(reported)

        self.player_info_wg.setLayout(vbox)
        return self.player_info_wg

    def setScore(self, player):
        self.score.setText(player.calculate_score().__str__())

    def set_stack_choice(self, cardstack):
        if StatusGame.getInstance().get_status_name() == "STACK_CHOOSING":
            self.stack_choice = cardstack.number - 1
            self.cardstacks[self.stack_choice].showCards()
            StatusGame.getInstance().set_status_name("STACK_CARD_TAKING")

    def init_opponent_cards(self, cards, CARD_DIMENSIONS):
        y_temp = 0
        spacing_x = self.playscene.width() / len(cards) - CARD_DIMENSIONS.width()
        x_temp = spacing_x / 2
        for i, card in enumerate(cards):
            card.turn_face_up()
            card.setOffset(x_temp, y_temp)
            self.playscene.addItem(card)
            x_temp += CARD_DIMENSIONS.width() + spacing_x
            #card.signals.clicked.connect(lambda card=card: self.change_card_location(card))

    def init_hand_cards(self, cards, CARD_DIMENSIONS):
        y_temp = self.playscene.height() - CARD_DIMENSIONS.height()
        spacing_x = self.playscene.width() / len(cards) - CARD_DIMENSIONS.width()
        x_temp = spacing_x / 2
        for i, card in enumerate(cards):
            card.turn_face_up()
            card.setOffset(x_temp, y_temp)
            self.playscene.addItem(card)
            x_temp += CARD_DIMENSIONS.width() + spacing_x
            card.signals.clicked.connect(lambda card=card: self.change_card_location(card))

    def init_card_decks(self, CARD_DIMENSIONS):
        self.carddecks = []  # 0 - my carddeck, 1 - player cardeck
        x = self.playscene.width() / 2 - CARD_DIMENSIONS.width() / 2
        y = self.playscene.height() / 2
        for i in range(0, 2):
            carddeck = CardDeck()
            carddeck.setPos(x, y)
            y -= CARD_DIMENSIONS.height() + 2
            self.carddecks.append(carddeck)
            self.playscene.addItem(carddeck)

    def init_card_stacks(self, cards1, cards2, CARD_DIMENSIONS): #cards to tupla
        self.cardstacks = []
        x = self.playscene.width() * 2 / 3
        y = self.playscene.height() / 2 - CARD_DIMENSIONS.height() / 2
        for i in range(2, 0, -1):
            cardstack = CardStack(i)  # 1 - 1, 2 - 2
            cardstack.signals.clicked.connect(lambda cardstack=cardstack: self.set_stack_choice(cardstack))
            cardstack.setPos(QPoint(x, y))
            x = self.playscene.width() / 8
            self.cardstacks.append(cardstack)
            self.playscene.addItem(cardstack)

        for card in cards1:
            card.signals.clicked.connect(lambda card=card: self.change_card_location(card))
            card.turn_face_up()
            self.playscene.addItem(card)
        for card in cards2:
            card.signals.clicked.connect(lambda card=card: self.change_card_location(card))
            card.turn_face_up()
            self.playscene.addItem(card)
        self.cardstacks.reverse()
        self.cardstacks[0].addCards(cards1)
        self.cardstacks[1].addCards(cards2)

    def add_to_left(self):
        for carddeck in self.carddecks:
            card = carddeck.remove_card()
            self.playscene.removeItem(card)
            card.location = "PLAYED_LEFT"
            self.player.add_card_to_left(card)

    def change_card_location(self, card):
        if (card.location == "HAND" or card.location == "HAND_STACK") and StatusGame.getInstance().get_status_name() == "GAME":
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
            print('no more cards to change')
            return

        anime1 = QVariantAnimation(self)
        anime2 = QVariantAnimation(self)
        self.player.remove_card_from_hand(card)

        stack_card = self.cardstacks[self.stack_choice].get_one_card()
        self.cardstacks[self.stack_choice].remove_card(stack_card, "HAND_STACK")
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
        if self.stack_index < 0:
            StatusGame.getInstance().set_status_name("GAME")
