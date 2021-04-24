from .qpolicynetwork import QPolicyNetwork
from . import (zeros, State, array, List, Dict, reshape,
               choice, TrainingEnum, ndarray, NetworkOutput,
               argmax, int64, fun, Batch, NetworkMode)
from .memory import Memory

MIN_SIZE_OF_BATCH = 0x20
ACTION_SIZE = 0x18

def zeros_as_list(len: int) -> List[float]:
    return [0 for _ in range(len)]

def get_cumulative_rewards(gamma: float =0.9) -> fun[[List[float]], List[float]]:

    def wrapped(arr: List[float]):
        l = len(arr)
        G = zeros_as_list(l)
        r_t_1 = 0
        T = reversed(range(0, l))

        for t, r_t in zip(T, arr[::-1]):
            r_t_1 = r_t_1 * gamma + r_t
            G[t] = r_t_1

        return G
    
    return wrapped

def get_cumulative_reward_reversed(gamma: float =0.9) -> fun[[List[float]], List[float]]:

    def wrapped(arr: List[float]):

        l = len(arr)
        G = zeros_as_list(l)
        r_t_1 = 0
        T = range(0, l)

        for t, r_t in zip(T, arr):
            r_t_1 = r_t_1 * gamma + r_t
            G[t] = r_t_1

        return G

    return wrapped

FACTORS = {
    60: 1.2,
    90: 1.2**2,
    120:1.2**3,
    150:1.2**4,
    180:1.2**5,
    210:1.2**6,
    240:1.2**7,
    300:1.2**8
}

PENALTIES = {
    10: 1.4,
    20: 1.4**2,
    40: 1.4**3,
    80: 1.4**4,
    160: 1.4**5,
    320: 1.4**6,
    640: 1.4**7
}


class ReinforceAgent(object):
    
    def __init__(self, session: str, state_size: int, action_size: int, 
                 gamma: float =0.99, alpha: float =0.001, flag: TrainingEnum =TrainingEnum.FULL_TRAINING, mode: NetworkMode = NetworkMode.SINGLE):
        self.state_size = state_size
        self.session = session
        self.action_size = action_size
        self.gamma = gamma
        self.learning_rate = alpha
        self.traumatic_memory: Memory =Memory()
        self.memory: Memory =Memory()
        self.model: QPolicyNetwork =None
        self.flag = flag
        self.mode = mode
        self.score = 0
        self.invalid_actions = 0
        self._action_getter = self.get_action_from_probs if self.flag is TrainingEnum.FULL_TRAINING else self.get_action_from_value

    def remember_S_A_R_B(self, state: State, action: int, reward: float, behavior: List[float]):
        self.memory.remember_S_A_R_B(state, action, reward, behavior)
        
    def remember_traumatic_S_A_R_B(self, state: State, action: int, reward: float, behavior: List[float]):
        self.traumatic_memory.remember_S_A_R_B(state, action, reward, behavior)

    def get_action(self, state: State) -> NetworkOutput:
        pass

    def get_action_from_probs(self, vec: ndarray, **args) -> NetworkOutput:
        probs = self.model.predict_probs(reshape(vec, [1, self.state_size]), **args)[0]
        try:
            action = choice(range(self.action_size), 1, p=probs)[0]
            return NetworkOutput(action, probs[action], probs)
        except:
            print(f"probabilities: {probs} contains NaN")
            raise Exception

    def get_action_from_value(self, vec: ndarray, **args) -> NetworkOutput:    
        values = self.model.predict_values(reshape(vec, [1, self.state_size]), **args)[0]
        indices = argmax(values)
        action = 0
        if isinstance(indices, int64):
            action = indices
        elif len(indices) == 1:
            action = indices[0]
        else:
            action = choice(indices, 1)[0]
        return NetworkOutput(action, values[action], values)
    
    def set_score(self, score: int):
        self.score = score 

    def set_invalid_actions_count(self, invalid_actions: int):
        self.invalid_actions = invalid_actions

    @property
    def beta(self):
        return FACTORS.get(max(list(filter(lambda x: x <= self.score, FACTORS.keys())), default=0), 1)

    @property
    def beta_penalty(self):
        return PENALTIES.get(max(list(filter(lambda x: x <= self.invalid_actions, PENALTIES.keys())), default=0), 1)

    def replay(self):
        self.persist_episode_and_clean_memory()
        self._replay(self.memory, message="Learning positive memories...")
        self._replay(self.traumatic_memory, message="Learning negative memories...")

    def sample(self, action: int) -> ndarray:
        z: ndarray =zeros(self.action_size)
        z[action] = 1
        return z

    def persist_episode_and_clean_memory(self) -> None:
        pass

    def _get_sample_batch_from_memory(self, memory: Memory, batch_size: int =MIN_SIZE_OF_BATCH) -> Dict[int, Batch]: 
        pass

    def _replay(self, memory: Memory, message=""):
        pass

    def clean_up(self):
        pass
