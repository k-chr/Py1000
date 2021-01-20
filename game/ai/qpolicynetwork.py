from __future__ import annotations

from . import (Activation, Input, Dense, n_sum, NetworkMode,
               TrainingEnum, relu, softmax, datetime,
               Adam, Model, ndarray, nan_to_num, path,
               k_sum, k_log, List, SGD, Tensor, MSE, Batch, reshape)


class QPolicyNetwork(object):

    __instances: List[QPolicyNetwork] =[]

    def __init__(self, fname: str, n_actions: int, batch_size: int, alpha: float, 
                 mem_dir: str, n_one_hot: int, start_from: datetime, flag: TrainingEnum, mode: NetworkMode):
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
        self.mode = mode
        self.layer_scale = 16 if self.mode & NetworkMode.LARGE else 4
        
    def predict_probs(self, vec: ndarray, **args):
        probs = nan_to_num(self.policy_predictor.predict(reshape(vec, [1, self.states_one_hot_len])))
        return probs / n_sum(probs)

    def predict_values(self, vec: ndarray, **args):
        values = self.policy_predictor.predict(reshape(vec, [1, self.states_one_hot_len]))
        return values

    def build_network(self):
        state_input = Input(shape=(self.states_one_hot_len,))
        wrapped = Dense(self.states_one_hot_len)(state_input)
        wrapped = Activation(relu)(wrapped)
        wrapped = Dense(self.layer_scale*self.states_one_hot_len)(wrapped)
        wrapped = Activation(relu)(wrapped)
        wrapped = Dense(self.layer_scale*self.action_output_size)(wrapped)
        wrapped = Activation(relu)(wrapped)
        wrapped = Dense(self.action_output_size)(wrapped)
        layers = Activation(softmax)(wrapped) if self.flag is TrainingEnum.FULL_TRAINING else wrapped
        self.policy_predictor = Model(state_input, layers)
        state = Input(shape=(self.states_one_hot_len,), name='state')
        discounted_reward_placeholder = Input(shape=(1,), name='discounted_reward')
        behavior_policy_placeholder = Input(shape=(1,), name='behavior_policy')
        inputs = [state, discounted_reward_placeholder, behavior_policy_placeholder] if self.flag is TrainingEnum.FULL_TRAINING else [state]
        trainer_layers = self.policy_predictor(state)
        model = Model(inputs=inputs, outputs=trainer_layers)
        self.load_weights_from_date()
        model.compile(optimizer=Adam(lr=self.alpha) if self.flag is TrainingEnum.FULL_TRAINING\
                        else SGD(lr=self.alpha), 
                     loss=self.loss_function_generator(discounted_reward_placeholder, behavior_policy_placeholder))
        self.policy_trainer = model
        self.policy_predictor.summary()

        
    def load_weights_from_date(self):
        if not self.init_date is None:
            date = self.init_date.strftime("%b_%d_%Y_%H_%M_%S")
            if not (path.isdir(path.join("previous_memories", f"{self.memories_directory}"))):
                from os import mkdir
                mkdir(path.join("previous_memories", f"{self.memories_directory}"))

            self.policy_predictor.load_weights(path.join("previous_memories",
                                        f"{self.memories_directory}", f"{self.network_name}_{self.mode.computed_name}_{self.flag.name}_{date}.h5"))

    def save_weights_to_date(self, date: datetime =None):
        date_str = (date if date is not None else datetime.now()).strftime("%b_%d_%Y_%H_%M_%S")
        if not (path.isdir(path.join("previous_memories", f"{self.memories_directory}"))):
                from os import mkdir
                mkdir(path.join("previous_memories", f"{self.memories_directory}"))
        self.policy_predictor.save_weights(path.join("previous_memories",
                                   f"{self.memories_directory}", f"{self.network_name}_{self.mode.computed_name}_{self.flag.name}_{date_str}.h5"))

    def loss_function_generator(self, discounted_reward: Tensor, behavior_policy: Tensor):

        if self.flag is not TrainingEnum.FULL_TRAINING:
            return MSE

        def gradient_loss(pi: Tensor, pi_prediction: Tensor):
            pi_s_a = k_sum(pi * pi_prediction, axis=1)
            importance_weight = pi_s_a / behavior_policy
            loss = -discounted_reward * k_log(pi_s_a)
            return loss * importance_weight
        return gradient_loss

    @staticmethod
    def get_instance(name: str, n_actions: int, batch_size: int, alpha: float, 
                 mem_dir: str, n_one_hot: int, start_from: datetime, flag: TrainingEnum, mode: NetworkMode =NetworkMode.SINGLE):
        l = [__instance for __instance in QPolicyNetwork.__instances if (
                __instance.states_one_hot_len == n_one_hot and __instance.action_output_size == n_actions and __instance.alpha == alpha 
                and __instance.init_date == start_from and __instance.memories_directory == mem_dir and __instance.network_name == name
                and flag is __instance.flag and mode & __instance.mode
            )]
        __instance = None

        if not any(l):
            __instance = QPolicyNetwork(name, n_actions, batch_size, alpha, mem_dir, n_one_hot, start_from, flag, mode)
            QPolicyNetwork.__instances.append(__instance)
            __instance.build_network()

        else:
            __instance = l[0]

        return __instance

    def train(self, memory: Batch, message: str =""):

        if memory is None:
            return

        try:
            network_input = {
                             'state':memory.states,
                             'discounted_reward':memory.rewards,
                             'behavior_policy': memory.behaviors
                            } if self.flag is TrainingEnum.FULL_TRAINING else {
                             'state':memory.states
                            }

            if message != "":
                print(message)

            self.policy_trainer.fit(network_input, memory.actions, epochs=1)

        except Exception as e:
            print(e)
