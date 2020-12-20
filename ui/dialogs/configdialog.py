from . import (QDialog, QGraphicsDropShadowEffect,
               QWidget, Qt, ConfigButton, Config, BlankBg,
               QEvent, QPainter, QPaintEvent, QPushButton,
               QVBoxLayout, QColor, QSize, QLabel, 
               QButtonGroup, QGroupBox, QSizePolicy,
               QHBoxLayout, Background, ConfigComboBox)
from typing import Tuple

class ConfigDialog(QDialog):

    def closeEvent(self, event: QEvent):
        event.ignore()

    def updatePreview(self, key):
        self.preview.setPixmap(Config.get_instance().get_background_by_name(key))

    def accept(self):
        Config.get_instance().set_background_config(self.combobox.currentText())
        super(ConfigDialog, self).accept()

    def handle_buttons(self, button: QPushButton):
       
        if(button.text() == "OK"):
            self.accept()
        elif(button.text() == "CANCEL"):
            self.done(QDialog.Rejected)

    def __set_flags(self):
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.Tool)

    def __set_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor("Black"))
        shadow.setOffset(0,0)
        self.setGraphicsEffect(shadow)

    def __create_label(text: str) -> QLabel:
        lab = QLabel(text)
        lab.setObjectName('configDialogLabel')
        lab.setAutoFillBackground(True)

        return lab

    def __create_dialog_buttons() -> Tuple[QGroupBox, QButtonGroup]:
        buttons = QButtonGroup()

        ok_button = ConfigButton(text="OK")
        cancel_button = ConfigButton(text="CANCEL")
        
        buttons.addButton(ok_button)
        buttons.addButton(cancel_button)

        hb = QHBoxLayout()
        hb.addWidget(ok_button)
        hb.addWidget(cancel_button)

        group = QGroupBox()
        group.setObjectName("configDialogButtonGroup")
        group.setFlat(True)
        group.setLayout(hb)
        group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        return (group, buttons)

    def __init__(self, parent: QWidget =None):
        super(ConfigDialog, self).__init__(parent)
        
        self.__set_flags()
        self.__set_shadow()

        self.combobox = ConfigComboBox()
        for key in Config.OPTIONS:
            self.combobox.addItem(key)

        self.combobox.setCurrentText(Config.get_option_key(Config.get_instance().get_name()))
        self.preview = Background()
        self.combobox.currentTextChanged.connect(self.updatePreview)
        self.pixmap = Config.get_instance().get_blank_background(BlankBg.BG3)
        group, self.__buttons = ConfigDialog.__create_dialog_buttons()
        self.__buttons.buttonPressed.connect(self.handle_buttons)

        layout = QVBoxLayout()
        layout.addWidget(ConfigDialog.__create_label('Choose background from comboBox'))
        layout.addWidget(self.combobox)
        layout.addWidget(ConfigDialog.__create_label('Preview: '))
        layout.addWidget(self.preview, 0, Qt.AlignCenter)
        layout.addWidget(group, 0, Qt.AlignBottom|Qt.AlignRight)

        self.setLayout(layout)


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
