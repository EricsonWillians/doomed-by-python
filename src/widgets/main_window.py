import sys
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication, qApp, QAction
from src import const


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.resize(const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.center()
        self.setWindowTitle(const.MAIN_WINDOW_TITLE)

        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(qApp.quit)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
