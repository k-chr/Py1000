from copy import deepcopy
from game.utils.csvlogger import CSVLogger
from game.card import Card
from game.utils.gamelogger import GameLogger
import tensorflow as tf

config = tf.compat.v1.ConfigProto(gpu_options = 
                         tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.9)
# device_count = {'GPU': 1}
)
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)
tf.compat.v1.disable_eager_execution()
from functools import reduce
from game.states.takingtrickstate import TakingTrickState
from game import NetworkOutput, Constraint
from game.envs.simpletakingtricksenv import SimpleTakingTricksEnv
from game.ai.takingtricksagent import TakingTricksAgent
from game.enums import Cards, Suits, TrainingEnum, NetworkMode, RewardMapperMode
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer, QCoreApplication
import sys
from datetime import datetime
from typing import List
import signal
import argparse
from numpy import zeros
from secrets import token_hex

sys.setrecursionlimit(10000)
BATCH_SIZE = Constraint[int](32, 256, 32)
ALPHA = Constraint[float](0.000001, 0.01, 0.0001)
EPISODES = Constraint[int](10_000, 1_000_000, 200_000)
DUMP_PERIOD = Constraint[int](100, 100_000, 5_000)
TEST_PERIOD = Constraint[int](10, 10_000, 150)
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

def get_size(string: str) -> int:
    try:
        val = int(string)
        val = min(max(BATCH_SIZE.MIN, val), BATCH_SIZE.MAX)
        return val
    except:
        raise argparse.ArgumentTypeError(f'provided batch size: {string} is not correct value')

def get_dump_freq(string: str) -> int:
    try:
        val = int(string)
        val = min(max(DUMP_PERIOD.MIN, val), DUMP_PERIOD.MAX)
        return val
    except:
        raise argparse.ArgumentTypeError(f'provided dump period: {string} is not correct value')

def get_test_freq(string: str) -> int:
    try:
        val = int(string)
        val = min(max(TEST_PERIOD.MIN, val), TEST_PERIOD.MAX)
        return val
    except:
        raise argparse.ArgumentTypeError(f'provided test frequency: {string} is not correct value')

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
                        help=f'Sets the length of learning process. Provide number in range <{EPISODES.MIN}; {EPISODES.MAX}>')
    parser.add_argument('--alpha', type=get_alpha, default=ALPHA.DEFAULT, 
                        help=f'Determines the value of learning rate. Provide number in range <{ALPHA.MIN}; {ALPHA.MAX}>')
    parser.add_argument('--dump-period', type=get_dump_freq, default=DUMP_PERIOD.DEFAULT, 
                        help=f'Indicates the frequency of exporting neural network\'s weights to file. Provide number in range <{DUMP_PERIOD.MIN}; {DUMP_PERIOD.MAX}>')
    parser.add_argument('--test-period', type=get_test_freq, default=TEST_PERIOD.DEFAULT, 
                        help=f'Indicates the frequency of performing tests during learning process. Provide number in range <{TEST_PERIOD.MIN}; {TEST_PERIOD.MAX}>')
    parser.add_argument('--batch-size', type=get_size, default=BATCH_SIZE.DEFAULT, 
                        help=f'Indicates the size of batches extracted from experience replay. Provide number in range <{BATCH_SIZE.MIN}; {BATCH_SIZE.MAX}>')                                                
    parser.add_argument("--store-invalid", default=False, action="store_true",
                    help="Deterimines whether to store and use invalid actions in separate buffer in full training stage.")
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


class TestCase:

    def __init__(self, player1: List[Card], player2: List[Card], stock1: List[Card], stock2: List[Card], who_starts: bool) -> None:
        self.player1: List[Card] =player1
        self.player2: List[Card] =player2
        self.stock1: List[Card] =stock1
        self.stock2: List[Card] =stock2
        self.who_starts: bool =who_starts


