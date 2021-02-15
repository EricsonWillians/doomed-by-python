import sys
import json
from PyQt5.Qt import Qt
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from src import const
from .actions.open_source_port_action import OpenSourcePortAction
from .actions.open_iwad_action import OpenIWadAction
from .actions.open_pwad_action import OpenPWadAction
from .actions.open_wad_finder import OpenWadFinder
from .actions.exit_action import ExitAction
from src.widgets.iwad_input import IWadInput
from src.widgets.pwad_list import PWadList
from src.widgets.path_input import PathInput
from src.widgets.launch_button import LaunchButton
from src.widgets.wad_finder import WadFinder
from pathlib import Path, PurePath


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = self.getConfig()
        self.initUi()

    def initUi(self):
        self.resize(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.center()
        self.setWindowTitle(const.MAIN_WINDOW_TITLE)
        self.centralWidget = QWidget()
        self.grid = QGridLayout()
        self.centralWidget.setLayout(self.grid)
        self.setCentralWidget(self.centralWidget)
        self.errorDialog = QErrorMessage()

        self.wadFinder = WadFinder()

        self.createMenu()
        self.addWidgets()

        self.show()

    def addWidgets(self):
        self.sourcePortPathInputLabel = QLabel("Source Port Path:")
        self.sourcePortPathInputLabel.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sourcePortPathInput = PathInput()

        self.sourcePortPathInput.installEventFilter(self)
        self.iwadInputLabel = QLabel("IWAD Path:")
        self.iwadInputLabel.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.iwadInput = IWadInput()
        self.pwadListLabel = QLabel("PWAD List:")
        self.pwadList = PWadList()
        self.pwadList.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.lostSoulLabel = QLabel()
        self.lostSoulPixmap = QPixmap("assets/lost_soul_sprite.png")
        self.lostSoulLabel.setPixmap(self.lostSoulPixmap)
        self.lostSoulLabel.setAlignment(Qt.AlignHCenter)
        self.launchButton = LaunchButton(
            self.sourcePortPathInput, self.iwadInput, self.pwadList)

        self.installGrid()

    def createMenu(self):
        self.openSourcePortAction = OpenSourcePortAction(
            self, self.setSourcePort, self.config, self.saveSourcePortPath)
        self.openIWadAction = OpenIWadAction(
            self, self.setIWad, self.config, self.saveWadPath)
        self.openPWadAction = OpenPWadAction(
            self, self.addPWads, self.config, self.saveWadPath)
        self.openWadFinder = OpenWadFinder(self, self.wadFinder)
        self.exitAction = ExitAction(self)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.openSourcePortAction)
        fileMenu.addAction(self.openIWadAction)
        fileMenu.addAction(self.openPWadAction)
        fileMenu.addAction(self.exitAction)

        viewMenu = menuBar.addMenu('&View')
        viewMenu.addAction(self.openWadFinder)
        helpMenu = menuBar.addMenu('&Help')

    def installGrid(self):
        self.grid.addWidget(self.sourcePortPathInputLabel, 0, 0)
        self.grid.addWidget(self.sourcePortPathInput, 1, 0)
        self.grid.addWidget(self.iwadInputLabel, 2, 0)
        self.grid.addWidget(self.iwadInput, 3, 0)
        self.grid.addWidget(self.pwadListLabel, 4, 0)
        self.grid.addWidget(self.pwadList, 5, 0)
        self.grid.addWidget(self.lostSoulLabel, 0, 1, 4, 1, Qt.AlignTop)
        self.grid.addWidget(self.launchButton, 5, 1, Qt.AlignBottom)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.KeyPress and
                source is self.sourcePortPathInput and event.key() == Qt.Key_Return):
            self.launchButton.onClick()
        return super(MainWindow, self).eventFilter(source, event)

    def setSourcePort(self, sourcePort: str):
        self.sourcePortPathInput.setText(sourcePort)

    def setIWad(self, wad: str):
        self.iwadInput.setText(wad)

    def addPWads(self, wads: list):
        existent = False
        for wad in wads:
            foundItems = self.pwadList.findItems(wad, Qt.MatchExactly)
            if len(foundItems) > 0:
                existent = True
                self.errorDialog.showMessage(
                    f"The wad {wad} has already been added to the wad list.")
        if not existent:
            self.pwadList.addItems(wads)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def saveWadPath(self, filename: str, isIWad: bool):
        iwadDir = self.config.get("iwadDir")
        pwadDir = self.config.get("pwadDir")
        if isIWad:
            iwadDir = str(PurePath(filename).parent)
        else:
            if filename:
                pwadDir = str(PurePath(filename[0]).parent)
        with open('config.json', 'w') as fp:
            json.dump({
                "iwadDir": iwadDir,
                "pwadDir": pwadDir
            }, fp)

    def saveSourcePortPath(self, filename: str):
        iwadDir = self.config.get("iwadDir")
        pwadDir = self.config.get("pwadDir")
        sourcePortDir = str(PurePath(filename).parent)
        with open('config.json', 'w') as fp:
            json.dump({
                "sourcePortDir": sourcePortDir,
                "iwadDir": iwadDir,
                "pwadDir": pwadDir
            }, fp)

    def getConfig(self):
        configData = {}
        if Path("config.json").exists():
            with open('config.json', 'r') as fp:
                configData = json.load(fp)
        else:
            home = str(Path.home())
            configData = {
                "sourcePortDir": home,
                "iwadDir": home,
                "pwadDir": home,
            }
        return configData
