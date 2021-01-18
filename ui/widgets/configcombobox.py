from . import QComboBox, QStyledItemDelegate, Qt, QWidget

class ConfigComboBox(QComboBox):

    def __init__(self, parent: QWidget =None):
        super(ConfigComboBox, self).__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setItemDelegate(QStyledItemDelegate())