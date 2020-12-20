from . import QPainter, QPixmap, QWidget, QSize, Qt, Config, QSizePolicy, QPaintEvent


class Background(QWidget):

    def __init__(self, parent: QWidget=None):
        super(Background, self).__init__(parent)
        self.setObjectName('preview')
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.__pixmap = Config.get_instance().get_background_config().scaled(self.width(), self.height())

    def paintEvent(self, event: QPaintEvent):
        super(Background, self).paintEvent(event)
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(0,0, self.__pixmap.scaled(QSize(self.width(), self.height())))
        painter.end()

    def setPixmap(self, pixmap: QPixmap):
        self.__pixmap = pixmap

        if pixmap is None:
            print("Invalid pixmap")
        self.update()