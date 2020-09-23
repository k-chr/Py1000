from . import Card, Suits, Cards, TakingTrickState, RandomCardGenerator, randint, GameRules, datetime
from ..utils.gamelogger import GameLogger
from ..utils.csvlogger import CSVLogger
INVALID_MOVE_REWARD = -0.5

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
        self.p1_invalid_actions = 0
        self.p2_invalid_actions = 0
        self.file_name = f"simpletakingtricksenv_session_{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}.log"
        self.csv_rewards = f"simpletakingtricksenv_rewards_{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}.csv"
        self.csv_invalid = f"simpletakingtricksenv_invalid_{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}.csv"
        self.logger = GameLogger(self.file_name)
        self.csv_inv_log = CSVLogger(self.csv_invalid)
        self.csv_rew_log = CSVLogger(self.csv_rewards)

    def reset(self):
        self.csv_inv_log.log((self.p1_invalid_actions, self.p2_invalid_actions))
        self.csv_rew_log.log((self.p1_score, self.p2_score))
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
        self.p1_invalid_actions = 0
        self.p2_invalid_actions = 0

        self.played_cards = []
        self.player1_tricks = []
        self.player2_tricks = []
        self.current_observation = {'is_player1_turn':player1,
                                    'data':TakingTrickState(hand_cards=self.player1 if player1 else self.player2,
                                                            tricks_taken_by_both_players=self.played_cards,
                                                            known_stock=self.left_stock if player1 else self.right_stock)}

        self.logger.append_to_log(f"player1_cards: {self.player1}")
        self.logger.append_to_log(f"player2_cards: {self.player2}")

        return self.current_observation

    def step(self, action: int): 
        player, tricks, op_tricks = (self.player1,  self.player1_tricks, self.player2_tricks) if self.is_player1_turn else (self.player2, self.player2_tricks, self.player1_tricks)
        reward = 0
        rewards = []
        done = False
        self.rules.set_card_collection(player)
        l = [card for card in player if card.id() == action]
        opponent_card = self.current_observation["data"].played_card
        if not any(l) or (opponent_card is not None and not self.rules.is_card_valid(l[0], opponent_card, self.current_observation["data"].trump)):
            reward = INVALID_MOVE_REWARD
            if self.is_player1_turn:
                self.p1_invalid_actions += 1
            else:
                self.p2_invalid_actions += 1
            rewards = [reward]
        else:
            card = l[0]
            player.remove(card)
            self.played_cards.append(card)
            self.logger.append_to_log(("player1" if self.is_player1_turn else "player2") + " played card " + card.__str__())
            
            if opponent_card is not None:
                op_reward = 0
                trick = [card, opponent_card]
                if card > opponent_card or card.suit is self.current_observation["data"].trump and not (card.suit is opponent_card.suit):
                    tricks.append(trick)
                    reward = card.value.value + opponent_card.value.value
                    reward *= 10
                else:
                    op_tricks.append(trick)
                    op_reward = card.value.value + opponent_card.value.value
                    op_reward *= 10
                done = len(self.played_cards) == 20
            
                self.is_player1_turn = not self.is_player1_turn if op_reward > 0 else self.is_player1_turn

                self.current_observation = {'is_player1_turn':self.is_player1_turn,
                                    'data':TakingTrickState(hand_cards=self.player1 if self.is_player1_turn else self.player2,
                                                            tricks_taken_by_both_players=self.played_cards, trump= self.current_observation["data"].trump,
                                                            known_stock=self.left_stock if self.is_player1_turn else self.right_stock)}
                rewards = [reward,op_reward]
                self.__update_op_rewards(op_reward)
            else:
                trump = Suits.NO_SUIT
                if(self.rules.has_pair(card)):
                    reward = card.suit.value * 10
                    trump = card.suit
                    self.logger.append_to_log(("player1" if self.is_player1_turn else "player2") + f" meld {trump.name} and got {trump.value} points")

                self.is_player1_turn = not self.is_player1_turn
                rewards = [reward]
                self.current_observation = {'is_player1_turn':self.is_player1_turn,
                                    'data':TakingTrickState(hand_cards=self.player1 if self.is_player1_turn else self.player2,
                                                            tricks_taken_by_both_players=self.played_cards, trump=trump, played_card=card,
                                                            known_stock=self.left_stock if self.is_player1_turn else self.right_stock)}
        self.__update_rewards(reward)
        return self.current_observation, rewards, done

    def __update_rewards(self, reward):
        if self.is_player1_turn:
            self.p1_score += reward
        else:
            self.p2_score += reward

    def __update_op_rewards(self, reward):
        if self.is_player1_turn:
            self.p2_score += reward
        else:
            self.p1_score += reward