import os
from PyQt5.QtGui import QPainter, QImage, QPixmap, QBrush, QWindow
from PyQt5.QtCore import Qt, QSize, QRect, QSortFilterProxyModel 
from PyQt5.QtWidgets import QStyledItemDelegate, QStyle

ITEM_WIDTH = 150
ITEM_HEIGHT = 200

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

        nfo = '%s/%s.nfo'%(path, os.path.basename(path))
        exists = os.path.exists(nfo)
        #print ('root:{}, path:{} : {}'.format(rpath, path, exists))
        return exists

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
        for file in files:
            if '-poster.' in file:
                qimage = QImage('%s/%s'%(filepath, file)).scaled(rsize,
                    Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
                break
        if not qimage: return

        lImgHeight = int(qimage.height() / pr)
        lImgWidth = int(qimage.width() / pr)
        rect = QStyleOptionViewItem.rect
        #voffset = (rect.height() - lImgHeight)/2
        hoffset = (rect.width() - lImgWidth)/2
        imgrect = QRect(rect.left() + hoffset, rect.top(), lImgWidth, lImgHeight)
        pixmap = QPixmap.fromImage(qimage)
        pixmap.setDevicePixelRatio(pr)

        QPainter.drawPixmap(imgrect, pixmap)
        txtrect = QRect(rect.left(), rect.top() + (ITEM_HEIGHT - 20), ITEM_WIDTH, 20)
        QPainter.drawText(txtrect, Qt.AlignCenter, os.path.basename(index.data(Qt.DisplayRole)))

        if QStyleOptionViewItem.state & QStyle.State_Selected:
            highlight_color = QStyleOptionViewItem.palette.highlight().color()
            highlight_color.setAlpha(50)
            highlight_brush = QBrush(highlight_color)
            QPainter.fillRect(rect, highlight_brush)

    def sizeHint(self, QStyleOptionViewItem, QModelIndex):
        return QSize(ITEM_WIDTH, ITEM_HEIGHT)
