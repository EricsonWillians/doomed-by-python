from PyQt5.QtWidgets import QAction, QFileDialog


class OpenPWadAction(QAction):

    def __init__(self, widget, addPWads, config, saveConfig):
        super().__init__('&Open PWADs', widget)
        self.widget = widget
        self.setShortcut('Ctrl+P')
        self.setStatusTip('Select PWAD files')
        self.triggered.connect(self._open)
        self.addPWads = addPWads
        self.config = config
        self.saveConfig = saveConfig

    def _open(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filenames, _ = QFileDialog.getOpenFileNames(
            self.widget, "Select PWAD files", self.config.get("pwadDir"), "WAD files (*.    wad, *.pk3)", options=options)
        if filenames:
            self.saveConfig(filenames, isWad=False)
            self.addPWads(filenames)
