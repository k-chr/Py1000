from ..card import Card, Suits, Cards
from typing import List

class GameRules(object):   

    def __init__(self, cards:List[Card]=None):
        self.cards = cards

    def setCardCollection(self, cards:List[Card]):
        self.cards = cards

    def isCardValid(self, card:Card, opponentCard:Card, trump:Suits=Suits.NO_SUIT):
        return not((self.isSuitPresent(opponentCard.suit) and (card.suit is not opponentCard.suit or self.isGreaterPresent(card))) or 
                   (self.isSuitPresent(trump) and card.suit is not trump))

    def isSuitPresent(self, suit:Suits):
        return any([card.suit is suit for card in self.cards])

    def isGreaterPresent(self, card:Card):
        return any([c > card for c in self.cards])

