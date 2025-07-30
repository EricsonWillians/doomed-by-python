from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtGui import QMovie, QSize
from PyQt5.Qt import Qt


class LostSoulWindow(QDialog):
    """A small window showing a loading animation."""

    def __init__(self, parent=None):
        flags = Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
        super().__init__(parent, flags)
        self.setObjectName("lostSoulWindow")
        self.setWindowTitle("Loading")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.label = QLabel(self)
        movie = QMovie("assets/lost_soul.gif")
        movie.setScaledSize(QSize(64, 64))
        self.label.setMovie(movie)
        movie.start()
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)

    def setRange(self, minimum: int, maximum: int):
        self.progress.setRange(minimum, maximum)

    def setValue(self, value: int):
        self.progress.setValue(value)
