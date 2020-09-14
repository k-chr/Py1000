from game.enums import Cards, Suits

class Card(object):

    def __init__(self, suit:Suits, value:Cards):
        self.suit = suit
        self.value = value
