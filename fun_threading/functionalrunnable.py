# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 16:27:03 2020

@author: Kamil Chrustowski
"""

from . import QRunnable, pyqtSlot

class FunctionalRunnable(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(FunctionalRunnable, self).__init__()
        self.args = args
        self.fn = fn
        self.kwargs = kwargs
        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)