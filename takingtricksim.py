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
EPISODES = 100_000
DUMP_PERIOD = 500
TRAINING_FLAG = TrainingEnum.FULL_TRAINING


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
        flag = args.training_flag
        self.player1 = TakingTricksAgent(40, "player1", last_weights=date, flag=flag)
        self.player2 = TakingTricksAgent(40, "player1", last_weights=date, flag=flag)
        self.env = SimpleTakingTricksEnv(flag)

    @pyqtSlot()
    def run(self):
        episode = 0

        while episode < EPISODES:
            done = False
            obs = self.env.reset()
            while not done:
                player = self.player1 if obs["is_player1_turn"] else self.player2
                op = self.player2 if obs["is_player1_turn"] else self.player1
                state = obs["data"]
                action = player.get_action(state)

                obs, rewards, done = self.env.step(action)
                if TRAINING_FLAG is TrainingEnum.FULL_TRAINING or TRAINING_FLAG is TrainingEnum.PRETRAINING_OWN_CARDS:
                    player.remember_S_A_R(state, action, rewards[0])
                elif TRAINING_FLAG is TrainingEnum.PRETRAINING_VALID_CARDS:
                    if(state.played_card is not None):
                        player.remember_S_A_R(state, action, rewards[0])
               

                #delayed reward
                if TRAINING_FLAG is TrainingEnum.FULL_TRAINING:
                    if(len(rewards) > 1):
                        op.rewards_memory[len(op.rewards_memory) - 1] += rewards[1]
            
            print(f"[{episode + 1}/{EPISODES}]")
            self.player1.replay()
            self.player2.replay()
            if (episode + 1) % DUMP_PERIOD == 0:
                self.player1.model.save_weights_to_date()
                self.player2.model.save_weights_to_date()

            episode += 1
        self.env.logger.end_logging()
        self.finished.emit()
        
    def sigint_handler(self, *args):
        self.env.logger.end_logging()
        self.env.csv_inv_log.save()
        self.env.csv_rew_log.save()
        QCoreApplication.exit()

def main(args: List[str]):
    app = QCoreApplication(args)
    parser = init_parser()
    sim = Sim(parser.parse_args(args), app)
    signal.signal(signal.SIGINT, sim.sigint_handler)
    sim.finished.connect(QCoreApplication.exit)
    QTimer.singleShot(0, sim.run)
    app.exec_()

if __name__ == "__main__":
    main(sys.argv)
