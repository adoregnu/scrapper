import os, sys

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage 

from PIL import Image, ImageQt
 
from movie_info_form import MovieInfoForm
from folder_view import FolderView

class CentralWidget(QWidget):
    def __init__(self, config):
        super().__init__()

        self.globalConfig = config
        if not 'FolderView' in config.sections():
            config.add_section('FolderView')

        self.fileView = FolderView(config)
        self.fileView.movieFound.connect(self.onFoundMovie)
        self.infoForm = MovieInfoForm()
        
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.fileView)
        mainLayout.addWidget(self.infoForm)
        mainLayout.addLayout(self.createImageView())
        self.setLayout(mainLayout)

        self.initCrawlRunner()

    def initCrawlRunner(self):
        from scrapy.crawler import CrawlerRunner
        from scrapy.utils.log import configure_logging
        from scrapy.utils.project import get_project_settings
        configure_logging()
        self.runner = CrawlerRunner(get_project_settings())


    def onFoundMovie(self, files):
        self.poster.clear()
        self.fanart.clear()
        self.infoForm.clearMovieInfo()

        for file in files:
            if file.endswith('.nfo'):
                self.infoForm.setMovieInfo(file)
                continue
            pixmap = QPixmap(file).scaled(400, 400, Qt.KeepAspectRatio,
                transformMode=Qt.SmoothTransformation)
            if 'poster' in file:
                self.poster.setPixmap(pixmap)
            elif 'fanart' in file:
                self.fanart.setPixmap(pixmap)

    def getPosterImage(self):
        path = self.fileView.absolutePath(self.fileView.currentIndex())
        _, _, files = next(os.walk(path))
        poster = next(filter(lambda x: '-poster' in x, files), False)
        if not poster:
            return None, None

        path = '%s/%s'%(path,poster)
        return Image.open(path), path

    def redrawPoster(self, path):
        self.poster.clear()
        pixmap = QPixmap(path).scaled(400, 400, Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation)
        self.poster.setPixmap(pixmap)

    def onRotatePoster(self):
        im, path = self.getPosterImage() 
        if not path: return

        rim = im.transpose(Image.ROTATE_90)
        rim.save(path)
        self.redrawPoster(path)

    def onCropLeft(self):
        im, path = self.getPosterImage()
        if not path: return

        w, h = im.size
        cim = im.crop((w - int(w*0.475), 0, w, h))
        cim.save(path)
        self.redrawPoster(path)

    def createImageView(self):
        layout = QVBoxLayout()
        self.poster = QLabel(self)
        self.poster.setAlignment(Qt.AlignCenter)
        self.fanart = QLabel(self)
        self.fanart.setMinimumWidth(400)
        self.rotate = QPushButton('Rotate 90 degree')
        self.rotate.clicked.connect(self.onRotatePoster)

        self.cropLeft = QPushButton('Crop Right')
        self.cropLeft.clicked.connect(self.onCropLeft)
        layout.addWidget(self.poster)
        hbox = QHBoxLayout()
        hbox.addWidget(self.rotate)
        hbox.addWidget(self.cropLeft)
        layout.addLayout(hbox)
        layout.addWidget(self.fanart)
        #layout.setContentsMargins(0, 0, 0, 0)
        #layout.setAlignment(Qt.AlignHCenter)
        return layout

    def scrap(self):
        scrapper_conf = self.globalConfig['Scrapper']
        selected = self.fileView.selectedIndexes()
        for index in selected:
            path = self.fileView.absolutePath(index)
            cid = os.path.basename(path)
            path = '/'.join(path.split('/')[0:-1])
            self.runner.crawl(scrapper_conf.get('site', 'javlibrary'),
                keyword=cid,
                outdir=path
            ).addBoth(lambda _, id: self.fileView.onListClicked(id), index)