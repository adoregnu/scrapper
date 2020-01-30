import os, sys

from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar, QDialog, QHBoxLayout,
    QAction, QActionGroup, QFileDialog, QToolButton, QComboBox, QLineEdit, QWidget, QLabel,
    QSpacerItem, QSizePolicy)

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QUrl

from central_widget import CentralWidget

class ArgsWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.addItem(QSpacerItem(10, 1, QSizePolicy.Fixed, QSizePolicy.Expanding))
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel('Num Pages:'))
        self.editPages = QLineEdit()
        layout.addWidget(self.editPages)
        layout.addWidget(QLabel('Stop Id:'))
        self.editStopId = QLineEdit()
        layout.addWidget(self.editStopId)
        self.setMaximumWidth(180)
        self.setLayout(layout)

    def reset(self):
        self.editPages.setText('1')
        self.editStopId.setText('')

    def getNumPages(self):
        return self.editPages.text()

    def getStopId(self):
        return self.editStopId.text()

class ScrapperGui(QMainWindow):
    left = 100
    top = 100
    width = 1040
    height = 720  
    argsWidget = None

    def __init__(self, reactor):
        super().__init__()
        self.setFont(QFont("Calibri", 10))
        self.setWindowTitle("Movie Scrapper")
        import configparser
        self.config = configparser.ConfigParser()
        self.config.read('scrapper.ini')
        self.initConfig()

        self.setCentralWidget(CentralWidget(self.config))
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
            self.centralWidget().changeDir(directory)

    def setSite(self, site):
        #print(site)
        self.scrapperConf['site'] = site
        sitesNeededArgs = self.scrapperConf.get('sites_needed_args', [])
        self.showArgsWidget(site in sitesNeededArgs)

    def showArgsWidget(self, bShow):
        aw = self.argsWidget
        if not aw:
            aw = ArgsWidget()
            aw.action = self.scrapToolbar.addWidget(aw)
            self.argsWidget = aw

        aw.action.setVisible(bShow)
        if bShow: aw.reset()

    def scrap(self):
        aw = self.argsWidget
        args = {}
        if aw.action.isVisible():
            args['num_page'] = aw.getNumPages()
            args['stop_id'] = aw.getStopId()
        self.centralWidget().scrap(**args)

    def createToolbar(self):
        self.toolbar = self.addToolBar('Files')

        action = QAction(QIcon('res/documents-folder-up@128px.png'), 'Up', self)
        action.triggered.connect(self.centralWidget().upDir)
        self.toolbar.addAction(action)

        action = QAction(QIcon('res/documents-search-folder@128px.png'), 'Browse', self)
        action.triggered.connect(self.selectFolder)
        self.toolbar.addAction(action)

        action = QAction(QIcon('res/documents-folder-download@128px.png'), 'Scrap', self)
        action.triggered.connect(self.scrap)
        self.toolbar.addAction(action)

        action = QAction(QIcon('res/controls-editor-save@128px.png'), 'Save', self)
        action.triggered.connect(self.centralWidget().saveAll)
        self.toolbar.addAction(action)

        action = QAction(QIcon('res/photo-and-video-film-play@128px.png'), 'Play', self)
        action.triggered.connect(self.centralWidget().fileView.playFile)
        self.toolbar.addAction(action)

        action = QAction(QIcon('res/miscellaneous-handcuffs@128px.png'), 'Switch View', self)
        action.triggered.connect(self.centralWidget().listView.switchModel)
        self.toolbar.addAction(action)

        self.scrapToolbar = self.addToolBar('Scrapper')
        self.sites = QComboBox(self)
        site = self.scrapperConf.get('site', 'javlibrary')
        sites = self.scrapperConf['sites'].split(',')
        self.sites.insertItems(1, sites)
        self.sites.setCurrentText(site)
        self.sites.currentTextChanged.connect(self.setSite)
        self.scrapToolbar.addWidget(self.sites)
        self.setSite(site)

    def createMenu(self):
        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        #filemenu.addToolBar()

        action = QAction('Rename files', self)
        action.triggered.connect(self.centralWidget().fileRenameTool)
        filemenu.addAction(action)

if __name__ == '__main__':
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "2"
    #QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    #QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    import qt5reactor
    qt5reactor.install()

    from twisted.internet import reactor
    ex = ScrapperGui(reactor)
    ex.show()
    reactor.run()
    #reactor.runReturn()
    #sys.exit(app.exec_())