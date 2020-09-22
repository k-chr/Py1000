from . import (Activation, Input, Dense, Sequential,
               relu, softmax, datetime, SGD,
               categorical_crossentropy, path, sum, log)

class QPolicyNetwork(Sequential):

    def __init__(self, fname: str, n_actions: int, batch_size: int, alpha: float, 
                 mem_dir: str, n_one_hot: int, start_from: datetime,):
        super(QPolicyNetwork, self).__init__()
        self.batch_size = batch_size
        self.states_one_hot_len = n_one_hot
        self.action_output_size = n_actions
        self.network_name = fname
        self.loss_function = loss
        self.alpha = alpha
        self.init_date = start_from
        self.memories_directory = mem_dir
        self.policy_trainer = None

    def build_network(self):
        self.add(Input(shape=(self.states_one_hot_len,)))
        self.add(Dense(self.states_one_hot_len))
        self.add(Activation(relu))
        self.add(Dense(2*self.action_output_size))
        self.add(Activation(relu))
        self.add(Dense(self.action_output_size))
        self.add(Activation(softmax))

        state = Input(shape=(self.states_one_hot_len,))
        discounted_reward_placeholder = Input(shape=(1,))

        layers = self(state)
        model = Sequential([state, discounted_reward_placeholder], layers)
        model.compile(optimizer=SGD(learning_rate=self.alpha), 
                     loss=self.loss_function_generator(discounted_reward_placeholder))
        self.policy_trainer = model
        
    def load_weights_from_date(self):
        if not self.init_date is None:
            date = self.init_date.strftime("%b_%d_%Y_%H_%M_%S")
            if not (path.isdir(path.join("previous_memories", f"{self.memories_directory}"))):
                from os import mkdir
                mkdir(path.join("previous_memories", f"{self.memories_directory}"))
            self.load_weights(path.join("previous_memories",
                                        f"{self.memories_directory}", f"{self.network_name}_{date}.h5"))

    def save_weights_to_date(self):
        date = datetime.now().strftime("%b_%d_%Y_%H_%M_%S")
        if not (path.isdir(path.join("previous_memories", f"{self.memories_directory}"))):
                from os import mkdir
                mkdir(path.join("previous_memories", f"{self.memories_directory}"))
        self.save_weights(path.join("previous_memories",
                                   f"{self.memories_directory}", f"{self.network_name}_{date}.h5"))

    def loss_function_generator(self, discounted_reward):
        def gradient_loss(pi, pi_prediction):
            loss = -sum(discounted_reward * log(
                     sum(pi * pi_prediction, axis=1)))
            return loss
        return gradient_loss
