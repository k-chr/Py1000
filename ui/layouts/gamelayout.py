import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# from card import *
from ui.dialogs.biddialog import BidDialog
from config import Config
from PyQt5.QtMultimedia import QSound, QSoundEffect
PLAY_SCENE_SIZE = 1200, 900


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
class GameLayout(QHBoxLayout):
    __isItTimeToSetBg = pyqtSignal()
   
    def __init__(self, player, windowSize=None, parent=None):
        super(GameLayout, self).__init__(parent)
        self.setAlignment(Qt.AlignAbsolute)
        self.player = player
        self.playscene = None
        self.view = None
        self.opponentLabel = None
        self.opponentScore = None
        self.player_info_wg = None
        self.scoreLabel = None
        self.score = None
        self.reported = None
        self.frame = None
        self.declared = None
        self.player.opponentScore.connect(self.on_opponentScore)
        self.player.cardsToHandInReady.connect(self.initCards)
        self.player.updateDeclaredValue.connect(self.setDeclaredValue)
        self.player.updateScore.connect(self.on_updateScore)
        self.player.move_card.connect(self.drop_card_from_opponent_hand)
        self.player.move_stack.connect(self.change_opponent_cards_with_stack)
        self.player.updateDeck.connect(self.collectFromDeck)
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
        self.layout.addWidget(self.create_player_info(player))
        self.w.setLayout(self.layout)
        self.__isItTimeToSetBg.connect(self.setBg)

    def setBg(self):
        print(self.view.width(), self.view.height())
        self.playscene.setPGeometry(self.view.geometry())
        # self.init_card_decks(CARD_DIMENSIONS)

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

    def on_opponentScore(self,score):
        self.opponentScore.setText(score.__str__())

    def on_updateScore(self, score):
        self.score.setText(score.__str__())

    def initCards(self,server, player, stacks):
        print("Im initiating own cards")
        # self.init_hand_cards(server, CARD_DIMENSIONS)
        # print("Im initiating enemy cards")
        # self.init_opponent_cards(player, CARD_DIMENSIONS)
        # print("Im initiating stack cards")
        # self.init_card_stacks(stacks[0], stacks[1], CARD_DIMENSIONS)
        print(self.player.is_HOST == False and self.player.is_FirstPlayer == False)
        print(self.player.is_HOST and self.player.value_rand != 0)
        # if((self.player.is_HOST == False and self.player.is_FirstPlayer == False) or (self.player.is_HOST and self.player.value_rand != 0)):
        #     StatusGame.getInstance().set_status_name("VALUE_DECLARATION")
        # else:
        #     StatusGame.getInstance().set_status_name("OPPONENT_MOVE")
        
    def create_player_info(self, player):
        self.player_info_wg = PlayerInfoWidget()
        self.player_info_wg.setFixedWidth(200)
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignVCenter| Qt.AlignHCenter )
        vbox.setContentsMargins(-6,-6,-6,-6)
        vbox.setSpacing(50)
        self.scoreLabel = QLabel('Score:')
        self.opponentLabel = QLabel('Opponent score: ')
        self.opponentLabel.setWordWrap(True)
        font = QFont('KBREINDEERGAMES', 40)
        smallFont = QFont('KBREINDEERGAMES', 18)
        self.scoreLabel.setFont(font)
        self.opponentLabel.setFont(smallFont)
        conf = Config.getInstance().get_text_config()
        bg = Config.getInstance().get_shadow_config()
        
        self.scoreLabel.setStyleSheet(f'color:{conf};')
        self.opponentLabel.setStyleSheet(f'color:{conf};')
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
        self.score.setText(player.score.__str__())
        self.score.setReadOnly(True)
        vbox.addWidget(self.score)
        vbox.addWidget(self.opponentLabel)
        self.opponentScore = QLineEdit()
        self.opponentScore.setFont(font)
        self.opponentScore.setStyleSheet("QLineEdit:!focus{ \
                                     border: 1px solid transparent;\
                                     background:  %s;\
                                     color: %s;\
                                 }\
                                 QLineEdit:focus{\
                                     background: %s;\
                                     color: %s;}"%(bg,conf,bg,conf))
        self.opponentScore.setText(player.score.__str__())
        self.opponentScore.setReadOnly(True)
        vbox.addWidget(self.opponentScore)
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
        # self.reported = Suit(self.frame,'')
        self.player.updateTrump.connect(self.reported.changeSuit)
        vbox.addWidget(self.reported)
        
        self.player_info_wg.setLayout(vbox)
        return self.player_info_wg

    def setDeclaredValue(self, val):
        self.declared.setText(str(val))

    def setScore(self, player):
        self.score.setText(player.calculate_score().__str__())

    def set_stack_choice(self, cardstack):
        pass
        # if StatusGame.getInstance().get_status_name() == "STACK_CHOOSING":
        #     self.stack_choice = cardstack.number - 1
        #     self.cardstacks[self.stack_choice].showCards()
        #     StatusGame.getInstance().set_status_name("STACK_CARD_TAKING")

    def init_opponent_cards(self, cards, CARD_DIMENSIONS):
        y_temp = 0
        spacing_x = self.playscene.width() / len(cards) - CARD_DIMENSIONS.width()
        x_temp = spacing_x / 2
        for i, card in enumerate(cards):
            card.setOffset(x_temp, y_temp)
            card.rotate180H()
            card.turn_back_up()
            card.location = "HAND"
            self.playscene.addItem(card)
            x_temp += CARD_DIMENSIONS.width() + spacing_x

    def init_hand_cards(self, cards, CARD_DIMENSIONS):
        y_temp = self.playscene.height() - CARD_DIMENSIONS.height()
        spacing_x = self.playscene.width() / len(cards) - CARD_DIMENSIONS.width()
        x_temp = spacing_x / 2
        for i, card in enumerate(cards):
            card.turn_face_up()
            card.setOffset(x_temp, y_temp)
            card.location = "HAND"
            self.playscene.addItem(card)
            x_temp += CARD_DIMENSIONS.width() + spacing_x
            card.signals.clicked.connect(lambda card=card: self.change_card_location(card))

    def init_card_decks(self, CARD_DIMENSIONS):
        self.carddecks = []  # 0 - my carddeck, 1 - player cardeck
        x = self.playscene.width() / 2 - CARD_DIMENSIONS.width() / 2
        y = self.playscene.height() / 2
        for i in range(0, 2):
            # carddeck = CardDeck()
            # carddeck.setPos(x, y)
            y -= CARD_DIMENSIONS.height() + 2
            # self.carddecks.append(carddeck)
            # self.playscene.addItem(carddeck)
    def on_stackAccepted(self, index):
        stack = self.cardstacks[index-1]
        if(self.player.is_HOST == True):
            msg = self.player.get_server().prepareServerMessage("STACK_CHANGED", STACK_INDEX=0 if index == 2 else 1, CARDS=[card.getTuple() for card in stack.cards])
            self.player.get_server().sendCmd(msg)
        else:
            msg = self.player.get_client().prepareClientMessage("STACK_CHANGED", STACK_INDEX=0 if index == 2 else 1, CARDS=[card.getTuple() for card in stack.cards])
            self.player.get_client().sendCmd(msg)
        # StatusGame.getInstance().set_status_name("VALUE_DECLARATION")

    def init_card_stacks(self, cards1, cards2, CARD_DIMENSIONS): 
        print("Im initiating stacks at the moment")#cards to tupla
        self.cardstacks = []
        x = self.playscene.width() * 2 / 3
        y = self.playscene.height() / 2 - CARD_DIMENSIONS.height() / 2
        for i in range(2, 0, -1):
            print("Im initiating single stack at the moment")
            # cardstack = CardStack(i)  # 1 - 1, 2 - 2
            # cardstack.signals.stackAccepted.connect(self.on_stackAccepted)
            # cardstack.signals.clicked.connect(lambda cardstack=cardstack: self.set_stack_choice(cardstack))
            # cardstack.setPos(QPoint(x, y))
            x = self.playscene.width() / 8
            # self.cardstacks.append(cardstack)
            # self.playscene.addItem(cardstack)
        self.cardstacks[0].addCards(cards1)
        self.cardstacks[1].addCards(cards2)
        for i, card in enumerate(cards1):
            card.signals.clicked.connect(lambda cardID=i: self.cardstacks[1].onCardToExchange(cardID))
            card.turn_back_up()
            card.location="HAND_STACK"
            self.playscene.addItem(card)
        for i, card in enumerate(cards2):
            card.location="HAND_STACK"
            card.signals.clicked.connect(lambda cardID=i:  self.cardstacks[0].onCardToExchange(cardID))
            card.turn_back_up()
            self.playscene.addItem(card)
        self.cardstacks.reverse()

    def add_to_left(self):
        for carddeck in self.carddecks:
            card = carddeck.remove_card()
            self.playscene.removeItem(card)
            card.location = "PLAYED_LEFT"
            self.player.add_card_to_left(card)

    def drop_card_from_opponent_hand(self, card):
        print("dropping card")
        
        # card1 = Card(*card)
        if self.carddecks[1].card is None:
            card_to_remove = None
            for c in self.player.opponent_cards:
                # if c == card1:
                    card_to_remove = c
            # playRandomCardSound(self)
            print("to remove ", card_to_remove)
            card_to_remove.setZValue(1)
            self.player.remove_card_from_opponent_hand(card_to_remove)
            anime = QVariantAnimation(self)
            anime.valueChanged.connect(card_to_remove.setOffset)
            anime.setDuration(500)
            
            anime.setStartValue(card_to_remove.offset())
            anime.setEndValue(self.carddecks[1].pos())
            anime.start()
            card_to_remove.turn_face_up()
            self.carddecks[1].add_card(card_to_remove)
        if self.carddecks[0].card is not None and self.player.is_HOST == True:
            who = ""
            if self.carddecks[0].card > self.carddecks[1].card or (self.carddecks[0].card.suit != self.carddecks[1].card.suit and self.carddecks[1].card.suit != self.reported.get_suit()):
                who = "SERVER"
            else:
                who = "PEER"
            self.collectFromDeck(who)
            d = self.player.get_server().prepareServerMessage("WHO_TAKES", WHO=who)
            self.player.get_server().sendCmd(d)
        elif (self.carddecks[0].card is None):
            # StatusGame.getInstance().set_status_name('YOUR_MOVE')
            pass
            
        print("opponent cards size: ", len(self.player.opponent_cards))

    def change_opponent_cards_with_stack(self, tup, index):
        print("changing stack")
        
        # list_ = [Card(*c) for c in tup]
        val = False
        stack = self.cardstacks[index].cards
        # if (list_[0] == stack[0] and list_[1] == stack[1]) or (list_[0] == stack[1] and list_[1] == stack[0]):
            # return
        stack_cards = []
        cards = []
        # if list_[0] == stack[0] or list_[0] == stack[1]:
        #     miss_card = None
        #     for stack_card in stack:
        #         if stack_card != list_[0]:
        #             miss_card = stack_card
        #             break
        #     for c in self.player.opponent_cards:
        #         if c == list_[1]:
        #             cards.append(c)
        #             break
        #     stack_cards.append(miss_card)
        # elif list_[1] == stack[0] or list_[1] == stack[1]:
        #     miss_card = None
        #     for stack_card in stack:
        #         if stack_card != list_[1]:
        #             miss_card = stack_card
        #             break
        #     for c in self.player.opponent_cards:
        #         if c == list_[0]:
        #             cards.append(c)
        #             break
        #     stack_cards.append(miss_card)            
        # else:
        #     for idx, c1 in enumerate(list_):
        #         miss_card = None
        #         stack_card = stack[idx]
        #         if stack_card != c1:
        #             miss_card = stack_card
        #         for c in self.player.opponent_cards:
        #             if c == c1:
        #                 cards.append(c)
        #                 break
        #         stack_cards.append(miss_card)            
        # print("cards to move", cards)
        # print("stack-cards to move", stack_cards)
        # for idx, c2 in enumerate(cards):
        #     stack_card = stack_cards[idx]
        #     anime1 = QVariantAnimation(self)
        #     anime2 = QVariantAnimation(self)
        #     self.player.remove_card_from_opponent_hand(c2)
        #     c2.setZValue(1)
        #     self.cardstacks[index].remove_card(stack_card, "HAND_STACK")
        #     temp_pos_stack = stack_card.offset()
        #     temp_pos_card = c2.offset()
        #     c2.rotate180H()
        #     c2.turn_back_up()
        #     anime1.valueChanged.connect(stack_card.setOffset)
        #     anime1.setDuration(500)
        #     playRandomCardSound(self)
        #     anime1.setStartValue(stack_card.offset())
        #     anime1.setEndValue(temp_pos_card)
        #     stack_card.rotate180H()
        #     stack_card.turn_back_up()
        #     anime1.start()

        #     self.player.add_card_to_opponent_hand(stack_card)
        #     stack_card.setZValue(1)
        #     anime2.valueChanged.connect(c2.setOffset)
        #     anime2.setDuration(500)
        #     playRandomCardSound(self)
        #     anime2.setStartValue(c2.offset())
        #     anime2.setEndValue(temp_pos_stack)
        #     anime2.start()

        #     self.cardstacks[index].add_card(c2)
    def change_card_location(self, card):
        print("Im here")
        # if (card.location == "HAND" ) and StatusGame.getInstance().get_status_name() == "YOUR_MOVE":
        #     self.drop_card_from_hand(card)
        # elif card.location == "HAND" and StatusGame.getInstance().get_status_name() == "STACK_CARD_TAKING":
        #     self.change_card_with_stack(card)

    def isSuitPresent(self, suit):
        val = False
        for card in self.player.hand_cards:
            if card.suit == suit:
                val = True
                break
        return val

    def isGreaterPresent(self, card1):
        val = False
        for card in self.player.hand_cards:
            if card > card1:
                val = True
                break
        return val

    def isTrumpPresent(self):
        val = False
        suit = self.reported.get_suit()
        for card in self.player.hand_cards:
            if card.suit == suit:
                val = True
                break
        return val

    def drop_card_from_hand(self, card):
    
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
            # StatusGame.getInstance().set_status_name("OPPONENT_MOVE")
            self.player.remove_card_from_hand(card)
            IS_TRUMP = False
            if self.carddecks[1].card is None:
                for c in self.player.hand_cards:
                    if card.isPair(c):
                        IS_TRUMP = True
                        # self.player.reportedSuits.append(BIDDING[card.suit])
                        self.player.on_trumpChanged(card.suit)
                        break
            if self.player.is_HOST == True:
                if IS_TRUMP:
                    msg_dict = self.player.get_server().prepareServerMessage("MULTI_EVENT", FIRST='TRUMP_CHANGED',SECOND='CARD_PLAYED', FIRST_ARG=card.suit, SECOND_ARG=card.getTuple())
                    self.player.get_server().sendCmd(msg_dict)
                else:
                    msg_dict = self.player.get_server().prepareServerMessage("CARD_PLAYED", CARD=card.getTuple())
                    self.player.get_server().sendCmd(msg_dict)
            else:
                if IS_TRUMP:
                    msg_dict = self.player.get_client().prepareClientMessage("MULTI_EVENT", FIRST='TRUMP_CHANGED',SECOND='CARD_PLAYED', FIRST_ARG=card.suit, SECOND_ARG=card.getTuple())
                    self.player.get_client().sendCmd(msg_dict)
                else:
                    msg_dict = self.player.get_client().prepareClientMessage("CARD_PLAYED", CARD=card.getTuple())
                    self.player.get_client().sendCmd(msg_dict)
            card.setZValue(1)
            anime = QVariantAnimation(self)
            anime.valueChanged.connect(card.setOffset)
            anime.setDuration(500)
            
            # playRandomCardSound(self)
            anime.setStartValue(card.offset())
            anime.setEndValue(self.carddecks[0].pos())
            anime.start()
            self.carddecks[0].add_card(card)
            if self.carddecks[1].card is not None and self.player.is_HOST == True:
                who = ""
                if self.carddecks[1].card < self.carddecks[0].card or (self.carddecks[0].card.suit != self.carddecks[1].card.suit and self.carddecks[0].card.suit == self.reported.get_suit()):
                    who = "SERVER"
                else:
                    who = "PEER"
                self.collectFromDeck(who)
                d = self.player.get_server().prepareServerMessage("WHO_TAKES", WHO=who)
                QTimer.singleShot(1000,lambda dic = d:self.player.get_server().sendCmd(dic))
                
        print("cards size: ", len(self.player.hand_cards))
    def change_card_with_stack(self, card):
        print(self.stack_choice, self.cardstacks[self.stack_choice], self.cardstacks[self.stack_choice].current_selection, self.cardstacks[0].current_selection)
        if(self.stack_choice < 0 or self.cardstacks[self.stack_choice].current_selection  < 0 ):
            return
        anime1 = QVariantAnimation(self)
        anime2 = QVariantAnimation(self)
        self.player.remove_card_from_hand(card)
        card.setZValue(1)
        stack_card = self.cardstacks[self.stack_choice].get_one_card()
        self.cardstacks[self.stack_choice].remove_card_in_situ(stack_card, "HAND")
        temp_pos_stack = stack_card.offset()
        temp_pos_card = card.offset()

        anime1.valueChanged.connect(stack_card.setOffset)
        anime1.setDuration(500)
        # playRandomCardSound(self)
        anime1.setStartValue(stack_card.offset())
        anime1.setEndValue(temp_pos_card)
        anime1.start()
        stack_card.setZValue(1)
        self.player.add_card_to_hand(stack_card)
        stack_card.signals.clicked.disconnect()
        stack_card.signals.clicked.connect(lambda card=stack_card: self.change_card_location(card))
        anime2.valueChanged.connect(card.setOffset)
        anime2.setDuration(500)
        # playRandomCardSound(self)
        anime2.setStartValue(card.offset())
        anime2.setEndValue(temp_pos_stack)
        anime2.start()
        card.location = "HAND_STACK"
        self.cardstacks[self.stack_choice].exchange_card(card)
    def add_to_opponent_left(self):
        for carddeck in self.carddecks:
            card = carddeck.remove_card()
            self.playscene.removeItem(card)
            card.location = "PLAYED_LEFT"
            self.player.add_card_to_opponent_left(card)

    def collectFromDeck(self, who):
        def wrapper(who):
            if(who == "SERVER" and self.player.is_HOST == True) or (who == "PEER" and self.player.is_HOST == False ):
                self.add_to_left()
                if(len(self.player.hand_cards) > 0):
                    # StatusGame.getInstance().set_status_name("YOUR_MOVE")
                    pass
                else:
                    if((self.player.is_main_player == True and len(self.player.played_left) == 20) or (self.player.is_main_player == False and len(self.player.played_left)>0)):
                        for c  in self.cardstacks[0].cards:
                            self.player.add_card_to_left(c)
                            self.playscene.removeItem(c)
                        for c  in self.cardstacks[1].cards:
                            self.player.add_card_to_left(c)
                            self.playscene.removeItem(c)
                        for stack in self.cardstacks:
                            stack.removeCards()
                    else:
                        for c  in self.cardstacks[0].cards:
                            self.player.add_card_to_opponent_left(c)
                            self.playscene.removeItem(c)
                        for c  in self.cardstacks[1].cards:
                            self.player.add_card_to_opponent_left(c)
                            self.playscene.removeItem(c)
                        for stack in self.cardstacks:
                            stack.removeCards()   
                    # StatusGame.getInstance().set_status_name("SCORING")
                    self.reported.changeSuit('')
                    self.declared.setText("0")
            else:
                self.add_to_opponent_left()
                if(len(self.player.hand_cards) > 0):    
                    # StatusGame.getInstance().set_status_name("OPPONENT_MOVE")
                    pass
                else:
                    if((self.player.is_main_player == True and len(self.player.played_left) == 20) or (self.player.is_main_player == False and len(self.player.played_left)>0)):
                        for c  in self.cardstacks[0].cards:
                            self.player.add_card_to_left(c)
                            self.playscene.removeItem(c)
                        for c  in self.cardstacks[1].cards:
                            self.player.add_card_to_left(c)
                            self.playscene.removeItem(c)
                        for stack in self.cardstacks:
                            stack.removeCards()
                    else:
                        for c  in self.cardstacks[0].cards:
                            self.player.add_card_to_opponent_left(c)
                            self.playscene.removeItem(c)
                        for c  in self.cardstacks[1].cards:
                            self.player.add_card_to_opponent_left(c)
                            self.playscene.removeItem(c)
                        for stack in self.cardstacks:
                            stack.removeCards()  
                    # StatusGame.getInstance().set_status_name("SCORING")
                    self.reported.changeSuit('')
                    self.declared.setText("0")
            if(self.player.is_HOST == False):
                self.player.cardsFromDeckTaken.emit()
            else:
                # self.player.prevStat = StatusGame.getInstance().get_status_name()
                # StatusGame.getInstance().set_status_name("PEER_DECK_CLEANING")
                pass
        QTimer.singleShot(1500, lambda someone=who:wrapper(someone))