from .reinforceagent import ReinforceAgent
from .qpolicynetwork import QPolicyNetwork
from . import datetime, List, GiveawayState, choice, State, TrainingEnum

class GiveawayAgent(ReinforceAgent):

    def __init__(self, batch_size, prefix: str,
                 gamma=0.99, alpha=0.001, last_weights: datetime =None,
                 state_size=24, action_size=24, flag: TrainingEnum =TrainingEnum.FULL_TRAINING):
        super(GiveawayAgent, self).__init__(state_size, action_size, gamma=gamma, alpha=alpha, flag=flag)

        self.model = QPolicyNetwork.get_instance("GiveawayAgent", action_size, batch_size,
                                   alpha, prefix, state_size, last_weights, flag)
