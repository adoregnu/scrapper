from PyQt5.QtWidgets import (QLabel,  QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QApplication, QFrame)
from PyQt5.QtCore import (Qt, QEvent, QSize)
from PyQt5.QtGui import QKeyEvent, QPixmap, QWindow
 
from PIL import ImageQt
import jav.utils as utils

class CoverWidget(QWidget):
    _image = None 
    def __init__(self, title, editable = True, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setMinimumWidth(400)
        self._label.setMinimumHeight(350)
        self._label.setFrameShape(QFrame.Panel)
        self._label.setFrameShadow(QFrame.Sunken)
        self._label.setLineWidth(1)

        layout.addWidget(self._label)
        if editable:
            hbox = QHBoxLayout()
            self._btnRotate = QPushButton('Rotate 90 degree')
            self._btnRotate.clicked.connect(self.onClickRotate)
            self._btnCrop = QPushButton('Crop Right')
            self._btnCrop.clicked.connect(self.onClickCrop)
            hbox.addWidget(self._btnRotate)
            hbox.addWidget(self._btnCrop)
            layout.addLayout(hbox)
        self.setLayout(layout)

    def draw(self):
        self._label.clear()
        pr = QWindow().devicePixelRatio()
        size = QSize(self._label.width(), self._label.height()) * pr
 
        qim = ImageQt.ImageQt(self._image.image())
        pixmap = QPixmap.fromImage(qim)
        pixmap.setDevicePixelRatio(pr)
        pixmap = pixmap.scaled(size, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self._label.setPixmap(pixmap)

    def image(self):
        #print('image')
        return self._image

    def setImage(self, image):
        if not image:
            if self._image: del self._image
            self._image = None
            self._label.clear()
            return

        #print('setImage {}'.format(image))
        if isinstance(image, str):
            self._image = utils.AvImage(image)
        elif isinstance(image, utils.AvImage):
            self._image = image
        else:
            print('unknown format')
            return
        self.draw()

    def onClickRotate(self):
        #print('onClickRotate')
        self._image = self._image.rotate()
        self.draw()
        QApplication.postEvent(self,
            QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier))

    def onClickCrop(self):
        #print('onClickCrop')
        self._image = self._image.cropLeft()
        self.draw()
        QApplication.postEvent(self,
            QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier))