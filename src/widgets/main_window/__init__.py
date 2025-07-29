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
from src.widgets.log_window import LogWindow
from src.widgets.pwad_info import PWadInfo
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
        self.sourcePortPathInput.setToolTip('Path to gzdoom or zandronum')
        self.sourcePortPathInput.setText(
            self.config.get('lastSourcePort', 'gzdoom')
        )

        self.sourcePortPathInput.installEventFilter(self)
        self.iwadInputLabel = QLabel("IWAD Path:")
        self.iwadInputLabel.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.iwadInput = IWadInput()
        self.iwadInput.setToolTip('Main IWAD file')
        self.iwadInput.setText(self.config.get('lastIWad', ''))
        self.iwadBrowseButton = QPushButton('Browse...')
        self.iwadBrowseButton.setToolTip('Select an IWAD file')
        self.iwadBrowseButton = QPushButton('Browse...')

        for wad in self.config.get('lastPWads', []):
            self.pwadList.addWad(wad)
        self.pwadAddButton = QPushButton('Add...')
        self.pwadAddButton.setToolTip('Add PWAD or PK3 files')
        self.pwadAddButton.clicked.connect(self.openPWadAction._open)
        self.pwadRemoveButton = QPushButton('Remove')
        self.pwadRemoveButton.setToolTip('Remove selected mods')
        self.pwadRemoveButton.clicked.connect(self.removeSelectedPWads)
        self.pwadUpButton = QPushButton('Up')
        self.pwadUpButton.setToolTip('Move selected mods up')
        self.pwadUpButton.clicked.connect(self.pwadList.moveUp)
        self.pwadDownButton = QPushButton('Down')
        self.pwadDownButton.setToolTip('Move selected mods down')
        self.pwadDownButton.clicked.connect(self.pwadList.moveDown)
        self.pwadAddButton = QPushButton('Add...')
        self.pwadAddButton.clicked.connect(self.openPWadAction._open)
        self.pwadRemoveButton = QPushButton('Remove')
        self.pwadRemoveButton.clicked.connect(self.removeSelectedPWads)

        pwadBtnsLayout.addWidget(self.pwadUpButton)
        pwadBtnsLayout.addWidget(self.pwadDownButton)
        self.pwadButtons.setLayout(pwadBtnsLayout)
        self.extraOptionsLabel = QLabel("Extra Options:")
        self.extraOptionsInput = QLineEdit()
        self.extraOptionsInput.setToolTip('Additional command line arguments')
        self.extraOptionsInput.setText(self.config.get('lastOptions', ''))
        self.lostSoulLabel = QLabel()
        self.lostSoulPixmap = QPixmap("assets/lost_soul_sprite.png")
        self.lostSoulLabel.setPixmap(self.lostSoulPixmap)
        self.lostSoulLabel.setAlignment(Qt.AlignHCenter)
        self.logWindow = LogWindow(self)
        self.pwadInfo = PWadInfo()
        self.launchButton = LaunchButton(
            self.sourcePortPathInput,
            self.iwadInput,
            self.pwadList,
            self.extraOptionsInput,
            self.logWindow,
        )
        self.pwadList.itemSelectionChanged.connect(self.updatePWadInfo)
        self.updatePWadInfo()
        )

        self.grid.addWidget(self.pwadInfo, 4, 1, 4, 1)