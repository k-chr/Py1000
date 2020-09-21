from .state import State
from . import Card, List, zeros

class GiveawayState(State):

    def __init__(self, hand_cards: List[Card]):
        self.hand_cards = hand_cards

    def to_one_hot_vec(self):
        hand = zeros([24,])
        for card in self.hand_cards:
            hand[card.id()] = 1

        return hand