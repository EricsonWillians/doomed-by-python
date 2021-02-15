from PyQt5.QtWidgets import QAction, qApp


class OpenWadFinder(QAction):

    def __init__(self, widget, wadFinder):
        super().__init__('&Wad Finder', widget, checkable=True)
        self.setShortcut('Ctrl+W')
        self.setStatusTip('Open the wad finder')
        self.wadFinder = wadFinder
        self.triggered.connect(self.setVisible)

    def setVisible(self):
        isVisible = self.wadFinder.isVisible()
        self.wadFinder.setVisible(not isVisible)
