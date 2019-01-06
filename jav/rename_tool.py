import os
import traceback

from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QDialog, QLineEdit,
    QListWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt5.QtGui import QStandardItemModel

class FileList(QTableWidget):
    def __init__(self, files, parent=None):
        super().__init__(len(files), 2, parent)
        self.verticalHeader().hide()
        stylesheet = '''
            QHeaderView::section {
                background-color:qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #616161, stop: 0.5 #505050,
                    stop: 0.6 #434343, stop:1 #656565);
                color: white;
                padding-left: 4px;
                border: 1px solid #6c6c6c;
            }
        '''
        self.setMinimumWidth(500)
        self.setStyleSheet(stylesheet)

        self.setHorizontalHeaderLabels(['Old', 'New'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setSelectionMode(QAbstractItemView.NoSelection)

        for i, file in enumerate(files):
            self.setItem(i, 0, QTableWidgetItem(os.path.basename(file)))

    def previewRename(self):
        import re
        #toremove = ['FHD', 'fhd', 'hhb', '1080', '720']
        #subprog = re.compile('|'.join(toremove))
        try :
            idprog = re.compile(self.parent().regexp.text())
        except:
            traceback.print_exc()
        for index in range(self.rowCount()):
            file = self.item(index, 0).text()
            tmp = file.split('.')
            ext = tmp[-1]
            #file = subprog.sub('', file)
            nameonly = ''.join(tmp[0:-1])
            try:
                m = idprog.search(nameonly)
                cid = '-'.join([m.group(1), m.group(2)]).upper()
                if m.lastindex == 2:
                    new = '{0}/{0}.{1}'.format(cid, ext)
                elif m.lastindex == 3:
                    new = '{0}/{0}-{1}.{2}'.format(cid, m.group(3), ext)
                self.setItem(index, 1, QTableWidgetItem(new))
            except:
                traceback.print_exc()

    def doRename(self):
        import shutil
        index = 0
        while self.rowCount() > 0:
            srcf = self.item(index, 0).text()
            dstf = self.item(index, 1).text()
            if not dstf: continue
            srcp = '/'.join([self.parent().path, srcf])
            dstp = '/'.join([self.parent().path, dstf])
            try:
                os.makedirs(os.path.dirname(dstp), exist_ok=True)
                #print('%s => %s'%(srcp, dstp))
                shutil.move(srcp ,dstp)
                self.removeRow(index)
            except:
                index += 1

class FileRenameDialog(QDialog):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path

        self.setupUi()

    def getFileList(self):
        import glob
        exts = ('*.mp4', '*.mkv', '*.avi', '*.wmv', '*.smi',
            '*.srt', '*.sup', '*.idx', '*.sub')
        files = []
        for ext in exts:
            files.extend(glob.glob('%s/%s'%(self.path, ext)))

        return files

    def setupUi(self):
        self.setWindowTitle("File Rname Tool")

        layout = QVBoxLayout()
        innerTop = QHBoxLayout()
        self.currpath = QLineEdit(self.path)
        self.currpath.setDisabled(True)
        exp = r'([a-zA-Z]+)(?:-|00)?([0-9]{3,4})-?([0-9])?'
        self.regexp = QLineEdit(exp)
        innerTop.addWidget(self.currpath)
        innerTop.addWidget(self.regexp)
        layout.addLayout(innerTop)

        self.fileTable = FileList(self.getFileList(), parent=self)
        layout.addWidget(self.fileTable)

        innerBottom = QHBoxLayout()
        self.previewBtn = QPushButton('Preview')
        self.previewBtn.clicked.connect(self.fileTable.previewRename)
        self.renameBtn = QPushButton('Rename')
        self.renameBtn.clicked.connect(self.fileTable.doRename)
        self.cancelBtn = QPushButton('Cancel')
        self.cancelBtn.clicked.connect(self.close)
        innerBottom.addStretch()
        innerBottom.addWidget(self.previewBtn)
        innerBottom.addWidget(self.renameBtn)
        innerBottom.addWidget(self.cancelBtn)
        layout.addLayout(innerBottom)

        self.setLayout(layout)
