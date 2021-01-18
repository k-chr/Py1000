from .reinforceagent import ReinforceAgent
from .qpolicynetwork import QPolicyNetwork
from . import datetime, List, BiddingState, choice, State, TrainingEnum

class BiddingAgent(ReinforceAgent):

    def __init__(self, batch_size, prefix: str,
                 gamma=0.99, alpha=0.001, last_weights: datetime =None,
                 state_size=51, action_size=2, flag: TrainingEnum =TrainingEnum.FULL_TRAINING):
        super(BiddingAgent, self).__init__(state_size, action_size, gamma=gamma, alpha=alpha, flag=flag)

        self.model = QPolicyNetwork.get_instance("BiddingAgent", action_size, batch_size,
                                   alpha, prefix, state_size, last_weights, flag)
