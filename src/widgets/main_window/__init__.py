import sys
from PyQt5.Qt import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from src import const
from .actions.open_action import OpenAction
from .actions.exit_action import ExitAction
from src.widgets.wad_list import WadList
from src.widgets.path_input import PathInput
from src.widgets.launch_button import LaunchButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        self.resize(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.center()
        self.setWindowTitle(const.MAIN_WINDOW_TITLE)
        self.centralWidget = QWidget()
        self.grid = QGridLayout()
        self.centralWidget.setLayout(self.grid)
        self.setCentralWidget(self.centralWidget)
        self.error_dialog = QErrorMessage()

        self.createMenu()
        self.addWidgets()

        self.show()

    def addWidgets(self):
        self.wadListLabel = QLabel("Wad List:")
        self.wadList = WadList()
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pathInputLabel = QLabel("GZDoom Path:")
        self.pathInputLabel.setMaximumHeight(20)
        self.pathInput = PathInput()
        self.lostSoulLabel = QLabel()
        self.lostSoulPixmap = QPixmap("assets/lost_soul_sprite.png")
        self.lostSoulLabel.setPixmap(self.lostSoulPixmap)
        self.lostSoulLabel.setAlignment(Qt.AlignHCenter)
        self.launchButton = LaunchButton(self.pathInput, self.wadList)
        self.grid.addWidget(self.pathInputLabel, 0, 0)
        self.grid.addWidget(self.pathInput, 1, 0)
        self.grid.addWidget(self.wadListLabel, 2, 0)
        self.grid.addWidget(self.wadList, 3, 0)
        self.grid.addWidget(self.lostSoulLabel, 0, 1, 4, 1, Qt.AlignTop)
        self.grid.addWidget(self.launchButton, 2, 1, Qt.AlignBottom)
        self.grid.addWidget(self.launchButton, 3, 1, Qt.AlignBottom)
        self.grid.setColumnStretch(0, 3)
        self.grid.setColumnStretch(1, 1)
        
    def createMenu(self):
        self.openAction = OpenAction(self, self.addWads)
        self.exitAction = ExitAction(self)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.exitAction)

        helpMenu = menuBar.addMenu('&Help')

    def addWads(self, wads):
        existent = False
        for wad in wads:
            foundItems = self.wadList.findItems(wad, Qt.MatchExactly)
            if len(foundItems) > 0:
                existent = True
                self.error_dialog.showMessage(f"The wad {wad} has already been added to the wad list.")
        if not existent:
            self.wadList.addItems(wads)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
