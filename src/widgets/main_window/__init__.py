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
from .actions.open_wad_repository import OpenWadRepository
from .actions.exit_action import ExitAction
from src.widgets.iwad_input import IWadInput
from src.widgets.pwad_list import PWadList
from src.widgets.path_input import PathInput
from src.widgets.launch_button import LaunchButton
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

        self.createMenu()
        self.addWidgets()

        # Load Norton Commander inspired theme
        theme_file = Path('assets/nc_theme.qss')
        if theme_file.exists():
            with open(theme_file, 'r') as fh:
                self.setStyleSheet(fh.read())

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
        self.iwadBrowseButton = QPushButton('Browse...')
        self.iwadBrowseButton.clicked.connect(self.openIWadAction._open)
        self.iwadInputContainer = QWidget()
        iwadLayout = QHBoxLayout()
        iwadLayout.setContentsMargins(0, 0, 0, 0)
        iwadLayout.addWidget(self.iwadInput)
        iwadLayout.addWidget(self.iwadBrowseButton)
        self.iwadInputContainer.setLayout(iwadLayout)
        self.pwadListLabel = QLabel("PWAD List:")
        self.pwadList = PWadList()
        self.pwadList.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.pwadAddButton = QPushButton('Add...')
        self.pwadAddButton.clicked.connect(self.openPWadAction._open)
        self.pwadRemoveButton = QPushButton('Remove')
        self.pwadRemoveButton.clicked.connect(self.removeSelectedPWads)
        self.pwadButtons = QWidget()
        pwadBtnsLayout = QHBoxLayout()
        pwadBtnsLayout.setContentsMargins(0, 0, 0, 0)
        pwadBtnsLayout.addWidget(self.pwadAddButton)
        pwadBtnsLayout.addWidget(self.pwadRemoveButton)
        self.pwadButtons.setLayout(pwadBtnsLayout)
        self.extraOptionsLabel = QLabel("Extra Options:")
        self.extraOptionsInput = QLineEdit()
        self.lostSoulLabel = QLabel()
        self.lostSoulPixmap = QPixmap("assets/lost_soul_sprite.png")
        self.lostSoulLabel.setPixmap(self.lostSoulPixmap)
        self.lostSoulLabel.setAlignment(Qt.AlignHCenter)
        self.launchButton = LaunchButton(
            self.sourcePortPathInput,
            self.iwadInput,
            self.pwadList,
            self.extraOptionsInput,
        )

        self.installGrid()

    def createMenu(self):
        self.openSourcePortAction = OpenSourcePortAction(
            self, self.setSourcePort, self.config, self.saveSourcePortPath)
        self.openIWadAction = OpenIWadAction(
            self, self.setIWad, self.config, self.saveWadPath)
        self.openPWadAction = OpenPWadAction(
            self, self.addPWads, self.config, self.saveWadPath)
        self.openWadRepository = OpenWadRepository(self)

        self.exitAction = ExitAction(self)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.openSourcePortAction)
        fileMenu.addAction(self.openIWadAction)
        fileMenu.addAction(self.openPWadAction)
        fileMenu.addAction(self.exitAction)
        helpMenu = menuBar.addMenu('&Help')
        helpMenu.addAction(self.openWadRepository)

    def installGrid(self):
        self.grid.addWidget(self.sourcePortPathInputLabel, 0, 0)
        self.grid.addWidget(self.sourcePortPathInput, 1, 0)
        self.grid.addWidget(self.iwadInputLabel, 2, 0)
        self.grid.addWidget(self.iwadInputContainer, 3, 0)
        self.grid.addWidget(self.pwadListLabel, 4, 0)
        self.grid.addWidget(self.pwadList, 5, 0)
        self.grid.addWidget(self.pwadButtons, 6, 0)
        self.grid.addWidget(self.extraOptionsLabel, 7, 0)
        self.grid.addWidget(self.extraOptionsInput, 8, 0)
        self.grid.addWidget(self.lostSoulLabel, 0, 1, 4, 1, Qt.AlignTop)
        self.grid.addWidget(self.launchButton, 8, 1, Qt.AlignBottom)

    def eventFilter(self, source, event):
        if (
            event.type() == QEvent.KeyPress and
            source is self.sourcePortPathInput and
            event.key() == Qt.Key_Return
        ):
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

    def removeSelectedPWads(self):
        for item in self.pwadList.selectedItems():
            self.pwadList.takeItem(self.pwadList.row(item))

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
