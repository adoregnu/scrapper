import os, sys
import traceback
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QTabWidget

from movie_info_view import MovieInfoView
from movie_list_view import MovieListView
from folder_view import FolderView
import jav.utils as utils

class CentralWidget(QWidget):
    crawledMovieInfo = None

    def __init__(self, config):
        super().__init__()

        self.globalConfig = config
        if not 'FolderView' in config.sections():
            config.add_section('y')

        self.scrapperConfig = self.globalConfig['Scrapper']
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
        self.crawler = None
        self.site = None
        self.numCids = 0

    def onMovieDoubleClicked(self, index):
        self.movieTab.setCurrentWidget(self.infoView)
        self.fileView.setCurrentIndex(index)

    def updateFromFile(self, files, index = None):
        self.infoView.clearMovieInfo(True, self.numCids > 1)
        if not files: return

        #print(files)
        nfo = next(filter(lambda x:x.endswith('.nfo'), files), False)
        if not nfo:
            return

        info = utils.nfo2dict(nfo)
        if index:
            info['path'] = self.fileView.getPath(index) 
        else:
            info['path'] = self.fileView.getPath() 

        for file in files:
            if file.endswith('.nfo'): continue
            if '-poster' in file:
                info['poster'] = utils.AvImage(file)
            elif '-fanart' in file:
                info['fanart'] = file
        #print('file set movie info')
        #print(info)
        self.infoView.setMovieInfo(info, self.numCids > 1)

    def updateFromScrapy(self, info):
        #self.infoView.clearMovieInfo(False, True)
        donotcrop = []
        if self.scrapperConfig.get('studios_skipping_crop'):
            donotcrop = self.scrapperConfig['studios_skipping_crop'].split(',')
            #print(donotcrop)
        try :
            info['fanart'] = info['thumb']
            if not info.get('studio') or info['studio'] in donotcrop:
                info['poster'] = info['thumb']
            else:
                info['poster'] = info['thumb'].cropLeft()

            #print('scrapy set movie info')
            self.infoView.setMovieInfo(info, False)
        except:
            traceback.print_exc()

    def onFoundMovie(self, movieinfo):
        if isinstance(movieinfo, list):
            self.updateFromFile(movieinfo)
        elif isinstance(movieinfo, dict):
            self.updateFromScrapy(movieinfo)

    '''
    def onScrapDone(self, _):
        self.numCids = 0

    # don't do anything related to Qt UI in scrapy signal. it doesn't work.
    def onSpiderClosed(self, spider):
        #import pprint as pp
        #pp.pprint(spider.movieinfo)
        try:
            self.crawledMovieInfo = spider.movieinfo
        except:
            self.crawledMovieInfo = None
    '''
    def onSpiderClosed(self, spider):
        self.numCids = 0
        self.listView.refresh()

    def onItemScraped(self, item, response, spider):
        if not response.meta.get('id'): return
        cid = response.meta['id']
        #print(cid)
        minfo = dict(item)
        minfo['path'] = self.fileView.getPath(cid['idx'])
        if 'releasedate' in minfo:
            minfo['year'] = minfo['releasedate'].split('-')[0]
        if 'actor_thumb' in minfo:
            del minfo['actor_thumb']

        #print(response.request.headers)
        if self.numCids > 1:
            mfiles = self.fileView.getFiles(cid['idx'])
            self.updateFromFile(mfiles, cid['idx'])
            self.updateFromScrapy(minfo)
            self.infoView.saveMovieInfo()
        else:
            self.updateFromScrapy(minfo)
            #self.onFoundMovie(minfo)

    def runCrawler(self, **kw):
        from scrapy import signals
        site = self.scrapperConfig.get('site', 'r18')
        if not self.crawler or self.site != site:
            self.site = site
            self.crawler = self.runner.create_crawler(site)
            self.crawler.signals.connect(self.onItemScraped, signals.item_scraped)
            self.crawler.signals.connect(self.onSpiderClosed, signals.spider_closed)
        self.runner.crawl(self.crawler, **kw)
        #deferd = self.runner.crawl(self.crawler, **kw)
        #deferd.addBoth(self.onScrapDone)

    def scrap(self, **kw):
        if kw:
            kw['outdir'] = self.fileView.rootPath()
            self.runCrawler(**kw)
            return

        selected = self.fileView.getSelectedIndexes()
        if len(selected) < 1:
            print('select movie!')
            return

        cids = [{'cid':os.path.basename(self.fileView.getPath(idx)), 'idx':idx} for idx in selected]
        self.numCids = len(cids)
        #print('num cids:', self.numCids)
        #print(cids, self.fileView.rootPath())
        self.runCrawler(**{'cids':cids})
        '''
        for index in selected:
            path = self.fileView.getPath(index)
            cid = os.path.basename(path)
            self.runCrawler(**{'keyword':cid, 'outdir':path})
        '''

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