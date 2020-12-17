from . import QPainter, QPixmap, QWidget, QSize, Qt


class Background(QWidget):

    def __init__(self, pixmap: QPixmap, height: int, width: int, parent: QWidget=None):
        super(Background, self).__init__(parent)
        self.pixmap = pixmap
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setStyleSheet("background-color: transparent;background: none; background-repeat: none; border: 10px;")

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(0,0, self.pixmap.scaled(QSize(self.width(), self.height())))
        painter.end()

    def setPixmap(self, pixmap):
        self.pixmap = pixmap

        if pixmap is None:
            print("Invalid pixmap")
        self.update()