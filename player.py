from card import *
MAX_VALUE = 1000

class Player:
    def __init__(self):
        self.hand_cards = []
        self.score = 0
        self.declared_value = 100
        self.is_main_player = False
        self.is_reported = False

        self.played_left = [] #cards gain during play time

    #declared
    def add_to_declared_value(self, value):
        self.declared_value += value


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

        if self.is_reported:
            for tup in BIDDING.keys():
                if self.is_card_in_left(tup[0]) and self.is_card_in_left(tup[1]):
                    value += BIDDING.get(tup)

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
        self.hand_cards = cards

    def remove_all_cards_from_left(self):
        cards = self.hand_cards
        return cards

    def add_card_to_left(self, card):
        self.hand_cards.append(card)

    def remove_card_from_left(self, card):
        self.hand_cards.remove(card)