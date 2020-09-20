from keras.models import Sequential 
from keras.layers.core import Dense, Activation
from keras.layers.core.activations import relu, softmax
from datetime import datetime
from keras.optimizers import SGD
from keras.losses import categorical_crossentropy
from os import path