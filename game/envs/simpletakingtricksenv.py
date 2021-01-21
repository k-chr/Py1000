from . import Suits, Card, TakingTrickState, RandomCardGenerator, randint, GameRules, datetime, TrainingEnum
from ..utils.gamelogger import GameLogger
from ..utils.csvlogger import CSVLogger
from .env_player import EnvPlayer
from .. import choice, NetworkOutput, List, deque, Deque

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
        self.date = datetime.now()
        self.file_name = f"simpletakingtricksenv_session_{self.date.strftime('%b_%d_%Y_%H_%M_%S')}.log"
        self.csv_rewards = f"simpletakingtricksenv_rewards_{self.date.strftime('%b_%d_%Y_%H_%M_%S')}.csv"
        self.csv_invalid = f"simpletakingtricksenv_invalid_{self.date.strftime('%b_%d_%Y_%H_%M_%S')}.csv"
        self.csv_score = f"simpletakingtricksenv_score_{self.date.strftime('%b_%d_%Y_%H_%M_%S')}.csv"
        self.logger = GameLogger(self.file_name)
        self.csv_inv_log = CSVLogger(self.csv_invalid)
        self.csv_rew_log = CSVLogger(self.csv_rewards)
        self.csv_score_log = CSVLogger(self.csv_score)
        self.player1 = EnvPlayer("player1")
        self.player2 = EnvPlayer("player2")
        self.unknown_stock: List[Card] =[] 
     
    def log_episode_info(self):
        self.player1.save()
        self.player2.save()
        self.csv_inv_log.log((self.player1.invalid_actions, self.player2.invalid_actions, 
                              self.player1.invalid_actions + self.player2.invalid_actions, 
                              self.player1.mean_invalid_actions_count + self.player2.mean_invalid_actions_count))
        self.csv_rew_log.log((self.player1.rewards, self.player2.rewards,
                              self.player1.rewards + self.player2.rewards,
                              self.player1.mean_reward + self.player2.mean_reward))
        self.csv_score_log.log((self.player1.score, self.player2.score,
                                self.player1.score + self.player2.score,
                                self.player1.mean_score + self.player2.mean_score))
        self.logger.append_to_log(f"{self.player1.name}'s' score is {self.player1.score} |\
                                    {self.player2.name}'s' score is {self.player2.score}")

    def end_logging(self):
        self.logger.end_logging()
        self.csv_inv_log.save()
        self.csv_rew_log.save()
        self.csv_score_log.save()

    def reset(self):
        player1 = randint(0, 1) == 1
        cards = self.generator.generate_stack_and_players_cards()
        stock_ind = choice([0, 1], size=1)[0]
        stock, uknown_stock = (cards[stock_ind], cards[int(not stock_ind)])
        self.unknown_stock = uknown_stock

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
    def player_handler(self) -> EnvPlayer:
        return self.player1 if self.is_player1_turn else self.player2

    @property
    def done(self) -> bool:
        return len(self.played_cards) == 20
        
    @property
    def opponent_handler(self) -> EnvPlayer:
        return self.player2 if self.is_player1_turn else self.player1

    def step(self, action: NetworkOutput): 
       return self.__fun(action)

    def __update_rewards(self, reward: float):
        self.player_handler.rewards += reward if reward is not None else 0

    def __update_op_rewards(self, reward: float):
        self.opponent_handler.rewards += reward if reward is not None else 0

    def __own_card_estimator_step(self, agentAction: NetworkOutput):
        action = agentAction.action
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

    def __full_training_step(self, agentAction: NetworkOutput):
        reward = 0
        action = agentAction.action
        op_reward = 0
        card: Card =None
        trump: Suits =self.current_observation["data"].trump
        l = [card for card in self.player_handler.hand_cards if card.id() == action]
        opponent_card: Card = self.current_observation["data"].played_card
        played_cards: List[Card] = self.current_observation["data"].tricks_taken_by_both_players
        known_stock: List[Card] = self.current_observation["data"].known_stock
        the_same_player = False
        if not any(l) or (opponent_card is not None and not GameRules.is_card_valid(
                self.player_handler.hand_cards, l[0], opponent_card, trump)):
            reward = INVALID_MOVE_REWARD
            self.player_handler.invalid_actions += 1
            card = opponent_card
            the_same_player = True
            op_reward = None
        else:
            card = l[0]
            self.player_handler.hand_cards.remove(card)
            card_with_probs = {c.__str__():agentAction.probs[c.id()] for c in self.player_handler.hand_cards}
            self.logger.append_to_log("____________________________________________________________________________")
            self.logger.append_to_log(f"state info: [tricks, unknown stock, known stock, played card, current trump")
            self.logger.append_to_log(f"tricks taken by both players: {played_cards}")
            self.logger.append_to_log(f"unknown stock: {self.unknown_stock}")
            self.logger.append_to_log(f"known stock: {known_stock}")
            self.logger.append_to_log(f"played card: {opponent_card}")
            self.logger.append_to_log(f"current trump: {trump}")
            self.logger.append_to_log("____________________________________________________________________________")
            self.logger.append_to_log(f"{self.player_handler.name}'s cards with probabilities: {card_with_probs}")
            self.logger.append_to_log(self.player_handler.name + " played card " + card.__str__())
            
            reward = VALID_MOVE_REWARD
            if opponent_card is not None:
                self.played_cards.append(card)
                self.played_cards.append(opponent_card)
                trick_value = (card.value.value + opponent_card.value.value)
                trick = [card, opponent_card]
                if GameRules.does_card_beat_opponents_one(card, opponent_card, trump):
                    self.player_handler.tricks.append(trick)
                    reward += trick_value
                    op_reward -= trick_value
                    self.player_handler.score += trick_value
                    the_same_player = True
                else:
                    self.opponent_handler.tricks.append(trick)
                    op_reward = trick_value
                    reward -= trick_value
                    self.opponent_handler.score += trick_value

                card = None
                
            else:
                if(GameRules.has_pair(self.player_handler.hand_cards, card)):
                    reward += (card.suit.value)
                    self.player_handler.score += card.suit.value
                    trump = card.suit
                    self.logger.append_to_log(self.player_handler.name + f" meld {trump.name} by {card} and got {trump.value} points")
                op_reward = None
        self.logger.append_to_log("____________________________________________________________________________")

        rewards = [reward, op_reward]
        self.__update_rewards(reward)
        self.__update_op_rewards(op_reward)
        if not the_same_player:
            self.logger.append_to_log(f"player1_cards: {self.player1.hand_cards}")
            self.logger.append_to_log(f"player2_cards: {self.player2.hand_cards}")
            
        self.is_player1_turn = not self.is_player1_turn if not the_same_player else self.is_player1_turn
        self.current_observation = self.create_observation(trump=trump, card=card)
        return self.current_observation, rewards, self.done

    def __valid_card_estimator_step(self, agentAction: NetworkOutput):
        reward = 0
        action = agentAction.action
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
