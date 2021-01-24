import tensorflow as tf

config = tf.compat.v1.ConfigProto(gpu_options = 
                         tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.9)
# device_count = {'GPU': 1}
)
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)

from functools import reduce
from game.states.takingtrickstate import TakingTrickState
from game import NetworkOutput, Constraint
from game.envs.simpletakingtricksenv import SimpleTakingTricksEnv
from game.ai.takingtricksagent import TakingTricksAgent
from game.enums import TrainingEnum, NetworkMode, RewardMapperMode
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer, QCoreApplication
import sys
from datetime import datetime
from typing import List
import signal
import argparse
from numpy import zeros
from secrets import token_hex

sys.setrecursionlimit(10000)
ALPHA = Constraint[float](0.000001, 0.01, 0.0001)
EPISODES = Constraint[int](100_000, 1_000_000, 200_000)
DUMP_PERIOD = 500
TRAINING_FLAG = TrainingEnum.PRETRAINING_OWN_CARDS
REWARD_MAPPPER = RewardMapperMode.DISCOUNTED
NETWORK = NetworkMode.SINGLE

def get_network_type(string: str) -> NetworkMode:
    try: 
        return reduce(lambda x, y: (x if isinstance(x, NetworkMode) \
                            else NetworkMode[x]) | NetworkMode[y], string.split('|'),
                            NetworkMode.SINGLE & NetworkMode.CLUSTER)
    except:
        raise argparse.ArgumentTypeError(f'provided network mode flag: {string} is not available')

def get_episodes(string: str) -> int:
    try:
        val = int(string)
        val = min(max(EPISODES.MIN, val), EPISODES.MAX)
        return val
    except:
        raise argparse.ArgumentTypeError(f'provided episodes count: {string} is not correct value')

def get_reward_mapper_type(string: str) -> RewardMapperMode:
    try: 
        return RewardMapperMode[string]
    except:
        raise argparse.ArgumentTypeError(f'provided reward mapper flag: {string} is not available')

def get_alpha(string: str) -> float:
    try:
        val = float(string)
        val = min(max(ALPHA.MIN, val), ALPHA.MAX)
        return val
    except:
        raise argparse.ArgumentTypeError(f'provided alpha: {string} is not correct value')

def get_date(string: str) -> datetime:
    try:
        return datetime.strptime(string, "%b_%d_%Y_%H_%M_%S")
    except:
        raise argparse.ArgumentTypeError('provided date is not convertible')

def get_training_flag(string: str) -> TrainingEnum:
    try: 
        return TrainingEnum[string]
    except:
        raise argparse.ArgumentTypeError(f'provided training flag: {string} is not available')

def init_parser() -> argparse.ArgumentParser: 
    parser = argparse.ArgumentParser()

    parser.add_argument('--date', type=get_date, help='expected format: Mon_DD_YY_HH_MM_ss')
    parser.add_argument('--training-flag', type=get_training_flag, default=TRAINING_FLAG, 
                        help=f'available values: {TrainingEnum._member_names_}')
    parser.add_argument('--network-mode', type=get_network_type, default=NETWORK, 
                        help=f'available values: {NetworkMode._member_names_} and their combinations using \"|\" separator')
    parser.add_argument('--rewards-flag', type=get_reward_mapper_type, default=REWARD_MAPPPER, 
                        help=f'available values: {RewardMapperMode._member_names_}')
    parser.add_argument('--episodes', type=get_episodes, default=EPISODES.DEFAULT, 
                        help=f'provide number in range <{EPISODES.MIN}; {EPISODES.MAX}>')
    parser.add_argument('--alpha', type=get_alpha, default=ALPHA.DEFAULT, 
                        help=f'provide number in range <{ALPHA.MIN}; {ALPHA.MAX}>')

    def handler(message: str):
        print(message, file=sys.stderr)
        parser.print_help(sys.stderr)
        parser.exit(2)

    setattr(parser, 'error', handler)
    return parser

def get_default_action(state: TakingTrickState) -> NetworkOutput:
    card = state.hand_cards[0]
    probs = zeros(state.action_space)
    probs[card.id()] = 1
    return NetworkOutput(card.id(), 1, probs)


