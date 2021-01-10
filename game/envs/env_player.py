from typing import overload
from ..card import Card
from .. import List


class EnvPlayer(object):

    @overload
    def __init__(self, hand_cards: List[Card], known_stock: List[Card] =[]):
        self.reset()
        self.hand_cards = hand_cards
        self.known_stock = known_stock

    @overload
    def __init__(self, name: str =""):
        self.name = name
        self.reset()

    def reset(self, hand_cards: List[Card] =[], known_stock: List[Card] =[]):
        self.score = 0
        self.invalid_actions = 0
        self.rewards = 0
        self.hand_cards: List[Card] = hand_cards
        self.known_stock: List[Card] = known_stock
        self.tricks: List[Card] = []

    