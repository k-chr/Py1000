from game.envs.simpletakingtricksenv import SimpleTakingTricksEnv
from game.ai.takingtricksagent import TakingTricksAgent
from game.enums import TrainingEnum
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer, QCoreApplication
import sys
from datetime import datetime
from typing import List
import signal
sys.setrecursionlimit(10000)
EPISODES = 100_000
DUMP_PERIOD = 500
TRAINING_FLAG = TrainingEnum.PRETRAINING_VALID_CARDS
class Sim(QObject):
    finished = pyqtSignal()
    def __init__(self, args: List[str], parent=None):
        super(Sim, self).__init__(parent)
       
        date1 = None
        date2 = None
        if len(args) > 1:
            date1 = datetime.strptime(args[1], "%b_%d_%Y_%H_%M_%S")
        self.player1 = TakingTricksAgent(40, "player1", last_weights=date1, flag=TRAINING_FLAG)
        self.player2 = TakingTricksAgent(40, "player1", last_weights=date1, flag=TRAINING_FLAG)
        self.env = SimpleTakingTricksEnv(TRAINING_FLAG)

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
    sim = Sim(args, app)
    signal.signal(signal.SIGINT, sim.sigint_handler)
    sim.finished.connect(QCoreApplication.exit)
    QTimer.singleShot(0, sim.run)
    app.exec_()

if __name__ == "__main__":
    main(sys.argv)