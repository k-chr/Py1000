from config import BlankBg
from . import (QDialog, QGraphicsDropShadowEffect,
               QWidget, QPalette, Qt, ConfigButton, Config,
               QEvent, QPainter, QPaintEvent, QPushButton,
               QVBoxLayout, QColor, QSize, QLabel, QBrush, 
               QFont, QButtonGroup, QGroupBox, QSizePolicy,
               QHBoxLayout, Background, ConfigComboBox)


class ConfigDialog(QDialog):

    __preview_size = QSize(540, 320)

    def closeEvent(self, event: QEvent):
        event.ignore()

    def updatePreview(self, key):
        self.preview.setPixmap(Config.get_instance().get_background_by_name(key).scaled(ConfigDialog.__preview_size, Qt.KeepAspectRatio))

    def accept(self):
        Config.get_instance().set_background_config(self.combobox.currentText())
        super(ConfigDialog, self).accept()

    def handle_buttons(self, button: QPushButton):
        print(button)
        if(button.text() == "OK"):
            self.accept()
        elif(button.text() == "CANCEL"):
            self.done(QDialog.Rejected)

    def __init__(self, parent: QWidget =None):
        super(ConfigDialog, self).__init__(parent)
        self.setFixedSize(700, 600)
        config = Config.get_instance()
        self.combobox = ConfigComboBox()
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        for key in Config.OPTIONS:
            self.combobox.addItem(key)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.Tool)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor("Black"))
        shadow.setOffset(0,0)
        
        self.setGraphicsEffect(shadow)
        self.combobox.setCurrentText(Config.get_option_key(config.get_name()))
        self.preview = Background(config.get_background_config(), ConfigDialog.__preview_size.height(), ConfigDialog.__preview_size.width())
        self.layout = QVBoxLayout()
        lab = QLabel('Choose background from comboBox')
        lab.setFixedHeight(30)
        
        lab.setStyleSheet("QLabel{padding-left: 2px; padding-right: 2px; padding-top: 2px; padding-bottom: 2px;}")
        lab.setFont(QFont('KBREINDEERGAMES', 18))
        lab.setAutoFillBackground(True)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QColor(255,255,255,128)))
        lab.setPalette(palette)
        lab.setContentsMargins(2,2,2,2)
        self.layout.addWidget(lab)
        self.layout.addWidget(self.combobox)
        lab2 = QLabel('Preview: ')
        lab2.setFixedHeight(30)
        lab2.setStyleSheet("QLabel{padding-left: 2px; padding-right: 2px; padding-top: 2px; padding-bottom: 2px;}")
        lab2.setAutoFillBackground(True)
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(255,255,255,128))
        lab2.setPalette(pal)
        lab2.setContentsMargins(2,2,2,2)
        lab2.setFont(QFont('KBREINDEERGAMES', 18))
        self.layout.addWidget(lab2)
        self.layout.addWidget(self.preview, 0, Qt.AlignCenter)
        self.combobox.currentTextChanged.connect(self.updatePreview)
        self.pixmap = config.get_blank_background(BlankBg.BG1)
        self.buttons = QButtonGroup()
        self.ok_button = ConfigButton(text="OK")
        group = QGroupBox()
        group.setContentsMargins(0,0,0,0)
        group.setFlat(True)
        group.setStyleSheet("border:0;")
        self.cancel_button = ConfigButton(text="CANCEL")
        self.buttons.addButton(self.ok_button)
        self.buttons.addButton(self.cancel_button)
        self.buttons.buttonPressed.connect(self.handle_buttons)
        hb = QHBoxLayout()
        hb.addWidget(self.ok_button)
        hb.addWidget(self.cancel_button)
        group.setLayout(hb)
        group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setLayout(self.layout)
        self.layout.addWidget(group,0, Qt.AlignBottom|Qt.AlignRight)
        
        self.setCursor(config.get_cursor())
        self.combobox.setCursor(config.get_cursor())

    def paintEvent(self, event: QPaintEvent):
        super(ConfigDialog, self).paintEvent(event)
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(0,0, self.pixmap.scaled(QSize(self.width(), self.height())))
        painter.end()

    @staticmethod
    def getDialog(parent=None):
        dialog = ConfigDialog(parent)
        result = dialog.exec_()
        return result == QDialog.Accepted


