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
    cardsToHandInReady = pyqtSignal(list,list,tuple)
    def __init__(self):
        super(Player, self).__init__()
        self.bidding_initiator = False
        self.hand_cards = []
        self.score = 0
        self.declared_value = 100
        self.is_main_player = False
        self.reportedSuits = []
        self.opponnent_cards = []
        self.played_left = [] #cards gained during play time

    #declared
    def add_to_declared_value(self, value):
        self.declared_value += value
    def playAsPeer(self):
        ip, result = NetworkDialog.getDialog('Peer') 
        print(ip,' ',result)
        if(result):
            self.__client = Peer(ip)
            self.__client.tryToConnect()
        else:
            StatusGame.getInstance().set_status_name("APP_START")
    def playAsHost(self):
        self.__server = Server()
        ip, result = NetworkDialog.getDialog('Host',receiver= self.__server) 
        print(ip,' ',result)
        StatusGame.getInstance().set_status_name("GAME")
    def has_client(self):
        print(self.__client is None == False)
        return self.__client is None == False

    def on_status_changed(self, status):
        if status == "GAME":
            if self.__server is not None:
               generator = RandomCardGenerator(0) 
               stack1,stack2, player,server = generator.generate_stack_and_players_cards()
               self.hand_cards = server
               self.opponnent_cards = player
               self.cardsToHandInReady.emit(self.hand_cards, self.opponnent_cards,(tuple(stack1), tuple(stack2)))
               
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

        
        if self.is_main_player:
            if value >= self.declared_value:
                self.addToScore(self.declared_value)
            else:
                self.subFromScore(self.declared_value)
                value = value * (-1)
        else:
            value = round(value/10) * 10
            self.addToScore(value)

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

    #LEFT CARDS
    def add_cards_to_left(self, cards):
        self.played_left = cards

    def remove_all_cards_from_left(self):
        cards = self.played_left
        return cards

    def add_card_to_left(self, card):
        self.played_left.append(card)

    def remove_card_from_left(self, card):
        self.played_left.remove(card)