class Sim(QObject):
    finished = pyqtSignal()

    def __dump_cfg(self):
        from os import makedirs, path
        if not path.isdir(path.join(self.session)):
            makedirs(path.join(self.session), exist_ok=True)

        with open(path.join(self.session, "config.cfg"), 'w') as file:
            file.write(f"TRAINING_FLAG = {self.flag.name}\n")
            file.write(f"NETWORK_MODE = {self.network_type.computed_name}\n")
            file.write(f"REWARDS_MAPPER_TYPE = {self.reward_mapper_type.name}\n")
            file.write(f"ALPHA = {self.alpha}\n")
            file.write(f"EPISODES = {self.episodes}\n")
            file.write(f"DATE = {self.date.strftime('%b_%d_%Y_%H_%M_%S')}\n")

        return

    def __init__(self, args: argparse.Namespace, parent=None):
        super(Sim, self).__init__(parent)
        self.date: datetime =args.date
        self.flag: TrainingEnum =args.training_flag
        self.network_type: NetworkMode =args.network_mode
        self.reward_mapper_type: RewardMapperMode =args.rewards_flag
        self.episodes: int =args.episodes
        self.alpha: float =args.alpha
        self.session = f"sessions\\session_{token_hex(8)}_{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}"
        self.__dump_cfg()
        self.player1 = TakingTricksAgent(32, "player_agent", self.session, last_weights=self.date, flag=self.flag, alpha= self.alpha, 
                                            mode=self.network_type, reward_mode=self.reward_mapper_type)
        self.player2 = TakingTricksAgent(32, "player_agent", self.session, last_weights=self.date, flag=self.flag, alpha= self.alpha, 
                                            mode=self.network_type, reward_mode=self.reward_mapper_type)
        self.env = SimpleTakingTricksEnv(self.date, self.flag, self.session)

    @pyqtSlot()
    def run(self):
        episode = 0

        while episode < self.episodes:
            done = False
            obs = self.env.reset()
            steps = 0

            while not done:
                player = self.player1 if obs["is_player1_turn"] else self.player2
                op = self.player2 if obs["is_player1_turn"] else self.player1
                state: TakingTrickState =obs["data"]
                output: NetworkOutput =player.get_action(state) if len(state.hand_cards) > 1 else get_default_action(state)
                steps += 1
                obs, rewards, done = self.env.step(output)
                if len(state.hand_cards) > 1:
                    if rewards[0] < 0 and ((not self.flag is TrainingEnum.FULL_TRAINING
                            ) or (self.flag is TrainingEnum.FULL_TRAINING and rewards[1] is None
                        )):
                        player.remember_traumatic_S_A_R_B(state, output.action, rewards[0], output.action_prob)
                    else:
                        player.remember_S_A_R_B(state, output.action, rewards[0], output.action_prob)

                #delayed reward
                    if(len(rewards) > 1 and rewards[1] is not None):
                        op.memory.update_last_reward(rewards[1])

            self.env.log_episode_info()
            print(f"[{episode + 1}/{self.episodes}]")

            if self.flag is TrainingEnum.FULL_TRAINING:
                self.player1.set_score(self.env.player1.score)
                self.player1.set_invalid_actions_count(self.env.player1.invalid_actions)
                self.player2.set_score(self.env.player2.score)
                self.player2.set_invalid_actions_count(self.env.player2.invalid_actions)

            self.player1.replay()
            self.player2.replay()

            if (episode + 1) % DUMP_PERIOD == 0:
                self.player1.model.save_weights_to_date()
                self.player2.model.save_weights_to_date()

            episode += 1
        self.finished.emit()
        
    def sigint_handler(self, *args):
        self.env.end_logging()
        QCoreApplication.exit()

def main(args: List[str]):
    app = QCoreApplication(args)
    parser = init_parser()
    sim = Sim(parser.parse_args(args[1:]), app)
    signal.signal(signal.SIGINT, sim.sigint_handler)
    sim.finished.connect(lambda:sim.sigint_handler())
    QTimer.singleShot(0, sim.run)
    app.exec_()

if __name__ == "__main__":
    main(sys.argv)
