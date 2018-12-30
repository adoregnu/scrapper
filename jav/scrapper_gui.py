import os, sys

from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar, QDialog,
    QAction, QActionGroup, QFileDialog, QToolButton, QComboBox)

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QUrl

from central_widget import CentralWidget

class ScrapperGui(QMainWindow):
    left = 100
    top = 100
    width = 1040
    height = 720  

    def __init__(self, reactor):
        super().__init__()
        self.setWindowTitle("Movie Scrapper")
        import configparser
        self.config = configparser.ConfigParser()
        self.config.read('scrapper.ini')
        self.initConfig()

        self.cw = CentralWidget(self.config)
        self.setCentralWidget(self.cw)
        self.createToolbar()
        self.createMenu()
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.reactor = reactor

    def initConfig(self):
        if not self.config.has_section('Scrapper'):
            self.config.add_section('Scrapper')
        if not self.config.has_section('FolderView'):
            self.config.add_section('FolderView')

        self.scrapperConf = self.config['Scrapper']

    def closeEvent(self, event):
        QApplication.instance().quit()
        with open('scrapper.ini', 'w') as configfile:
            self.config.write(configfile)

    def selectFolder(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        #dialog.setSidebarUrls([QUrl.fromLocalFile(place)])
        if dialog.exec_() == QDialog.Accepted:
            directory = dialog.selectedFiles()[0]
            #print(directory)
            self.cw.fileView.changeDir(directory)

    def setSite(self, site):
        #print(site)
        self.scrapperConf['site'] = site

    def createToolbar(self):
        self.toolbar = self.addToolBar('Files')

        action = QAction(QIcon('res/documents-folder-up@128px.png'), 'Up', self)
        action.triggered.connect(self.cw.fileView.upDir)
        self.toolbar.addAction(action)

        action = QAction(QIcon('res/documents-search-folder@128px.png'), 'Browse', self)
        action.triggered.connect(self.selectFolder)
        self.toolbar.addAction(action)

        action = QAction(QIcon('res/documents-folder-download@128px.png'), 'Scrap', self)
        action.triggered.connect(self.cw.scrap)
        self.toolbar.addAction(action)

        action = QAction(QIcon('res/controls-editor-save@128px.png'), 'Save', self)
        action.triggered.connect(self.cw.saveAll)
        self.toolbar.addAction(action)


        self.scrapToolbar = self.addToolBar('Scrapper')
        self.sites = QComboBox()
        site = self.scrapperConf.get('site', 'javlibrary')
        sites = ['javlibrary', 'avwiki', 'dmm', 'r18', 'mgstage', 'actionjav']
        self.sites.insertItems(1, sites)
        self.sites.setCurrentText(site)
        self.sites.currentTextChanged.connect(self.setSite)
        self.scrapToolbar.addWidget(self.sites)

    def createMenu(self):
        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        #filemenu.addToolBar()

        action = QAction('Rename files', self)
        action.triggered.connect(self.cw.fileView.fileRenameTool)
        filemenu.addAction(action)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    import qt5reactor
    qt5reactor.install()

    from twisted.internet import reactor
    ex = ScrapperGui(reactor)
    ex.show()
    reactor.run()
    #reactor.runReturn()
    #sys.exit(app.exec_())