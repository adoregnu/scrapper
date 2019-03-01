import os, sys
import traceback
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QTabWidget

from movie_info_view import MovieInfoView
from movie_list_view import MovieListView
from folder_view import FolderView
import jav.utils as utils

class CentralWidget(QWidget):
    def __init__(self, config):
        super().__init__()

        self.globalConfig = config
        if not 'FolderView' in config.sections():
            config.add_section('y')

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(3, 3, 3, 3)

        self.fileView = FolderView(config)
        self.fileView.movieFound.connect(self.onFoundMovie)
        mainLayout.addWidget(self.fileView)

        self.movieTab = QTabWidget()
        self.movieTab.setContentsMargins(0, 0, 0, 0)
        self.listView = MovieListView(config, self.fileView.model, parent=self)
        self.listView.movieDoubleClicked.connect(self.onMovieDoubleClicked)
        self.movieTab.addTab(self.listView, 'List')

        self.infoView = MovieInfoView()
        self.movieTab.addTab(self.infoView, 'Detail')
        
        mainLayout.addWidget(self.movieTab)
        self.setLayout(mainLayout)

        self.initCrawlRunner()

    def initCrawlRunner(self):
        from scrapy.crawler import CrawlerRunner
        from scrapy.utils.log import configure_logging
        from scrapy.utils.project import get_project_settings
        configure_logging()
        self.runner = CrawlerRunner(get_project_settings())

    def onMovieDoubleClicked(self, index):
        self.movieTab.setCurrentWidget(self.infoView)
        self.fileView.setCurrentIndex(index)

    def updateFromFile(self, files):
        self.infoView.clearMovieInfo()
        if not files: return

        nfo = next(filter(lambda x:x.endswith('.nfo'), files), False)
        if not nfo:
            return

        info = {}
        info = utils.nfo2dict(nfo)
        info['path'] = self.fileView.getPath() 

        for file in files:
            if file.endswith('.nfo'): continue
            if '-poster' in file:
                info['poster'] = utils.AvImage(file)
            elif '-fanart' in file:
                info['fanart'] = file
        self.infoView.setMovieInfo(info)

    def updateFromScrapy(self, info):
        self.infoView.clearMovieInfo(False)
        configScrapper = self.globalConfig['Scrapper']
        donotcrop = []
        if configScrapper.get('studioSkipCrop'):
            donotcrop = configScrapper['studioSkipCrop'].split(',')
            print(donotcrop)
        try :
            info['fanart'] = info['thumb']
            if not info.get('studio') or info['studio'] in donotcrop:
                info['poster'] = info['thumb']
            else:
                info['poster'] = info['thumb'].cropLeft()

            self.infoView.setMovieInfo(info)
        except:
            traceback.print_exc()

    def onFoundMovie(self, movieinfo):
        if isinstance(movieinfo, list):
            self.updateFromFile(movieinfo)
        elif isinstance(movieinfo, dict):
            self.updateFromScrapy(movieinfo)

    def onScrapDone(self, _, id):
        if self.crawledMovieInfo:
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
        selected = self.fileView.getSelectedIndexes()
        for index in selected:
            path = self.fileView.getPath(index)
            cid = os.path.basename(path)
            #path = '/'.join(path.split('/')[0:-1])
            crawler = self.runner.create_crawler(scrapper_conf.get('site', 'r18'))
            crawler.signals.connect(self.onSpiderClosed, signals.spider_closed)
            deferd = self.runner.crawl(crawler, keyword=cid, outdir=path)
            deferd.addBoth(self.onScrapDone, index)

    def saveAll(self):
        self.infoView.saveMovieInfo()
        self.listView.refresh()

    def changeDir(self, path):
        self.fileView.folderList.changeDir(path)

    def upDir(self):
        self.fileView.folderList.upDir()

    def fileRenameTool(self):
        config = self.globalConfig['FolderView']
        from rename_tool import FileRenameDialog
        dlg = FileRenameDialog(config.get('currdir', ''), self)
        dlg.exec_()

    def refresh(self):
        self.listView.refresh()