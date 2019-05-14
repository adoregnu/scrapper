import os
from collections import OrderedDict
import xml.etree.ElementTree as ET

from PyQt5.QtWidgets import (QLabel, QLineEdit, QPlainTextEdit, QDataWidgetMapper
    , QWidget, QHBoxLayout, QVBoxLayout, QStyledItemDelegate, QGridLayout, QCheckBox)
from PyQt5.QtCore import Qt
 
from movie_info_model import MovieInfoModel
from genre_widget import GenreWidget
from cover_widget import CoverWidget
from rating_widget import RatingWidget

class MovieInfoDelegate(QStyledItemDelegate):
    def __init__(self, parent = None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        print('createEditor {}'.format(index.column()))

    def setEditorData(self, editor, index):
        data = index.model().data(index, Qt.DisplayRole)
#        print('setEditorData column:{}, type:{}'.format(index.column(), type(editor)))
        if isinstance(editor, QLineEdit):
            editor.setText(data)
        elif isinstance(editor, QPlainTextEdit):
            editor.setPlainText(data)
        else:
            editor.setImage(data)

    def setModelData(self, editor, model, index):
#        print('setModelData column:{}'.format(index.column()))
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
        self.controls['rating'] = ['Rating:', RatingWidget()]
        self.controls['year'] = ['Year:', QLineEdit()]
        self.controls['releasedate'] = ['Release Date:', QLineEdit()]
        self.controls['id'] = ['ID:', QLineEdit()]
        self.controls['studio'] = ['Studio:', QLineEdit()]
        self.controls['set'] = ['Movie Set:', QLineEdit()]
        self.controls['plot'] = ['Plot:', QPlainTextEdit()]
        self.controls['genre'] = ['Genre:', GenreWidget()]
        self.controls['actor'] = ['Actor:', GenreWidget()]

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
        self.poster = CoverWidget('poster')
        self.fanart = CoverWidget('fanart', False)
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
            if 'genre' == key or 'actor' == key or 'rating' == key:
                self.mapper.addMapping(ctrl[self.ID_CTRL], index, b'Value')
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

    def setMovieInfo(self, movieinfo, bypassFilter):
        if not movieinfo: return
        self.model.setMovieInfo(movieinfo, bypassFilter)
        self.mapper.toFirst()

    def clearMovieInfo(self, forceClear = True, keepColumnFilter = False):
        self.model.clearMovieInfo(forceClear, keepColumnFilter)
        if not keepColumnFilter:
            for _, val in self.controls.items():
                val[self.ID_CHECK].setCheckState(Qt.Unchecked)
    
        self.mapper.toFirst()

    def saveMovieInfo(self):
        import traceback
        #print('updateMovie')
        try:
            self.model.saveMovieInfo()
        except:
            traceback.print_exc()
