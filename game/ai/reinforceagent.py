from .qpolicynetwork import QPolicyNetwork
from . import zeros, State, array, List, choice, TrainingEnum, ndarray, argmax, int64

class ReinforceAgent(object):
    
    def __init__(self, state_size: int, action_size: int, 
                 gamma: float =0.99, alpha: float =0.001, flag: TrainingEnum =TrainingEnum.FULL_TRAINING):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.learning_rate = alpha
        self.states_memory: List[State] =[]
        self.actions_memory = []
        self.rewards_memory = []
        self.model: QPolicyNetwork =None
        self.flag = flag
        self.__action_getter = self.get_action_from_probs if self.flag is TrainingEnum.FULL_TRAINING else self.get_action_from_value

    def remember_S_A_R(self, state: State, action: int, reward: float):
        self.states_memory.append(state)
        self.actions_memory.append(action)
        self.rewards_memory.append(reward)

    def get_action(self, state: State):
        vec = state.to_one_hot_vec()[None]
        return self.__action_getter(vec)

    def get_action_from_probs(self, vec):
        probs = self.model.predict_probs(vec)
        try:
            action = choice(range(self.action_size), 1, p=probs[0])[0]
            return action
        except:
            print(f"probabilities: {probs[0]} contains NaN")
            raise Exception

    def get_action_from_value(self, vec):    
        values = self.model.predict_values(vec)
        indices = argmax(values[0])
        if isinstance(indices, int64):
            return indices
        if len(indices) == 1:
            return indices[0]
        action = choice(indices, 1)[0]
        return action

    def replay(self):
        state_batch = array([state.to_one_hot_vec() for state in self.states_memory])
        action_batch = self.actions_batch()
        discounted_rewards_batch = self.get_cumulative_rewards() if self.flag is TrainingEnum.FULL_TRAINING else array(self.rewards_memory)
        try:
            d = {'state':state_batch, 'discounted_reward':discounted_rewards_batch} if self.flag is TrainingEnum.FULL_TRAINING else {'state':state_batch}
            self.model.policy_trainer.fit(d, action_batch, epochs=1) 
            print('Replayed successfully')       
        except Exception as e:
            import sys
            import traceback
            print(f"type of exception {type(e)}")
            print(f"shapes: st {state_batch.shape} | act {action_batch.shape} | rew {discounted_rewards_batch.shape}")
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
        self.clean_memory()

    def actions_batch(self) -> ndarray:
        return array([self.sample(action) for action in self.actions_memory])

    def clean_memory(self):
        self.states_memory = []
        self.actions_memory = []
        self.rewards_memory = []

    def sample(self, action: int) -> ndarray:
        z: ndarray =zeros(self.action_size)
        z[action] = 1
        return z

    def get_cumulative_rewards(self) -> ndarray:

        l = len(self.rewards_memory)
        G = zeros(l)
        r_t_1 = 0

        T = reversed(range(0, l))
        for t, r_t in zip(T, self.rewards_memory[::-1]):
            r_t_1 = r_t_1 * self.gamma + r_t
            G[t] = r_t_1
        return array([array(g) for g in G])
