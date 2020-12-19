from . import QComboBox, QStyledItemDelegate, Qt, QWidget, Config

class ConfigComboBox(QComboBox):

    def __init__(self, parent: QWidget =None):
        super(ConfigComboBox, self).__init__(parent)
        self.setFont(Config.FONT_MD)
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setItemDelegate(QStyledItemDelegate())