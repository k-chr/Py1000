from __future__ import annotations
from random import randint, shuffle
from copy import deepcopy
from typing import List, Deque, Callable, NamedTuple
from numpy import zeros, concatenate, array, nan_to_num, sum as n_sum, ndarray, argmax, int64
from numpy.random import choice
from datetime import datetime
from os import path
from enum import Enum
from collections import deque