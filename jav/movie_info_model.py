import os
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex

import jav.utils as utils

class MovieInfoModel(QAbstractItemModel):
    row = [
        ('path', 'title', 'originaltitle', 'year', 'releasedate', 'id', 'studio',
         'set', 'plot', 'genre', 'actor', 'poster', 'fanart'),
    ]
    def __init__(self, parent=None):
        super().__init__()
        self.columnFilter = []
        self.movieInfo = {}

    def setColumnFilter(self, filters):
        self.columnFilter = filters

    def setMovieInfo(self, movieinfo):
        if not self.columnFilter:
            self.movieInfo = movieinfo
            return

        for column in self.columnFilter:
            if movieinfo.get(column):
                self.movieInfo[column] = movieinfo[column]

    def clearMovieInfo(self, forceclear):
        if forceclear or not self.columnFilter:
            self.columnFilter = []
            self.movieInfo = {}

    def saveMovieInfo(self):
        curpath = self.movieInfo['path']
        path = '%s/%s.nfo'%(curpath, os.path.basename(curpath))
        utils.dict2nfo(self.movieInfo, path)
        fields = ['poster', 'fanart']
        for field in fields:
            img = self.movieInfo[field]
            if isinstance(img, utils.AvImage):
                img.save('%s/%s-%s.%s'%(
                    curpath, os.path.basename(curpath), field, img.ext()
                ))

        def saveActorThumb(actor):
            if not 'thumb' in actor: return
            if not isinstance(actor['thumb'], utils.AvImage): return

            path = '%s/.actors'%curpath
            os.makedirs(path, exist_ok=True)
            thumb = actor['thumb']
            thumb.save('%s/%s'%(path, os.path.basename(thumb.url)))

        actors = self.movieInfo['actor']
        #print(actors)
        if isinstance(actors, list):
            for actor in actors:
                saveActorThumb(actor)
        elif isinstance(actors, dict):
            saveActorThumb(actors)

    def rowCount(self, parent=None):
        return 1

    def columnCount(self, parent=None):
        return len(self.row[0])

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsEditable

    def index(self, row, column, parent):
        item = self.movieInfo.get(self.row[row][column])
        if item:
            return self.createIndex(row, column, item)
        else:
            return self.createIndex(row, column, '')
    
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return

        key = self.row[index.row()][index.column()]
        #key = self.index2key[index.column()]
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
        else: #if isinstance(value, str) and len(value) > 0:
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
        elif isinstance(item, dict):
            return item['name']
        else:
            return item