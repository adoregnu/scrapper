import os, sys

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton
from PyQt5.QtCore import Qt, QBuffer, QByteArray, QIODevice
from PyQt5.QtGui import QPixmap, QImage 

from movie_info_view import MovieInfoView
from folder_view import FolderView
import jav.utils as utils

class CentralWidget(QWidget):
    def __init__(self, config):
        super().__init__()

        self.globalConfig = config
        if not 'FolderView' in config.sections():
            config.add_section('FolderView')

        self.fileView = FolderView(config)
        self.fileView.movieFound.connect(self.onFoundMovie)
        self.infoView = MovieInfoView()
        
        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(3, 3, 3, 3)

        mainLayout.addWidget(self.fileView)
        mainLayout.addWidget(self.infoView)
        self.setLayout(mainLayout)
        self.initCrawlRunner()

    def initCrawlRunner(self):
        from scrapy.crawler import CrawlerRunner
        from scrapy.utils.log import configure_logging
        from scrapy.utils.project import get_project_settings
        configure_logging()
        self.runner = CrawlerRunner(get_project_settings())

    def updateFromFile(self, files):
        self.infoView.clearMovieInfo()
        if not files: return

        nfo = next(filter(lambda x:x.endswith('.nfo'), files), False)
        if not nfo:
            return

        info = {}
        info = utils.nfo2dict(nfo)
        info['path'] = self.fileView.getSelectPath() 

        for file in files:
            if file.endswith('.nfo'): continue
            if '-poster' in file:
                info['poster'] = utils.AvImage(file)
            elif '-fanart' in file:
                info['fanart'] = file #utils.AvImage(file)
        #print('updateFromFile {}'.format(info))
        self.infoView.setMovieInfo(info)

    def updateFromScrapy(self, info):
        self.infoView.clearMovieInfo(False)

        donotcrop = ['heyzo','1pondo', 'Carib', 'caribpr', 'pacopacomama']
        info['path'] = self.fileView.getSelectPath()
        try :
            info['fanart'] = info['thumb']
            if info['studio'] in donotcrop:
                info['poster'] = info['thumb']
            else:
                info['poster'] = info['thumb'].cropLeft()
        except Exception as e:
            print('updateFromScrapy : {}'.format(str(e)))
        self.infoView.setMovieInfo(info)

    def onFoundMovie(self, movieinfo):
        if isinstance(movieinfo, list):
            self.updateFromFile(movieinfo)
        elif isinstance(movieinfo, dict):
            self.updateFromScrapy(movieinfo)

    def onScrapDone(self, _, id):
        self.onFoundMovie(self.crawledMovieInfo)
        self.crawledMovieInfo = None

    # don't do anything related to Qt UI in scrapy signal. it doesn't work.
    def onSpiderClosed(self, spider):
        #import pprint as pp
        #pp.pprint(spider.movieinfo)
        self.crawledMovieInfo = spider.movieinfo

    def scrap(self):
        from scrapy import signals
        scrapper_conf = self.globalConfig['Scrapper']
        selected = self.fileView.selectedIndexes()
        for index in selected:
            path = self.fileView.absolutePath(index)
            cid = os.path.basename(path)
            path = '/'.join(path.split('/')[0:-1])
            crawler = self.runner.create_crawler(scrapper_conf.get('site', 'r18'))
            crawler.signals.connect(self.onSpiderClosed, signals.spider_closed)
            deferd = self.runner.crawl(crawler, keyword=cid, outdir=path)
            deferd.addBoth(self.onScrapDone, index)

    def saveAll(self):
        self.infoView.updateMovie()