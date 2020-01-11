from PyQt5.QtCore import QSize, QRect, QObject, pyqtSignal, QRectF, QPointF, pyqtProperty, QVariantAnimation
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsItem, QGraphicsRectItem
import os

#CARD CONSTANTS
SIDE_FACE = 0
SIDE_BACK = 1
CARD_DIMENSIONS = QSize(80, 116)
CARD_RECT = QRect(0, 0, 80, 116)
CARD_SPACING_X = 4.5

SUITS = ["c", "s", "h", "d"] #D - diamonds ♦, S - spades ♠, H - hearts ♥, C - clubs ♣
VALUES = ["9", "10", "11", "12", "13", "14"]
POINTS = {"9": 0, "10": 10, "11": 2, "12": 3, "13": 4, "14": 11}
BIDDING = {("h12", "h13"): 100, ("c12", "c13"): 60, ("s12", "s13"): 40, ("d12", "d13"): 80}
WHERE = ["HAND", "CARD_DECK", "STACK", "PLAYED_LEFT"]
STATUS_GAME = ["VALUE_DECLARATION", "STACK_CHOOSING", "GAME", "SCORING"]

def getCardList():
    cardlist = []
    for suit in SUITS:
        for value in VALUES:
            cardlist.append(str(suit + value))
    return cardlist

class Signals(QObject):
    carddeck = pyqtSignal()
    cardstack = pyqtSignal()


class Card(QGraphicsPixmapItem):
    def __init__(self, suit, value, location):
        super(Card, self).__init__()
        self.signals = Signals()

        self.suit = suit
        self.value = value
        self.side = None
        self.face = None
        self.back = None
        self.location = location

        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        #self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.setZValue(-1)
        self.load_images()

    def load_images(self):
        self.face = QPixmap(
            os.path.join('cards', '%s%s.png' % (self.value, self.suit))
        )
        self.back = QPixmap(
            os.path.join('images', 'back.png')
        )

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

    #poprzekształcać dobrze
    def mousePressEvent(self, e):
        if self.location == "HAND" and STATUS_GAME == "GAME":
            super(Card, self).mousePressEvent(e)
            self.signals.carddeck.emit()
            e.accept()
        elif self.location == "HAND" and STATUS_GAME == "STACK_CHOOSING":
            super(Card, self).mousePressEvent(e)
            self.signals.cardstack.emit()
            e.accept()

        '''if not self.is_face_up:
            self.turn_face_up()
            return
        else:
            self.turn_back_up()

        super(Card, self).mouseReleaseEvent(e)'''

    #def mouseDoubleClickEvent(self, e):



'''
        if not self.is_face_up and self.stack.cards[-1] == self:
            self.turn_face_up()  # We can do this without checking.
            e.accept()
            return

        if self.stack and not self.stack.is_free_card(self):
            e.ignore()
            return

        self.stack.activate()

        e.accept()

        super(Card, self).mouseReleaseEvent(e)


    def mouseReleaseEvent(self, e):
        self.stack.deactivate()

        items = self.collidingItems()
        if items:
            # Find the topmost item from a different stack:
            for item in items:
                if ((isinstance(item, Card) and item.stack != self.stack) or
                        (isinstance(item, StackBase) and item != self.stack)):

                    if item.stack.is_valid_drop(self):
                        # Remove card + all children from previous stack, add to the new.
                        # Note: the only place there will be children is on a workstack.
                        cards = self.stack.remove_card(self)
                        item.stack.add_cards(cards)
                        break

        # Refresh this card's stack, pulling it back if it was dropped.
        self.stack.update()

        super(Card, self).mouseReleaseEvent(e)

    def mouseDoubleClickEvent(self, e):
        if self.stack.is_free_card(self):
            self.signals.doubleclicked.emit()
            e.accept()

        super(Card, self).mouseDoubleClickEvent(e)
'''

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
            #self.update()

    def remove_card(self):
        if self.card is not None:
            self.card.location = None
            tmp = self.card
            self.card = None
            #self.update()
            return tmp

    def update(self):
        self.card.setOffset(self.pos() + QPointF(self.offset_x, self.offset_y))

class CardStack(QGraphicsPixmapItem):
    def __init__(self, number):
        super(CardStack, self).__init__()
        self.setPixmap(QPixmap(
            os.path.join('images', '%s.png' % (number))
        ))
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.setZValue(-1)
        self.cards = []
        self.isShowed = False

    def addCards(self, cards):
        temp = self.x()
        for card in cards[:]:
            card.setOffset(temp, self.y() + 50)
            temp += CARD_SPACING_X + CARD_DIMENSIONS.width()
            card.turn_back_up()
        self.cards = cards

    def removeCards(self):
        for card in self.cards[:]:
            card.location = None
        self.cards = []

    def add_card(self, card):
        card.location = "STACK"
        self.cards.append(card)

    def remove_card(self, card):
        card.location = "HAND"
        return self.cards.remove(card)

    def showCards(self):
        for card in self.cards[:]:
            card.turn_face_up()

    def hideCards(self):
        for card in self.cards[:]:
            card.turn_back_up()

    def mousePressEvent(self, e):
        if self.isShowed is False:
            self.showCards()
            self.isShowed = True
        else:
            self.hideCards()
            self.isShowed = False
