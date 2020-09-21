from .reinforceagent import ReinforceAgent
from .qpolicynetwork import QPolicyNetwork
from . import datetime, List, GiveawayState, choice, State

class GiveawayAgent(ReinforceAgent):

    def __init__(self, batch_size, prefix: str,
                 gamma=0.99, alpha=0.001, last_weights: datetime =None,
                 state_size=24, action_size=24):
        super(GiveawayAgent, self).__init__(state_size, action_size, gamma=gamma, alpha=alpha)

        self.model = QPolicyNetwork("GiveawayAgent", action_size, batch_size,
                                   alpha, prefix, state_size, last_weights)

        self.model.build_network()
        self.model.load_weights_from_date()
   
