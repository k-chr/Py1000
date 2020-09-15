from . import *

class CardGraphicsView(QGraphicsView):
    """ extends QGraphicsView for resize event handling  """
    def __init__(self, parent=None):
        super(CardGraphicsView, self).__init__(parent)               
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    def resizeEvent(self, event):
        self.fitInView(QRectF(self.viewport().rect()),Qt.KeepAspectRatio)