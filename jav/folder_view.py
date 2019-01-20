import os
import glob

from PyQt5.QtWidgets import QFileSystemModel, QListView, QWidget, QVBoxLayout, QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot 

class FolderList(QListView):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Dir View")
        self.clicked.connect(self.onListClicked)
        self.doubleClicked.connect(self.onListDoubleClicked)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self.doubleClicked.emit(self.currentIndex())
        if event.key() == Qt.Key_Backspace:
            self.upDir()
        elif event.key() in [Qt.Key_Up, Qt.Key_Down]:
            self.clicked.emit(self.currentIndex())
        #self.scrollTo(self.currentIndex())

    def onListDoubleClicked(self, index):
        finfo = self.model().fileInfo(index)
        if not finfo.isDir():
            return

        path = finfo.absoluteFilePath()
        self.changeDir(path)

    def onListClicked(self, index):
        finfo = self.model().fileInfo(index)

        info_files = []
        if finfo.isDir():
            path = finfo.absoluteFilePath()
            #print(path)
            info_files.extend(glob.glob('%s/*.nfo'%path))
            info_files.extend(glob.glob('%s/*.jpg'%path))

        self.parent().movieFound.emit(info_files)

    def changeDir(self, path):
        self.setRootIndex(self.model().setRootPath(path))
        self.config['currdir'] = path

    def upDir(self):
        tmp = self.config['currdir'].split('/')
        if tmp[0] == '':
            return
        elif len(tmp) == 2 and tmp[1] == '':
            self.changeDir('')
        else:
            self.changeDir('/'.join(tmp[0:-1]))

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

    def getSelectedIndexes(self):
        return self.folderList.selectedIndexes()

    def playFile(self):
        index = self.folderList.currentIndex()
        if not index.isValid():
            return

        import glob
        exts = ('*.mp4', '*.mkv', '*.avi', '*.wmv')
        files = []
        path = self.model.filePath(index)
        for ext in exts:
            files.extend(glob.glob('%s/%s'%(path, ext)))
        if not len(ext): return

        files.sort()
        os.startfile(files[0])
