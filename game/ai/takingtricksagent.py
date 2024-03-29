from typing import Deque
import operator
from .reinforceagent import (ReinforceAgent, Batch, MIN_SIZE_OF_BATCH,
                             get_cumulative_rewards, NetworkOutput,
                             get_cumulative_reward_reversed)
from .qpolicynetwork import QPolicyNetwork
from .qpolicydnncluster import TakingTrickQPolicyDNNCluster
from . import (datetime, TakingTrickState, NetworkMode, 
               RewardMapperMode, TrainingEnum, ndarray, 
               array, zeros, GameRules, List, State,
               choice, Dict, fun, Union)
from ..states import DECK_SIZE
from .memory import Memory
from .memorycluster import TakingTrickClusterMemory

def _get_own_cards_vec(state: TakingTrickState) -> ndarray:
    hand: ndarray =zeros(state.action_space)

    for card in state.hand_cards:
        hand[card.id()] = 1

    return hand

def get_reward_modifier(beta: float) -> fun[[float], float]:

    def wrapped(reward: float):
        return beta * reward
    
    return wrapped

def _get_valid_cards_vec(state: TakingTrickState) -> ndarray:

    if state.played_card is None:
        return _get_own_cards_vec(state)

    hand: ndarray =zeros(state.action_space)

    for card in state.hand_cards:
        if GameRules.is_card_valid(state.hand_cards, card, state.played_card, state.trump):
            hand[card.id()] = 1

    return hand

def _sample_state(state: State) -> ndarray:
    return state.to_one_hot_vec()

rewards_mappers: Dict[RewardMapperMode, fun[[float], fun[[List[float]], List[float]]]] = {
    RewardMapperMode.DISCOUNTED: get_cumulative_rewards, 
    RewardMapperMode.DISCOUNTED_REVERSED: get_cumulative_reward_reversed,
    RewardMapperMode.NOT_MODIFIED: lambda _: lambda arr: arr
}

action_mappers: Dict[TrainingEnum, Union[fun[[TakingTrickState], ndarray], fun[[int], ndarray]]] = {
    TrainingEnum.PRETRAINING_OWN_CARDS: _get_own_cards_vec,
    TrainingEnum.PRETRAINING_VALID_CARDS: _get_valid_cards_vec
}


