from . import Card, Suits, Cards, TakingTrickState, RandomCardGenerator, randint, GameRules

INVALID_MOVE_REWARD = -50

class SimpleTakingTricksEnv(object):
    
    def __init__(self):
        self.player1 = []
        self.player2 = []
        self.rules = GameRules()
        self.left_stock = []
        self.right_stock = []
        self.generator = RandomCardGenerator()
        self.current_observation = {}
        self.played_cards = []
        self.player1_tricks = []
        self.player2_tricks = []
        self.p1_score = 0
        self.p2_score = 0

    def reset(self):
        player1 = randint(0, 1) == 1
        cards = self.generator.generate_stack_and_players_cards()
        if player1:
            self.player1 = cards[2]
            self.player2 = cards[3]
        else:
            self.player1 = cards[3]
            self.player2 = cards[2]
        
        self.left_stock = cards[0]
        self.right_stock = cards[1]
        self.is_player1_turn = player1
        self.p1_score = 0
        self.p2_score = 0
        self.played_cards = []
        self.player1_tricks = []
        self.player2_tricks = []
        self.current_observation = {'is_player1_turn':player1,
                                    'data':TakingTrickState(hand_cards=self.player1 if player1 else self.player2,
                                                            tricks_taken_by_both_players=self.played_cards,
                                                            known_stock=self.left_stock if player1 else self.right_stock)}
        return self.current_observation

    def step(self, action: int): 
        player, tricks, op_tricks = self.player1,  self.player1_tricks, self.player2_tricks if self.is_player1_turn else self.player2, self.player2_tricks, self.player1_tricks
        reward = 0
        done = False
        rules.set_card_collection(player)

        if not any([card.id() == action for card in self.player]):
            reward = INVALID_MOVE_REWARD
            return self.current_observation, [reward], done

        card = [card for card in player if card.id() == action][0]
        opponent_card = self.current_observation["data"].played_card
        if opponent_card is not None:
            if not rules.is_card_valid(card, opponent_card, self.current_observation["data"].trump):
                reward = INVALID_MOVE_REWARD
                return self.current_observation, [reward], done
            player.remove(card)
            self.played_cards.append(card)
            op_reward = 0
            if card > opponent_card or card.suit is self.current_observation["data"].trump and not (card.suit is opponent_card.suit):
                tricks.append([card, opponent_card])
                reward = card.value.value + opponent_card.value.value
                op_reward = 0
            else:
                op_tricks.append([card, opponent_card])
                reward = 0
                op_reward = card.value.value + opponent_card.value.value

            done = len(self.played_cards) == 24
            
            self.is_player1_turn = not self.is_player1_turn if op_reward > 0 else self.is_player1_turn

            self.current_observation = {'is_player1_turn':self.is_player1_turn,
                                    'data':TakingTrickState(hand_cards=self.player1 if self.is_player1_turn else self.player2,
                                                            tricks_taken_by_both_players=self.played_cards, trump= self.current_observation["data"].trump,
                                                            known_stock=self.left_stock if self.is_player1_turn else self.right_stock)}
            return self.current_observation, [reward,op_reward], done
        self.is_player1_turn = not self.is_player1_turn

        player.remove(card)
        self.played_cards.append(card)
        trump = Suits.NO_SUIT
        if(rules.has_pair(card)):
            reward = card.suit.value
            trump = card.suit
        self.current_observation = {'is_player1_turn':self.is_player1_turn,
                                    'data':TakingTrickState(hand_cards=self.player1 if self.is_player1_turn else self.player2,
                                                            tricks_taken_by_both_players=self.played_cards, trump=trump,
                                                            known_stock=self.left_stock if self.is_player1_turn else self.right_stock)}
        return self.current_observation, [reward], done
