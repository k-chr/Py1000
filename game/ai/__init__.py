from __future__ import annotations
from typing import Callable
from keras import Sequential, Model
from keras.backend.common import _EPSILON 
from keras.layers import Dense, Activation, InputLayer
from keras import Input
from keras.activations import relu, softmax
from keras.optimizers import Adam, SGD, Nadam
from tensorflow.python.framework.ops import Tensor
from keras.losses import MSE
from keras.losses import categorical_crossentropy
from keras.backend import  print_tensor
import keras.backend
from .. import (path, datetime, zeros, Union, reshape,
                choice, List, array, Dict, MIN_CARDS_IN_HAND, 
                MAX_CARDS_IN_HAND, nan_to_num, n_sum, ndarray,
                argmax, int64, deque, Deque, Callable as fun, 
                Batch, NetworkOutput, clip)
from ..enums import TrainingEnum, RewardMapperMode, NetworkMode
from ..states.biddingstate import BiddingState
from ..states.giveawaystate import GiveawayState
from ..states.takingtrickstate import TakingTrickState
from ..states.state import State
from ..utils.gamerules import GameRules
from ..utils.csvlogger import CSVLogger
k_sum = keras.backend.sum
k_log = keras.backend.log
k_pow = keras.backend.pow
k_mean = keras.backend.mean
transpose = keras.backend.transpose
from tensorflow import math, clip_by_value
div_no_nan = math.divide_no_nan

MIN_PROB = _EPSILON
MAX_PROB = 1 - _EPSILON