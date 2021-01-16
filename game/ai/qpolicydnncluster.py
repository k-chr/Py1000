from __future__ import annotations
from .qpolicynetwork import QPolicyNetwork
from . import Dict, datetime, TrainingEnum, NetworkMode, ndarray, Union, Batch, List

MAX_CARDS_IN_HAND = 0xA

class TakingTrickQPolicyDNNCluster(QPolicyNetwork):

    __instances: List[TakingTrickQPolicyDNNCluster] =[] 

    def __init__(self, fname: str, n_actions: int, batch_size: int, alpha: float, mem_dir: str, n_one_hot: int, 
                       start_from: datetime, flag: TrainingEnum, mode: NetworkMode):
        super().__init__(fname, n_actions, batch_size, alpha, mem_dir, n_one_hot, start_from, flag, mode)
        self.nodes : Dict[int, QPolicyNetwork] ={}

    def build_network(self):
        for i in range(2, MAX_CARDS_IN_HAND + 1):
            self.nodes[i] = QPolicyNetwork.get_instance(f'{self.network_name}_node_{i}', self.action_output_size, self.batch_size, 
                                                           self.alpha, self.memories_directory, self.states_one_hot_len, self.init_date, self.flag, self.mode)
        
    def predict_probs(self, vec: ndarray, cards_in_hand: int):
        if cards_in_hand >= 2 and cards_in_hand <= MAX_CARDS_IN_HAND:
            self.policy_predictor = self.nodes[cards_in_hand].policy_predictor

        return super().predict_probs(vec)
    
    def predict_values(self, vec: ndarray, cards_in_hand: int):
        if cards_in_hand >= 2 and cards_in_hand <= MAX_CARDS_IN_HAND:
            self.policy_predictor = self.nodes[cards_in_hand].policy_predictor

        return super().predict_values(vec)

    def save_weights_to_date(self):
        for _, node in self.nodes.items():
            node.save_weights_to_date()

    def learn(self, memory: Union[Batch, Dict[int, Batch]]):
        if isinstance(memory, Batch):
            return super().learn(memory)

        for idx, batch in memory.items():
            self.nodes[idx].learn(batch)

    
    @staticmethod
    def get_instance(name: str, n_actions: int, batch_size: int, alpha: float, 
                 mem_dir: str, n_one_hot: int, start_from: datetime, flag: TrainingEnum, mode: NetworkMode =NetworkMode.SINGLE):
        l = [__instance for __instance in TakingTrickQPolicyDNNCluster.__instances if (
                __instance.states_one_hot_len == n_one_hot and __instance.action_output_size == n_actions and __instance.alpha == alpha 
                and __instance.init_date == start_from and __instance.memories_directory == mem_dir and __instance.network_name == name
                and flag is __instance.flag and mode & __instance.mode
            )]
        __instance = None

        if not any(l):
            __instance = TakingTrickQPolicyDNNCluster(name, n_actions, batch_size, alpha, mem_dir, n_one_hot, start_from, flag, mode)
            TakingTrickQPolicyDNNCluster.__instances.append(__instance)
            __instance.build_network()

        else:
            __instance = l[0]

        return __instance
    