from .reinforceagent import ReinforceAgent
from .qpolicynetwork import QPolicyNetwork
from . import datetime, List, TakingTrickState, choice, State, TrainingEnum

class TakingTricksAgent(ReinforceAgent):

    def __init__(self, batch_size, prefix: str,
                 gamma=0.99, alpha=0.0001, last_weights: datetime=None,
                 state_size=100, action_size=24, flag: TrainingEnum =TrainingEnum.FULL_TRAINING):
        super(TakingTricksAgent, self).__init__(state_size, action_size, gamma=gamma, alpha=alpha, flag=flag)

        self.model = QPolicyNetwork.get_instance("TakingTricksAgent", action_size, batch_size,
                                   alpha, prefix, state_size, last_weights, flag)
