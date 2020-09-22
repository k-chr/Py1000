from game.envs.simpletakingtricksenv import SimpleTakingTricksEnv
from game.ai.takingtricksagent import TakingTricksAgent
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer, QCoreApplication
import sys
from datetime import datetime
from typing import List
sys.setrecursionlimit(10000)
EPISODES = 100_000
DUMP_PERIOD = 500
class Sim(QObject):
    finished = pyqtSignal()
    def __init__(self, args: List[str], parent=None):
        super(Sim, self).__init__(parent)
       
        date1 = None
        date2 = None
        if len(args) == 3:
            date1 = datetime.strptime(args[1], "%b_%d_%Y_%H_%M_%S")
            date2 = datetime.strptime(args[2], "%b_%d_%Y_%H_%M_%S")
        self.player1 = TakingTricksAgent(40, "player1", last_weights=date1)
        self.player2 = TakingTricksAgent(40, "player2", last_weights=date2)
        self.env = SimpleTakingTricksEnv()

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
                player.remember_S_A_R(state, action, rewards[0])

                #delayed reward
                if(len(rewards) > 1):
                    op.rewards_memory[len(op.rewards_memory) - 1] += rewards[1]
            
            print(f"[{episode}/{EPISODES}] player1 total reward: {sum(self.player1.rewards_memory)} | player2 total reward: {sum(self.player2.rewards_memory)}")
            
            self.player1.replay()
            self.player2.replay()
            if (episode + 1) % DUMP_PERIOD == 0:
                self.player1.model.save_weights_to_date()
                self.player2.model.save_weights_to_date()

            episode += 1
        self.env.logger.end_logging()
        self.finished.emit()


def main(args: List[str]):
    app = QCoreApplication(args)
    sim = Sim(args, app)
    sim.finished.connect(QCoreApplication.exit)
    QTimer.singleShot(0, sim.run)
    app.exec_()

if __name__ == "__main__":
    main(sys.argv)