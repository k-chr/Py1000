from __future__ import annotations
from enum import Enum, IntFlag
from random import randint, shuffle
from copy import deepcopy
from typing import List, Deque, Callable, NamedTuple, Dict, Union
from numpy import zeros, concatenate, array, nan_to_num, sum as n_sum, ndarray, argmax, int64, asarray, reshape
from numpy.random import choice
from datetime import datetime
from os import path
from collections import deque

def DECK_SIZE():
    return 24

Batch = NamedTuple("BatchSAR", [('states', ndarray), ('actions', ndarray), ('rewards', ndarray), ('behaviors', ndarray)])
NetworkOutput = NamedTuple("NetworkOutput", [('action', int), ('action_prob', float), ('probs', List[float])])