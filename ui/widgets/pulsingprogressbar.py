"""
Created on Sun Sep  13 01:04:18 2020

@author: Kamil Chrustowski
"""


from .. import *

class PulsingProgressBar(QProgressBar):
    def __init__(self,width, height, parent = None):
        super(PulsingProgressBar, self).__init__(parent)
        self.setMinimum(0)
        self.setMaximum(0)
        self.setValue(0)
        self.setFixedSize(QSize(width, height))
        self.setStyle(QStyleFactory.create('WindowsVista'))
        self.setStyleSheet("QProgressBar:horizontal {border: 1px solid gray;border-radius: 3px;background: white;padding: 1px;}QProgressBar::chunk {background: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #05B8CC, stop: 1 white);}")
        self.setTextVisible(False)
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(0)
        self.setGraphicsEffect(self.glow)
        self.glow.setXOffset(0)
        self.glow.setYOffset(0)
        self.glow.setColor(QColor("#05B8CC"))
        self.animu = QPropertyAnimation(self.glow, b"blurRadius")
        self.animu.setStartValue(0)
        self.animu.setEndValue(100)
        self.animu.setDuration(1000)
        self.animu.setLoopCount(-1)
        self.animu.start()
    def end(self):
        self.setMaximum(100)
        self.setValue(100)
        self.animu.stop()