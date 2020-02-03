from PyQt5.Qt import *
import os
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QSizePolicy
from configbutton import ConfigButton
class InitDialog(QDialog):
    __values = [110,120,130,140,150,160,170,180,190,200,210,220,230,
                240,250,260,270,280,290,300,310,320,330,340,350,360]
    __value = 0
    def closeEvent(self, event):
        event.ignore()   
    def __init__(self, parent=None, minimum=110, forbidden=130):
        super(InitDialog, self).__init__(parent)     
        layout = QGridLayout()
        self.setAutoFillBackground(True)
        sh = QGraphicsDropShadowEffect(self)
        sh.setBlurRadius(50)
        self.setGraphicsEffect(sh)
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignCenter)
        layout.setHorizontalSpacing(3)
        layout.setVerticalSpacing(3)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.pixmap = QPixmap(os.path.join('images\\backgrounds', 'blank3.png'))
        self.setAttribute(Qt.WA_TranslucentBackground)
        label = QLabel('Click value or cancel, if you have no opportunity to make a bid, or you want to say \"PASS\":')
        label.setFont(QFont('KBREINDEERGAMES', 18))
        label.setWordWrap(True)
        label.setAutoFillBackground(True)
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(255,255,255,128))
        label.setPalette(pal)
        layout.addWidget(label, 0, 0,1, 14)
        self.buttonGroup = QButtonGroup()
        cols = 13
        i = 0
        row = 1
        for val in sorted(self.__values):
            button = ConfigButton(text=str(val))
            self.buttonGroup.addButton(button)
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.addWidget(button, row, i)
            i += 1
            if(i >= cols):
                i = 0
                row+=1
        for b in self.buttonGroup.buttons():
            if int(b.text()) < minimum or (forbidden > minimum and int(b.text()) >= forbidden) or (forbidden <= minimum and int(b.text()) >= minimum):
                b.setEnabled(False)
        self.buttonGroup.buttonClicked.connect(self.__setValue)        
        self.cancel_button = ConfigButton(text="CANCEL")
        self.cancel_button.clicked.connect(lambda: self.reject())
        group = QGroupBox()
        group.setContentsMargins(0,0,0,0)
        group.setFlat(True)
        group.setStyleSheet("background: none;border:0;")
        hb = QHBoxLayout()
        hb.addWidget(self.cancel_button, 0, Qt.AlignRight|Qt.AlignBottom)
        group.setLayout(hb)
        group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(group, 3,0, 3,13)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(600, 200)
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.save()
        painter.drawPixmap(0,0, self.pixmap.scaled(QSize(self.width(), self.height())))
        painter.restore()
    def __setValue(self, button):
        self.__value = int(button.text())
        self.done(QDialog.Accepted)
    def getValue(self):
        return self.__value
    @staticmethod
    def getDialog(parent=None, title="Bidding", min=110, max=130):
        dialog = InitDialog(parent, min, max)
        dialog.setWindowTitle(title)
        result = dialog.exec_()
        value = dialog.getValue()
        return (value, result == QDialog.Accepted)