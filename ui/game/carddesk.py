from . import *
from .gameplayscene import GamePlayScene
from .cardgraphicsview import CardGraphicsView

class CardDesk(QWidget):

    def __init__(self, parent=None):
        super(CardDesk, self).__init__(parent)  
        self.__initUI()

    def __initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)
        self.scene = GamePlayScene()
        self.view = CardGraphicsView(self.scene)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.view.setSceneRect(QRectF(self.view.viewport().rect()))
        self.view.setRenderHint(QPainter.Antialiasing) 
        layout.addWidget(self.view)