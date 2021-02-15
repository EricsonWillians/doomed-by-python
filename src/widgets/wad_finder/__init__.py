from PyQt5.QtWidgets import *
from src import const


class WadFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        self.resize(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.setWindowTitle(const.MAIN_WINDOW_TITLE)
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.error_dialog = QErrorMessage()
