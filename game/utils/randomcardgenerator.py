from ..card import Card, Suits, Cards
from random import randint, shuffle
from copy import deepcopy

class RandomCardGenerator:

    def __init__(self):
        self.__cards = []
        self.__init_cards()

    def __init_cards(self):
        if len(self.__cards) > 0:
            self.__cards = []
        for suit in list(Suits):
            for value in list(Cards):
                self.__cards.append(Card(suit, value))

    def get_cards(self):
        return deepcopy(self.__cards)

    def generate_stack_and_players_cards(self):
        end_value = randint(10,30)
        cards = deepcopy(self.__cards)
        for i in range(0, end_value):
            shuffle(cards)
        stack1 = []
        stack2 = []
        player1 = []
        player2 = []
        first_player_served = False
        stack1_served = False
        stack2_served = False

        while len(cards) > 0:
            card = cards.pop()
            if first_player_served == False:
                player1.append(card)
                first_player_served = True
                if(len(stack1) < 2):
                    stack1_served = False
            elif stack1_served == False:
                if len(stack1) < 2:
                    stack1.append(card)
                stack1_served = True
                if(len(stack2) < 2):
                    stack2_served = False
            elif stack2_served == False:
                if len(stack2) < 2:
                    stack2.append(card)
                stack2_served = True
            else:
                player2.append(card)
                first_player_served = False
        return stack1, stack2, player1, player2