from typing import overload
from ..card import Card
from .. import List, deque, Deque

DQ_SIZE = 10

def mean(collection: Deque):
    if len(collection) == 0: return 0
    return sum(collection, 0) / len(collection)


class EnvPlayer(object):

    @overload
    def __init__(self, hand_cards: List[Card], known_stock: List[Card] =[]):
        self.__init_queues()
        self.reset(hand_cards, known_stock)
        self.score = 0
        self.invalid_actions = 0
        self.rewards = 0

    def __init__(self, name: str =""):
        self.__init_queues()
        self.name = name
        self.reset()

    def __init_queues(self):        
        self.__score_deque: Deque[float] =deque(maxlen=DQ_SIZE)  
        self.__invalid_deque: Deque[int] =deque(maxlen=DQ_SIZE)  
        self.__rewards_deque: Deque[float] =deque(maxlen=DQ_SIZE)  

    def save(self):
        self.__score_deque.append(self.score) 
        self.__invalid_deque.append(self.invalid_actions)
        self.__rewards_deque.append(self.rewards)

    def reset(self, hand_cards: List[Card] =[], known_stock: List[Card] =[]):
        self.score = 0
        self.invalid_actions = 0
        self.rewards = 0
        self.hand_cards: List[Card] = hand_cards
        self.known_stock: List[Card] = known_stock
        self.tricks: List[Card] = []
        
    @property
    def mean_score(self):
        return mean(self.__score_deque)

    @property
    def mean_invalid_actions_count(self):
        return mean(self.__invalid_deque)

    @property
    def mean_reward(self):
        return mean(self.__rewards_deque)
    