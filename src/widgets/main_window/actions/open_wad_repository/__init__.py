from PyQt5.QtWidgets import QAction, qApp
import webbrowser


class OpenWadRepository(QAction):

    def __init__(self, widget):
        super().__init__('&Download wads', widget)
        self.setShortcut('Ctrl+W')
        self.setStatusTip('Open the doom world wad repository')
        self.triggered.connect(self.openLink)

    def openLink(self):
        webbrowser.open('https://www.doomworld.com/idgames')
