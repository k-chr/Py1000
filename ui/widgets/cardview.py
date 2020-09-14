from .. import *

class CardView(QGraphicsPixmapItem):
    def __init__(self, id:str, location=None):
        super(CardView).__init__()
        self.id = id
        self.location = location
        self.face = None
        self.back = None
        self.setTransformationMode(Qt.SmoothTransformation)
        

