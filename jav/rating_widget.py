
from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QApplication, QHBoxLayout, QVBoxLayout)
from PyQt5.QtCore import Qt, pyqtProperty, QEvent
from PyQt5.QtGui import QKeyEvent

class RatingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)

        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.valueChanged[int].connect(self.OnChangeValue)
        mainLayout.addWidget(self._slider)
        self._value = QLineEdit()
        self._value.setMaximumWidth(50)
        mainLayout.addWidget(self._value)

        self.setLayout(mainLayout)

    def OnChangeValue(self, value):
        v = value/10
        self._value.setText(str(v))
        QApplication.postEvent(self,
            QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier))

    def getValue(self):
        return self._value.text()

    def setValue(self, value):
        if not value:
            value = 0

#       print('setValue :', value)
        v = float(value) * 10
        self._slider.setValue(int(v))
        self._value.setText(str(value))

    Value = pyqtProperty(str, getValue, setValue)
