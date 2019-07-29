import os
import glob

from PyQt5.QtWidgets import (QFileSystemModel, QListView, QWidget, QVBoxLayout,
    QLineEdit, QMenu, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal

class FolderList(QListView):
    prevPath = []
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Dir View")
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onContextMenu)
        self.clicked.connect(self.onListClicked)
        self.doubleClicked.connect(self.onListDoubleClicked)

        self.contextMenu = QMenu()
        delAction = self.contextMenu.addAction("Delete")
        delAction.triggered.connect(self.onDelete)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self.doubleClicked.emit(self.currentIndex())
        if event.key() == Qt.Key_Backspace:
            self.upDir()
        elif event.key() in [Qt.Key_Up, Qt.Key_Down]:
            self.clicked.emit(self.currentIndex())

    def onContextMenu(self, point):
        self.contextMenu.exec_(self.viewport().mapToGlobal(point))

    def onDelete(self):
        import shutil
        index = self.currentIndex()
        if not index.isValid():
            return

        try:
            f = self.model().fileInfo(index)
            path = f.absoluteFilePath()
            if f.isDir():
                shutil.rmtree(path)
            elif f.isSymLink():
                os.unlink(path)
            else:
                os.remove(path)
        except Exception as e:
            print(e)

    def onListDoubleClicked(self, index):
        finfo = self.model().fileInfo(index)
        if not finfo.isDir():
            return

        path = finfo.absoluteFilePath()
        self.prevPath.append(index)
        self.changeDir(path)

    def getFiles(self, index):
        finfo = self.model().fileInfo(index)

        info_files = []
        if finfo.isDir():
            path = finfo.absoluteFilePath()
            #print(path)
            info_files.extend(glob.glob('%s/*.nfo'%path))
            info_files.extend(glob.glob('%s/*.jpg'%path))
        return info_files

    def onListClicked(self, index):
        info_files = self.getFiles(index)
        self.parent().movieFound.emit(info_files)

    def changeDir(self, path):
        self.setRootIndex(self.model().setRootPath(path))
        self.config['currdir'] = path
        self.scrollTo(self.currentIndex())

    def upDir(self):
        tmp = self.config['currdir'].split('/')
        if tmp[0] == '':
            return
        elif len(tmp) == 2 and tmp[1] == '':
            self.changeDir('')
        else:
            self.changeDir('/'.join(tmp[0:-1]))
        if len(self.prevPath):
            self.setCurrentIndex(self.prevPath.pop())

class FolderView(QWidget):
    movieFound = pyqtSignal(list)

    def __init__(self, config):
        super().__init__()
        self.config = config['FolderView']
        self.resize(200, 400)
        self.setMaximumWidth(200)
        self.setMinimumWidth(150)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.currPath = QLineEdit()
        self.model = QFileSystemModel()
        self.model.rootPathChanged.connect(self.currPath.setText)
        self.folderList = FolderList(self.config, parent=self)
        self.folderList.setModel(self.model)
        self.folderList.changeDir(self.config.get('currdir', ''))

        layout.addWidget(self.currPath)
        layout.addWidget(self.folderList)
        self.setLayout(layout)

    def setCurrentIndex(self, index):
        self.folderList.setCurrentIndex(index)
        self.folderList.onListClicked(index)

    def getPath(self, index = None):
        if not index: index = self.folderList.currentIndex()
        return self.model.filePath(index)

    def rootPath(self):
        return self.model.rootPath()

    def getSelectedIndexes(self):
        return self.folderList.selectedIndexes()

    def getFiles(self, index):
        return self.folderList.getFiles(index)

    def playFile(self):
        index = self.folderList.currentIndex()
        if not index.isValid():
            return

        import glob
        exts = ('*.mp4', '*.mkv', '*.avi', '*.wmv')
        files = []
        path = self.model.filePath(index)
        #print(path)
        for ext in exts:
            files.extend(glob.glob('%s/%s'%(path, ext)))
        if len(files) < 1: return

        files.sort()
        os.startfile(files[0])
