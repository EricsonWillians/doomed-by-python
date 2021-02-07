import sys
from PyQt5.Qt import Qt
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from src import const
from .actions.open_action import OpenAction
from .actions.exit_action import ExitAction
from src.widgets.iwad_list import IWadList
from src.widgets.pwad_list import PWadList
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
        self.pathInputLabel = QLabel("GZDoom Path:")
        self.pathInputLabel.setMaximumHeight(20)
        self.pathInput = PathInput()
        self.pathInput.installEventFilter(self)
        self.iwadListLabel = QLabel("IWAD:")
        self.iwadList = IWadList()
        self.pwadListLabel = QLabel("PWAD List:")
        self.pwadList = PWadList()
        self.lostSoulLabel = QLabel()
        self.lostSoulPixmap = QPixmap("assets/lost_soul_sprite.png")
        self.lostSoulLabel.setPixmap(self.lostSoulPixmap)
        self.lostSoulLabel.setAlignment(Qt.AlignHCenter)
        self.launchButton = LaunchButton(self.pathInput, self.iwadList)

        self.installGrid()

    def createMenu(self):
        self.openAction = OpenAction(self, self.addWads)
        self.exitAction = ExitAction(self)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.exitAction)

        helpMenu = menuBar.addMenu('&Help')

    def installGrid(self):
        self.grid.addWidget(self.pathInputLabel, 0, 0)
        self.grid.addWidget(self.pathInput, 1, 0)
        self.grid.addWidget(self.iwadListLabel, 2, 0)
        self.grid.addWidget(self.iwadList, 3, 0)
        self.grid.addWidget(self.pwadListLabel, 4, 0)
        self.grid.addWidget(self.pwadList, 5, 0)
        self.grid.addWidget(self.lostSoulLabel, 0, 1, 4, 1, Qt.AlignTop)
        self.grid.addWidget(self.launchButton, 5, 1, Qt.AlignBottom)
        self.grid.setRowStretch(0, 1)
        self.grid.setRowStretch(1, 1)
        self.grid.setRowStretch(2, 1)
        self.grid.setRowStretch(3, 1)
        self.grid.setRowStretch(4, 1)
        self.grid.setRowStretch(5, 6)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.KeyPress and
                source is self.pathInput and event.key() == Qt.Key_Return):
            self.launchButton.onClick()
        return super(MainWindow, self).eventFilter(source, event)

    def addWads(self, wads):
        existent = False
        for wad in wads:
            foundItems = self.iwadList.findItems(wad, Qt.MatchExactly)
            if len(foundItems) > 0:
                existent = True
                self.error_dialog.showMessage(
                    f"The wad {wad} has already been added to the wad list.")
        if not existent:
            self.iwadList.addItems(wads)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
