import os
import traceback

from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QDialog, QLineEdit,
    QListWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu
)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt

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
        #self.setContextMenuPolicy(Qt.CustomContextMenu) 
        #self.customContextMenuRequested.connect(self.onContextMenu)

        self.setHorizontalHeaderLabels(['Old', 'New'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setSelectionMode(QAbstractItemView.NoSelection)

        self.contextMenu = QMenu()
        delAction = self.contextMenu.addAction("Delete Row")
        delAction.triggered.connect(self.onDelete)

        for i, file in enumerate(files):
            self.setItem(i, 0, QTableWidgetItem(os.path.basename(file)))

    def contextMenuEvent(self, event):
        self.contextMenu.exec_(self.viewport().mapToGlobal(event.pos()))

    def onDelete(self):
        #print()
        self.removeRow(self.currentRow())

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
        while self.rowCount() > 0 and self.rowCount() != index:
            try:
                srcf = self.item(index, 0).text()
                dstf = self.item(index, 1).text()
                srcp = '/'.join([self.parent().path, srcf])
                dstp = '/'.join([self.parent().path, dstf])
                os.makedirs(os.path.dirname(dstp), exist_ok=True)
                print('%s => %s'%(srcp, dstp))
                if not os.path.exists(dstp):
                    shutil.move(srcp, dstp)
                self.removeRow(index)
            except Exception as e:
                index += 1
                print(index, e)
                break

class FileRenameDialog(QDialog):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path

        self.setupUi()

    def getFileList(self):
        import glob
        exts = ('*.mp4', '*.mkv', '*.avi', '*.wmv', '*.smi',
            '*.srt', '*.sup', '*.idx', '*.sub', '*.m4v')
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
        exp = r'([a-zA-Z]+)(?:-|00)?([0-9]{3,5})(?:\D)?([0-9A-Fa-f])?'
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
        #self.cancelBtn = QPushButton('Cancel')
        #self.cancelBtn.clicked.connect(self.close)
        innerBottom.addStretch()
        innerBottom.addWidget(self.previewBtn)
        innerBottom.addWidget(self.renameBtn)
        #innerBottom.addWidget(self.cancelBtn)
        layout.addLayout(innerBottom)

        self.setLayout(layout)
