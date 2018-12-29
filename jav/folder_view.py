import os
import glob

from PyQt5.QtWidgets import QFileSystemModel, QListView
from PyQt5.QtCore import pyqtSignal, pyqtSlot 

class FolderView(QListView):
    movieFound = pyqtSignal(list)

    def __init__(self, config):
        super().__init__()
        self.globalConfig = config
        self.config = config['FolderView']
        self.model = QFileSystemModel()
        self.setModel(self.model)
        self.changeDir(self.config.get('currdir', ''))

        self.setWindowTitle("Dir View")
        self.resize(200, 480)
        self.setMaximumWidth(200)
        self.doubleClicked.connect(self.onListDoubleClicked)
        self.clicked.connect(self.onListClicked)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.onListClicked(self.currentIndex())

    def onListDoubleClicked(self, index):
        finfo = self.model.fileInfo(index)
        if not finfo.isDir():
            return

        path = finfo.absoluteFilePath()
        self.changeDir(path)

    def onListClicked(self, index):
        finfo = self.model.fileInfo(index)

        info_files = []
        if finfo.isDir():
            path = finfo.absoluteFilePath()
            #print(path)
            info_files.extend(glob.glob('%s/*.nfo'%path))
            info_files.extend(glob.glob('%s/*.jpg'%path))

        self.movieFound.emit(info_files)

    def changeDir(self, path):
        self.setRootIndex(self.model.setRootPath(path))
        self.config['currdir'] = path

    def upDir(self):
        tmp = self.config['currdir'].split('/')
        print(tmp)
        if tmp[0] == '':
            return
        elif len(tmp) == 2 and tmp[1] == '':
            self.changeDir('')
        else:
            self.changeDir('/'.join(tmp[0:-1]))

    def fileRenameTool(self):
        from rename_tool import FileRenameDialog
        dlg = FileRenameDialog(self.config.get('currdir', ''), self)
        dlg.exec_()

    def absolutePath(self, index):
        return self.model.fileInfo(index).absoluteFilePath()