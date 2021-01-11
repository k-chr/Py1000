from .state import State
from . import zeros, concatenate, List, Card, Suits, deepcopy

class TakingTrickState(State):

    def __init__(self, hand_cards: List[Card], known_stock: List[Card],
                 tricks_taken_by_both_players: List[Card], played_card: Card =None, trump: Suits =Suits.NO_SUIT):
        self.hand_cards = deepcopy(hand_cards)
        self.known_stock = deepcopy(known_stock)
        self.tricks = deepcopy(tricks_taken_by_both_players)
        self.played_card = deepcopy(played_card) if played_card is not None else None
        self.trump = trump

    def to_one_hot_vec(self):
        hand = zeros(24)
        for card in self.hand_cards:
            hand[card.id()] = 1

        stock = zeros(24)
        for card in self.known_stock:
            stock[card.id()] = 1

        tricks = zeros(24)
        for card in self.tricks:
            tricks[card.id()] = 1

        played_card = zeros(24)
        if self.played_card is not None:
            played_card[self.played_card.id()] = 1

        trump = zeros(4)
        if not self.trump is Suits.NO_SUIT:
            trump[(self.trump.value - 40)//20] = 1

        return concatenate((hand, stock, tricks, played_card, trump), axis=0)