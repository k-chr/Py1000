
MAX_VALUE = 1000
from net.server import *
from threading import *
from time import sleep
from statusgame import StatusGame
from ui.dialogs.networkdialog import NetworkDialog
from ui.dialogs.farewelldialog import FarewellDialog
from peer import Peer
from ui.dialogs.biddialog import BidDialog
from PyQt5.QtCore import QObject, pyqtSignal
# from randomcardgenerator import RandomCardGenerator
RULE = 900
class Player(QObject):
    __server = None
    __client = None
    winnerSignal = pyqtSignal(str)
    opponentScore = pyqtSignal(int)
    updateScore = pyqtSignal(int)
    cardsFromDeckTaken = pyqtSignal()
    cardsToHandInReady = pyqtSignal(list,list,tuple)
    updateDeclaredValue = pyqtSignal(int)
    updateTrump = pyqtSignal(str)
    move_card = pyqtSignal(tuple)
    move_stack = pyqtSignal(list,int)
    updateDeck = pyqtSignal(str)
    currentBid = 0
    forbidden = 130
    def __init__(self):
        super(Player, self).__init__()
        self.bidding_initiator = False
        self.hand_cards = []
        self.score = 900
        self.prevStat = ""
        self.declared_value = 100
        self.is_main_player = False
        self.is_FirstPlayer = False
        self.reportedSuits = []
        self.__currentTrump = ""
        self.opponent_cards = []
        self.opponent_left = []
        self.signalsNotConnected = True
        self.clientSignalsNotConnected = True
        self.played_left = [] #cards gained during play time
        self.is_HOST = False
        self.cardsFromDeckTaken.connect(self.clientReady)
    #declared
    def on_peerReady(self):
        self.__server.setNewPlayer()
    def onGameEnd(self, who):
        initStr = "YOU WON!" if (who == "SERVER" and self.is_HOST == True) or (who == 'PEER' and self.is_HOST == False) else "YOU LOST!" if who != "DRAW" else "It\'s a draw!"
        res = FarewellDialog.getDialog(title = initStr)
        self.cleanUp()
        StatusGame.getInstance().set_status_name('BACK_TO_MENU')
    def clientReady(self):
        msg = self.__client.prepareClientMessage("DECK_TAKEN")
        self.__client.sendCmd(msg)
    def on_opponentScoreUpdate(self, value):
        self.opponent_score = value
        self.opponentScore.emit(value)
    def on_whoTakes(self, who):
        self.updateDeck.emit(who)
    def on_cardPlayed(self, card):
        self.move_card.emit(card)
    def initNewHand(self):
        if(self.is_Done() == True or self.opponent_score >= 1000):
            if(self.is_HOST and self.__server is not None):
                who = "SERVER" if self.is_Done() and self.opponent_score < 1000 else "DRAW" if self.is_Done() and self.opponent_score >= 1000 else "PEER"
                msg = self.__server.prepareServerMessage("RESULT", WHO=who)
                self.__server.sendCmd(msg)
                self.onGameEnd(who)
        else:
            StatusGame.getInstance().set_status_name("NEXT_GAME")
    def on_stackChanged(self, stack, index):
        self.move_stack.emit(stack, index)
    def on_trumpChanged(self, trump):
        self.__currentTrump = trump
        self.updateTrump.emit(self.__currentTrump)
    def on_valueDeclared(self,val):
        print(val)
    def on_whoStarts(self, who):
        print("who starts?", who)
        print("I'm a ", "PEER" if self.is_HOST == False else "SERVER")
        print(self.is_HOST == True and who == 'SERVER')
        print(self.is_HOST == False and who == "PEER")
        if (self.is_HOST == True and who == 'SERVER') or (self.is_HOST == False and who == "PEER"):
            self.is_FirstPlayer = True
        else:
            self.is_FirstPlayer = False
    def on_newBid(self, value):
        if(value == 0):
            StatusGame.getInstance().set_status_name("STACK_CHOOSING")
            self.is_main_player = True
            self.updateDeclaredValue.emit(self.declared_value)
        else:
            self.currentBid=value
            StatusGame.getInstance().set_status_name("VALUE_DECLARATION")
    def add_to_declared_value(self, value):
        self.declared_value += value
    def playAsPeer(self):
        self.is_HOST = False
        ip, result = NetworkDialog.getDialog('Peer') 
        print(ip,' ',result)
        if(result):
            self.__client = Peer(ip)
            self.__client.tryToConnect()
        else:
            StatusGame.getInstance().set_status_name("APP_START")
    def playAsHost(self):
        self.is_HOST = True
        self.__server = Server()
        ip, result = NetworkDialog.getDialog('Host',receiver= self.__server) 
        print(ip,' ',result)
        if(result == True):
            self.__server.initPlayerChoosen.connect(self.on_player_choosen)
            StatusGame.getInstance().set_status_name("GAME")
        else:
            self.__server = None
    def find_pair(self, tup):
        return tup[0] in self.hand_cards and tup[1] in self.hand_cards     
    def computeForbiddenVal(self):
        val = 130
        
        self.forbidden = val
    def on_got_cards(self,server=list(), player=list(), stack1 = list(), stack2=list()):
        # self.hand_cards = [Card(tup[0], tup[1]) for tup in player]
        self.computeForbiddenVal()
        print("forbidden value",self.forbidden)
        # self.opponent_cards = [Card(tup[0], tup[1]) for tup in server]
        # s1 = [Card(tup[0], tup[1]) for tup in stack1]
        # s2 = [Card(tup[0], tup[1]) for tup in stack2]
        # self.cardsToHandInReady.emit(self.hand_cards, self.opponent_cards,(tuple(s1), tuple(s2)))
    def on_player_choosen(self, val):
        print("I'm here again")
        print(val)
        if(val == 0):
            self.is_FirstPlayer = True
        else:
            self.is_FirstPlayer = False
        self.value_rand = val
        msg_dict = self.__server.prepareServerMessage('WHO_STARTS', WHO='SERVER' if val == 0 else 'PEER')
        if(self.signalsNotConnected == True):
            self.__server.peerReady.connect(self.on_peerReady)
            self.__server.sendCmd(msg_dict)
            self.__server.deckTaken.connect(self.on_deckTaken)
            self.__server.new_bid.connect(self.on_newBid)
            self.__server.cardPlayed.connect(self.on_cardPlayed)
            self.__server.stackChanged.connect(self.on_stackChanged)
            self.__server.trumpChanged.connect(self.on_trumpChanged)
            self.__server.value_declared.connect(self.on_valueDeclared)
            self.__server.opponentScoreChanged.connect(self.on_opponentScoreUpdate)
            self.signalsNotConnected = False
        self.__server.sendCmd(msg_dict)
        self.on_whoStarts('SERVER' if val == 0 else 'PEER')
        StatusGame.getInstance().set_status_name('CARDS_HANDIN')
    def on_deckTaken(self):
        if(self.prevStat != "SCORING"):
            StatusGame.getInstance().set_status_name(self.prevStat)
    def get_client(self):
        return self.__client
    def get_server(self):
        return self.__server
    def has_client(self):
        print(self.__client is None == False)
        return self.__client is None == False
    def cleanUp(self):
        try:
            self.winnerSignal.disconnect()
        except:
            pass
        try:
            self.opponentScore.disconnect()
        except:
            pass
        try:
            self.updateScore.disconnect()
        except:
            pass
        try:
            self.cardsFromDeckTaken.disconnect()
        except:
            pass
        try:
            self.cardsToHandInReady.disconnect()
        except:
            pass
        try:
            self.updateDeclaredValue.disconnect()
        except:
            pass
        try:
            self.updateTrump.disconnect()
        except:
            pass
        try:
            self.move_card.disconnect()
        except:
            pass
        try:
            self.move_stack.disconnect()
        except:
            pass
        try:
            self.updateDeck.disconnect()
        except:
            pass
        self.opponent_score = 0
        self.bidding_initiator = False
        self.hand_cards = []
        self.score = 0
        self.prevStat = ""
        self.declared_value = 100
        self.is_main_player = False
        self.is_FirstPlayer = False
        self.reportedSuits = []
        self.__currentTrump = ""
        self.opponent_cards = []
        self.opponent_left = []

        self.played_left = [] #cards gained during play time
        self.signalsNotConnected = True
        self.clientSignalsNotConnected = True
        self.is_HOST = False
        if(self.__server is not None):
            self.__server.cleanUp()
        if(self.__client is not None):
            self.__client.cleanUp()
    def on_status_changed(self, status):
        print("STATUS CHANGED: ", status)
        if status == "GAME":
            print("before")
            if self.__server is not None and self.is_HOST != False:
                print("in")
                self.__server.randomizeStartingPlayer()
            else:
                StatusGame.getInstance().set_status_name('CARDS_HANDIN')
        elif status == "NEXT_GAME":
            self.bidding_initiator = False
            self.hand_cards = []
            self.prevStat = ""
            self.declared_value = 100
            self.is_main_player = False
            self.is_FirstPlayer = False
            self.reportedSuits = []
            self.__currentTrump = ""
            self.opponent_cards = []
            self.opponent_left = []
            self.played_left = []
            if self.__server is not None and self.is_HOST != False:
                StatusGame.getInstance().set_status_name("PEER_CLEANING")
            else:
                msg = self.__client.prepareClientMessage('READY')
                self.__client.sendCmd(msg)
                StatusGame.getInstance().set_status_name('CARDS_HANDIN')       
        elif status == "CARDS_HANDIN":
            
            if self.__server is not None and self.is_HOST != False:
                print("I\'m gonna randomize cards")
                # generator = RandomCardGenerator(self.value_rand) 
                # stack1,stack2, player,server = generator.generate_stack_and_players_cards()
                # self.hand_cards = server
                self.computeForbiddenVal()
                print("forbidden Value", self.forbidden)
                # self.opponent_cards = player
                # QTimer.singleShot(400, lambda hand_cards = self.hand_cards, opponent_cards=self.opponent_cards, s1 = tuple(stack1), s2 = tuple(stack2):self.cardsToHandInReady.emit(hand_cards, opponent_cards,(s1, s2)))
                # op_stacks = [[stack[0].getTuple(), stack[1].getTuple()] for stack in [stack1, stack2]]
                # op_server = [card.getTuple() for card in reversed(server)]
                # op = [card.getTuple() for card in reversed(player)]
                # print(op_stacks, op_server, op)
                # msg_dict = self.__server.prepareServerMessage('CARDS_HANDIN', STACKS=op_stacks,
                #                                               SERVER_CARDS=op_server, PLAYER_CARDS=op)
                # QTimer.singleShot(1000, lambda msg = msg_dict:self.__server.sendCmd(msg))
            else:
                if(self.clientSignalsNotConnected == True):
                    self.__client.gameEnded.connect(self.onGameEnd)
                    self.__client.gotCards.connect(self.on_got_cards)
                    self.__client.who_starts.connect(self.on_whoStarts)
                    self.__client.cardPlayed.connect(self.on_cardPlayed)
                    self.__client.new_bid.connect(self.on_newBid)
                    self.__client.stackChanged.connect(self.on_stackChanged)
                    self.__client.trumpChanged.connect(self.on_trumpChanged)
                    self.__client.who_takes.connect(self.on_whoTakes)
                    self.__client.opponentScoreChanged.connect(self.on_opponentScoreUpdate)
                    self.clientSignalsNotConnected = False
        elif status == "STACK_CHOOSING":
            print("stack choosing")
        elif status == "VALUE_DECLARATION":
            self.computeForbiddenVal()
            ret, val = BidDialog.get_dialog(min=self.currentBid if self.is_main_player == False else self.declared_value, max=self.forbidden)
            
            if self.is_main_player == False:
                self.declared_value = ret
                StatusGame.getInstance().set_status_name("OPPONENT_MOVE")
                if self.__server is not None and self.is_HOST != False:
                    msg_dict = self.__server.prepareServerMessage('NEW_BID', BID_VALUE=self.declared_value+10 if self.declared_value > 0 else self.declared_value)
                    QTimer.singleShot(300, lambda msg = msg_dict:self.__server.sendCmd(msg))
                else:
                    msg_dict = self.__client.prepareClientMessage('NEW_BID', BID_VALUE=self.declared_value+10 if self.declared_value > 0 else self.declared_value)
                    QTimer.singleShot(300, lambda msg = msg_dict:self.__client.sendCmd(msg))   
            else:
                self.declared_value = ret if ret > 100 else self.declared_value
                self.updateDeclaredValue.emit(self.declared_value)
                StatusGame.getInstance().set_status_name("YOUR_MOVE")
                if self.__server is not None and self.is_HOST != False:
                    msg_dict = self.__server.prepareServerMessage('VALUE_DECLARED', GAME_VALUE=self.declared_value)
                    QTimer.singleShot(300, lambda msg = msg_dict:self.__server.sendCmd(msg))
                else:
                    msg_dict = self.__client.prepareClientMessage('VALUE_DECLARED', GAME_VALUE=self.declared_value)
                    QTimer.singleShot(300, lambda msg = msg_dict:self.__client.sendCmd(msg))   
            
            
        elif status == "STACK_CARD_TAKING":
            print("stack card taking")
        elif status == "SCORING":
            self.calculate_score()
            self.updateScore.emit(self.score)
            if self.__server is not None and self.is_HOST != False:
               msg_dict = self.__server.prepareServerMessage('SCORE',VALUE = self.score)
               QTimer.singleShot(300, lambda msg = msg_dict:self.__server.sendCmd(msg))
               
            else:
               msg_dict = self.__client.prepareClientMessage('SCORE',VALUE = self.score)
               QTimer.singleShot(300, lambda msg = msg_dict:self.__client.sendCmd(msg))
            QTimer.singleShot(3000, lambda: self.initNewHand())
            
        elif status == "OPPONENT_MOVE":
            print("waiting for opponent move")
        elif status == "YOUR_MOVE":
            print("waiting for your move")
        elif status == "TRUMP_CHANGE":
            print("trump changed")
        
    #SCORE
    def set_score(self, value):
        self.score = value

    def add_to_score(self, value):
        self.score += value

    def sub_from_score(self, value):
        self.score -= value

    def is_card_in_left(self, value):
        is_card = False
        for card in self.played_left[:]:
            temp = card.suit + str(card.value)
            if temp is value:
                is_card = True
        return is_card

    def add_card_to_opponent_left(self,card):
        self.opponent_left.append(card)
    def calculate_score(self):
        print(self.played_left)
        print(self.opponent_left)
        print(len(self.opponent_left) + len(self.played_left))
        value = 0
        #tu też muszą znajdować się z musików
        for card in self.played_left[:]:
            # value += POINTS.get(card.value, 0)
            pass
        if (len(self.played_left) > 0):
            for rep in self.reportedSuits:
                value += rep
        if self.is_main_player:
            if value >= self.declared_value:
                self.add_to_score(self.declared_value)
            else:
                self.sub_from_score(self.declared_value)
                value = value * (-1)
        else:
            value = round(value/10) * 10
            if self.score < RULE:
                self.add_to_score(value)
        self.played_left = []
        self.opponent_left = []
        self.reportedSuits = []
        self.declared_value = 0
        self.forbidden = 130
        self.currentBid = 0
        return self.score

    def is_Done(self):
        return self.score >= MAX_VALUE

    #HAND CARDS
    def add_cards_to_hand(self, cards):
        self.hand_cards = cards

    def remove_all_cards_from_hand(self):
        cards = self.hand_cards
        return cards

    def add_card_to_hand(self, card):
        card.location = "HAND"
        self.hand_cards.append(card)
        
    def remove_card_from_hand(self, card):
        self.hand_cards.remove(card)
    #OPPONENT's CARDS
    def remove_card_from_opponent_hand(self, card):
        self.opponent_cards.remove(card)
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

    def add_card_to_left(self, card):
        self.played_left.append(card)
    
    