from . import Suits, Card, TakingTrickState, RandomCardGenerator, randint, GameRules, datetime, TrainingEnum
from ..utils.gamelogger import GameLogger
from ..utils.csvlogger import CSVLogger
from .env_player import EnvPlayer
from .. import choice

INVALID_MOVE_REWARD = -50
MY_CARD_REWARD = 0.1
NOT_MY_CARD_REWARD = -MY_CARD_REWARD
VALID_MOVE_REWARD = -INVALID_MOVE_REWARD/30
FULL_TRAINING_REWARD_FACTOR = 1

class SimpleTakingTricksEnv(object):
    
    def __init__(self, flag: TrainingEnum =TrainingEnum.FULL_TRAINING):

        self.flag = flag
        self.__fun =  self.__full_training_step if self.flag is TrainingEnum.FULL_TRAINING else self.__valid_card_estimator_step if (
           self.flag is TrainingEnum.PRETRAINING_VALID_CARDS) else self.__own_card_estimator_step
        self.generator = RandomCardGenerator()
        self.current_observation = {}
        self.played_cards = []
        self.file_name = f"simpletakingtricksenv_session_{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}.log"
        self.csv_rewards = f"simpletakingtricksenv_rewards_{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}.csv"
        self.csv_invalid = f"simpletakingtricksenv_invalid_{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}.csv"
        self.logger = GameLogger(self.file_name)
        self.csv_inv_log = CSVLogger(self.csv_invalid)
        self.csv_rew_log = CSVLogger(self.csv_rewards)
        self.player1 = EnvPlayer("player1")
        self.player2 = EnvPlayer("player2")

    def log_players_csv_info(self):
        self.csv_inv_log.log((self.player1.invalid_actions, self.player2.invalid_actions))
        self.csv_rew_log.log((self.player1.rewards, self.player2.rewards))

    def reset(self):
        player1 = randint(0, 1) == 1
        cards = self.generator.generate_stack_and_players_cards()
        stock = cards[choice([0, 1], size=1)[0]]
        if player1:
            self.player1.reset(cards[2], stock)
            self.player2.reset(cards[3])
        else:
            self.player1.reset(cards[3])
            self.player2.reset(cards[2], stock)
        
        self.is_player1_turn = player1
        self.played_cards = []
        self.current_observation = self.create_observation()

        self.logger.append_to_log(f"player1_cards: {self.player1.hand_cards}")
        self.logger.append_to_log(f"player2_cards: {self.player2.hand_cards}")

        return self.current_observation

    def create_observation(self, card: Card =None, trump: Suits =Suits.NO_SUIT):
        return {'is_player1_turn':self.is_player1_turn,
                'data':TakingTrickState(hand_cards=self.player_handler.hand_cards,
                                        tricks_taken_by_both_players=self.played_cards, trump=trump, 
                                        played_card=card,
                                        known_stock=self.player_handler.known_stock)}

    @property
    def player_handler(self):
        return self.player1 if self.is_player1_turn else self.player2

    @property
    def done(self):
        return len(self.played_cards) == 20
        
    @property
    def opponent_handler(self):
        return self.player2 if self.is_player1_turn else self.player1

    def step(self, action: int): 
       return self.__fun(action)

    def __update_rewards(self, reward: float):
        self.player_handler.rewards += reward

    def __update_op_rewards(self, reward: float):
        self.opponent_handler.rewards += reward

    def __own_card_estimator_step(self, action: int):
        reward = 0
        rewards = []
        card: Card =None
        trump: Suits =self.current_observation["data"].trump
        opponent_card: Card =self.current_observation["data"].played_card
        l = [card for card in self.player_handler.hand_cards if card.id() == action]
        if not any(l):
            reward = NOT_MY_CARD_REWARD
            self.player_handler.invalid_actions += 1
        else:
            reward = MY_CARD_REWARD
            card = l[0]
            self.player_handler.hand_cards.remove(card)

            if opponent_card is not None:
                self.played_cards.append(opponent_card)
                self.played_cards.append(card)
            else:
                if(GameRules.has_pair(self.player_handler.hand_cards, card)):
                    trump = card.suit
                    self.logger.append_to_log((self.player_handler.name) + f" meld {trump.name} and got {trump.value} points")

        self.__update_rewards(reward)

        if reward > 0:
            self.is_player1_turn = not self.is_player1_turn
            self.current_observation = self.create_observation(card=card if opponent_card is None else None, trump=trump)
        rewards = [reward]
        return self.current_observation, rewards, self.done

    def __full_training_step(self, action: int):
        reward = 0
        op_reward = 0
        card: Card =None
        trump: Suits =self.current_observation["data"].trump
        l = [card for card in self.player_handler.hand_cards if card.id() == action]
        opponent_card: Card = self.current_observation["data"].played_card

        if not any(l) or (opponent_card is not None and not GameRules.is_card_valid(
                self.player_handler.hand_cards, l[0], opponent_card, trump)):
            reward = INVALID_MOVE_REWARD
            self.player_handler.invalid_actions += 1
            card = opponent_card
        else:
            card = l[0]
            self.player_handler.hand_cards.remove(card)
            self.logger.append_to_log(self.player_handler.name + " played card " + card.__str__())
            
            if opponent_card is not None:
                self.played_cards.append(card)
                self.played_cards.append(opponent_card)

                trick = [card, opponent_card]
                if GameRules.does_card_beat_opponents_one(card, opponent_card, trump):
                    self.player_handler.tricks.append(trick)
                    reward += (card.value.value + opponent_card.value.value)
                else:
                    self.opponent_handler.tricks.append(trick)
                    op_reward = (card.value.value + opponent_card.value.value)
                card = None
                
            else:
                if(GameRules.has_pair(self.player_handler.hand_cards, card)):
                    reward += (card.suit.value)
                    trump = card.suit
                    self.logger.append_to_log(self.player_handler.name + f" meld {trump.name} by {card} and got {trump.value} points")

        rewards = [reward,op_reward] if op_reward > 0 else [reward]
        self.__update_rewards(reward)
        self.__update_op_rewards(op_reward)
        if reward >= 0:
            self.logger.append_to_log(f"player1_cards: {self.player1.hand_cards}")
            self.logger.append_to_log(f"player2_cards: {self.player2.hand_cards}")
            self.player_handler.score += reward
            self.opponent_handler.score += op_reward
        self.is_player1_turn = not self.is_player1_turn if (op_reward > 0 or opponent_card is None) and reward >= 0 else self.is_player1_turn
        self.current_observation = self.create_observation(trump=trump, card=card)
        return self.current_observation, rewards, self.done

    def __valid_card_estimator_step(self, action):
        reward = 0
        op_reward = 0
        card: Card =None
        l = [card for card in self.player_handler.hand_cards if card.id() == action]
        opponent_card: Card =self.current_observation["data"].played_card
        trump: Suits =self.current_observation["data"].trump
        if not any(l) or (opponent_card is not None and not GameRules.is_card_valid(self.player_handler.hand_cards, l[0], opponent_card, trump)):
            reward = INVALID_MOVE_REWARD
            self.player_handler.invalid_actions += 1
        else:
            reward = VALID_MOVE_REWARD
            card = l[0]
            self.player_handler.hand_cards.remove(card)
            self.logger.append_to_log(self.player_handler.name + " played card " + card.__str__())
            
            if opponent_card is not None:
                trick = [card, opponent_card]
                if GameRules.does_card_beat_opponents_one(card, opponent_card, trump):
                    self.player_handler.tricks.append(trick)
                else:
                    self.opponent_handler.tricks.append(trick)
                    op_reward = 1
                self.played_cards.append(card)
                self.played_cards.append(opponent_card)
                card = None
            else:
                if(GameRules.has_pair(self.player_handler.hand_cards, card)):
                    trump = card.suit
                    self.logger.append_to_log(self.player_handler.name + f" meld {trump.name} and got {trump.value} points")
                
        self.__update_rewards(reward)
        rewards = [reward]
        self.is_player1_turn = not self.is_player1_turn if (op_reward > 0 or opponent_card is None) else self.is_player1_turn
        if reward >= 0:
            self.current_observation = self.create_observation(trump=trump, card=card)
        return self.current_observation, rewards, self.done
