from PyQt5.QtWidgets import QAction, QFileDialog


class OpenAction(QAction):

    def __init__(self, widget):
        super().__init__('&Open', widget)
        self.widget = widget
        self.setShortcut('Ctrl+O')
        self.setStatusTip('Select wad files')
        self.triggered.connect(self._open)

    def _open(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileNames, _ = QFileDialog.getOpenFileNames(
            self.widget, "Select wad files", "", "WAD files (*.wad)", options=options)
        if fileNames:
            print(fileNames)
