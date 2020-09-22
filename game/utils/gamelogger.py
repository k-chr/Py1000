from .. import datetime, path

class GameLogger(object):

    def __init__(self, fname: str):
        self.fname = fname
        with open(path.join("logs", self.fname), 'w') as f:
            f.write(f"[{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}] started logging session" + '\n')

    def append_to_log(self, info: str):
        with open(path.join("logs", self.fname), "a") as f:
            f.write(f"[{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}] {info}" + '\n')

    def end_logging(self):
        with open(path.join("logs", self.fname), 'a') as f:
            f.write(f"[{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}] ended logging session" + '\n')
