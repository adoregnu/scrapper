import os
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex
from PyQt5.QtWidgets import QListView, QAbstractItemView, QMenu

class MovieListView(QListView):
    movieDoubleClicked = pyqtSignal(QModelIndex, bool)
    def __init__(self, config, model, parent = None):
        super().__init__(parent)
        self.numItems = 0
        self.model = model
        self.globalConfig = config
        self.config = config['FolderView']
        self.model.directoryLoaded.connect(self.onDirectoryLoaded)
        self.listMode = [
            {'model':None, 'delegate':None, 'init':self.initNfoModel},
            {'model':None, 'delegate':None, 'init':self.initTorrentModel}
        ]
        self.listModeIndex = -1
        self.switchModel()
        self.doubleClicked.connect(self.onDoubleClicked)
        self.clicked.connect(self.onClicked)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onContextMenu)

        self.contextMenu = QMenu()
        self.delAction = self.contextMenu.addAction("Mark Downloaded")
        #delAction.triggered.connect(self.onMarkDownloaded)

    def onContextMenu(self, point):
        if self.listModeIndex == 1:
            action = self.contextMenu.exec_(self.viewport().mapToGlobal(point))
            if action == self.delAction: 
                index = self.proxy.mapToSource(self.indexAt(point))
                self.proxy.markDownloaded(index)
                self.refresh()

    def createModel(self, m):
        model = self.listMode[self.listModeIndex]
        if not model['model']:
            model['model'] = m.FilterProxyModel(self.globalConfig['qbtorrent'])
            model['model'].setDynamicSortFilter(True)
            model['model'].setSourceModel(self.model)
            model['deletage'] = m.MovieListDelegate()

        self.ITEM_WIDTH = m.ITEM_WIDTH

    def initNfoModel(self):
        import movie_list_model_nfo as nm 
        self.setViewMode(QListView.IconMode)
        self.setMovement(QListView.Static)
        
        self.createModel(nm)

    def initTorrentModel(self):
        import movie_list_model_torrent as tm
        self.setViewMode(QListView.ListMode)
        self.createModel(tm)

    def switchModel(self):
        self.listModeIndex = (self.listModeIndex + 1) % 2
        model = self.listMode[self.listModeIndex]
        model['init']()
        self.proxy = model['model'] 
        self.proxy.invalidate()
        self.setItemDelegate(model['deletage'])
        self.setModel(self.proxy)
        self.updateRoot()

    def onClicked(self, index):
        srcIndex = self.proxy.mapToSource(index)
        self.movieDoubleClicked.emit(srcIndex, False)

    def onDoubleClicked(self, index):
        srcIndex = self.proxy.mapToSource(index)
        if self.listModeIndex == 0:
            self.movieDoubleClicked.emit(srcIndex, True)
        else:
            self.proxy.startDownload(srcIndex)
            self.refresh()

    def onDirectoryLoaded(self, newpath):
        #print('onDirectoryLoaded %s\n'%newpath)
        self.proxy.invalidate()
        self.updateRoot(newpath)

    def updateRoot(self, path = None):
        if not path:
            path = self.model.rootPath()
        index = self.proxy.mapFromSource(self.model.index(path))
        self.setRootIndex(index)
        numMovie = self.proxy.rowCount(index)
        if numMovie > 0:
            self.parent().parent().setTabText(0, 'List (%d)' % numMovie)

    def refresh(self):
        self.proxy.invalidate()

    def resizeEvent(self, QResizeEvent):
        if self.listModeIndex == 0:
            size = QResizeEvent.size()
            items = size.width() / self.ITEM_WIDTH
            if not self.numItems:
                self.numItems = items
            if items != self.numItems:
                self.proxy.invalidate()
                self.numItems = items

        super().resizeEvent(QResizeEvent)
