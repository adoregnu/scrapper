import os, sys

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage 
 
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

    def onRotatePoster(self):
        from PIL import Image, ImageQt
        path = self.fileView.absolutePath(self.fileView.currentIndex())
        _, _, files = next(os.walk(path))
        poster = next(filter(lambda x: '-poster' in x, files), False)
        if not poster:
            return

        path = '%s/%s'%(path,poster)
        im = Image.open(path)
        rim = im.transpose(Image.ROTATE_90)
        rim.save(path)

        self.poster.clear()
        pixmap = QPixmap(path).scaled(400, 400, Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation)
        self.poster.setPixmap(pixmap)

    def createImageView(self):
        layout = QVBoxLayout()
        self.poster = QLabel(self)
        self.poster.setAlignment(Qt.AlignCenter)
        self.fanart = QLabel(self)
        self.fanart.setMinimumWidth(400)
        self.rotate = QPushButton('Rotate poster 90 degree')
        self.rotate.clicked.connect(self.onRotatePoster)
        layout.addWidget(self.poster)
        layout.addWidget(self.rotate)
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