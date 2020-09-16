from . import Suits, QLabel, QPixmap, QSize, os

class SuitLabel(QLabel):
    __size =[50,50]
    __pixmaps = {Suits.C:'club.png',Suits.H:'heart.png', Suits.S:'spade.png', Suits.D:'diamond.png', Suits.NO_SUIT:'default.png'}
    def __init__(self,parent=None, suit:Suits=Suits.NO_SUIT):
        super(SuitLabel, self).__init__(parent)
        self.setFixedHeight(self.__size[1])
        self.setFixedWidth(self.__size[0])
        self.setAutoFillBackground(True)
        self.setText("NONE")
        self.setPixmap
        self.__suit = suit
        self.__pixmap = QPixmap(os.path.join('images', self.__pixmaps[self.__suit])).scaled(QSize(self.__size[0], self.__size[1]))
        self.setPixmap(self.__pixmap)

    def changeSuit(self, suit:Suits):
        name = self.__pixmaps.get(suit, '')
        print(name)
        if(name != ''):
            self.__suit = suit
            self.__pixmap = QPixmap(os.path.join('images', self.__pixmaps[self.__suit])).scaled(QSize(self.__size[0], self.__size[1]))
            self.setPixmap(self.__pixmap)
            self.update()

    def get_suit(self):
        return self.__suit