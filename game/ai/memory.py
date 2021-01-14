from . import (List, State, deque,
               array, choice, Deque,
               fun, ndarray, zeros, 
               NamedTuple)

MAX_DATA_SIZE = 0x2000
MIN_SIZE = 0x20


Batch = NamedTuple("BatchSAR", [('states', ndarray), ('actions', ndarray), ('rewards', ndarray)])

def produce_sample(index: int) -> ndarray:
    empty: ndarray = zeros(MIN_SIZE if index < MIN_SIZE else index + 1)
    empty[index] = 1
    return empty


class Memory:

    def __init__(self):
        self.clean()
        self.init_queues() 

    def remember_S_A_R(self, state: State, action: int, reward: float):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)

    def init_queues(self):
        self.actions_queue: Deque[int] =deque(maxsize=MAX_DATA_SIZE)
        self.states_queue: Deque[State] =deque(maxsize=MAX_DATA_SIZE)
        self.rewards_queue: Deque[float] =deque(maxsize=MAX_DATA_SIZE)

    def clean(self, reward_mapper: fun[[float], float] =None, rewards_mapper: fun[[List[float], List[float]]]=None):
        if reward_mapper is not None:
            for i in range(len(self.rewards)):
                self.rewards[i] = reward_mapper(self.rewards[i])
        if rewards_mapper is not None:
            self.rewards = rewards_mapper(self.rewards)

        for i in range(len(self.states)):
            self.actions_queue.append(self.actions[i])
            self.states_queue.append(self.states[i])
            self.rewards_queue.append(self.rewards[i] if reward_mapper is None else reward_mapper(self.rewards[i]))
        self.states: List[State] =[]
        self.actions: List[int] =[]
        self.rewards: List[float] =[]

    def update_last_reward(self, reward: float):
        self.rewards[len(self.rewards) - 1] += reward

    def prepare_sample_batch(self, batch_size=MIN_SIZE, action_mapper: fun[[int], ndarray] =lambda x: produce_sample(x), 
        state_mapper: fun[[State], ndarray] =lambda s: s.to_one_hot_vec()) -> Batch:

        indices: List[int] = choice(range(len(self.states_queue)), batch_size if batch_size >= MIN_SIZE else MIN_SIZE, replace=False)
        s: List[ndarray] = []
        a: List[ndarray] = []
        r: List[ndarray] = []
        for idx in indices:
            s.append(state_mapper(self.states_queue[idx]))
            a.append(action_mapper(self.actions_queue[idx]))
            r.append(array(self.rewards_queue[idx]))

        return Batch(array(s), array(a), array(r))
