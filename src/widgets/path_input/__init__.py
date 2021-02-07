from PyQt5.QtWidgets import QLineEdit


class PathInput(QLineEdit):

    def __init__(self):
        super().__init__()
        self.insert('gzdoom')
