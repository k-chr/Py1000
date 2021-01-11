from csv import writer, QUOTE_NONE
from os import path

class CSVLogger(object):

    def __init__(self, name):
      self.name = path.join("csvs", name)
      self.output = open(self.name, mode='a', newline='')
      self.writer = writer(self.output, quoting=QUOTE_NONE, delimiter=',')
      self.count_rows = 0

    def log(self, tup):
      self.writer.writerow(tup)
      self.count_rows += 1
      if self.count_rows == 500:
        self.count_rows = 0
        self.save()
        self.output = open(self.name, mode='a', newline='')
        self.writer = writer(self.output, quoting=QUOTE_NONE, delimiter=',')
      
    def save(self):
      self.output.close()