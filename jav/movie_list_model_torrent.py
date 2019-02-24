import os, glob
from PyQt5.QtGui import QPainter, QImage, QPixmap, QBrush, QWindow
from PyQt5.QtCore import Qt, QSize, QRect, QSortFilterProxyModel, QPoint, pyqtSignal, QModelIndex
from PyQt5.QtWidgets import QListView, QStyledItemDelegate, QStyle

ITEM_WIDTH = 800
ITEM_HEIGHT = 500

class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()

    def filterAcceptsRow(self, row, parent):
        #print('filterAcceptsRow')
        if not parent.isValid():
            return False

        smodel = self.sourceModel()
        index = smodel.index(row, 0, parent)
        fileInfo = smodel.fileInfo(index)
        if not fileInfo.isDir():
            return False

        #path = smodel.filePath(index)
        path = fileInfo.absoluteFilePath()
        rpath = smodel.rootPath()
        #print('filter: root:%s, path:%s'%(rpath, path))
        #if parent == smodel.index(smodel.rootPath()):
        #    return super().filterAcceptsRow(row, parent)
        #if smodel.rootPath().startswith(path):
        if rpath == path or rpath.startswith(path):
            return True

        return len(glob.glob('%s/*.torrent'%(path))) > 0
        #print ('root:{}, path:{} : {}'.format(rpath, path, exists))
        #return exists

    def startDownload(self, index):
        from qbittorrent import Client
        qb = Client('http://bsyoo.me:9090')
        qb.login('admin', 's82ohigh')
        #torrents = qb.torrents()
        try:
            fileInfo = self.sourceModel().fileInfo(index)
            path = fileInfo.absoluteFilePath()
            torrents = glob.glob('%s/*.torrent'%path)
            with open(torrents[0], 'rb') as f:
                qb.download_from_file(f)
        except Exception as e:
            print(e)

class MovieListDelegate(QStyledItemDelegate):
    def __init__(self):
        super().__init__()
        self.pixmap = QPixmap()

    def paint(self, QPainter, QStyleOptionViewItem, QModelIndex):
        proxyModel = QModelIndex.model()
        index = proxyModel.mapToSource(QModelIndex)
        model = QModelIndex.model().sourceModel()
        #index = QModelIndex
        #model = QModelIndex.model()
        #print('paint:%s'%index.data(Qt.DisplayRole))
        #filepath = model.fileInfo(index).absoluteFilePath()
        filepath = model.filePath(index)
        try :
            _, _, files = next(os.walk(filepath))
        except Exception as e:
            print('filepath:%s, error:%s'%(filepath, str(e)))
            return 

        pr = QWindow().devicePixelRatio()
        lsize = QSize(ITEM_WIDTH, ITEM_HEIGHT - 20)
        rsize = lsize * pr

        qimage = None
        rect = QStyleOptionViewItem.rect
        offsetx = 0
        files.reverse()
        for file in files:
            if not '.jpg' in file:
                continue
            qimage = QImage('%s/%s'%(filepath, file)).scaled(rsize,
                Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)

            lImgHeight = int(qimage.height() / pr)
            lImgWidth = int(qimage.width() / pr)
            imgrect = QRect(rect.left() + offsetx, rect.top(), lImgWidth, lImgHeight)
            pixmap = QPixmap.fromImage(qimage)
            pixmap.setDevicePixelRatio(pr)
            QPainter.drawPixmap(imgrect, pixmap)
            offsetx += lImgWidth + 10

        txtrect = QRect(rect.left(), rect.top() + (ITEM_HEIGHT - 20), ITEM_WIDTH, 20)
        QPainter.drawText(txtrect, Qt.AlignCenter, os.path.basename(index.data(Qt.DisplayRole)))

        if QStyleOptionViewItem.state & QStyle.State_Selected:
            highlight_color = QStyleOptionViewItem.palette.highlight().color()
            highlight_color.setAlpha(50)
            highlight_brush = QBrush(highlight_color)
            QPainter.fillRect(rect, highlight_brush)

    def sizeHint(self, QStyleOptionViewItem, QModelIndex):
        return QSize(ITEM_WIDTH*3, ITEM_HEIGHT)