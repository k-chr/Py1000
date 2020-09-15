from .. import *

class CardView(QGraphicsPixmapItem):
    def __init__(self, dataContext:Card, location:CardLocation=None):
        super(CardView, self).__init__()
        self.dataContext = dataContext
        self.location = location
        self.face = None
        self.back = None
        self.side = CardSide.BACK
        self.rot180 = False
        self.animation = QPropertyAnimation(self, b'pos')
        self.setTransformationMode(Qt.SmoothTransformation)
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(-1)
        self.clicked = pyqtSignal(Card)
        self.__loadImages()

    def __loadImages(self):
        self.face = QPixmap(
            os.path.join('images\\cards', '%s_%s.png' % (self.dataContext.suit.name, self.dataContext.value.name))
        )
        self.face = self.face.scaled(Defaults.CARD_DIMENSIONS.width(), Defaults.CARD_DIMENSIONS.height())
        self.back = QPixmap(
            os.path.join('images\\cards', 'back.png')
        )
        self.back = self.back.scaled(Defaults.CARD_DIMENSIONS.width(), Defaults.CARD_DIMENSIONS.height())

    def turn_card(self, side:CardSide):
        self.side = side
        pixmap = self.face if self.side is CardSide.FRONT else self.back
        self.setPixmap(pixmap.transformed(QTransform().scale(-1,-1)) if self.rot180 else pixmap)

    def rotate180H(self):
        self.rot180 = not self.rot180
        self.setPixmap(self.pixmap().transformed(QTransform().scale(-1, -1)))

    def mousePressEvent(self, e):
        super(CardView, self).mousePressEvent(e)
        if self.location is not CardLocation.HAND:
            e.ignore()
            return

        self.clicked.emit(self.dataContext)
        e.accept()
