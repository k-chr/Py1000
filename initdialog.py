from PyQt5.Qt import *
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QSlider


class InitDialog(QDialog):
    def closeEvent(self, event):
        event.ignore()

    def slider_value_changed(self, value):
        if not value:
            return
        self.slider.setValue(int(value))

    def slider_changed(self, value):
        self.slider_value.setText(str(value))

    def __init__(self, parent=None, min=100, max=120):
        super(InitDialog, self).__init__(parent)
        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel('Enter bidding value:'), 0, 0)

        #tu też ustawianie tego, czy miedzy 100 a 120 czy więcej w zależności od posiadanego statusu gracza (czy ma meldunek, czy nie
        slider_hbox = QHBoxLayout()
        slider_hbox.addWidget(QLabel('100'))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(100, max)
        self.slider.setSingleStep(10)
        self.slider.setSliderPosition(100)
        self.slider.setTickPosition(QSlider.TicksAbove)
        self.slider.valueChanged.connect(self.slider_changed)
        slider_hbox.addWidget(self.slider)
        slider_hbox.addWidget(QLabel(max.__str__()))

        self.slider_value = QLineEdit(min.__str__())
        objValidator = QIntValidator(self)
        objValidator.setRange(min, max)
        self.slider_value.setValidator(objValidator)
        self.slider_value.textChanged.connect(self.slider_value_changed)
        slider_hbox.addWidget(self.slider_value)

        slider_widget = QWidget()
        slider_widget.setLayout(slider_hbox)
        layout.addWidget(slider_widget, 0, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                   Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)  # podłączenie pod std. f-cje zdarzenia
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons, 1, 0, 1, 2)

    @staticmethod
    def getDialog(parent=None, title="Init", name=None, min=100, max=120):
        dialog = InitDialog(parent, min, max)
        dialog.setWindowTitle(title)
        result = dialog.exec_()
        value = dialog.slider.value()
        return (value, result == QDialog.Accepted)

