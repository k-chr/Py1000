from game.envs.simpletakingtricksenv import SimpleTakingTricksEnv
from game.ai.takingtricksagent import TakingTricksAgent
from game.enums import TrainingEnum
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer, QCoreApplication
import sys
from datetime import datetime
from typing import List
import signal
import argparse

sys.setrecursionlimit(10000)
STEPS_BATCH_SIZE = 100
EPISODES = 200_000
DUMP_PERIOD = 500
TRAINING_FLAG = TrainingEnum.PRETRAINING_OWN_CARDS


def get_date(string: str) -> datetime:
    try:
        return datetime.strptime(string, "%b_%d_%Y_%H_%M_%S")
    except:
        raise argparse.ArgumentTypeError('provided date is not convertible')

def get_flag(string: str) -> TrainingEnum:
    try: 
        return TrainingEnum[string]
    except:
        raise argparse.ArgumentTypeError(f'provided training flag: {string} is not availabe')

def init_parser() -> argparse.ArgumentParser: 
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=get_date, help='expected format: Mon_DD_YY_HH_MM_ss')
    parser.add_argument('--training-flag', type=get_flag, default=TRAINING_FLAG, 
                        help=f'available values: {TrainingEnum._member_names_}')

    def handler(message: str):
        print(message, file=sys.stderr)
        parser.print_help(sys.stderr)
        parser.exit(2)

    setattr(parser, 'error', handler)
    return parser

class Sim(QObject):
    finished = pyqtSignal()

    def __init__(self, args: argparse.Namespace, parent=None):
        super(Sim, self).__init__(parent)
        date = args.date
        self.flag = args.training_flag
        self.player1 = TakingTricksAgent(40, "player1", last_weights=date, flag=self.flag, alpha=0.01 if not self.flag is TrainingEnum.FULL_TRAINING else 0.0001)
        self.player2 = TakingTricksAgent(40, "player1", last_weights=date, flag=self.flag, alpha=0.01 if not self.flag is TrainingEnum.FULL_TRAINING else 0.0001)
        self.env = SimpleTakingTricksEnv(self.flag)

    @pyqtSlot()
    def run(self):
        episode = 0

        while episode < EPISODES:
            done = False
            obs = self.env.reset()
            steps = 0

            while not done:
                player = self.player1 if obs["is_player1_turn"] else self.player2
                op = self.player2 if obs["is_player1_turn"] else self.player1
                state = obs["data"]
                action = player.get_action(state)
                steps += 1
                obs, rewards, done = self.env.step(action)
                if rewards[0] < 0 and ((not self.flag is TrainingEnum.FULL_TRAINING
                        ) or (self.flag is TrainingEnum.FULL_TRAINING and rewards[1] == 0
                    )):
                    player.remeber_traumatic_S_A_R(state, action, rewards[0])
                else:
                    player.remember_S_A_R(state, action, rewards[0])

                #delayed reward
                if(len(rewards) > 1):
                    op.memory.update_last_reward(rewards[1])

                if(len(player.traumatic_memory.states) == STEPS_BATCH_SIZE):
                    player.replay_traumatic_only()

            self.env.log_episode_info()
            print(f"[{episode + 1}/{EPISODES}]")

            if self.flag is TrainingEnum.FULL_TRAINING:
                self.player1.scale_rewards(self.env.player1.score)
                self.player2.scale_rewards(self.env.player2.score)

            self.player1.replay()
            self.player2.replay()

            if (episode + 1) % DUMP_PERIOD == 0:
                self.player1.model.save_weights_to_date()
                self.player2.model.save_weights_to_date()

            episode += 1
        self.finished.emit()
        
    def sigint_handler(self, *args):
        self.env.log_episode_info()
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
