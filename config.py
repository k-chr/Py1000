# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 23:14:38 2020

@author: Kamil Chrustowski
"""
import os
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QCursor, QFont, QPixmap, Qt
from ui.widgets.configbutton import ConfigButton   
               
        
class Config:

    __instance = None

    BGS = 'images\\backgrounds'

    BLANK1 = os.path.join(BGS, 'blank1.png')
    BLANK2 = os.path.join(BGS, 'blank2.png')
    BLANK3 = os.path.join(BGS, 'blank3.png')
    BLANK4 = os.path.join(BGS, 'blank4.png')
    BLANK = os.path.join(BGS, 'blank.png')

    FONT_XXL = QFont('KBREINDEERGAMES', 40)
    FONT_XL = QFont('KBREINDEERGAMES', 18)
    FONT_LG = QFont('KBREINDEERGAMES', 16)
    FONT_MD = QFont('KBREINDEERGAMES', 14)
    FONT_SM = QFont('KBREINDEERGAMES', 12)
    FONT_XS = QFont('KBREINDEERGAMES', 10)

    GAME_CURSOR = QCursor(QPixmap(os.path.join(
                    'images', 'gondola_coursor.png'
                    )
                ).scaled(QSize(25, 25), Qt.KeepAspectRatio), -1, -1)


    STYLE_FILE = 'ui\\py1000.qss'

    DEFAULT_BG = 'bg2.png'

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
       
        self.__playing_background = os.path.join(Config.BGS, Config.DEFAULT_BG)
        self.__name = Config.DEFAULT_BG
        self.__shadow = Config.SHADOWS[self.__name]
        self.__text = Config.TEXT[self.__name]
        Config.__instance = self

    def get_shadow_config(self) -> str:
        return self.__shadow

    def get_text_config(self) -> str:
        return self.__text

    def get_background_config(self) -> str:
        return self.__playing_background

    def get_name(self) -> str:
        return self.__name

    def set_background_config(self, name: str):
        self.__name = name
        self.__shadow = Config.SHADOWS[self.__name]
        self.__text = Config.TEXT[self.__name]
        self.__playing_background = os.path.join(Config.BGS, name)
            