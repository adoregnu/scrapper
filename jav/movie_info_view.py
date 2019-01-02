import os
from collections import OrderedDict
import xml.etree.ElementTree as ET

from PyQt5.QtWidgets import (QLabel, QLineEdit, QPlainTextEdit, QListWidget,
    QDataWidgetMapper, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QApplication, QStyledItemDelegate, QFrame, QGridLayout, QCheckBox)
from PyQt5.QtCore import (Qt, pyqtProperty, QEvent)
from PyQt5.QtGui import QKeyEvent, QPixmap
 
from PIL import Image, ImageQt

import jav.utils as utils
from movie_info_model import MovieInfoModel

class ListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self._listWidget = QListWidget()
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
        print(item.text())
        self._listWidget.takeItem(self._listWidget.row(item))

    def getListValue(self):
        #print('getListValue')
        vals = []
        for i in range(self._listWidget.count()):
            vals.append(self._listWidget.item(i).text())
        return ';'.join(vals)

    def setListValue(self, value):
        self._listWidget.clear()
        if not value: return
        self._listWidget.insertItems(0, value.split(';'))

    listValue = pyqtProperty(str, getListValue, setListValue)

class ImageLabel(QWidget):
    _image = None 
    def __init__(self, title, editable = True, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setMinimumWidth(400)
        self._label.setMinimumHeight(350)
        self._label.setFrameShape(QFrame.Panel)
        self._label.setFrameShadow(QFrame.Sunken)
        self._label.setLineWidth(1)

        layout.addWidget(self._label)
        if editable:
            hbox = QHBoxLayout()
            self._btnRotate = QPushButton('Rotate 90 degree')
            self._btnRotate.clicked.connect(self.onClickRotate)
            self._btnCrop = QPushButton('Crop Right')
            self._btnCrop.clicked.connect(self.onClickCrop)
            hbox.addWidget(self._btnRotate)
            hbox.addWidget(self._btnCrop)
            layout.addLayout(hbox)
        self.setLayout(layout)

    def draw(self):
        self._label.clear()
        qim = ImageQt.ImageQt(self._image.image())
        pixmap = QPixmap.fromImage(qim).scaled(400, 400, Qt.KeepAspectRatio,
                transformMode=Qt.SmoothTransformation)
        self._label.setPixmap(pixmap)

    def image(self):
        #print('image')
        return self._image

    def setImage(self, image):
        if not image:
            if self._image: del self._image
            self._image = None
            self._label.clear()
            return

        #print('setImage {}'.format(image))
        if isinstance(image, str):
            self._image = utils.AvImage(image)
        elif isinstance(image, utils.AvImage):
            self._image = image
        else:
            print('unknown format')
            return
        self.draw()

    def onClickRotate(self):
        #print('onClickRotate')
        self._image = self._image.rotate()
        self.draw()
        QApplication.postEvent(self,
            QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier))

    def onClickCrop(self):
        #print('onClickCrop')
        self._image = self._image.cropLeft(0.5)
        self.draw()
        QApplication.postEvent(self,
            QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier))

class MovieInfoDelegate(QStyledItemDelegate):
    def __init__(self, parent = None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        print('createEditor {}'.format(index.column()))

    def setEditorData(self, editor, index):
        data = index.model().data(index, Qt.DisplayRole)
        if isinstance(editor, QLineEdit):
            editor.setText(data)
        elif isinstance(editor, QPlainTextEdit):
            editor.setPlainText(data)
        else:
            editor.setImage(data)

    def setModelData(self, editor, model, index):
        #print('setModelData column:{}'.format(index.column()))
        if isinstance(editor, QLineEdit):
            model.setData(index, editor.text(), Qt.DisplayRole)
        elif isinstance(editor, QPlainTextEdit):
            model.setData(index, editor.toPlainText(), Qt.DisplayRole)
        else:
            model.setData(index, editor.image(), Qt.DisplayRole)

class MovieInfoView(QWidget):
    ID_DESC = 0
    ID_CHECK = 1
    ID_CTRL = 2
    def __init__(self):
        super().__init__()
        self.initWidgets()
        self.mapWidget2Model()

    def initWidgets(self):
        from collections import OrderedDict
        self.controls = OrderedDict() 
        self.controls['path'] = ['Path:', QLineEdit()]
        self.controls['title'] = ['Title:', QLineEdit()]
        self.controls['originaltitle'] = ['Original Title:', QLineEdit()]
        self.controls['year'] = ['Year:', QLineEdit()]
        self.controls['releasedate'] = ['Release Date:', QLineEdit()]
        self.controls['id'] = ['ID:', QLineEdit()]
        self.controls['studio'] = ['Studio:', QLineEdit()]
        self.controls['set'] = ['Movie Set:', QLineEdit()]
        self.controls['plot'] = ['Plot:', QPlainTextEdit()]
        self.controls['genre'] = ['Genre:', ListWidget()]
        self.controls['actor'] = ['Actor:', ListWidget()]

        left = QGridLayout()
        row = 0
        for _, ctrl in self.controls.items():
            check = QCheckBox()
            check.stateChanged.connect(self.onChecked)
            ctrl.insert(self.ID_CHECK, check)
            left.addWidget(ctrl[self.ID_CHECK], row, 0, Qt.AlignTop|Qt.AlignRight)
            left.addWidget(QLabel(ctrl[self.ID_DESC]), row, 1, Qt.AlignTop|Qt.AlignRight)
            left.addWidget(ctrl[self.ID_CTRL], row, 2)
            row += 1

        right = QVBoxLayout()
        self.poster = ImageLabel('poster')
        self.fanart = ImageLabel('fanart', False)
        right.addWidget(self.poster)
        right.addWidget(self.fanart)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(left)
        layout.addLayout(right)
        self.setLayout(layout)

    def mapWidget2Model(self):
        self.mapper = QDataWidgetMapper(self)
        self.model = MovieInfoModel()
        self.mapper.setModel(self.model)

        index = 0
        for key, ctrl in self.controls.items():
            if 'genre' == key or 'actor' == key:
                self.mapper.addMapping(ctrl[self.ID_CTRL], index, b'listValue')
            else:
                self.mapper.addMapping(ctrl[self.ID_CTRL], index)
            index += 1
        self.mapper.addMapping(self.poster, index)
        index += 1
        self.mapper.addMapping(self.fanart, index)
        self.mapper.setItemDelegate(MovieInfoDelegate())

    def onChecked(self, state):
        columnFilter = []
        for key, val in self.controls.items():
            if val[self.ID_CHECK].isChecked():
                columnFilter.append(key)

        self.model.setColumnFilter(columnFilter)

    def setMovieInfo(self, movieinfo):
        if not movieinfo: return
        self.model.setMovieInfo(movieinfo)
        self.mapper.toFirst()

    def clearMovieInfo(self, forceclear = True):
        self.model.clearMovieInfo(forceclear)
        if forceclear:
            for _, val in self.controls.items():
                val[self.ID_CHECK].setCheckState(Qt.Unchecked)
    
        self.mapper.toFirst()

    def updateMovie(self):
        #print('updateMovie')
        self.model.saveMovieInfo()