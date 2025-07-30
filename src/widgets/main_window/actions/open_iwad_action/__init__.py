from PyQt5.QtWidgets import QAction, QFileDialog


class OpenIWadAction(QAction):

    def __init__(self, widget, setIWad, config, saveWadPath):
        super().__init__('&Open IWAD', widget)
        self.widget = widget
        self.setShortcut('Ctrl+I')
        self.setStatusTip('Select an IWAD file')
        self.triggered.connect(self._open)
        self.setIWad = setIWad
        self.config = config
        self.saveWadPath = saveWadPath

    def _open(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self.widget,
            "Select an IWAD file",
            self.config.get("iwadDir"),
            "WAD files (*.wad)",
            options=options,
        )
        if fileName:
            self.saveWadPath(fileName, isIWad=True)
            self.setIWad(fileName)
