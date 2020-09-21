from .reinforceagent import ReinforceAgent
from .qpolicynetwork import QPolicyNetwork
from . import datetime, List, TakingTrickState, choice, State

class TakingTricksAgent(ReinforceAgent):

    def __init__(self, batch_size, prefix: str,
                 gamma=0.99, alpha=0.001, last_weights: datetime=None,
                 state_size=100, action_size=24):
        super(TakingTricksAgent, self).__init__(state_size, action_size, gamma=gamma, alpha=alpha)

        self.model = QPolicyNetwork("TakingTricksAgent", action_size, batch_size,
                                   alpha, prefix, state_size, last_weights)

        self.model.build_network()
        self.model.load_weights_from_date()
   