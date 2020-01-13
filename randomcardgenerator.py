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
        cardlist1 = []
        cardlist2 = []
        for i in range(0, 10):
            cardlist1.append(self.random_card())
            cardlist2.append(self.random_card())
        return cardlist1, cardlist2

    def generate_stack_cards(self):
        cardstack1 = []
        cardstack2 = []
        for i in range(0, 2):
            cardstack1.append(self.random_card())
            cardstack2.append(self.random_card())
        return cardstack1, cardstack2

    def random_card(self):
        temp = random.choice(self.cards)
        self.cards.remove(temp)
        return temp
