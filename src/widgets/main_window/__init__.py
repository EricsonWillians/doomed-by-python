import sys
import json
from PyQt5.Qt import Qt
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import *  # noqa: F401,F403
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QAction
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
from src.widgets.lost_soul_window import LostSoulWindow
from src.widgets.doom_soul_widget import DoomSoulWidget

from pathlib import Path, PurePath

# Import performance settings with fallback
try:
    from src.performance import perf_settings
except ImportError:
    # Fallback if performance module has issues
    class FallbackPerfSettings:
        def get(self, key, default=None):
            return default
        def set(self, key, value):
            pass
    perf_settings = FallbackPerfSettings()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = self.getConfig()
        self.initUi()

    def initUi(self):
        # Set minimum and preferred sizes for better scaling
        self.setMinimumSize(640, 480)
        self.resize(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.center()
        self.setWindowTitle(const.MAIN_WINDOW_TITLE)
        
        # Create central widget with responsive layout
        self.centralWidget = QWidget()
        self.setupResponsiveLayout()
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

    def setupResponsiveLayout(self):
        """Create a responsive layout that adapts to window resizing."""
        # Main horizontal layout
        self.mainLayout = QHBoxLayout(self.centralWidget)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setContentsMargins(12, 12, 12, 12)
        
        # Left panel for controls
        self.leftPanel = QWidget()
        self.leftPanel.setMinimumWidth(320)
        self.leftPanel.setMaximumWidth(600)  # Allow more width for larger screens
        self.leftPanel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.leftLayout = QVBoxLayout(self.leftPanel)
        self.leftLayout.setSpacing(8)
        self.leftLayout.setContentsMargins(0, 0, 0, 0)
        
        # Right panel for skull and info
        self.rightPanel = QWidget()
        self.rightPanel.setMinimumWidth(200)
        self.rightPanel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.rightLayout = QVBoxLayout(self.rightPanel)
        self.rightLayout.setSpacing(12)
        self.rightLayout.setContentsMargins(0, 0, 0, 0)
        
        # Add panels to main layout with proper stretch
        self.mainLayout.addWidget(self.leftPanel, 2)  # Left panel gets 2/3 of space
        self.mainLayout.addWidget(self.rightPanel, 1)  # Right panel gets 1/3 of space

    def addWidgets(self):
        # === LEFT PANEL WIDGETS ===
        
        # Source Port section
        self.sourcePortGroup = QGroupBox("Source Port")
        sourcePortLayout = QVBoxLayout(self.sourcePortGroup)
        
        self.sourcePortPathInput = PathInput()
        self.sourcePortPathInput.setToolTip('Path to gzdoom or zandronum')
        self.sourcePortPathInput.setText(self.config.get('lastSourcePort', 'gzdoom'))
        self.sourcePortPathInput.installEventFilter(self)
        sourcePortLayout.addWidget(self.sourcePortPathInput)
        
        # IWAD section
        self.iwadGroup = QGroupBox("IWAD (Main Game)")
        iwadLayout = QVBoxLayout(self.iwadGroup)
        
        self.iwadInput = IWadInput()
        self.iwadInput.setToolTip('Main IWAD file')
        self.iwadInput.setText(self.config.get('lastIWad', ''))
        
        self.iwadBrowseButton = QPushButton('Browse...')
        self.iwadBrowseButton.setToolTip('Select an IWAD file')
        self.iwadBrowseButton.clicked.connect(self.openIWadAction._open)
        
        iwadInputLayout = QHBoxLayout()
        iwadInputLayout.addWidget(self.iwadInput, 1)
        iwadInputLayout.addWidget(self.iwadBrowseButton, 0)
        iwadLayout.addLayout(iwadInputLayout)
        
        # PWAD section
        self.pwadGroup = QGroupBox("PWADs (Mods)")
        pwadLayout = QVBoxLayout(self.pwadGroup)
        
        self.pwadList = PWadList()
        self.pwadList.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pwadList.setMinimumHeight(120)
        for wad in self.config.get('lastPWads', []):
            self.pwadList.addWad(wad)
        self.pwadList.orderChanged.connect(self.saveConfig)
        pwadLayout.addWidget(self.pwadList)
        
        # PWAD buttons
        self.pwadButtons = QWidget()
        pwadBtnsLayout = QHBoxLayout(self.pwadButtons)
        pwadBtnsLayout.setContentsMargins(0, 0, 0, 0)
        pwadBtnsLayout.setSpacing(4)
        
        self.pwadAddButton = QPushButton('Add...')
        self.pwadAddButton.setToolTip('Add PWAD or PK3 files')
        self.pwadAddButton.clicked.connect(self.openPWadAction._open)
        
        self.pwadRemoveButton = QPushButton('Remove')
        self.pwadRemoveButton.setToolTip('Remove selected mods')
        self.pwadRemoveButton.clicked.connect(self.removeSelectedPWads)
        
        self.pwadUpButton = QPushButton('↑')
        self.pwadUpButton.setToolTip('Move selected mods up')
        self.pwadUpButton.setMaximumWidth(30)
        self.pwadUpButton.clicked.connect(self.pwadList.moveUp)
        
        self.pwadDownButton = QPushButton('↓')
        self.pwadDownButton.setToolTip('Move selected mods down')
        self.pwadDownButton.setMaximumWidth(30)
        self.pwadDownButton.clicked.connect(self.pwadList.moveDown)
        
        pwadBtnsLayout.addWidget(self.pwadAddButton)
        pwadBtnsLayout.addWidget(self.pwadRemoveButton)
        pwadBtnsLayout.addStretch()
        pwadBtnsLayout.addWidget(self.pwadUpButton)
        pwadBtnsLayout.addWidget(self.pwadDownButton)
        pwadLayout.addWidget(self.pwadButtons)
        
        # Extra Options section
        self.optionsGroup = QGroupBox("Extra Options")
        optionsLayout = QVBoxLayout(self.optionsGroup)
        
        self.extraOptionsInput = QLineEdit()
        self.extraOptionsInput.setToolTip('Additional command line arguments')
        self.extraOptionsInput.setText(self.config.get('lastOptions', ''))
        optionsLayout.addWidget(self.extraOptionsInput)
        
        # Launch button
        self.launchButton = LaunchButton(
            self.sourcePortPathInput,
            self.iwadInput,
            self.pwadList,
            self.extraOptionsInput,
            None,  # Will set logWindow later
            None,  # Will set loadingWindow later
        )
        self.launchButton.setMinimumHeight(40)
        self.launchButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # === RIGHT PANEL WIDGETS ===
        
        # Skull widget
        self.lostSoulWidget = DoomSoulWidget(
            skull_gif_path="assets/lost_soul.gif",
            animated_background=self.config.get('animatedBackground', False)
        )
        self.lostSoulWidget.setMinimumSize(180, 180)
        self.lostSoulWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # PWAD info panel
        self.pwadInfo = PWadInfo()
        self.pwadInfo.setMinimumHeight(120)
        self.pwadInfo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # === DIALOGS ===
        self.logWindow = LogWindow(self)
        self.loadingWindow = LostSoulWindow(self)
        
        # Update launch button with dialogs
        self.launchButton.logWindow = self.logWindow
        self.launchButton.loadingWindow = self.loadingWindow
        
        # Connect signals
        self.pwadList.itemSelectionChanged.connect(self.updatePWadInfo)
        self.updatePWadInfo()

        self.installResponsiveLayout()

    def createMenu(self):
        self.openSourcePortAction = OpenSourcePortAction(
            self, self.setSourcePort, self.config, self.saveSourcePortPath)
        self.openIWadAction = OpenIWadAction(
            self, self.setIWad, self.config, self.saveWadPath)
        self.openPWadAction = OpenPWadAction(
            self, self.addPWads, self.config, self.saveWadPath)
        self.openWadRepository = OpenWadRepository(self)
        self.exitAction = ExitAction(self)

        # Create animated background toggle action
        self.animatedBgAction = QAction('&Animated Background', self)
        self.animatedBgAction.setCheckable(True)
        self.animatedBgAction.setChecked(self.config.get('animatedBackground', False))
        self.animatedBgAction.triggered.connect(self.toggleAnimatedBackground)
        
        # Create performance mode toggle action
        self.performanceModeAction = QAction('&Performance Mode', self)
        self.performanceModeAction.setCheckable(True)
        self.performanceModeAction.setChecked(self.config.get('performanceMode', False))
        self.performanceModeAction.triggered.connect(self.togglePerformanceMode)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.openSourcePortAction)
        fileMenu.addAction(self.openIWadAction)
        fileMenu.addAction(self.openPWadAction)
        fileMenu.addAction(self.exitAction)
        
        configMenu = menuBar.addMenu('&Config')
        configMenu.addAction(self.animatedBgAction)
        configMenu.addAction(self.performanceModeAction)
        
        helpMenu = menuBar.addMenu('&Help')
        helpMenu.addAction(self.openWadRepository)

    def installResponsiveLayout(self):
        """Install the responsive layout with proper widget arrangement."""
        
        # === LEFT PANEL LAYOUT ===
        self.leftLayout.addWidget(self.sourcePortGroup)
        self.leftLayout.addWidget(self.iwadGroup)
        self.leftLayout.addWidget(self.pwadGroup, 1)  # Give PWAD list most space
        self.leftLayout.addWidget(self.optionsGroup)
        self.leftLayout.addWidget(self.launchButton)
        
        # === RIGHT PANEL LAYOUT ===
        self.rightLayout.addWidget(self.lostSoulWidget, 1)  # Skull gets most space
        self.rightLayout.addWidget(self.pwadInfo, 1)  # Info panel gets equal space
        
        # Add stretch to prevent widgets from being too tall
        self.rightLayout.addStretch(0)

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
        dialog = self.loadingWindow
        dialog.setRange(0, len(wads))
        dialog.setValue(0)
        dialog.show()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            for i, wad in enumerate(wads):
                dialog.setValue(i)
                if not self.pwadList.addWad(wad):
                    msg = (
                        f"The wad {wad} has already "
                        "been added to the wad list."
                    )
                    self.errorDialog.showMessage(msg)
                QApplication.processEvents()
            dialog.setValue(len(wads))
        finally:
            QApplication.restoreOverrideCursor()
            dialog.hide()
        self.saveConfig()

    def removeSelectedPWads(self):
        for item in self.pwadList.selectedItems():
            index = self.pwadList.indexOfTopLevelItem(item)
            self.pwadList.takeTopLevelItem(index)
        self.saveConfig()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def saveWadPath(self, filename: str, isIWad: bool):
        if isIWad:
            self.config["iwadDir"] = str(PurePath(filename).parent)
            self.config["lastIWad"] = filename
        else:
            if filename:
                self.config["pwadDir"] = str(PurePath(filename[0]).parent)
        self.saveConfig()

    def saveSourcePortPath(self, filename: str):
        self.config["sourcePortDir"] = str(PurePath(filename).parent)
        self.config["lastSourcePort"] = filename
        self.saveConfig()

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
                "lastIWad": "",
                "lastPWads": [],
                "lastSourcePort": "gzdoom",
                "lastOptions": "",
                "animatedBackground": False,
            }
        return configData

    def saveConfig(self):
        self.config["lastIWad"] = self.iwadInput.text()
        self.config["lastPWads"] = [
            item.data(0, Qt.UserRole) for item in self.pwadList.getItems()
        ]
        self.config["lastSourcePort"] = self.sourcePortPathInput.text()
        self.config["lastOptions"] = self.extraOptionsInput.text()
        self.config["animatedBackground"] = self.animatedBgAction.isChecked()
        self.config["performanceMode"] = getattr(self, 'performanceModeAction', type('obj', (object,), {'isChecked': lambda: False})()).isChecked()
        with open('config.json', 'w') as fp:
            json.dump(self.config, fp)

    def resizeEvent(self, event):
        """Handle window resize to adjust layout dynamically."""
        super().resizeEvent(event)
        
        # Get current window size
        width = event.size().width()
        height = event.size().height()
        
        # Adjust layout based on window size
        if width < 700:
            # Very narrow window - reduce spacing
            self.mainLayout.setSpacing(8)
            self.mainLayout.setContentsMargins(8, 8, 8, 8)
            self.leftLayout.setSpacing(6)
            self.rightLayout.setSpacing(8)
        elif width > 1200:
            # Very wide window - increase spacing
            self.mainLayout.setSpacing(20)
            self.mainLayout.setContentsMargins(20, 16, 20, 16)
            self.leftLayout.setSpacing(12)
            self.rightLayout.setSpacing(16)
        else:
            # Normal window - default spacing
            self.mainLayout.setSpacing(12)
            self.mainLayout.setContentsMargins(12, 12, 12, 12)
            self.leftLayout.setSpacing(8)
            self.rightLayout.setSpacing(12)
        
        # Adjust skull widget size constraints based on available space
        if hasattr(self, 'lostSoulWidget'):
            if width < 700 or height < 500:
                # Small window - reduce skull size
                self.lostSoulWidget.setMinimumSize(150, 150)
            else:
                # Normal/large window - normal skull size
                self.lostSoulWidget.setMinimumSize(180, 180)

    def closeEvent(self, event):
        self.saveConfig()
        super().closeEvent(event)

    def updatePWadInfo(self):
        """Update the mod info panel based on current selection."""
        paths = [
            item.data(0, Qt.UserRole)
            for item in self.pwadList.selectedItems()
        ]
        self.pwadInfo.showInfo(paths)

    def toggleAnimatedBackground(self):
        """Toggle the animated background on/off."""
        enabled = self.animatedBgAction.isChecked()
        self.lostSoulWidget.setAnimatedBackground(enabled)
        self.saveConfig()
    
    def togglePerformanceMode(self):
        """Toggle performance mode on/off."""
        enabled = self.performanceModeAction.isChecked()
        if enabled:
            # Enable performance optimizations
            perf_settings.set('animation_fps', 15)
            perf_settings.set('enable_antialiasing', False)
            perf_settings.set('skull_scaling_quality', 'fast')
        else:
            # Restore default settings
            perf_settings.set('animation_fps', 20)
            perf_settings.set('enable_antialiasing', False)
            perf_settings.set('skull_scaling_quality', 'smooth')
        
        # Update config and restart animations with new settings
        self.config['performanceMode'] = enabled
        self.saveConfig()
        
        # Restart the skull widget with new settings
        if hasattr(self, 'lostSoulWidget'):
            self.lostSoulWidget.setAnimatedBackground(self.animatedBgAction.isChecked())
