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

    def renameFiles(self):
        import re
        exts = ('*.mp4', '*.mkv', '*.avi', '*.wmv', '*.smi', '*.srt')
        files = []
        for ext in exts:
            files.extend(glob.glob('%s/%s'%(self.config['currdir'], ext)))

        idCountProg = re.compile(r'(\w+-\d+(?:[\-\d]{2}|\w)?)')
        idNoCountProg = re.compile(r'(\w+-\d+)')
        for file in files:
            ext = file.split('.')[-1]
            m = idCountProg.search(os.path.basename(file))
            if not m: continue
            idCount = m.group(0).upper()
            m = idNoCountProg.search(idCount)
            idNoCount = m.group(0)
            #print('mkdir %s/%s'%(os.path.dirname(file), idNoCount))
            os.makedirs('%s/%s'%(os.path.dirname(file), idNoCount), exist_ok = True)
            new = '{0}/{1}/{2}.{3}'.format(os.path.dirname(file), idNoCount, idCount, ext)
            #print('move %s -> %s'%(file, new))
            os.rename(file, new)

    def absolutePath(self, index):
        return self.model.fileInfo(index).absoluteFilePath()

