from PyQt5.QtWidgets import QAction, qApp

class ExitAction(QAction):

    def __init__(self, widget):
        super().__init__('&Exit', widget)
        self.setShortcut('Ctrl+Q')
        self.setStatusTip('Exit application')
        self.triggered.connect(qApp.quit)