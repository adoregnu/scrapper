from PyQt5.QtWidgets import (QLineEdit, QListWidget, QWidget, QHBoxLayout
    , QVBoxLayout, QPushButton, QApplication)
from PyQt5.QtCore import (Qt, pyqtProperty, QEvent)
from PyQt5.QtGui import QKeyEvent

class GenreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self._listWidget = QListWidget()
        self._listWidget.itemDoubleClicked.connect(self.onActorNameDblClicked)
        mainLayout.addWidget(self._listWidget)

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignTop)
        self._newItem = QLineEdit()
        self._add = QPushButton('Add')
        self._add.clicked.connect(self.onAddClicked)
        self._remove = QPushButton('Remove')
        self._remove.clicked.connect(self.onRemoveClicked)
        right.addWidget(self._newItem)
        right.addWidget(self._add)
        right.addWidget(self._remove)
        mainLayout.addLayout(right)

        self.setLayout(mainLayout)

    def onActorNameDblClicked(self, item):
        self._newItem.setText(item.text())

    def onAddClicked(self):
        text = self._newItem.text().strip()
        if not len(text): return
        items = self._listWidget.findItems(text, Qt.MatchExactly)
        if (len(items) > 0):
            print('already exists actor name!')
            return

        self._listWidget.addItem(text)
        self._newItem.clear()
        QApplication.postEvent(self,
            QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier))

    def onRemoveClicked(self):
        if not self._listWidget.currentItem():
            return

        item = self._listWidget.currentItem()
        #print(item.text())
        self._listWidget.takeItem(self._listWidget.row(item))
        QApplication.postEvent(self,
            QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier))

    def getValue(self):
        vals = []
        for i in range(self._listWidget.count()):
            vals.append(self._listWidget.item(i).text())
        return ';'.join(vals)

    def setValue(self, value):
        self._listWidget.clear()
        if not value: return
        self._listWidget.insertItems(0, value.split(';'))

    Value = pyqtProperty(str, getValue, setValue)