from . import (QDialog, QGraphicsDropShadowEffect,
               QWidget, QPalette, Qt, ConfigButton, Config, BlankBg,
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
        lab.setObjectName('configDialogLabel')
        
        lab.setFont(QFont('KBREINDEERGAMES', 18))
        lab.setAutoFillBackground(True)
        self.layout.addWidget(lab)
        self.layout.addWidget(self.combobox)
        lab2 = QLabel('Preview: ')
        lab2.setAutoFillBackground(True)
        lab2.setObjectName('configDialogLabel')
        lab2.setFont(QFont('KBREINDEERGAMES', 18))
        self.layout.addWidget(lab2)
        self.layout.addWidget(self.preview, 0, Qt.AlignCenter)
        self.combobox.currentTextChanged.connect(self.updatePreview)
        self.pixmap = config.get_blank_background(BlankBg.BG4)
        self.buttons = QButtonGroup()
        self.ok_button = ConfigButton(text="OK")
        group = QGroupBox()
        group.setObjectName("configDialogButtonGroup")
        group.setFlat(True)
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
        self.layout.addWidget(group, 0, Qt.AlignBottom|Qt.AlignRight)


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


