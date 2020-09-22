from .qpolicynetwork import QPolicyNetwork
from . import zeros, State, array, List

class ReinforceAgent(object):
    
    def __init__(self, state_size: int, action_size: int, 
                 gamma: float =0.99, alpha: float =0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.learning_rate = alpha
        self.states_memory: List[State] =[]
        self.actions_memory = []
        self.rewards_memory = []
        self.model: QPolicyNetwork =None
        
    def remember_S_A_R(self, state: State, action: int, reward: float):
        self.states_memory.append(state)
        self.actions_memory.append(action)
        self.rewards_memory.append(reward)

    def get_action(self, state: State):
        vec = state.to_one_hot_vec()[None]
        print(vec.shape)
        print(vec)
        probs = self.model.predict(vec)
        action = choice(range(self.action_size), 1, p=probs)[0]
        return action

    def replay(self):
        state_batch = array([state.to_one_hot_vec() for state in self.states_memory])
        action_batch = array([sample(action) for action in self.actions_memory])
        discounted_rewards_batch = self.get_cumulative_rewards()
        self.model.policy_trainer.train_on_batch([state_batch, discounted_rewards_batch], action_batch)
        self.states_memory = []
        self.actions_memory = []
        self.rewards_memory = []

    def sample(self, action: int):
        z = zeros(self.action_size)
        z[action] = 1
        return z

    def get_cumulative_rewards(self):

        l = len(self.rewards_memory)
        G = zeros(l)
        r_t_1 = 0

        T = reversed(range(0, l))
        for t, r_t in zip(T, self.rewards_memory[::-1]):
            r_t_1 = r_t_1 * self.gamma + r_t
            G[t] = r_t_1
