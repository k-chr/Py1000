# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 16:29:06 2020

@author: Kamil Chrustowski
"""
from PyQt5.QtCore import QThread
class FunctionalThread(QThread):
    def __init__(self, function, *args, **kwargs):
        super(FunctionalThread, self).__init__()
        self.fn = function
        self.args = args
        self.kwargs = kwargs
    def __del__(self):
        self.wait()
 
    def run(self):
        self.fn(*self.args,**self.kwargs)
        self.terminate()
        return