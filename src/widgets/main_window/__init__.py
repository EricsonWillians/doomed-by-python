import sys
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import *
from src import const
from .actions.open_action import OpenAction
from .actions.exit_action import ExitAction
from src.widgets.wad_list import WadList


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
        self.addComponents()

        self.show()

    def addComponents(self):
        self.wadList = WadList()
        self.grid.addWidget(self.wadList, 0, 0)

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
