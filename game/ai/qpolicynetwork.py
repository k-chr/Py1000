from __future__ import annotations
from . import (Activation, Input, Dense, Sequential,InputLayer, TrainingEnum,
               relu, softmax, datetime, Adam, Model, print_tensor,
               categorical_crossentropy, path, k_sum, k_log, List)

class QPolicyNetwork(object):

    __instances: List[QPolicyNetwork] = []

    def __init__(self, fname: str, n_actions: int, batch_size: int, alpha: float, 
                 mem_dir: str, n_one_hot: int, start_from: datetime, flag: TrainingEnum):
        super(QPolicyNetwork, self).__init__()
        self.batch_size = batch_size
        self.states_one_hot_len = n_one_hot
        self.action_output_size = n_actions
        self.network_name = fname
        self.alpha = alpha
        self.init_date = start_from
        self.memories_directory = mem_dir
        self.policy_predictor: Model =None
        self.policy_trainer: Model =None
        self.flag = flag
        
    def predict(self, vec):
        return self.policy_predictor.predict(vec)

    def build_network(self):
        state_input = Input(shape=(self.states_one_hot_len,))
        wrapped = Dense(self.states_one_hot_len)(state_input)
        wrapped = Activation(relu)(wrapped)
        wrapped = Dense(2*self.action_output_size)(wrapped)
        wrapped = Activation(relu)(wrapped)
        wrapped = Dense(self.action_output_size)(wrapped)
        layers = Activation(softmax)(wrapped)
        self.policy_predictor = Model(state_input, layers)
        state = Input(shape=(self.states_one_hot_len,))
        discounted_reward_placeholder = Input(shape=(1,))

        trainer_layers = self.policy_predictor(state)
        model = Model([state, discounted_reward_placeholder], trainer_layers)
        model.compile(optimizer=Adam(learning_rate=self.alpha), 
                     loss=self.loss_function_generator(discounted_reward_placeholder))
        self.policy_trainer = model
        
    def load_weights_from_date(self):
        if not self.init_date is None:
            date = self.init_date.strftime("%b_%d_%Y_%H_%M_%S")
            if not (path.isdir(path.join("previous_memories", f"{self.memories_directory}"))):
                from os import mkdir
                mkdir(path.join("previous_memories", f"{self.memories_directory}"))
            self.policy_predictor.load_weights(path.join("previous_memories",
                                        f"{self.memories_directory}", f"{self.network_name}_{date}.h5"))

    def save_weights_to_date(self):
        date = datetime.now().strftime("%b_%d_%Y_%H_%M_%S")
        if not (path.isdir(path.join("previous_memories", f"{self.memories_directory}"))):
                from os import mkdir
                mkdir(path.join("previous_memories", f"{self.memories_directory}"))
        self.policy_predictor.save_weights(path.join("previous_memories",
                                   f"{self.memories_directory}", f"{self.network_name}_{date}.h5"))

    def loss_function_generator(self, discounted_reward):
        def gradient_loss(pi, pi_prediction):
            loss = -k_sum(discounted_reward * k_log(
                     k_sum(pi * pi_prediction, axis=1)))
            return loss
        return gradient_loss

    @staticmethod
    def get_instance(  name: str, n_actions: int, batch_size: int, alpha: float, 
                 mem_dir: str, n_one_hot: int, start_from: datetime, flag: TrainingEnum):
        l = [__instance for __instance in  QPolicyNetwork.__instances if (
                __instance.states_one_hot_len == n_one_hot and __instance.action_output_size == n_actions and __instance.alpha == alpha 
                and __instance.init_date == start_from and __instance.memories_directory == mem_dir and __instance.network_name == name
                and flag is __instance.flag
            )]
        __instance = None
        if not any(l):
            __instance = QPolicyNetwork(name, n_actions, batch_size, alpha, mem_dir, n_one_hot, start_from, flag)
            QPolicyNetwork.__instances.append(__instance)
            __instance.build_network()
            __instance.load_weights_from_date()

        else:
            __instance = l[0]

        return __instance

