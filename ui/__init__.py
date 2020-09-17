"""
Created on Sat Sep  12 20:41:42 2020

@author: Kamil Chrustowski
"""
from __future__ import annotations
from PyQt5.QtCore import Qt, QSize, QEvent, QPropertyAnimation, QTimer, QCoreApplication, pyqtSignal, QRectF 
from PyQt5.QtGui import QBrush, QPalette, QPainter, QFontMetrics, QFont, QTransform, QColor, QPixmap
from PyQt5.QtWidgets import  (QGroupBox, QApplication,
                              QButtonGroup, QHBoxLayout,
                              QWidget, QPushButton,
                              QGraphicsDropShadowEffect, QStyleFactory,
                              QProgressBar, QDialog,
                              QVBoxLayout, QLabel, 
                              QSizePolicy, QGridLayout, 
                              QGraphicsPixmapItem, QGraphicsView,
                              QGraphicsScene, QGraphicsItem, QLabel)

from game.card import *
from game.enums import Suits
from enum import Enum
import os

class Defaults(object):
    
    CARD_DIMENSIONS = QSize(120, 174)
    CARD_RECT = QRect(0, 0, 120, 174)
    CARD_SPACING_X = 10

class CardSide(Enum):
    FRONT = 0
    BACK = 1

class CardLocation(Enum):
    HAND = 0x1
    OPPONENT_HAND = 0x2
    CARD_DECK = 0x3
    STACK = 0x4
    PLAYED_LEFT = 0x5

