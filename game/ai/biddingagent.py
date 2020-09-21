from .reinforceagent import ReinforceAgent
from .qpolicynetwork import QPolicyNetwork
from . import datetime, List, BiddingState, choice, State

class BiddingAgent(ReinforceAgent):

    def __init__(self, batch_size, prefix: str,
                 gamma=0.99, alpha=0.001, last_weights: datetime =None,
                 state_size=51, action_size=2):
        super(BiddingAgent, self).__init__(state_size, action_size, gamma=gamma, alpha=alpha)

        self.model = QPolicyNetwork("BiddingAgent", action_size, batch_size,
                                   alpha, prefix, state_size, last_weights)

        self.model.build_network()
        self.model.load_weights_from_date()
   