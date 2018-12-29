import os
from collections import OrderedDict
import xml.etree.ElementTree as ET

from PyQt5.QtWidgets import (QLabel, QLineEdit, QTextEdit, QGroupBox, QFormLayout, QListWidget,
    QDataWidgetMapper, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QApplication)
from PyQt5.QtCore import (Qt, QAbstractListModel, QAbstractItemModel, QModelIndex, QVariant,
    pyqtProperty, QByteArray, QEvent)
from PyQt5.QtGui import QKeyEvent

import jav.utils as utils

class MovieInfoModel(QAbstractItemModel):
    index2key = ['path', 'title', 'originaltitle', 'year', 'releasedate',
        'id', 'studio', 'set', 'plot', 'genre', 'actor']
    def __init__(self, parent=None):
        super().__init__()
        self.xmlPath = None

    def setMovieInfo(self, file):
        self.xmlPath = file
        self.tree = ET.parse(file)
        self.movieInfo = utils.xml2dict(self.tree.getroot())
        self.movieInfo['path'] = os.path.dirname(file)

    def clearMovieInfo(self):
        self.movieInfo = {}

    def saveMovieInfo(self):
        from xml.etree.ElementTree import fromstring, dump
        root = ET.fromstring(utils.XML_TEMPLATE)
        utils.dict2xml(self.movieInfo, root)
        utils.indent_xml(root)
        #ET.dump(root)
        self.tree = ET.ElementTree(root)
        self.tree.write(self.xmlPath)
 
    def rowCount(self, parent=None):
        return 1

    def columnCount(self, parent=None):
        return len(self.key2index)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsEditable

    def index(self, row, column, parent):
        item = self.movieInfo.get(self.index2key[column])
        if item:
            return self.createIndex(row, column, item)
        else:
            return self.createIndex(row, column, '')
            #return QModelIndex()
    
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return

        key = self.index2key[index.column()]
        if key == 'genre':
            item = self.movieInfo.get(key)
            if isinstance(item, list):
                item.append(value.split(';')[-1])
            else:
                self.movieInfo[key] = value.split(';')
        elif key == 'actor':
            item = self.movieInfo.get(key)
            if isinstance(item, dict):
                self.movieInfo[key] = [item]
                item = self.movieInfo[key]
                item.append({'name':value.split(';')[-1]})
            elif isinstance(item, list):
                item.append({'name':value.split(';')[-1]})
            else:
                self.movieInfo[key] = {'name':value}
                item = self.movieInfo[key]
        elif isinstance(value, str) and len(value) > 0:
            self.movieInfo[key] = value
        return True

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if isinstance(item, list):
            if isinstance(item[0],str):
                return ';'.join(item)
            elif isinstance(item[0], dict):
                return ';'.join([i['name'] for i in item])
        if isinstance(item, dict):
            return item['name']
        return item

class EditableListWidget(QWidget):
    def __init__(self, parent=None):
        super(EditableListWidget, self).__init__(parent)
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
        #return ';'.join([self._listWidget.item(i).text() for i in range(self._listWidget.count())])

    def setListValue(self, value):
        self._listWidget.clear()
        if not value: return
        self._listWidget.insertItems(0, value.split(';'))

    listValue = pyqtProperty(str, getListValue, setListValue)
 
class MovieInfoForm(QGroupBox):

    def __init__(self):
        super().__init__('Movie Info')

        from collections import OrderedDict
        self.controls = OrderedDict() 
        self.controls['Path:'] = QLineEdit()
        self.controls['Title:'] = QLineEdit()
        self.controls['Original Title:'] = QLineEdit()
        self.controls['Year:'] = QLineEdit()
        self.controls['Release Date:'] = QLineEdit()
        self.controls['ID:'] = QLineEdit()
        self.controls['Studio:'] = QLineEdit()
        self.controls['Movie Set:'] = QLineEdit()
        self.controls['Plot:'] = QTextEdit()
        self.controls['Genre:'] = EditableListWidget()
        self.controls['Actor:'] = EditableListWidget()

        layout = QFormLayout()
        for key, ctrl in self.controls.items():
            layout.addRow(QLabel(key), ctrl)
        self.setLayout(layout)

        self.mapper = QDataWidgetMapper(self)
        self.model = MovieInfoModel()
        self.mapper.setModel(self.model)

    def setMovieInfo(self, file):
        self.model.setMovieInfo(file)
        index = 0
        for key, ctrl in self.controls.items():
            if 'Genre:' == key or 'Actor:' == key:
                self.mapper.addMapping(ctrl, index, b'listValue')
            else:
                self.mapper.addMapping(ctrl, index)
            index += 1
        self.mapper.toFirst()

    def clearMovieInfo(self):
        self.model.clearMovieInfo()
        self.mapper.toFirst()
        #self.mapper.clearMapping()

    def updateMovie(self):
        print('updateMovie')
        self.model.saveMovieInfo()