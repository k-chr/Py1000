from .reinforceagent import ReinforceAgent
from .qpolicynetwork import QPolicyNetwork
from . import datetime, TakingTrickState, TrainingEnum, ndarray, array, zeros, GameRules, List, State, choice
from .memory import Memory

def _get_own_cards_vec(state: TakingTrickState) -> ndarray:
    hand = zeros(24)
    for card in state.hand_cards:
        hand[card.id()] = 1
    return hand

def _get_valid_cards_vec(state: TakingTrickState) -> ndarray:
    if state.played_card is None:
        return _get_own_cards_vec(state)

    hand = zeros(24)
    for card in state.hand_cards:
        if GameRules.is_card_valid(state.hand_cards, card, state.played_card, state.trump):
            hand[card.id()] = 1
    return hand


class TakingTricksAgent(ReinforceAgent):

    @property
    def __MAX_ERRORS(self):
        return 500

    def __init__(self, batch_size, prefix: str,
                 gamma=0.99, alpha=0.0001, last_weights: datetime=None,
                 state_size=100, action_size=24, flag: TrainingEnum =TrainingEnum.FULL_TRAINING):
        super(TakingTricksAgent, self).__init__(state_size, action_size, gamma=gamma, alpha=alpha, flag=flag)

        self.model = QPolicyNetwork.get_instance("TakingTricksAgent", action_size, batch_size,
                                   alpha, prefix, state_size, last_weights, flag)
        self.__errors = 0

    def get_action(self, state: State) -> int:
        if self.__errors >= self.__MAX_ERRORS and self.flag is TrainingEnum.FULL_TRAINING:
            self.__errors = 0
            vec = list(map(lambda card: card.id(), list(filter(lambda x:GameRules.is_card_valid(
                    state.hand_cards, x, state.played_card, trump=state.trump), state.hand_cards
                ))))
            return choice(vec, 1)[0]
            
        return super().get_action(state)

    def remeber_traumatic_S_A_R(self, state: State, action: int, reward: float):
        self.__errors += 1
        return super().remeber_traumatic_S_A_R(state, action, reward)
    
    def remember_S_A_R(self, state: State, action: int, reward: float):
        self.errors = 0
        return super().remember_S_A_R(state, action, reward)

    def actions_batch(self, memory: Memory) -> ndarray:

        if self.flag is TrainingEnum.FULL_TRAINING:
            return super().actions_batch(memory)
        elif self.flag is TrainingEnum.PRETRAINING_OWN_CARDS:
            return array([_get_own_cards_vec(state) for state in memory.states])
        else:
            return array([_get_valid_cards_vec(state) for state in memory.states])
