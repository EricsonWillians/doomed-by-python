from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtGui import QMovie
from PyQt5.Qt import Qt


class LostSoulWindow(QDialog):
    """A small window showing a loading animation."""

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Loading")
        layout = QVBoxLayout()
        self.label = QLabel()
        movie = QMovie("assets/lost_soul.gif")
        self.label.setMovie(movie)
        movie.start()
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)
        self.setLayout(layout)

    def setRange(self, minimum: int, maximum: int):
        self.progress.setRange(minimum, maximum)

    def setValue(self, value: int):
        self.progress.setValue(value)
