import json
from PyQt5.QtWidgets import QAction, QFileDialog
from os import path


class OpenIWadAction(QAction):

    def __init__(self, widget, setIWad, config, saveConfig):
        super().__init__('&Open IWAD', widget)
        self.widget = widget
        self.setShortcut('Ctrl+I')
        self.setStatusTip('Select an IWAD file')
        self.triggered.connect(self._open)
        self.setIWad = setIWad
        self.config = config
        self.saveConfig = saveConfig

    def _open(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self.widget, "Select an IWAD file", self.config.get("iwadDir"), "WAD files (*.wad)", options=options)
        if fileName:
            self.saveConfig(fileName, isWad=True)
            self.setIWad(fileName)
