from PyQt5.Qt import *
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QSlider


class InitDialog(QDialog):
    def closeEvent(self, event):
        event.ignore()

    def __init__(self, parent=None, min=100, max=120):
        super(InitDialog, self).__init__(parent)
        self.setFixedSize(250, 80)
        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel('Enter bidding value:'), 0, 0)

        self.combobox = QComboBox()
        self.combobox.setFixedWidth(100)
        for i in range(min, max+1, 10):
            self.combobox.addItem(i.__str__())

        layout.addWidget(self.combobox, 0, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                   Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)  # podłączenie pod std. f-cje zdarzenia
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons, 1, 0, 1, 2)

    @staticmethod
    def getDialog(parent=None, title="Init", min=100, max=120):
        dialog = InitDialog(parent, min, max)
        dialog.setWindowTitle(title)
        result = dialog.exec_()
        value = int(dialog.combobox.currentText())
        return (value, result == QDialog.Accepted)