test_suit: List[TestCase] =[
    TestCase([
        Card(Suits.H, Cards.QUEEN),
        Card(Suits.H, Cards.KING),
        Card(Suits.H, Cards.ACE),
        Card(Suits.H, Cards.TEN),
        Card(Suits.D, Cards.QUEEN),
        Card(Suits.D, Cards.KING),
        Card(Suits.D, Cards.ACE),
        Card(Suits.D, Cards.TEN),
        Card(Suits.S, Cards.JACK),
        Card(Suits.S, Cards.NINE)
    ], [
        Card(Suits.H, Cards.JACK),
        Card(Suits.H, Cards.NINE),
        Card(Suits.C, Cards.QUEEN),
        Card(Suits.C, Cards.KING),
        Card(Suits.C, Cards.ACE),
        Card(Suits.C, Cards.TEN),
        Card(Suits.S, Cards.ACE),
        Card(Suits.S, Cards.TEN),
        Card(Suits.D, Cards.JACK),
        Card(Suits.D, Cards.NINE)
    ], [        
        Card(Suits.C, Cards.NINE),
        Card(Suits.C, Cards.JACK)
    ], [        
        Card(Suits.S, Cards.QUEEN),
        Card(Suits.S, Cards.KING)
    ], True),
    TestCase([
        Card(Suits.H, Cards.QUEEN),
        Card(Suits.H, Cards.TEN),
        Card(Suits.H, Cards.NINE),
        Card(Suits.D, Cards.KING),
        Card(Suits.D, Cards.ACE),
        Card(Suits.S, Cards.QUEEN),
        Card(Suits.S, Cards.KING),
        Card(Suits.C, Cards.JACK),
        Card(Suits.C, Cards.NINE),
        Card(Suits.C, Cards.TEN)
    ], [
        Card(Suits.H, Cards.ACE),
        Card(Suits.H, Cards.KING),
        Card(Suits.D, Cards.TEN),
        Card(Suits.D, Cards.QUEEN),
        Card(Suits.S, Cards.TEN),
        Card(Suits.S, Cards.JACK),
        Card(Suits.S, Cards.NINE),
        Card(Suits.C, Cards.QUEEN),
        Card(Suits.C, Cards.ACE),
        Card(Suits.C, Cards.KING)
    ], [        
        Card(Suits.S, Cards.ACE),
        Card(Suits.H, Cards.JACK)
    ], [        
        Card(Suits.D, Cards.JACK),
        Card(Suits.D, Cards.NINE)
    ], False),

    TestCase([
        Card(Suits.H, Cards.QUEEN),
        Card(Suits.H, Cards.ACE),
        Card(Suits.H, Cards.JACK),
        Card(Suits.D, Cards.NINE),
        Card(Suits.D, Cards.KING),
        Card(Suits.D, Cards.TEN),
        Card(Suits.S, Cards.NINE),
        Card(Suits.S, Cards.JACK),
        Card(Suits.S, Cards.ACE),
        Card(Suits.S, Cards.TEN)
    ], [
        Card(Suits.C, Cards.TEN),
        Card(Suits.C, Cards.ACE),
        Card(Suits.C, Cards.QUEEN),
        Card(Suits.C, Cards.NINE),
        Card(Suits.C, Cards.JACK),
        Card(Suits.H, Cards.NINE),
        Card(Suits.H, Cards.KING),
        Card(Suits.D, Cards.ACE),
        Card(Suits.D, Cards.QUEEN),
        Card(Suits.D, Cards.JACK)
    ], [        
        Card(Suits.C, Cards.KING),
        Card(Suits.S, Cards.QUEEN)
    ], [        
        Card(Suits.H, Cards.TEN),
        Card(Suits.S, Cards.KING)
    ], True),
    TestCase([
        Card(Suits.H, Cards.QUEEN),
        Card(Suits.H, Cards.ACE),
        Card(Suits.H, Cards.JACK),
        Card(Suits.D, Cards.NINE),
        Card(Suits.D, Cards.KING),
        Card(Suits.D, Cards.TEN),
        Card(Suits.S, Cards.NINE),
        Card(Suits.S, Cards.JACK),
        Card(Suits.S, Cards.ACE),
        Card(Suits.S, Cards.TEN)
    ], [
        Card(Suits.C, Cards.TEN),
        Card(Suits.C, Cards.ACE),
        Card(Suits.C, Cards.QUEEN),
        Card(Suits.C, Cards.NINE),
        Card(Suits.C, Cards.JACK),
        Card(Suits.H, Cards.NINE),
        Card(Suits.H, Cards.KING),
        Card(Suits.D, Cards.ACE),
        Card(Suits.D, Cards.QUEEN),
        Card(Suits.D, Cards.JACK)
    ], [        
        Card(Suits.C, Cards.KING),
        Card(Suits.S, Cards.QUEEN)
    ], [        
        Card(Suits.H, Cards.TEN),
        Card(Suits.S, Cards.KING)
    ], False),
    TestCase([
        Card(Suits.H, Cards.QUEEN),
        Card(Suits.H, Cards.KING),
        Card(Suits.H, Cards.NINE),
        Card(Suits.C, Cards.ACE),
        Card(Suits.C, Cards.TEN),
        Card(Suits.D, Cards.TEN),
        Card(Suits.D, Cards.QUEEN),
        Card(Suits.D, Cards.KING),
        Card(Suits.D, Cards.NINE),
        Card(Suits.S, Cards.ACE)
    ], [
        Card(Suits.H, Cards.ACE),
        Card(Suits.H, Cards.TEN),
        Card(Suits.D, Cards.ACE),
        Card(Suits.C, Cards.QUEEN),
        Card(Suits.C, Cards.KING),
        Card(Suits.C, Cards.NINE),
        Card(Suits.S, Cards.QUEEN),
        Card(Suits.S, Cards.KING),
        Card(Suits.S, Cards.NINE),        
        Card(Suits.S, Cards.TEN)
    ], [        
        Card(Suits.C, Cards.JACK),
        Card(Suits.D, Cards.JACK)
    ], [        
        Card(Suits.H, Cards.JACK),
        Card(Suits.S, Cards.JACK)
    ], True),
    TestCase([
        Card(Suits.H, Cards.QUEEN),
        Card(Suits.H, Cards.KING),
        Card(Suits.H, Cards.NINE),
        Card(Suits.C, Cards.ACE),
        Card(Suits.C, Cards.TEN),
        Card(Suits.D, Cards.TEN),
        Card(Suits.D, Cards.QUEEN),
        Card(Suits.D, Cards.KING),
        Card(Suits.D, Cards.NINE),
        Card(Suits.S, Cards.ACE)
    ], [
        Card(Suits.H, Cards.ACE),
        Card(Suits.H, Cards.TEN),
        Card(Suits.D, Cards.ACE),
        Card(Suits.C, Cards.QUEEN),
        Card(Suits.C, Cards.KING),
        Card(Suits.C, Cards.NINE),
        Card(Suits.S, Cards.QUEEN),
        Card(Suits.S, Cards.KING),
        Card(Suits.S, Cards.NINE),        
        Card(Suits.S, Cards.TEN)
    ], [        
        Card(Suits.C, Cards.JACK),
        Card(Suits.D, Cards.JACK)
    ], [        
        Card(Suits.H, Cards.JACK),
        Card(Suits.S, Cards.JACK)
    ], False),
    TestCase([
        Card(Suits.H, Cards.NINE),
        Card(Suits.H, Cards.JACK),
        Card(Suits.H, Cards.QUEEN),
        Card(Suits.D, Cards.QUEEN),
        Card(Suits.D, Cards.TEN),
        Card(Suits.D, Cards.NINE),
        Card(Suits.C, Cards.QUEEN),
        Card(Suits.C, Cards.KING),
        Card(Suits.C, Cards.ACE),
        Card(Suits.C, Cards.NINE)
    ], [
        Card(Suits.H, Cards.KING),
        Card(Suits.H, Cards.TEN),
        Card(Suits.D, Cards.KING),
        Card(Suits.D, Cards.ACE),
        Card(Suits.C, Cards.TEN),
        Card(Suits.C, Cards.JACK),
        Card(Suits.S, Cards.QUEEN),
        Card(Suits.S, Cards.KING),
        Card(Suits.S, Cards.NINE),
        Card(Suits.S, Cards.JACK)
    ], [        
        Card(Suits.D, Cards.JACK),
        Card(Suits.S, Cards.TEN)
    ], [        
        Card(Suits.H, Cards.ACE),
        Card(Suits.S, Cards.ACE)
    ], True),
    TestCase([
        Card(Suits.H, Cards.NINE),
        Card(Suits.H, Cards.JACK),
        Card(Suits.H, Cards.QUEEN),
        Card(Suits.D, Cards.QUEEN),
        Card(Suits.D, Cards.TEN),
        Card(Suits.D, Cards.NINE),
        Card(Suits.C, Cards.QUEEN),
        Card(Suits.C, Cards.KING),
        Card(Suits.C, Cards.ACE),
        Card(Suits.C, Cards.NINE)
    ], [
        Card(Suits.H, Cards.KING),
        Card(Suits.H, Cards.TEN),
        Card(Suits.D, Cards.KING),
        Card(Suits.D, Cards.ACE),
        Card(Suits.C, Cards.TEN),
        Card(Suits.C, Cards.JACK),
        Card(Suits.S, Cards.QUEEN),
        Card(Suits.S, Cards.KING),
        Card(Suits.S, Cards.NINE),
        Card(Suits.S, Cards.JACK)
    ], [        
        Card(Suits.D, Cards.JACK),
        Card(Suits.S, Cards.TEN)
    ], [        
        Card(Suits.H, Cards.ACE),
        Card(Suits.S, Cards.ACE)
    ], False),
    TestCase([
        Card(Suits.H, Cards.NINE),
        Card(Suits.H, Cards.JACK),
        Card(Suits.H, Cards.ACE),
        Card(Suits.D, Cards.NINE),
        Card(Suits.D, Cards.TEN),
        Card(Suits.D, Cards.ACE),
        Card(Suits.S, Cards.JACK),
        Card(Suits.S, Cards.NINE),
        Card(Suits.S, Cards.TEN),
        Card(Suits.S, Cards.ACE)
    ], [
        Card(Suits.H, Cards.QUEEN),
        Card(Suits.H, Cards.KING),
        Card(Suits.H, Cards.TEN),
        Card(Suits.D, Cards.QUEEN),
        Card(Suits.D, Cards.KING),
        Card(Suits.D, Cards.JACK),
        Card(Suits.C, Cards.NINE),
        Card(Suits.C, Cards.JACK),
        Card(Suits.C, Cards.QUEEN),
        Card(Suits.C, Cards.ACE)
    ], [        
        Card(Suits.C, Cards.KING),
        Card(Suits.C, Cards.TEN)
    ], [        
        Card(Suits.S, Cards.TEN),
        Card(Suits.S, Cards.KING)
    ], True),
    TestCase([
        Card(Suits.H, Cards.NINE),
        Card(Suits.H, Cards.JACK),
        Card(Suits.H, Cards.ACE),
        Card(Suits.D, Cards.NINE),
        Card(Suits.D, Cards.TEN),
        Card(Suits.D, Cards.ACE),
        Card(Suits.S, Cards.JACK),
        Card(Suits.S, Cards.NINE),
        Card(Suits.S, Cards.TEN),
        Card(Suits.S, Cards.ACE)
    ], [
        Card(Suits.H, Cards.QUEEN),
        Card(Suits.H, Cards.KING),
        Card(Suits.H, Cards.TEN),
        Card(Suits.D, Cards.QUEEN),
        Card(Suits.D, Cards.KING),
        Card(Suits.D, Cards.JACK),
        Card(Suits.C, Cards.NINE),
        Card(Suits.C, Cards.JACK),
        Card(Suits.C, Cards.QUEEN),
        Card(Suits.C, Cards.ACE)
    ], [        
        Card(Suits.C, Cards.KING),
        Card(Suits.C, Cards.TEN)
    ], [        
        Card(Suits.S, Cards.TEN),
        Card(Suits.S, Cards.KING)
    ], False),

]

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
            file.write(f"DATE = {self.date.strftime('%b_%d_%Y_%H_%M_%S') if self.date is not None else None}\n")
            file.write(f"BATCH_SIZE = {self.batch_size}\n")
            file.write(f"TEST_PERIOD = {self.test_period}\n")
            file.write(f"DUMP_PERIOD = {self.dump_period}\n")
            file.write(f"STORE_INVALID = {self.store_invalid}\n")
        return

    def __init__(self, args: argparse.Namespace, parent=None):
        super(Sim, self).__init__(parent)
        self.date: datetime =args.date
        self.flag: TrainingEnum =args.training_flag
        self.network_type: NetworkMode =args.network_mode
        self.reward_mapper_type: RewardMapperMode =args.rewards_flag
        self.episodes: int =args.episodes
        self.alpha: float =args.alpha
        self.batch_size: int =args.batch_size
        self.dump_period: int =args.dump_period
        self.test_period: int =args.test_period
        self.store_invalid: bool =args.store_invalid
        self.current_episode = 0
        self.test_ord = 0
        self.session = f"sessions\\session_{token_hex(8)}_{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}"
        self.__dump_cfg()
        self.player1 = TakingTricksAgent(self.batch_size, "player_agent", self.session, last_weights=self.date, flag=self.flag, alpha= self.alpha, 
                                            mode=self.network_type, reward_mode=self.reward_mapper_type)
        self.player2 = TakingTricksAgent(self.batch_size, "player_agent", self.session, last_weights=self.date, flag=self.flag, alpha= self.alpha, 
                                            mode=self.network_type, reward_mode=self.reward_mapper_type)
        self.env = SimpleTakingTricksEnv(self.date, self.flag, self.session)
        test_header = (
            "Test Ep.", "Learning Ep.", "Case 1 Player1", "Case 1 Player2", "Case 2 Player1",
            "Case 2 Player2","Case 3 Player1","Case 3 Player2","Case 4 Player1","Case 4 Player2",
            "Case 5 Player1","Case 5 Player2","Case 6 Player1","Case 6 Player2","Case 7 Player1","Case 7 Player2",
            "Case 8 Player1","Case 8 Player2","Case 9 Player1","Case 9 Player2","Case 10 Player1","Case 10 Player2"
        )
        self.test_score_csv = CSVLogger(self.session+"\\tests", "test_score_improvement.csv", header=test_header, limit=20)
        self.test_invalid_actions_csv = CSVLogger(self.session+"\\tests", "test_invalid_action_improvement.csv", header=test_header, limit=20)

    def test_game_play(self):
        self.test_ord += 1
        logger = GameLogger(self.session+"\\tests", f"test_no_{self.test_ord}.log" )
        logger.append_to_log(f"Test Benchmark No. {self.test_ord}")
        record_score = [self.test_ord, self.current_episode + 1]
        record_invalid = [self.test_ord, self.current_episode + 1]
        try:
            for test_ord, case in enumerate(test_suit):
                logger.append_to_log(f"Test case No. {test_ord + 1}")
                logger.append_to_log(f"player1: {case.player1}")
                logger.append_to_log(f"player2: {case.player2}")
                logger.append_to_log(f"stock1: {case.stock1}")
                logger.append_to_log(f"stock2: {case.stock2}")
                logger.append_to_log("who starts?: " + ("player1" if case.who_starts else "player2"))
                done = False
                obs = self.env.controlled_reset(deepcopy(case.player1), deepcopy(case.player2),
                                                deepcopy(case.stock1), deepcopy(case.stock2), 
                                                case.who_starts, test_ord+1, 
                                                test_num=(0 if test_ord != 0 else self.test_ord))
                steps = 0
                while not done:
                    player = self.player1 if obs["is_player1_turn"] else self.player2
                    state: TakingTrickState =obs["data"]
                    output: NetworkOutput =player.act(state) if len(state.hand_cards) > 1 else get_default_action(state)
                    steps += 1
                    obs, rewards, done = self.env.test_step(output)
                    if len(state.hand_cards) > 1:                        
                        if rewards[0] < 0 and rewards[1] is None:
                            player.errors = 1
                logger.append_to_log(f"player1: score = {self.env.player1.score}; invalid actions = {self.env.player1.invalid_actions}") 
                logger.append_to_log(f"player2: score = {self.env.player2.score}; invalid actions = {self.env.player2.invalid_actions}") 
                record_score.append(self.env.player1.score)
                record_score.append(self.env.player2.score)
                record_invalid.append(self.env.player1.invalid_actions)
                record_invalid.append(self.env.player2.invalid_actions)
            logger.end_logging()
            self.test_invalid_actions_csv.log(tuple(record_invalid))
            self.test_score_csv.log(tuple(record_score))
            self.player1.errors = 0
            self.player2.errors = 0
        except Exception as e:
            print(e)

    @pyqtSlot()
    def run(self):
        self.current_episode = 0
        try:
            while self.current_episode < self.episodes:
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
                        if rewards[0] < 0 and (self.flag is TrainingEnum.FULL_TRAINING and rewards[1] is None and self.store_invalid is True):
                            player.remember_traumatic_S_A_R_B(state, output.action, rewards[0], output.probs)
                        else:
                            player.remember_S_A_R_B(state, output.action, rewards[0], output.probs)
                        
                        if rewards[0] < 0 and ((self.flag is not TrainingEnum.FULL_TRAINING) or (self.flag is TrainingEnum.FULL_TRAINING and rewards[1] is None)):
                            player.errors = 1
                        
                    #delayed reward
                        if(len(rewards) > 1 and rewards[1] is not None):
                            op.memory.update_last_reward(rewards[1], state)

                self.env.log_episode_info()
                print(f"[{self.current_episode + 1}/{self.episodes}]")

                if self.flag is TrainingEnum.FULL_TRAINING:
                    self.player1.set_score(self.env.player1.score)
                    self.player1.set_invalid_actions_count(self.env.player1.invalid_actions)
                    self.player2.set_score(self.env.player2.score)
                    self.player2.set_invalid_actions_count(self.env.player2.invalid_actions)

                self.player1.replay()
                self.player2.replay()
                if(self.current_episode + 1) % self.test_period == 0 and self.flag is TrainingEnum.FULL_TRAINING:
                    self.test_game_play()

                if (self.current_episode + 1) % self.dump_period == 0:
                    self.player1.model.save_weights_to_date()
                    self.player2.model.save_weights_to_date()

                self.current_episode += 1
        except Exception as e:
            print(e)
        self.finished.emit()
        
    def sigint_handler(self, *args):
        try:
            self.env.end_logging()
            self.player1.clean_up()
        except:
            pass
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
