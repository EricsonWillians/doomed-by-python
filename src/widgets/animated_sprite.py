from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, QRect


class AnimatedSprite(QLabel):
    """Display an animated sprite sheet."""

    def __init__(self, path: str, columns: int, rows: int,
                 interval: int = 120):
        super().__init__()
        self._sheet = QPixmap(path)
        self._columns = columns
        self._rows = rows
        self._frame_w = self._sheet.width() // columns
        self._frame_h = self._sheet.height() // rows
        self._frame = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_frame)
        self._timer.start(interval)
        self._update_pixmap()

    def _next_frame(self):
        self._frame = (self._frame + 1) % (self._columns * self._rows)
        self._update_pixmap()

    def _update_pixmap(self):
        col = self._frame % self._columns
        row = self._frame // self._columns
        rect = QRect(
            col * self._frame_w,
            row * self._frame_h,
            self._frame_w,
            self._frame_h,
        )
        self.setPixmap(self._sheet.copy(rect))
