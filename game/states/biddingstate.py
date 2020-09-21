from .state import State
from . import List, Card, zeros, concatenate

class BiddingState(State):

    def __init__(self, hand_cards: List[Card], current_bid: int):
        assert len(hand_cards) == 10
        self.hand_cards = hand_cards
        self.current_bid = current_bid

    def to_one_hot_vec(self):
        
        z = zeros([24,])

        for card in self.hand_cards:
            z[card.id()] = 1

        bids = zeros([27,])
        bids[(self.current_bid-100)//10] = 1

        return concatenate((z, bids))