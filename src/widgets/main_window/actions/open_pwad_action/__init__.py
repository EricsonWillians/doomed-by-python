from PyQt5.QtWidgets import QAction, QFileDialog


class OpenPWadAction(QAction):

    def __init__(self, widget, addPWads):
        super().__init__('&Open PWADs', widget)
        self.widget = widget
        self.setShortcut('Ctrl+P')
        self.setStatusTip('Select PWAD files')
        self.triggered.connect(self._open)
        self.addPWads = addPWads

    def _open(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileNames, _ = QFileDialog.getOpenFileNames(
            self.widget, "Select PWAD files", "", "WAD files (*.wad, *.pk3)", options=options)
        if fileNames:
            self.addPWads(fileNames)
