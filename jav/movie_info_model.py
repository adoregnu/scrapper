import os
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex

import jav.utils as utils

class MovieInfoModel(QAbstractItemModel):
    row = [
        ('path', 'title', 'originaltitle', 'rating', 'year', 'releasedate', 'id', 'studio',
         'set', 'plot', 'genre', 'actor', 'poster', 'fanart'),
    ]
    def __init__(self, parent=None):
        super().__init__()
        self.columnFilter = []
        self.movieInfo = {}

    def setColumnFilter(self, filters):
        self.columnFilter = filters

    def adjustActor(self, movieinfo):
        from jav.actor_map import adjust_actor
        actors = movieinfo['actor']
        if isinstance(actors, str):
            movieinfo['actor'] = adjust_actor(actors)
        elif isinstance(actors, list):
            for actor in actors:
                actor['name'] = adjust_actor(actor['name'])
        elif isinstance(actors, dict):
                actors['name'] = adjust_actor(actors['name'])

    def setMovieInfo(self, movieinfo, bypassFilter):
        if movieinfo.get('actor'):
            self.adjustActor(movieinfo)

        if bypassFilter or not self.columnFilter:
            self.movieInfo = movieinfo
            return

        for column in self.columnFilter:
            if movieinfo.get(column):
                print('update column ', column, movieinfo[column])
                self.movieInfo[column] = movieinfo[column]

    def clearMovieInfo(self, forceClear, keepColumnFilter):
        if forceClear:
            self.movieInfo = {}
        if not keepColumnFilter:
            self.columnFilter = []

    def saveMovieInfo(self):
        curpath = self.movieInfo['path']
        path = '%s/%s.nfo'%(curpath, os.path.basename(curpath))
        #print(self.movieInfo)
        utils.dict2nfo(self.movieInfo, path)
        fields = ['poster', 'fanart']
        for field in fields:
            if not self.movieInfo.get(field): continue
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

        if not self.movieInfo.get('actor'): return

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

    def setGenre(self, value):
        key = 'genre'
        item = self.movieInfo.get(key)
        if isinstance(item, list):
            item.append(value.split(';')[-1])
        else:
            self.movieInfo[key] = value.split(';')

    def setActor(self, value):
        key = 'actor'
        actors = self.movieInfo.get(key)
        if actors and not isinstance(actors, list):
            actors = [actors]
        else:
            actors = []

        if not len(value):
            names = []
        else:
            names = value.split(';')
            names.sort()
        #print('names: ', names)
        if not len(actors):
            actors.append({'name':value})
        else:
            actors = sorted(actors, key=lambda a: a['name'])
            i = 0
            j = 0
            while i < len(names) and j < len(actors):
                actor = actors[j]['name']
                if names[i] == actor:
                    i += 1
                    j += 1
                elif names[i] < actor:
                    actors.insert(j, {'name':names[i]})
                    i += 1
                    j += 1
                elif names[i] > actor:
                    actors.pop(j)

            while j < len(actors):
                actors.pop(j)
            while i < len(names):
                actors.append({'name':names[i]})
                i += 1

        self.movieInfo[key] = actors
        #print('result: {}'.format(actors))

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        key = self.row[index.row()][index.column()]
        #key = self.index2key[index.column()]
        if key == 'genre':
            self.setGenre(value)
        elif key == 'actor':
            self.setActor(value)
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