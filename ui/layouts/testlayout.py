# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 09:50:03 2020

@author: Kamil Chrustowski
"""
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from card import *
from ui.dialogs.biddialog import BidDialog
from config import Config
from game.utils.randomcardgenerator import RandomCardGenerator
PLAY_SCENE_SIZE = 1200, 900
class Suit(QLabel):
    __size =[50,50]
    __suit = ""
    __pixmap = None
    __pixmaps = {'C':'club.png','H':'heart.png', 'S':'spade.png', 'D':'diamond.png', '':'default.png'}
    def __init__(self,parent=None, suit=""):
        super(Suit, self).__init__(parent)
        self.setFixedHeight(self.__size[1])
        self.setFixedWidth(self.__size[0])
        self.setAutoFillBackground(True)
        self.setText("NONE")
        self.setPixmap
        self.__suit = suit
        self.__pixmap = QPixmap(os.path.join('images', self.__pixmaps[self.__suit])).scaled(QSize(self.__size[0], self.__size[1]))
        self.setPixmap(self.__pixmap)
    def changeSuit(self, suit):
        name = self.__pixmaps.get(suit, '')
        print(name)
        if(name != ''):
            self.__suit = suit
            self.__pixmap = QPixmap(os.path.join('images', self.__pixmaps[self.__suit])).scaled(QSize(self.__size[0], self.__size[1]))
            self.setPixmap(self.__pixmap)
            self.update()
    def get_suit(self):
        return self.__suit
class GamePlayScene(QGraphicsScene):
    __pixmap = None
    def __init__(self, parent = None, pixmap=None):
        super(GamePlayScene, self).__init__()
        self.__pixmap = pixmap
        self.__parent_size = parent.geometry()
    def drawBackground(self,painter, rect):
        if self.__pixmap is None:
            return
        painter.save()
        geometry = QApplication.desktop().geometry()
        painter.drawPixmap((self.width()-self.__parent_size.width())//2,(self.height()-self.__parent_size.height())//2, self.__pixmap.scaled(QSize(geometry.width(), geometry.height()))) 
        painter.restore()
    def setPGeometry(self, geo):
        self.__parent_size = geo
        print(geo)
        self.invalidate()
class PlayerInfoWidget(QWidget):
    def __init__(self, parent = None):
        super(PlayerInfoWidget, self).__init__()
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setStyleSheet("background-color: transparent;background: none; background-repeat: none; border: 10px;")
        self.pixmap = QPixmap(os.path.join('images\\backgrounds', 'blank.png'))
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(60)
        shadow.setXOffset(-1)
        shadow.setYOffset(-1)
        shadow.setColor(QColor(Config.getInstance().get_shadow_config()))
        self.setGraphicsEffect(shadow)
    def paintEvent(self,event):
        painter = QPainter()
        painter.begin(self)
        painter.save()
        painter.drawPixmap(0,0, self.pixmap.scaled(self.size()))
        painter.restore()
        painter.end()
class TestLayout(QHBoxLayout):
    scoreString = 100
    __isItTimeToSetBg = pyqtSignal()
    updateScore = pyqtSignal(int)
    cardsToHandInReady = pyqtSignal(list,list,tuple)
    updateDeclaredValue = pyqtSignal(int)
    updateTrump = pyqtSignal(str)
    move_card = pyqtSignal(tuple)
    move_stack = pyqtSignal(list,int)
    updateDeck = pyqtSignal(str)
    def add_to_score(self, value):
        self.scoreString += value

    def sub_from_score(self, value):
        self.scoreString -= value
    def calculate_score(self):
        value = 0
        #tu też muszą znajdować się z musików
        for card in self.played_left[:]:
            value += POINTS.get(card.value, 0)
        if (len(self.played_left) > 0):
            for rep in self.reportedSuits:
                value += rep
        if self.is_main_player:
            if value >= self.declared_value:
                self.addToScore(self.declared_value)
            else:
                self.subFromScore(self.declared_value)
                value = value * (-1)
        else:
            value = round(value/10) * 10
            self.addToScore(value)
        self.played_left = []
        self.opponent_left = []
        self.declared_value = 0
        self.forbidden = 130
        self.currentBid = 0
        return self.score
    #HAND CARDS
    def add_cards_to_hand(self, cards):
        self.hand_cards = cards

    def remove_all_cards_from_hand(self):
        cards = self.hand_cards
        return cards

    def add_card_to_hand(self, card):
        self.hand_cards.append(card)
    
    def remove_card_from_hand(self, card):
        print(self.hand_cards)
        for c in self.hand_cards:
            if c == card:
                self.hand_cards.remove (c)
                break;
        #self.hand_cards.remove(card)
    #OPPONENT's CARDS
    def remove_card_from_opponent_hand(self, card):
        print(self.opponent_cards)
        for c in self.opponent_cards:
            if c == card:
                self.opponent_cards.remove (c)
                break;
        #self.opponent_cards.remove(card)
    def add_card_to_opponent_hand(self,card):
        self.opponent_cards.append(card)
    #LEFT CARDS
    def add_cards_to_left(self, cards):
        self.played_left = cards
    def remove_card_from_left(self, card):
        self.played_left.remove(card)
    def remove_all_cards_from_left(self):
        cards = self.played_left
        return cards
    def computeForbiddenVal(self):
        val = 130
        print("Cards in hand",self.hand_cards)
        print(Card('D', 13) == Card('D', 13, "HAND"))
        print(Card('H', 12) in self.hand_cards, Card('H', 13) in self.hand_cards)
        print(Card('D', 12) in self.hand_cards, Card('D', 13) in self.hand_cards)
        print(Card('C', 12) in self.hand_cards, Card('C', 13) in self.hand_cards)
        print(Card('S', 12) in self.hand_cards, Card('S', 13) in self.hand_cards)
        print(self.find_pair( (Card('H', "12"), Card('H', "13"))))
        if self.find_pair( (Card('H', "12"), Card('H', "13"))):
            val += 100
        if self.find_pair( (Card('D', "12"), Card('D', "13"))):
            val+=80
        if self.find_pair( (Card('C', "12"), Card('C', "13"))):
            val += 60
        if self.find_pair( (Card('S', "12"), Card('S', "13"))):
            val += 40
        self.forbidden = val
    def add_card_to_left(self, card):
        self.played_left.append(card)
    def add_card_to_opponent_left(self, card):
        self.opponent_left.append(card)
    def find_pair(self, tup):
        return tup[0] in self.hand_cards and tup[1] in self.hand_cards  
    def add_to_declared_value(self, value):
        self.declared_value += value
    def __init__(self, windowSize=None, parent=None):
        super(TestLayout, self).__init__(parent)
        self.setAlignment(Qt.AlignAbsolute)
        self.hand_cards = []
        self.forbidden = 130
        self.declared_value = 0
        self.opponent_cards = []
        self.opponent_left = []
        self.played_left = []
        self.reportedValues = []
        self.playscene = None
        self.view = None
        self.player_info_wg = None
        self.scoreLabel = None
        self.score = None
        self.reported = None
        self.frame = None
        self.declared = None
        self.cardsToHandInReady.connect(self.initCards)
        self.updateDeclaredValue.connect(self.setDeclaredValue)
        self.__currentTrump = None
        self.move_card.connect(self.drop_card_from_opponent_hand)
        self.move_stack.connect(self.change_opponent_cards_with_stack)
        self.updateDeck.connect(self.collectFromDeck)
        self.setContentsMargins(0,0,0,0)
        self.stack_choice = None
        self.stack_index = 1  
        self.w = QWidget()
        geometry = QApplication.desktop().geometry()
        self.bg = QPixmap(Config.getInstance().get_background_config())
        self.bgPalette = QPalette()
        self.bgPalette.setBrush(QPalette.Background,QBrush(self.bg.scaled(geometry.width(), geometry.height())))
        self.w.setPalette(self.bgPalette)
        self.w.setAutoFillBackground(True)
        self.addWidget(self.w)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.create_playscene(windowSize))
        self.layout.addWidget(self.create_player_info())
        self.w.setLayout(self.layout)
        self.__isItTimeToSetBg.connect(self.setBg)

    def setBg(self):
        print(self.view.width(), self.view.height())
        self.playscene.setPGeometry(self.view.geometry())
        self.init_card_decks(CARD_DIMENSIONS)
        stack1, stack2, player, server = RandomCardGenerator(0).generate_stack_and_players_cards()
        self.initCards(server, player, [stack1, stack2])
    def create_playscene(self, WINDOW_SIZE):
        self.view = QGraphicsView()
        self.view.setContentsMargins(0,0,0,0)
        print(self.view.size())
        self.view.setAlignment(Qt.AlignAbsolute)
        geometry = QApplication.desktop().geometry()
        
        self.playscene = GamePlayScene(parent = self.view,pixmap=self.bg.scaled(geometry.width(), geometry.height()))
        self.view.setScene(self.playscene)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view.setStyleSheet("background-color: transparent;background: none; background-repeat: none;border: 0px;")
        self.playscene.setSceneRect(QRectF(0, 0, *PLAY_SCENE_SIZE))
        QTimer.singleShot(100, lambda: self.__isItTimeToSetBg.emit())
        return self.view
    
    def initCards(self,server, player, stacks):
        print("Im initiating own cards")
        self.init_hand_cards(server, CARD_DIMENSIONS)
        print("Im initiating enemy cards")
        self.init_opponent_cards(player, CARD_DIMENSIONS)
        print("Im initiating stack cards")
        self.init_card_stacks(stacks[0], stacks[1], CARD_DIMENSIONS)

        print("Opponents cards pos: ",[card1.pos() for card1 in self.opponent_cards])
        print("Opponents cards scene pos: ",[card1.scenePos() for card1 in self.opponent_cards])
        print("Opponents cards offset: ",[card1.offset() for card1 in self.opponent_cards])
        print("Stack no 1 pos: ", [card1.pos() for card1 in self.cardstacks[0].cards] )
        print("Stack no 1 scene pos: ", [card1.scenePos() for card1 in self.cardstacks[0].cards] )
        print("Stack no 1 offset: ", [card1.offset() for card1 in self.cardstacks[0].cards] )
        print("Stack no 2 pos: ", [card1.pos() for card1 in self.cardstacks[1].cards] )
        print("Stack no 2 scene pos: ", [card1.scenePos() for card1 in self.cardstacks[1].cards] )
        print("Stack no 2 offset: ", [card1.offset() for card1 in self.cardstacks[1].cards] )
        print("Player cards pos: ",[card1.pos() for card1 in self.hand_cards])
        print("Player cards scene pos: ",[card1.scenePos() for card1 in self.hand_cards])
        print("Player cards offset: ",[card1.offset() for card1 in self.hand_cards])
        self.computeForbiddenVal()
    def create_player_info(self):
        self.player_info_wg = PlayerInfoWidget()
        self.player_info_wg.setFixedWidth(200)
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignVCenter| Qt.AlignHCenter )
        vbox.setContentsMargins(-6,-6,-6,-6)
        vbox.setSpacing(50)
        self.scoreLabel = QLabel('Score:')
        font = QFont('KBREINDEERGAMES', 40)
        smallFont = QFont('KBREINDEERGAMES', 18)
        self.scoreLabel.setFont(font)
        conf = Config.getInstance().get_text_config()
        bg = Config.getInstance().get_shadow_config()
        
        self.scoreLabel.setStyleSheet(f'color:{conf};')
        vbox.addWidget(self.scoreLabel)

        self.score = QLineEdit()
        self.score.setFont(font)
        self.score.setStyleSheet("QLineEdit:!focus{ \
                                     border: 1px solid transparent;\
                                     background:  %s;\
                                     color: %s;\
                                 }\
                                 QLineEdit:focus{\
                                     background: %s;\
                                     color: %s;}"%(bg,conf,bg,conf))
        self.score.setText(self.scoreString.__str__())
        self.score.setReadOnly(True)
        vbox.addWidget(self.score)
        dec_val = QLabel('Your declared value:')
        dec_val.setWordWrap(True)
        dec_val.setStyleSheet(f'color:{conf};')
        dec_val.setFont(smallFont)
        vbox.addWidget(dec_val)
        self.declared = QLineEdit()
        self.declared.setReadOnly(True)
        self.declared.setFont(font)
        self.declared.setText("0")
        self.declared.setStyleSheet("QLineEdit:!focus{ border: 1px solid transparent;background: %s;color: %s;} QLineEdit:focus{background: %s;color: %s;}"%(bg,conf,bg,conf))
        vbox.addWidget(self.declared)

        # tutaj coś pokombinować
        label = QLabel('Current reported suit:')
        label.setFont(smallFont)
        label.setWordWrap(True)
        label.setStyleSheet(f'color:{conf};')
        vbox.addWidget(label)
        self.frame = QFrame()
        self.frame.setFixedSize(QSize(50,50))
        self.reported = Suit(self.frame,'')
        self.updateTrump.connect(self.reported.changeSuit)
        vbox.addWidget(self.reported)
        
        self.player_info_wg.setLayout(vbox)
        return self.player_info_wg
    def setDeclaredValue(self, val):
        self.declared.setText(str(val))
    def setScore(self, player):
        self.score.setText(self.calculate_score().__str__())

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
            card.turn_back_up()
            self.opponent_cards.append(card)
            card.setOffset(x_temp, y_temp)
            card.rotate180H()
            card.location = "OPPONENT_HAND"
            self.playscene.addItem(card)
            x_temp += CARD_DIMENSIONS.width() + spacing_x
            card.signals.clicked.connect(lambda card=card: self.change_card_location(card))
    def init_hand_cards(self, cards, CARD_DIMENSIONS):
        y_temp = self.playscene.height() - CARD_DIMENSIONS.height()
        spacing_x = self.playscene.width() / len(cards) - CARD_DIMENSIONS.width()
        x_temp = spacing_x / 2
        for i, card in enumerate(cards):
            card.turn_face_up()
            card.setOffset(x_temp, y_temp)
            card.location = "HAND"
            self.hand_cards.append(card)
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
    def on_stackAccepted(self, index):
        stack = self.cardstacks[index-1]
        
        StatusGame.getInstance().set_status_name("VALUE_DECLARATION")
    def init_card_stacks(self, cards1, cards2, CARD_DIMENSIONS): 
        print("Im initiating stacks at the moment")#cards to tupla
        self.cardstacks = []
        x = self.playscene.width() * 2 / 3
        y = self.playscene.height() / 2 - CARD_DIMENSIONS.height() / 2
        for i in range(2, 0, -1):
            print("Im initiating single stack at the moment")
            cardstack = CardStack(i)  # 1 - 1, 2 - 2
            cardstack.signals.stackAccepted.connect(self.on_stackAccepted)
            cardstack.signals.clicked.connect(lambda cardstack=cardstack: self.set_stack_choice(cardstack))
            cardstack.setPos(QPoint(x, y))
            x = self.playscene.width() / 8
            self.cardstacks.append(cardstack)
            self.playscene.addItem(cardstack)

        for i, card in enumerate(cards1):
            card.signals.clicked.connect(lambda cardID=i: self.cardstacks[0].onCardToExchange(cardID))
            card.turn_back_up()
            card.location="HAND_STACK"
            self.playscene.addItem(card)
        for i, card in enumerate(cards2):
            card.location="HAND_STACK"
            card.signals.clicked.connect(lambda cardID=i:  self.cardstacks[1].onCardToExchange(cardID))
            card.turn_back_up()
            self.playscene.addItem(card)
        self.cardstacks.reverse()
        self.cardstacks[0].addCards(cards1)
        self.cardstacks[1].addCards(cards2)

    def add_to_left(self):
        for carddeck in self.carddecks:
            card = carddeck.remove_card()
            self.playscene.removeItem(card)
            card.location = "PLAYED_LEFT"
            self.add_card_to_left(card)

    def drop_card_from_opponent_hand(self, card):
        # print("dropping card")
        # print("Opponents cards pos: ",[card1.pos() for card1 in self.opponent_cards])
        # print("Opponents cards scene pos: ",[card1.scenePos() for card1 in self.opponent_cards])
        # print("Opponents cards offset: ",[card1.offset() for card1 in self.opponent_cards])
        # print("Stack no 1 pos: ", [card1.pos() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 1 scene pos: ", [card1.scenePos() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 1 offset: ", [card1.offset() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 2 pos: ", [card1.pos() for card1 in self.cardstacks[1].cards] )
        # print("Stack no 2 scene pos: ", [card1.scenePos() for card1 in self.cardstacks[1].cards] )
        # print("Stack no 2 offset: ", [card1.offset() for card1 in self.cardstacks[1].cards] )
        # print("Player cards pos: ",[card1.pos() for card1 in self.hand_cards])
        # print("Player cards scene pos: ",[card1.scenePos() for card1 in self.hand_cards])
        # print("Player cards offset: ",[card1.offset() for card1 in self.hand_cards])
        
        if self.carddecks[1].card is None:
            card_to_remove = None
            print(card, self.opponent_cards)
            for c in self.opponent_cards:
                if c == card:
                    card_to_remove = c
            print("to remove ", card_to_remove)
            self.remove_card_from_opponent_hand(card_to_remove)
            anime = QVariantAnimation(self)
            card_to_remove.rotate180H()
            card_to_remove.turn_face_up()
            anime.valueChanged.connect(card_to_remove.setOffset)
            anime.setDuration(500)
            anime.setStartValue(card_to_remove.offset())
            anime.setEndValue(self.carddecks[1].pos())
            anime.start()
            card_to_remove.turn_face_up()
            self.carddecks[1].add_card(card_to_remove)
        if self.carddecks[0].card is not None:
            who = ""
            if self.carddecks[0].card > self.carddecks[1].card or (self.carddecks[0].card.suit != self.carddecks[1].card.suit and self.carddecks[1].card.suit != self.reported.get_suit()):
                who = "SERVER"
            else:
                who = "PEER"
            QTimer.singleShot(1500,lambda person = who :self.collectFromDeck(person))
        elif (self.carddecks[0].card is None):
            StatusGame.getInstance().set_status_name('YOUR_MOVE')
            
        print("opponent cards size: ", len(self.opponent_cards))
    def change_opponent_cards_with_stack(self, tup, index):
        print("changing stack")
        # print("Opponents cards pos: ",[card1.pos() for card1 in self.opponent_cards])
        # print("Opponents cards scene pos: ",[card1.scenePos() for card1 in self.opponent_cards])
        # print("Opponents cards offset: ",[card1.offset() for card1 in self.opponent_cards])
        # print("Stack no 1 pos: ", [card1.pos() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 1 scene pos: ", [card1.scenePos() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 1 offset: ", [card1.offset() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 2 pos: ", [card1.pos() for card1 in self.cardstacks[1].cards] )
        # print("Stack no 2 scene pos: ", [card1.scenePos() for card1 in self.cardstacks[1].cards] )
        # print("Stack no 2 offset: ", [card1.offset() for card1 in self.cardstacks[1].cards] )
        # print("Player cards pos: ",[card1.pos() for card1 in self.hand_cards])
        # print("Player cards scene pos: ",[card1.scenePos() for card1 in self.hand_cards])
        # print("Player cards offset: ",[card1.offset() for card1 in self.hand_cards])
        
        list_ = [Card(*c) for c in tup]
        val = False
        stack = self.cardstacks[index].cards
        if (list_[0] == stack[0] and list_[1] == stack[1]) or (list_[0] == stack[1] and list_[1] == stack[0]):
            return
        stack_cards = []
        cards = []
        if list_[0] == stack[0] or list_[0] == stack[1]:
            miss_card = None
            for stack_card in stack:
                if stack_card != list_[0]:
                    miss_card = stack_card
                    break
            for c in self.opponent_cards:
                if c == list_[1]:
                    cards.append(c)
                    break
            stack_cards.append(miss_card)
        elif list_[1] == stack[0] or list_[1] == stack[1]:
            miss_card = None
            for stack_card in stack:
                if stack_card != list_[1]:
                    miss_card = stack_card
                    break
            for c in self.opponent_cards:
                if c == list_[0]:
                    cards.append(c)
                    break
            stack_cards.append(miss_card)            
        else:
            for idx, c1 in enumerate(list_):
                miss_card = None
                stack_card = stack[idx]
                if stack_card != c1:
                    miss_card = stack_card
                for c in self.opponent_cards:
                    if c == c1:
                        cards.append(c)
                        break
                stack_cards.append(miss_card)            
        print("cards to move", cards)
        print("stack-cards to move", stack_cards)
        for idx, c2 in enumerate(cards):
            stack_card = stack_cards[idx]
            anime1 = QVariantAnimation(self)
            anime2 = QVariantAnimation(self)
            self.remove_card_from_opponent_hand(c2)

            self.cardstacks[index].remove_card(stack_card, "HAND_STACK")
            temp_pos_stack = stack_card.offset()
            temp_pos_card = c2.offset()

            anime1.valueChanged.connect(stack_card.setOffset)
            anime1.setDuration(500)
            anime1.setStartValue(stack_card.offset())
            anime1.setEndValue(temp_pos_card)
            stack_card.rotate180H()
            anime1.start()

            self.add_card_to_opponent_hand(stack_card)

            anime2.valueChanged.connect(c2.setOffset)
            anime2.setDuration(500)
            anime2.setStartValue(c2.offset())
            anime2.setEndValue(temp_pos_stack)
            anime2.start()

            self.cardstacks[index].add_card(c2)
    def change_card_location(self, card):
        print("Im here")
        if (card.location == "HAND" ) and StatusGame.getInstance().get_status_name() == "YOUR_MOVE":
            self.drop_card_from_hand(card)
        elif card.location == "HAND" and StatusGame.getInstance().get_status_name() == "STACK_CARD_TAKING":
            self.change_card_with_stack(card)
        elif card.location == "OPPONENT_HAND" and StatusGame.getInstance().get_status_name() == "OPPONENT_MOVE":
            self.drop_card_from_opponent_hand(card)
    def isSuitPresent(self, suit):
        val = False
        for card in self.hand_cards:
            if card.suit == suit:
                val = True
                break
        return val
    def isGreaterPresent(self, card1):
        val = False
        for card in self.hand_cards:
            if card > card1:
                val = True
                break
        return val
    def isTrumpPresent(self):
        val = False
        suit = self.reported.get_suit()
        for card in self.hand_cards:
            if card.suit == suit:
                val = True
                break
        return val
    def on_trumpChanged(self, trump):
        self.__currentTrump = trump
        self.updateTrump.emit(self.__currentTrump)
    def drop_card_from_hand(self, card):
        # print("Opponents cards pos: ",[card1.pos() for card1 in self.opponent_cards])
        # print("Opponents cards scene pos: ",[card1.scenePos() for card1 in self.opponent_cards])
        # print("Opponents cards offset: ",[card1.offset() for card1 in self.opponent_cards])
        # print("Stack no 1 pos: ", [card1.pos() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 1 scene pos: ", [card1.scenePos() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 1 offset: ", [card1.offset() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 2 pos: ", [card1.pos() for card1 in self.cardstacks[1].cards] )
        # print("Stack no 2 scene pos: ", [card1.scenePos() for card1 in self.cardstacks[1].cards] )
        # print("Stack no 2 offset: ", [card1.offset() for card1 in self.cardstacks[1].cards] )
        # print("Player cards pos: ",[card1.pos() for card1 in self.hand_cards])
        # print("Player cards scene pos: ",[card1.scenePos() for card1 in self.hand_cards])
        # print("Player cards offset: ",[card1.offset() for card1 in self.hand_cards])
        if self.carddecks[1].card is not None:
            suit = self.carddecks[1].card.suit
            if self.isSuitPresent(suit) == True:
                print("We have such suit in hand")
                if card.suit != suit or (card > self.carddecks[1].card and self.isGreaterPresent(card) == True):
                    return
            else:
                if(self.isTrumpPresent() and card.suit != self.reported.get_suit()):
                    return
                    
        if self.carddecks[0].card is None:
            print("Checking if new card is trump")
            StatusGame.getInstance().set_status_name("OPPONENT_MOVE")
            self.remove_card_from_hand(card)
            if self.carddecks[1].card is None:
                print("Checking if new card is trump")
                print("size of hand_cards: " + len(self.hand_cards).__str__())
                print(card,self.hand_cards)
                for c in self.hand_cards:
                    print(card.isPair(c))
                    if card.isPair(c):
                        print(self.reportedValues)
                        self.reportedValues.append(BIDDING[card.suit])
                        self.on_trumpChanged(card.suit)
                        
                        break
            anime = QVariantAnimation(self)
            anime.valueChanged.connect(card.setOffset)
            anime.setDuration(500)
            anime.setStartValue(card.offset())
            anime.setEndValue(self.carddecks[0].pos())
            anime.start()
            self.carddecks[0].add_card(card)
            if self.carddecks[1].card is not None:
                who = ""
                if self.carddecks[1].card < self.carddecks[0].card or (self.carddecks[0].card.suit != self.carddecks[1].card.suit and self.carddecks[0].card.suit == self.reported.get_suit()):
                    who = "SERVER"
                else:
                    who = "PEER"
                QTimer.singleShot(1500,lambda person = who :self.collectFromDeck(person))
                
        print("cards size: ", len(self.hand_cards))
    def add_to_opponent_left(self):
        for carddeck in self.carddecks:
            card = carddeck.remove_card()
            self.playscene.removeItem(card)
            card.location = "PLAYED_LEFT"
            self.add_card_to_opponent_left(card)
    def change_card_with_stack(self, card):
        # print("Opponents cards pos: ",[card1.pos() for card1 in self.opponent_cards])
        # print("Opponents cards scene pos: ",[card1.scenePos() for card1 in self.opponent_cards])
        # print("Opponents cards offset: ",[card1.offset() for card1 in self.opponent_cards])
        # print("Stack no 1 pos: ", [card1.pos() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 1 scene pos: ", [card1.scenePos() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 1 offset: ", [card1.offset() for card1 in self.cardstacks[0].cards] )
        # print("Stack no 2 pos: ", [card1.pos() for card1 in self.cardstacks[1].cards] )
        # print("Stack no 2 scene pos: ", [card1.scenePos() for card1 in self.cardstacks[1].cards] )
        # print("Stack no 2 offset: ", [card1.offset() for card1 in self.cardstacks[1].cards] )
        # print("Player cards pos: ",[card1.pos() for card1 in self.hand_cards])
        # print("Player cards scene pos: ",[card1.scenePos() for card1 in self.hand_cards])
        # print("Player cards offset: ",[card1.offset() for card1 in self.hand_cards])
        if(self.stack_choice < 0 or self.cardstacks[self.stack_choice].current_selection  < 0 ):
            return
        anime1 = QVariantAnimation(self)
        anime2 = QVariantAnimation(self)
        self.remove_card_from_hand(card)

        stack_card = self.cardstacks[self.stack_choice].get_one_card()
        self.cardstacks[self.stack_choice].remove_card(stack_card, "HAND")
        temp_pos_stack = stack_card.offset()
        temp_pos_card = card.offset()

        anime1.valueChanged.connect(stack_card.setOffset)
        anime1.setDuration(500)
        anime1.setStartValue(stack_card.offset())
        anime1.setEndValue(temp_pos_card)
        anime1.start()

        self.add_card_to_hand(stack_card)

        anime2.valueChanged.connect(card.setOffset)
        anime2.setDuration(500)
        anime2.setStartValue(card.offset())
        anime2.setEndValue(temp_pos_stack)
        anime2.start()
        card.location = "HAND_STACK"
        self.cardstacks[self.stack_choice].add_card(card)
    def collectFromDeck(self, who):
        
        if(who == "SERVER" ):
            self.add_to_left()
            if(len(self.hand_cards) > 0):
                StatusGame.getInstance().set_status_name("YOUR_MOVE")
            else:

                StatusGame.getInstance().set_status_name("SCORING")
        else:
            self.add_to_opponent_left()
            if(len(self.hand_cards) > 0):    
                StatusGame.getInstance().set_status_name("OPPONENT_MOVE")
            else:
                StatusGame.getInstance().set_status_name("SCORING")