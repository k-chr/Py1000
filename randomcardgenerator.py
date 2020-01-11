from card import *
from random import *

class RandomCardGenerator:
    def __init__(self):
        self.cards = []
        self.init_cards()

    def init_cards(self):
        if not self.cards:
            for suit in SUITS:
                for value in VALUES:
                    self.cards.append(Card(suit, value))

    def generate_player_cards(self):
        cardlist = []
        for i in range(0, 10):
            temp = self.random_card()
            cardlist.append(temp)
        return cardlist

    def generate_stack_cards(self):
        cardstack = []
        for i in range(0, 2):
            temp = self.random_card()
            cardstack.append(temp)
        return cardstack

    def random_card(self):
        temp = random.choice(self.cards)
        self.cards.remove(temp)
        return temp
