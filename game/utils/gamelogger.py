from .. import datetime, path

class GameLogger(object):

    def __init__(self, fname: str):
        self.fname = fname
        self.count_rows = 0
        self.stream = open(path.join("logs", self.fname), 'a')
        self.stream.write(f"[{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}] started logging session" + '\n')

    def append_to_log(self, info: str):
        self.stream.write(f"[{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}] {info}" + '\n')
        self.count_rows += 1
        if self.count_rows == 500:
            self.count_rows = 0
            self.stream.close()
            self.stream = open(path.join("logs", self.fname), 'a')

    def end_logging(self):
        self.stream.write(f"[{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}] ended logging session" + '\n')
        self.stream.close()