from . import QGraphicsView, Qt

class CardGraphicsView(QGraphicsView):

    def __init__(self, parent =None):
        super(CardGraphicsView, self).__init__(parent)               
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    def resizeEvent(self, event):
        print(event)
        self.fitInView(self.scene().sceneRect(),Qt.KeepAspectRatio)
