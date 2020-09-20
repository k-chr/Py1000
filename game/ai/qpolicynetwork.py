from . import Activation, Dense, Sequential, relu, softmax, datetime, SGD, categorical_crossentropy, path

class QPolicyNetwork(Sequential):

    def __init__(self, fname: str, n_actions: int, batch_size: int, alpha: float, mem_dir: str,
                 dump_period: int, n_one_hot: int, start_from: datetime, loss=None):
        super(QPolicyNetwork, self).__init__()
        self.batch_size = batch_size
        self.dump_period = dump_period
        self.states_one_hot_len = n_one_hot
        self.action_output_size = n_actions
        self.network_name = fname
        self.loss_function = loss
        self.alpha = alpha
        self.init_date = start_from
        self.memories_directory = mem_dir

    def build_network(self):
        self.add(Dense(128, input_shape=(self.states_one_hot_len, self.batch_size)))
        self.add(Activation(relu))
        self.add(Dense(128))
        self.add(Activation(relu))
        self.add(Dense(self.action_output_size))
        self.add(Activation(softmax))
        self.compile(optimizer=SGD(learning_rate=self.alpha), loss= self.loss_function or categorical_crossentropy)
        
    def load_weights_from_date(self):
        if not self.init_date is None:
            date = self.init_date.strftime("%b_%d_%Y_%H_%M_%S")
            self.load_weights(path.join("previous_memories", f"{self.memories_directory}", f"{self.network_name}_{date}.h5"))

    def save_weights_to_date(self):
        date = datetime.now().strftime("%b_%d_%Y_%H_%M_%S")
        self.save_weights(path.join("previous_memories", f"{self.memories_directory}", f"{self.network_name}_{date}.h5"))
