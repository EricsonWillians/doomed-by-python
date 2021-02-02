from PyQt5.QtWidgets import QAction

class OpenFolderAction(QAction):

    def __init__(self, widget):
        super().__init__('&Open folder', widget)
        self.setShortcut('Ctrl+O')
        self.setStatusTip('Select a wad folder')
        self.triggered.connect(self.openFolder)

    def openFolder(self):
        print("folder")