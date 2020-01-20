from card import Card, SUITS, VALUES
from random import randint, shuffle
class RandomCardGenerator:
    __first_player = 0
    def __init__(self, first=0):
        self.cards = []
        self.__first_player = first
    def __init_cards(self):
        if len(self.cards) > 0:
            self.cards = []
        for suit in SUITS:
            for value in VALUES:
                self.cards.append(Card(suit, value))

    def generate_stack_and_players_cards(self):
        self.__init_cards()
        end_value = randint(10,30)
        for i in range(0, end_value):
            shuffle(self.cards)
        stack1 = []
        stack2 = []
        server = []
        player = []
        first_player_served = False
        stack1_served = False
        stack2_served = False
        for card in self.cards:
            if first_player_served == False:
                if self.__first_player == 0:
                    server.append(card)
                else:
                    player.append(card)
                first_player_served = True
                if(len (stack1) < 2):
                    stack1_served = False
            elif stack1_served == False:
                if len(stack1) < 2:
                    stack1.append(card)
                stack1_served = True
                if(len (stack2) < 2):
                    stack2_served = False
            elif stack2_served == False:
                if len(stack2) < 2:
                    stack2.append(card)
                stack2_served = True
            else:
                if self.__first_player == 1:
                    server.append(card)
                else:
                    player.append(card)
                first_player_served = False
        return stack1, stack2, player, server