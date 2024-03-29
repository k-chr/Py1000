from . import (List, State, deque,
               Deque, fun)

MAX_DATA_SIZE = 0x4000


class Memory:

    def __init__(self, max_size: int =MAX_DATA_SIZE):
        self.max_size = max_size
        self.__clean()
        self.init_queues() 
        self._length = 0

    @property
    def length(self):
        return self._length

    def remember_S_A_R_B(self, state: State, action: int, reward: float, behavior: List[float]):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.behaviors.append(behavior)

    def init_queues(self):
        self.actions_queue: Deque[int] =deque(maxlen=self.max_size)
        self.states_queue: Deque[State] =deque(maxlen=self.max_size)
        self.rewards_queue: Deque[float] =deque(maxlen=self.max_size)
        self.behaviors_queue: Deque[List[float]] =deque(maxlen=self.max_size)

    def save_data_for_replay_and_clean_temp(self, reward_mapper: fun[[float], float] =None,
                                                  rewards_mapper: fun[[List[float]], List[float]] =None):

        if reward_mapper is not None:

            for i in range(len(self.rewards)):
                self.rewards[i] = reward_mapper(self.rewards[i])

        if rewards_mapper is not None:
            self.rewards = rewards_mapper(self.rewards)

        for i in range(len(self.states)):
            self.actions_queue.append(self.actions[i])
            self.states_queue.append(self.states[i])
            self.rewards_queue.append(self.rewards[i])
            self.behaviors_queue.append(self.behaviors[i])
            self._length = min((self.max_size, self._length + 1))

        self.__clean()

    def __clean(self):
        self.states: List[State] =[]
        self.actions: List[int] =[]
        self.rewards: List[float] =[]
        self.behaviors: List[List[float]] =[]

    def update_last_reward(self, reward: float, state: State):
        self.rewards[len(self.rewards) - 1] += reward