class TakingTricksAgent(ReinforceAgent):

    @property
    def __MAX_ERRORS(self):
        return 1

    def __init__(self, batch_size: int, prefix: str, session: str,
                 gamma: float =0.99, alpha: float =0.0001, last_weights: datetime =None,
                 state_size: int =100, action_size: int =DECK_SIZE(), flag: TrainingEnum =TrainingEnum.FULL_TRAINING, 
                 mode: NetworkMode =NetworkMode.SINGLE, reward_mode: RewardMapperMode =RewardMapperMode.DISCOUNTED):
        super(TakingTricksAgent, self).__init__(session, state_size, action_size, gamma=gamma, alpha=alpha, flag=flag, mode=mode)
        initializer, memory_initializer = (TakingTrickQPolicyDNNCluster.get_instance, TakingTrickClusterMemory) if mode & NetworkMode.CLUSTER else (QPolicyNetwork.get_instance, Memory)
        self.model: Union[QPolicyNetwork, TakingTrickQPolicyDNNCluster] =initializer("TakingTricksAgent", session, action_size, batch_size,
                                   alpha, prefix, state_size, last_weights, flag, mode)
        self.memory = memory_initializer()
        self.traumatic_memory = memory_initializer()
        self.errors = 0
        self.__batch_size = batch_size
        self.__rewards_mapper: fun[[List[float]], List[float]] = rewards_mappers[reward_mode](self.gamma)
        self.__action_mapper = action_mappers.get(self.flag, self.sample)
        self.__state_mapper: fun[[State], ndarray] = _sample_state

    def act(self, state: TakingTrickState) -> NetworkOutput:
        output = self.get_action_from_value(state.to_one_hot_vec())
        if self.errors >= self.__MAX_ERRORS:
            self.errors = 0
            vec: List[int] =list(map(lambda card: card.id(), list(filter(lambda x: GameRules.is_card_valid(
                    state.hand_cards, x, state.played_card, trump=state.trump), state.hand_cards
                ))))
            d = {idx:output.probs[idx] for idx in vec}
            action = max(d.items(), key=operator.itemgetter(1))[0]
            output = NetworkOutput(action, output.probs[action], output.probs)
        return output

    def get_action(self, state: TakingTrickState) -> NetworkOutput:
        output = self._action_getter(state.to_one_hot_vec(), cards_in_hand=len(state.hand_cards))
        if self.errors >= self.__MAX_ERRORS:
            self.errors = 0
            state: TakingTrickState =state
            vec: List[int] =list(map(lambda card: card.id(), list(filter(lambda x: GameRules.is_card_valid(
                    state.hand_cards, x, state.played_card, trump=state.trump), state.hand_cards
                ))))
            action: int = choice(vec, 1)[0]
            output = NetworkOutput(action, output.probs[action], output.probs)
        
        return output

    def persist_episode_and_clean_memory(self) -> None:
        self.memory.save_data_for_replay_and_clean_temp(rewards_mapper=self.__rewards_mapper, 
                                                        reward_mapper=get_reward_modifier(self.beta))
                                                        
        self.traumatic_memory.save_data_for_replay_and_clean_temp(rewards_mapper=self.__rewards_mapper, 
                                                                  reward_mapper=get_reward_modifier(self.beta_penalty))

    def remember_traumatic_S_A_R_B(self, state: State, action: int, reward: float, behavior: List[float]):
        return super().remember_traumatic_S_A_R_B(state, action, reward, behavior)
    
    def remember_S_A_R_B(self, state: State, action: int, reward: float, behavior: List[float]):
        return super().remember_S_A_R_B(state, action, reward, behavior)

    def _get_sample_batch_from_memory(self, memory: Memory, batch_size: int) -> Union[Batch, Dict[int, Batch]]:
        get_action_vec = self.__action_mapper
        state_mapper = self.__state_mapper
        clipped = batch_size if batch_size >= MIN_SIZE_OF_BATCH else MIN_SIZE_OF_BATCH
        
        if self.mode & NetworkMode.CLUSTER:
            m: TakingTrickClusterMemory = memory

            return {i:prepare_batch_from_indices(mem, get_action_vec, state_mapper, self.__action_source(mem), 
                    list(range(mem.length)), clipped) for i, mem in m.cluster.items()}

        indices: List[int] = list(range(memory.length))

        return prepare_batch_from_indices(memory, get_action_vec, state_mapper, self.__action_source(memory), indices, clipped)

    def _replay(self, memory: Memory, message):
        data = self._get_sample_batch_from_memory(memory, self.__batch_size)
        self.model.train(data, message)

    def __action_source(self, memory: Memory):
        return memory.actions_queue\
                if self.flag is TrainingEnum.FULL_TRAINING \
                else memory.states_queue

    def clean_up(self):
        self.model.clean()

def prepare_batch_from_indices(memory: Memory, get_action_vec: Union[fun[[TakingTrickState], ndarray], fun[[int], ndarray]],
                               state_mapper: fun[[State], ndarray], action_source: Union[Deque[State],Deque[int]], indices: List[int], clipped: int) -> Batch:

    if memory.length < clipped:
        return None

    s: List[ndarray] =[]
    a: List[ndarray] =[]
    r: List[ndarray] =[]
    b: List[ndarray] =[]

    indices = choice(indices, clipped, replace=False)

    for idx in indices:
        s.append(state_mapper(memory.states_queue[idx]))
        a.append(get_action_vec(action_source[idx]))
        r.append(array(memory.rewards_queue[idx]))
        b.append(array(memory.behaviors_queue[idx]))

    return Batch(array(s), array(a), array(r), array(b))
