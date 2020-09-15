from . import *

class GamePlayScene(QGraphicsScene):
    __pixmap = None
    def __init__(self, parent = None):
        super(GamePlayScene, self).__init__(parent)