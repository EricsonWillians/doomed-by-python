from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, QRect


class AnimatedSprite(QLabel):
    """Optimized animated sprite sheet display with frame caching."""

    def __init__(self, path: str, columns: int, rows: int,
                 interval: int = 120):
        super().__init__()
        self._sheet = QPixmap(path)
        self._columns = columns
        self._rows = rows
        self._frame_w = self._sheet.width() // columns
        self._frame_h = self._sheet.height() // rows
        self._frame = 0
        self._total_frames = columns * rows
        
        # Pre-cache all frames for better performance
        self._frame_cache = []
        self._cache_frames()
        
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_frame)
        self._timer.start(interval)
        self._update_pixmap()

    def _cache_frames(self):
        """Pre-cache all sprite frames to avoid repeated copy operations."""
        for frame in range(self._total_frames):
            col = frame % self._columns
            row = frame // self._columns
            rect = QRect(
                col * self._frame_w,
                row * self._frame_h,
                self._frame_w,
                self._frame_h,
            )
            self._frame_cache.append(self._sheet.copy(rect))

    def _next_frame(self):
        self._frame = (self._frame + 1) % self._total_frames
        self._update_pixmap()

    def _update_pixmap(self):
        # Use cached frame instead of copying from sheet
        self.setPixmap(self._frame_cache[self._frame])
