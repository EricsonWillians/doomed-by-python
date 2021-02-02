from PyQt5.QtWidgets import QAction, QFileDialog


class OpenAction(QAction):

    def __init__(self, widget, add_wads):
        super().__init__('&Open', widget)
        self.widget = widget
        self.setShortcut('Ctrl+O')
        self.setStatusTip('Select wad files')
        self.triggered.connect(self._open)
        self.add_wads = add_wads

    def _open(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileNames, _ = QFileDialog.getOpenFileNames(
            self.widget, "Select wad files", "", "WAD files (*.wad)", options=options)
        if fileNames:
            self.add_wads(fileNames)
