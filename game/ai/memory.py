from . import List, State


class Memory:

    def __init__(self):
        self.clean()

    def remember_S_A_R(self, state: State, action: int, reward: float):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)

    def clean(self):
        self.states: List[State] =[]
        self.actions: List[int] =[]
        self.rewards: List[float] =[]

    def update_last_reward(self, reward: float):
        self.rewards[len(self.rewards) - 1] += reward