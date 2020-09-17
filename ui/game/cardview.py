from . import QGraphicsPixmapItem, Card, CardLocation, CardSide, QGraphicsItem, Qt, QPropertyAnimation, pyqtSignal, QPixmap, path, Defaults, QTransform

class CardView(QGraphicsPixmapItem):
    def __init__(self, dataContext: Card, location: CardLocation =None):
        super(CardView, self).__init__()
        self.data_context = dataContext
        self.location = location
        self.face = None
        self.back = None
        self.side = CardSide.BACK
        self.rot_180 = False
        self.animation = QPropertyAnimation(self, b'pos')
        self.setTransformationMode(Qt.SmoothTransformation)
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(-1)
        self.clicked = pyqtSignal(Card)
        self.__load_images()

    def __load_images(self):
        self.face = QPixmap(
            path.join('images\\cards', '%s_%s.png' % (self.data_context.suit.name, self.data_context.value.name))
        )
        self.face = self.face.scaled(Defaults.CARD_DIMENSIONS.width(), Defaults.CARD_DIMENSIONS.height())
        self.back = QPixmap(
            path.join('images\\cards', 'back.png')
        )
        self.back = self.back.scaled(Defaults.CARD_DIMENSIONS.width(), Defaults.CARD_DIMENSIONS.height())

    def turn_card(self, side: CardSide):
        self.side = side
        pixmap = self.face if self.side is CardSide.FRONT else self.back
        self.setPixmap(pixmap.transformed(QTransform().scale(-1,-1)) if self.rot_180 else pixmap)

    def rotate_180_h(self):
        self.rot_180 = not self.rot_180
        self.setPixmap(self.pixmap().transformed(QTransform().scale(-1, -1)))

    def mousePressEvent(self, e):
        super(CardView, self).mousePressEvent(e)
        if self.location is not CardLocation.HAND:
            e.ignore()
            return

        self.clicked.emit(self.data_context)
        e.accept()
