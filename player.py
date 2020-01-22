from card import *
MAX_VALUE = 1000
from server import *
from threading import *
from time import sleep
from statusgame import StatusGame
from networkdialog import NetworkDialog
from peer import Peer
from initdialog import InitDialog
from PyQt5.QtCore import QObject, pyqtSignal
from randomcardgenerator import RandomCardGenerator
class Player(QObject):
    __server = None
    __client = None
    updateScore = pyqtSignal(int)
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
        self.score = 0
        self.declared_value = 100
        self.is_main_player = False
        self.is_FirstPlayer = False
        self.reportedSuits = []
        self.__currentTrump = ""
        self.opponnent_cards = []
        self.played_left = [] #cards gained during play time
        self.is_HOST = False
    #declared
     
    def on_opponnentScoreUpdate(self, value):
        pass
    def on_whoTakes(self, who):
        self.updateDeck.emit(who)
    def on_cardPlayed(self, card):
        self.move_card.emit(card)
        
    def on_stackChanged(self, stack, index):
        self.move_stack.emit(stack, index)
    def on_trumpChanged(self, trump):
        self.__currentTrump = trump
        self.updateTrump.emit(self.__currentTrump)
    def on_valueDeclared(self,val):
        pass
    def on_whoStarts(self, who):
        if (self.is_HOST == True and who == 'SERVER') or (self.is_HOST == False and who == "PEER"):
            self.is_FirstPlayer = True
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
        val = 0
        for card in self.hand_cards:
            if str(card) == str(tup[0]) or str(card) == str(tup[1]):
                val+=1
        return val == 2        
    def computeForbiddenVal(self):
        val = 130
        print("Cards in hand",self.hand_cards)
        print(Card('D', 13) == Card('D', 13, "HAND"))
        print(Card('H', 12) in self.hand_cards, Card('H', 13) in self.hand_cards)
        print(Card('D', 12) in self.hand_cards, Card('D', 13) in self.hand_cards)
        print(Card('C', 12) in self.hand_cards, Card('C', 13) in self.hand_cards)
        print(Card('S', 12) in self.hand_cards, Card('S', 13) in self.hand_cards)
        print(self.find_pair( (Card('H', 12), Card('H', 13))))
        if self.find_pair( (Card('H', 12), Card('H', 13))):
            val += 100
        if self.find_pair( (Card('D', 12), Card('D', 13))):
            val+=80
        if self.find_pair( (Card('C', 12), Card('C', 13))):
            val += 60
        if self.find_pair( (Card('S', 12), Card('S', 13))):
            val += 40
        self.forbidden = val
    def on_got_cards(self,server=list(), player=list(), stack1 = list(), stack2=list()):
        self.hand_cards = [Card(tup[0], tup[1]) for tup in player]
        self.computeForbiddenVal()
        print("forbidden value",self.forbidden)
        self.opponnent_cards = [Card(tup[0], tup[1]) for tup in server]
        s1 = [Card(tup[0], tup[1]) for tup in stack1]
        s2 = [Card(tup[0], tup[1]) for tup in stack2]
        self.cardsToHandInReady.emit(self.hand_cards, self.opponnent_cards,(tuple(s1), tuple(s2)))
    def on_player_choosen(self, val):
        if(val == 0):
            self.is_FirstPlayer = True
        self.value_rand = val
        msg_dict = self.__server.prepareServerMessage('WHO_STARTS', WHO='SERVER' if val == 0 else 'PEER')
        self.__server.sendCmd(msg_dict)
        self.__server.new_bid.connect(self.on_newBid)
        self.__server.cardPlayed.connect(self.on_cardPlayed)
        self.__server.stackChanged.connect(self.on_stackChanged)
        self.__server.trumpChanged.connect(self.on_trumpChanged)
        self.__server.value_declared.connect(self.on_valueDeclared)
        self.__server.opponnentScoreChanged.connect(self.on_opponnentScoreUpdate)
        StatusGame.getInstance().set_status_name('CARDS_HANDIN')
    def get_client(self):
        return self.__client
    def get_server(self):
        return self.__server
    def has_client(self):
        print(self.__client is None == False)
        return self.__client is None == False
    def cleanUp(self):
        if(self.__server is not None):
            self.__server.cleanUp()
        if(self.__client is not None):
            self.__client.cleanUp()
    def on_status_changed(self, status):
        if status == "GAME":
            print("before")
            if self.__server is not None and self.is_HOST != False:
                print("in")
                self.__server.randomizeStartingPlayer()
            else:
                StatusGame.getInstance().set_status_name('CARDS_HANDIN')
        elif status == "CARDS_HANDIN":
            print('I\'m in')
            if self.__server is not None and self.is_HOST != False:
                print('I\'m in2')
                generator = RandomCardGenerator(self.value_rand) 
                print('I\'m in3')
                stack1,stack2, player,server = generator.generate_stack_and_players_cards()
                print('I\'m in4')
                self.hand_cards = server
                self.computeForbiddenVal()
                print("forbidden Value", self.forbidden)
                print('I\'m in cards generated and forbidden value computed')
                self.opponnent_cards = player
                QTimer.singleShot(200, lambda hand_cards = self.hand_cards, opponnent_cards=self.opponnent_cards, s1 = tuple(stack1), s2 = tuple(stack2):self.cardsToHandInReady.emit(hand_cards, opponnent_cards,(s1, s2)))
                print('I\'m in cards generated and forbidden value computed and probably cards should be placed on table')
                op_stacks = [[stack[0].getTuple(), stack[1].getTuple()] for stack in [stack1, stack2]]
                op_server = [card.getTuple() for card in reversed(server)]
                op = [card.getTuple() for card in reversed(player)]
                print(op_stacks, op_server, op)
                msg_dict = self.__server.prepareServerMessage('CARDS_HANDIN', STACKS=op_stacks,
                                                              SERVER_CARDS=op_server, PLAYER_CARDS=op)
                QTimer.singleShot(1000, lambda msg = msg_dict:self.__server.sendCmd(msg))
            else:
                self.__client.gotCards.connect(self.on_got_cards)
                self.__client.who_starts.connect(self.on_whoStarts)
                self.__client.cardPlayed.connect(self.on_cardPlayed)
                self.__client.new_bid.connect(self.on_newBid)
                self.__client.stackChanged.connect(self.on_stackChanged)
                self.__client.trumpChanged.connect(self.on_trumpChanged)
                self.__client.who_takes.connect(self.on_whoTakes)
                self.__client.opponnentScoreChanged.connect(self.on_opponnentScoreUpdate)
        elif status == "STACK_CHOOSING":
            print("stack choosing")
        elif status == "VALUE_DECLARATION":
            ret, val = InitDialog.getDialog(min=self.currentBid if self.is_main_player == False else self.declared_value, max=self.forbidden)
            self.declared_value = ret
            if self.is_main_player == False:
                StatusGame.getInstance().set_status_name("OPPONNENT_MOVE")
                if self.__server is not None and self.is_HOST != False:
                    msg_dict = self.__server.prepareServerMessage('NEW_BID', BID_VALUE=self.declared_value+10 if self.declared_value > 0 else self.declared_value)
                    QTimer.singleShot(300, lambda msg = msg_dict:self.__server.sendCmd(msg))
                else:
                    msg_dict = self.__client.prepareClientMessage('NEW_BID', BID_VALUE=self.declared_value+10 if self.declared_value > 0 else self.declared_value)
                    QTimer.singleShot(300, lambda msg = msg_dict:self.__client.sendCmd(msg))   
            else:
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
        elif status == "OPPONNENT_MOVE":
            print("waiting for opponnent move")
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
        self.hand_cards.append(card)
    
    def remove_card_from_hand(self, card):
        self.hand_cards.remove(card)
    #OPPONNENT's CARDS
    def remove_card_from_opponnent_hand(self, card):
        self.opponnent_cards.remove(card)
    def add_card_to_opponnent_hand(self,card):
        self.opponnent_cards.append(card)
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
    
    