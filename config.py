# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 23:14:38 2020

@author: Kamil Chrustowski
"""
from __future__ import annotations
import os
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCursor, QFont, QIcon, QPixmap
from enum import Enum


class BlankBg(Enum):
    BG0 = 0
    BG1 = 1
    BG2 = 2
    BG3 = 3
    BG4 = 4

    @staticmethod
    def from_name(name: str ='blank.png') -> BlankBg: 
        n = name.split('.')

        if(len(n) != 2 or n[1] == ''):
            return BlankBg.BG0
        else:
            name = n[0]

        import re
        n = re.split(r'(\d+)$', name)[0:2]
        if(len(n) != 2 or n[1] == ''): 
            return BlankBg.BG0
        
        return BlankBg[f'BG{n[1]}']


class FontWeight(Enum):
    XS = 10
    SM = 12
    MD = 14
    LG = 16
    XL = 18
    XXL = 40


class MenuEnum(Enum):
    HELP = 0
    NETWORK = 1
    QUIT = 2
    CONFIG = 3
    SINGLE_GAME = 4

        
class Config:

    __instance = None

    BGS = 'images\\backgrounds'

    BLANKS = ['blank1.png', 
             'blank2.png',
             'blank3.png',
             'blank4.png',
             'blank.png']

    FONT_XXL = QFont('KBREINDEERGAMES', 40)
    FONT_XL = QFont('KBREINDEERGAMES', 18)
    FONT_LG = QFont('KBREINDEERGAMES', 16)
    FONT_MD = QFont('KBREINDEERGAMES', 14)
    FONT_SM = QFont('KBREINDEERGAMES', 12)
    FONT_XS = QFont('KBREINDEERGAMES', 10)

    STYLE_FILE = 'ui\\py1000.qss'

    DEFAULT_BG = 'bg2.png'

    BANNER = 'banner.png'

    WELCOME_BG = 'main.jpg'

    OPTIONS = {
           'Gondola full of stars':'bg1.png',
           'Gondola swimming in the lake of tears':'bg2.png',
           'Gondola on the Moon':'bg3.png',
           'Gondola 2077':'bg4.png'
        }

    SHADOWS = {
           'bg1.png':'#8fd9ff',
           'bg2.png':'#386890',
           'bg3.png': '#f8f4dd',
           'bg4.png': '#617479'
        }

    TEXT = {   
           'bg1.png':'#476677',
           'bg2.png':'#f0f8ff',
           'bg3.png': '#2c1b01',
           'bg4.png': '#fffff0'
        }

    def get_blank_background(self, bg_type: BlankBg) -> QPixmap:
        return self.__blank_bgs[bg_type]

    def get_background_by_name(self, name: str) -> QPixmap:
        return self.__game_bgs.get(Config.OPTIONS.get(name, ''), None)

    @property
    def cursor(self) -> QCursor:
        return self.__game_cursor

    @staticmethod
    def get_option_key(value: str) -> str:
        for key, val in Config.OPTIONS.items():
            if val == value:
                return key
        return None 

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Config.__instance == None:
            Config()
        return Config.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Config.__instance != None:
            raise Exception("This class is a singleton!")
        
        self.__game_bgs = {}
        self.__game_cursor = None
        self.__name = Config.DEFAULT_BG
        self.__shadow = Config.SHADOWS[self.__name]
        self.__text = Config.TEXT[self.__name]
        self.__load_images()
        self.__playing_background = self.__game_bgs[Config.DEFAULT_BG]
        
        Config.__instance = self

    def __load_images(self):
        self.__game_bgs = {name:QPixmap(os.path.join(Config.BGS, name)) for name in Config.TEXT.keys()}
        self.__game_cursor = QCursor(QPixmap(os.path.join(
                    'images', 'gondola_coursor.png'
                    )
                ).scaled(QSize(25, 25), Qt.KeepAspectRatio), -1, -1)
        self.__blank_bgs = {BlankBg.from_name(name):QPixmap(os.path.join(Config.BGS, name)) for name in Config.BLANKS}
        self.__banner = QPixmap(os.path.join('images', Config.BANNER))
        self.__welcome_bg = QPixmap(os.path.join('images', Config.WELCOME_BG))
        self.__window_icon = QIcon(QPixmap(os.path.join('images', 'ico.png')))

    @property
    def window_icon(self) -> QIcon:
        return self.__window_icon

    @property
    def banner(self) -> QPixmap:
        return self.__banner

    @property
    def welcome_bg(self) -> QPixmap:
        return self.__welcome_bg

    def get_shadow_config(self) -> str:
        return self.__shadow

    def get_text_config(self) -> str:
        return self.__text

    def get_background_config(self) -> QPixmap:
        return self.__playing_background

    def get_name(self) -> str:
        return self.__name

    def set_background_config(self, name: str):
        self.__name = Config.OPTIONS[name]
        self.__shadow = Config.SHADOWS[self.__name]
        self.__text = Config.TEXT[self.__name]
        self.__playing_background = self.__game_bgs[self.__name]

    