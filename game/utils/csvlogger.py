from csv import writer, QUOTE_NONE
from os import path
from typing import Tuple, Any

CSVS_DIR = "csvs"


class CSVLogger(object):

    def __init__(self, session: str, name: str, header: Tuple[str] =None, limit=500):
        if not (path.isdir(path.join(session, CSVS_DIR))):
            from os import makedirs
            makedirs(path.join(session, CSVS_DIR), exist_ok=True)
        self.name = path.join(session, CSVS_DIR, name)
        self.open_stream()
        self.limit = max(limit, 1)
        if header:
            self.writer.writerow(header)

    def log(self, tup: Tuple[Any]):  
        self.writer.writerow(tup)
        self.count_rows += 1
        if self.count_rows == self.limit:
            self.save()
            self.open_stream()

    def open_stream(self):
        self.count_rows = 0
        self.output = open(self.name, mode='a', newline='')
        self.writer = writer(
                self.output, quoting=QUOTE_NONE, delimiter=',')

    def save(self):
        self.output.close()
