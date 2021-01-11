from .qpolicynetwork import QPolicyNetwork
from . import zeros, State, array, List, choice, TrainingEnum, ndarray, argmax, int64
from .memory import Memory

def get_cumulative_rewards(arr: List[float], gamma: float =0.9) -> ndarray:
  l = len(arr)
  G = zeros(l)
  r_t_1 = 0
  T = reversed(range(0, l))
  for t, r_t in zip(T, arr[::-1]):
      r_t_1 = r_t_1 * gamma + r_t
      G[t] = r_t_1
  return array([array(g) for g in G])

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


class ReinforceAgent(object):
    
    def __init__(self, state_size: int, action_size: int, 
                 gamma: float =0.99, alpha: float =0.001, flag: TrainingEnum =TrainingEnum.FULL_TRAINING):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.learning_rate = alpha
        self.traumatic_memory: Memory =Memory()
        self.memory: Memory =Memory()
        self.model: QPolicyNetwork =None
        self.flag = flag
        self.__action_getter = self.get_action_from_probs if self.flag is TrainingEnum.FULL_TRAINING else self.get_action_from_value

    def remember_S_A_R(self, state: State, action: int, reward: float):
        self.memory.remember_S_A_R(state, action, reward)

    def remeber_traumatic_S_A_R(self, state: State, action: int, reward: float):
        self.traumatic_memory.remember_S_A_R(state, action, reward)

    def get_action(self, state: State):
        vec = state.to_one_hot_vec()[None]
        return self.__action_getter(vec)

    def get_action_from_probs(self, vec: ndarray):
        probs = self.model.predict_probs(vec)
        try:
            action = choice(range(self.action_size), 1, p=probs[0])[0]
            return action
        except:
            print(f"probabilities: {probs[0]} contains NaN")
            raise Exception

    def get_action_from_value(self, vec: ndarray):    
        values = self.model.predict_values(vec)
        indices = argmax(values[0])
        if isinstance(indices, int64):
            return indices
        if len(indices) == 1:
            return indices[0]
        action = choice(indices, 1)[0]
        return action

    def replay(self):
        self.__replay(self.memory.states, self.memory.actions, self.memory.rewards, message="Learning positive memories...")
        self.__replay(self.traumatic_memory.states, self.traumatic_memory.actions, self.traumatic_memory.rewards, message="Learning negative memories...")
        self.clean_memory()

    def __replay(self, states: List[State], actions: List[int], rewards: List[float], message=""):
        state_batch = self.states_batch(states)
        action_batch = self.actions_batch(actions)
        discounted_rewards_batch = self.get_cumulative_rewards(rewards) if self.flag is TrainingEnum.FULL_TRAINING else array(rewards)
        if(len(state_batch) == 0 or len(action_batch) == 0 or len(discounted_rewards_batch) == 0):
            return
        print(message)
        try:
            d = {'state':state_batch, 'discounted_reward':discounted_rewards_batch} if self.flag is TrainingEnum.FULL_TRAINING else {'state':state_batch}
            self.model.policy_trainer.fit(d, action_batch, epochs=1) 
        except Exception as e:
            print(e)

    def replay_traumatic_only(self):
        self.__replay(self.traumatic_memory.states, self.traumatic_memory.actions, self.traumatic_memory.rewards, message="Learning negative memories...")
        self.traumatic_memory.clean()

    def actions_batch(self, actions: List[int]) -> ndarray:
        return array([self.sample(action) for action in actions])

    def states_batch(self, states: List[State]) -> ndarray:
        return array([state.to_one_hot_vec() for state in states])

    def clean_memory(self) -> None:
        self.memory.clean()
        self.traumatic_memory.clean()

    def sample(self, action: int) -> ndarray:
        z: ndarray =zeros(self.action_size)
        z[action] = 1
        return z

    def get_cumulative_rewards(self, rewards: List[float]) -> ndarray:
        return get_cumulative_rewards(rewards, self.gamma)

    def scale_rewards(self, score: int):
        beta = FACTORS.get(max(list(filter(lambda x: x <= score, FACTORS.keys())), default=0), 1)
        for i in range(len(self.memory.rewards)):
            self.memory.rewards[i] *= beta
