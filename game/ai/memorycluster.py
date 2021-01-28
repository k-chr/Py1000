from .memory import Memory, fun, List
from . import Dict, MIN_CARDS_IN_HAND, MAX_CARDS_IN_HAND
from ..states.takingtrickstate import TakingTrickState

SINGLE_CLUSTER_SIZE = 0x1000

class TakingTrickClusterMemory(Memory):

    def __init__(self):
        self.init_queues()

    def init_queues(self):
        self.cluster: Dict[int, Memory] = {i:Memory(SINGLE_CLUSTER_SIZE) for i in range(MIN_CARDS_IN_HAND, MAX_CARDS_IN_HAND + 1)}

    def remember_S_A_R_B(self, state: TakingTrickState, action: int, reward: float, behavior: List[float]):
        self.cluster[len(state.hand_cards)].remember_S_A_R_B(state, action, reward, behavior)

    def update_last_reward(self, reward: float, state: TakingTrickState):
        memory = self.cluster[len(state.hand_cards)]
        memory.rewards[len(memory.rewards) - 1] += reward

    def save_data_for_replay_and_clean_temp(self, reward_mapper: fun[[float], float], rewards_mapper: fun[[List[float]], List[float]]):
        for _, memory in self.cluster.items():
            memory.save_data_for_replay_and_clean_temp(reward_mapper, rewards_mapper)
