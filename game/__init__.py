from __future__ import annotations
from enum import Enum, IntFlag
from random import randint, shuffle
from copy import deepcopy
from typing import List, Deque, Callable, NamedTuple, Dict, Union, TypeVar, Generic
from numpy import (zeros, concatenate, array, 
                   nan_to_num, sum as n_sum, 
                   ndarray, argmax, int64, 
                   asarray, reshape, clip)
from numpy.random import choice
from datetime import datetime
from os import path
from collections import deque

T = TypeVar('T')


class Constraint(Generic[T]):
    
    def __init__(self, _min: T, _max: T, _default: T) -> None:
        self.MIN = min(_min, min( _max, _default)) 
        self.MAX = max(_min, max( _max, _default))
        self.DEFAULT = max(self.MIN, min(self.MAX, _default))


MAX_CARDS_IN_HAND = 0xA
MIN_CARDS_IN_HAND = 0x2

def DECK_SIZE():
    return 24

Batch = NamedTuple("BatchSAR", [('states', ndarray), ('actions', ndarray), ('rewards', ndarray), ('behaviors', ndarray)])
NetworkOutput = NamedTuple("NetworkOutput", [('action', int), ('action_prob', float), ('probs', List[float])])