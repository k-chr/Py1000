import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from card import *
from initdialog import *
from player import *

#TODO: inaczej to, bo nie zmienie później + jakoś żeby to do karty przesłać
STATUS_GAME = "GAME"
STTACK_CHOICE = -1

#window constants
PLAY_SCENE_SIZE = 852, 480
WINDOW_SIZE = 1100, 500
OFFSET_X = 5
OFFSET_Y = 340

class MainWindow(QMainWindow):
    def add_to_left(self):
        card1 = self.my_carddeck.remove_card()
        card2 = self.player_carddeck.remove_card()
        card1.location = "PLAYED_LEFT"
        card2.location = "PLAYED_LEFT"
        self.playscene.removeItem(card1)
        self.playscene.removeItem(card2)
        self.player.add_card_to_left(card1)
        self.player.add_card_to_left(card2)

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
            card.signals.carddeck.connect(lambda card=card: self.drop_card_from_hand(card))
            card.signals.cardstack.connect(lambda card=card: self.change_card_with_stack(card))

    def drop_card_from_hand(self, card):
        if self.my_carddeck.card is None:
            self.player.remove_card_from_hand(card)
            anime = QVariantAnimation(self)
            anime.valueChanged.connect(card.setOffset)
            anime.setDuration(500)
            anime.setStartValue(card.offset())
            anime.setEndValue(self.my_carddeck.pos())
            anime.start()
            self.my_carddeck.add_card(card)

    def change_card_with_stack(self, card):
        if self.is_first_stack:
            stack_card = self.numberOne.remove_card(self.numberOne.cards[self.stack_index])
            temp_pos = stack_card.pos()

            card.setOffset(*temp_pos)
            self.numberOne.add_card(card)

            stack_card.setOffset(*card.pos())
            self.player.add_card_to_hand(stack_card)
        else:
            stack_card = self.numberTwo.remove_card(self.numberOne.cards[self.stack_index])
            temp_pos = stack_card.pos()

            card.setOffset(*temp_pos)
            self.numberTwo.add_card(card)

            stack_card.setOffset(*card.pos())
            self.player.add_card_to_hand(stack_card)
        self.stack_index += 1


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

    def __init__(self):
        super(MainWindow, self).__init__()
        self.status_game = "GAME"

        #PLAYER CONTENT
        self.player = Player()
        self.is_first_stack = True
        self.stack_index = 0

        #BACKGROUND + PLAYSCENE
        self.view = QGraphicsView()
        self.playscene = QGraphicsScene()
        self.view.setScene(self.playscene)
        self.playscene.setSceneRect(QRectF(0, 0, *PLAY_SCENE_SIZE))

        felt = QBrush(QPixmap(os.path.join('images', 'green_bg2.jpg')))
        self.playscene.setBackgroundBrush(felt)

        #HAND
        temp_cards = []
        for _ in range(0, 10): temp_cards.append(Card('C', '10', "HAND"))
        #above is temporary
        self.init_hand_cards(temp_cards)

        #DECKS
        self.my_carddeck = CardDeck()
        self.player_carddeck = CardDeck()
        self.init_card_decks()

        #STACKS
        self.numberOne = CardStack(1)
        self.numberTwo = CardStack(2)
        self.numberOne.setPos(QPointF(50, 50))
        self.numberTwo.setPos(QPointF(550, 50))

        numberCards = []
        for x in range(0, 2):
            c = Card('C', '9', "STACK")
            numberCards.append(c)
            self.playscene.addItem(c)
        self.numberOne.addCards(numberCards)
        self.playscene.addItem(self.numberOne)
        self.playscene.addItem(self.numberTwo)

        #MERGING GUI ELEMENTS
        w = QWidget()
        self.setCentralWidget(w)
        hbox = QHBoxLayout()
        w.setLayout(hbox)
        hbox.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        hbox.addWidget(self.view)
        hbox.addWidget(self.player_info())

        self.initUI()

    def initUI(self):
        self.setGeometry(150, 150, *WINDOW_SIZE)
        self.setWindowTitle("CARD GAME THOUSAND")
        self.setFixedSize(*WINDOW_SIZE)
        self.show()
        self.toggle_declare_value_dialog()


    def init_card_decks(self):
        self.my_carddeck.setPos(350, 175)
        self.player_carddeck.setPos(350, 50)
        self.playscene.addItem(self.my_carddeck)
        self.playscene.addItem(self.player_carddeck)


    def toggle_declare_value_dialog(self, name=None):
        value, ok = InitDialog.getDialog(self, "Declare value", name)
        value = round(value/10) * 10

        if self.declared.text() == "":
            self.declared.setText(self.player.declared_value.__str__())

        if ok is True:
            self.declared.setText(value.__str__())
            self.player.declared_value = value
            self.declared.setReadOnly(True)



