from PyQt5.QtCore import QSize, QRect, QObject, pyqtSignal, QRectF, QPointF, pyqtProperty, QVariantAnimation
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtWidgets import *
from PyQt5.Qt import *
import os
from statusgame import *
from random import randint
#CARD CONSTANTS
SIDE_FACE = 0
SIDE_BACK = 1
CARD_DIMENSIONS = QSize(120, 174)
CARD_RECT = QRect(0, 0,120, 174)
CARD_SPACING_X = 10

SUITS = ["C", "S", "H", "D"] #D - diamonds ♦, S - spades ♠, H - hearts ♥, C - clubs ♣
VALUES = ["9", "10", "11", "12", "13", "14"]
POINTS = {"9": 0, "10": 10, "11": 2, "12": 3, "13": 4, "14": 11}
BIDDING = {'H': 100, 'C': 60, 'S': 40, 'D': 80}
WHERE = ["HAND", "HAND_STACK", "CARD_DECK", "STACK", "PLAYED_LEFT"]

def playRandomCardSound(parent):
    num = randint(1,8)
    QSound.play(os.path.join('sounds','c'+str(num) + '.wav'))
    
def getCardList():
    cardlist = []
    for suit in SUITS:
        for value in VALUES:
            cardlist.append(str(suit + value))
    return cardlist

class Signals(QObject):
    clicked = pyqtSignal()
    stackAccepted = pyqtSignal(int)

class Card(QGraphicsPixmapItem):
    def isPair(self, obj):
        if isinstance(obj, Card) == False:
            return False
        if self.suit == obj.suit:
            if (int(self.value) == 12 and int(obj.value) == 13) or (int(self.value) == 13 and int(obj.value) == 12):
                return True
        return False
    def __hash__(self):
        return hash(self.value) + hash(self.suit)
    def __repr__(self):
        return str(self.suit) + str(self.value)
    def __cmp__(self, obj):
        return 0 if isinstance(obj, Card) == True and obj.suit == self.suit and self.value == obj.value else 1 if self < obj else -1
    def __ne__(self,obj):
        return isinstance(obj, Card) == False or obj.suit != self.suit or self.value != obj.value
    def __eq__(self, obj):
        return isinstance(obj, Card) == True and obj.suit == self.suit and self.value == obj.value
    def __gt__(self, obj):
        return isinstance(obj, Card) and obj.suit == self.suit and POINTS[obj.value] < POINTS[self.value]
    def __lt__(self, obj):
        return isinstance(obj, Card) and obj.suit == self.suit and POINTS[obj.value] > POINTS[self.value]
    def __init__(self, suit, value, location=None):
        super(Card, self).__init__()
        self.signals = Signals()
        self.setTransformationMode(Qt.SmoothTransformation)
        self.suit = suit
        self.value = str(value)
        self.side = None
        self.face = None
        self.back = None
        self.location = location

        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.setZValue(-1)
        self.load_images()
    def rotate180H(self):
        self.back = self.back.transformed(QTransform().scale(-1, -1))
        self.face = self.face.transformed(QTransform().scale(-1, -1))
    def getTuple(self):
        return (self.suit, self.value)
    def load_images(self):
        self.face = QPixmap(
            os.path.join('images\\cards', '%s%s.png' % (self.value, self.suit))
        )
        self.face = self.face.scaled(CARD_DIMENSIONS.width(), CARD_DIMENSIONS.height())
        self.back = QPixmap(
            os.path.join('images\\cards', 'back.png')
        )
        self.back = self.back.scaled(CARD_DIMENSIONS.width(), CARD_DIMENSIONS.height())

    def turn_face_up(self):
        self.side = SIDE_FACE
        self.setPixmap(self.face)

    def turn_back_up(self):
        self.side = SIDE_BACK
        self.setPixmap(self.back)
    @property
    def is_face_up(self):
        return self.side == SIDE_FACE

    @property
    def color(self):
        return 'r' if self.suit in ('h', 'd') else 'b'

    def mousePressEvent(self, e):
        super(Card, self).mousePressEvent(e)
        self.signals.clicked.emit()
        e.accept()

class CardDeck(QGraphicsRectItem):
    def __init__(self):
        super(CardDeck, self).__init__()
        self.setRect(QRectF(CARD_RECT))
        self.setZValue(-1)
        self.offset_x = -0.2
        self.offset_y = -0.3
        self.card = None

    def add_card(self, card):
        if self.card is None:
            self.card = card
            self.card.location = "CARD_DECK"

    def remove_card(self):
        if self.card is not None:
            self.card.location = None
            tmp = self.card
            self.card = None
            return tmp

    def update(self):
        self.card.setOffset(self.pos() + QPointF(self.offset_x, self.offset_y))

class CardStack(QGraphicsPixmapItem):
    __clicks = 0
    
    current_selection = -1
    def __init__(self, number):
        super(CardStack, self).__init__()
        self.signals = Signals()
        self.number = number
        self.pixmap = QPixmap(os.path.join('images', '%s.png' % (number)))
        self.setPixmap(self.pixmap)
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.signals.clicked.connect(self.countClicks)
        self.stack_index = 1
        self.setZValue(-1)
        self.cards = []
        self.isShowed = False
    def onCardToExchange(self, cardID):
        if(StatusGame.getInstance().get_status_name() != "STACK_CARD_TAKING"):
            return
        if(int(cardID) == int(self.current_selection)):
            self.current_selection = -1
        else:
            self.current_selection = cardID
    def get_one_card(self):
        if self.current_selection == -1:
            return None
        else:
            return self.cards[self.current_selection]

    def addCards(self, cards):
        temp_x = self.x() + self.pixmap.width()
        for card in cards[:]:
            card.location = "STACK"
            card.setOffset(temp_x, self.y())
            temp_x += CARD_DIMENSIONS.width()
            card.turn_back_up()
        self.cards = list(cards)

    def removeCards(self):
        for card in self.cards[:]:
            card.location = None
        self.cards = []
    def countClicks(self):
        if StatusGame.getInstance().get_status_name() == "STACK_CHOOSING" or StatusGame.getInstance().get_status_name() == "STACK_CARD_TAKING":
            if(self.__clicks < 2):
                self.__clicks += 1
            else:
                return
            if(self.__clicks >= 2):
                self.hideCards()
                self.signals.stackAccepted.emit(self.number)
    def add_card(self, card):
        card.location = "STACK"
        self.cards.append(card)
    def exchange_card(self, card):
        card.location = "STACK"
        self.cards[self.current_selection] = card
        val = self.current_selection
        card.signals.clicked.disconnect()
        card.signals.clicked.connect(lambda cardID=val: self.onCardToExchange(cardID))
    def remove_card(self, card, location):
        card.location = location.__str__()
        self.cards.remove(card)
    def remove_card_in_situ(self,card, location):
        card.location = location.__str__()
        self.cards[self.cards.index(card)] = None
    def showCards(self):
        for card in self.cards[:]:
            card.turn_face_up()

    def hideCards(self):
        for card in self.cards[:]:
            card.turn_back_up()

    def mousePressEvent(self, e):
        super(CardStack, self).mousePressEvent(e)
        self.signals.clicked.emit()
        e.accept()