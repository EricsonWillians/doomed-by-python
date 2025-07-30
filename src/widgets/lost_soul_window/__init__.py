import numpy as np
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QWidget, QHBoxLayout, QSizePolicy
)
from PyQt5.QtGui import QMovie, QPixmap, QColor, QImage, QPainter
from PyQt5.QtCore import Qt, QSize, QTimer

def generate_doom2_blood_texture(width, height, t=0):
    """
    Returns a QPixmap of a scrolling, animated DOOM2-style blood river.
    t: animation phase/scroll (in pixels).
    """
    # Procedural blood river: sine + noise + red palette
    base = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        ymod = (y + t // 3) % height
        r = int(160 + 40 * np.sin(ymod * 0.18 + t * 0.04))
        g = int(0 + 18 * np.cos(ymod * 0.13 + t * 0.03))
        b = int(0 + 10 * np.sin(ymod * 0.27 + t * 0.01))
        for x in range(width):
            blood_wave = 10 * np.sin((x + t) * 0.09 + ymod * 0.08)
            drip = 18 * np.cos(x * 0.08 + t * 0.06)
            noise = np.random.randint(-8, 8)
            red = np.clip(r + blood_wave + drip + noise, 90, 255)
            green = np.clip(g + 6 * np.sin(x * 0.15), 0, 64)
            blue = np.clip(b + 8 * np.cos(x * 0.12), 0, 40)
            base[y, x, 0] = red
            base[y, x, 1] = green
            base[y, x, 2] = blue
    image = QImage(base.data, width, height, 3 * width, QImage.Format_RGB888)
    return QPixmap.fromImage(image)

class ScrollingDoom2Texture(QWidget):
    """A widget with a procedural, scrolling DOOM2 blood texture background."""
    def __init__(self, w, h, border=4, radius=20, parent=None):
        super().__init__(parent)
        self.setFixedSize(w, h)
        self._scroll = 0
        self._border = border
        self._radius = radius
        self._texture_width = max(128, w)
        self._texture_height = max(64, h)
        self._pixmap = generate_doom2_blood_texture(self._texture_width, self._texture_height)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._scroll_texture)
        self._timer.start(38)  # 26 FPS

    def _scroll_texture(self):
        self._scroll = (self._scroll + 2) % self._texture_width
        self._pixmap = generate_doom2_blood_texture(self._texture_width, self._texture_height, self._scroll)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Draw rounded border/background
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rect, self._radius, self._radius)
        painter.setClipPath(path)

        # Tile the procedural texture
        for x in range(0, self.width(), self._texture_width):
            for y in range(0, self.height(), self._texture_height):
                painter.drawPixmap(x, y, self._pixmap)

        # Draw the border
        pen = QColor('#ff2222')
        painter.setPen(QColor('#ff2222'))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(
            rect.adjusted(self._border//2, self._border//2, -self._border//2, -self._border//2),
            self._radius, self._radius
        )

class LostSoulWindow(QDialog):
    PADDING = 32   # Visibly hellish padding
    GIF_SIZE = 64

    def __init__(self, parent=None):
        flags = Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
        super().__init__(parent, flags)
        self.setObjectName("lostSoulWindow")
        self.setWindowTitle("Summoning from Hell...")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        # === BLOODY SCROLLING CONTAINER ===
        w = self.GIF_SIZE + 2 * self.PADDING
        h = self.GIF_SIZE + 2 * self.PADDING
        bloody_container = ScrollingDoom2Texture(w, h, border=4, radius=20, parent=self)
        # Layout for GIF on top of animated blood
        container_layout = QHBoxLayout(bloody_container)
        container_layout.setContentsMargins(self.PADDING, self.PADDING, self.PADDING, self.PADDING)
        container_layout.setSpacing(0)

        # LOST SOUL GIF (centered, floating above scrolling blood)
        self.label = QLabel(bloody_container)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedSize(self.GIF_SIZE, self.GIF_SIZE)
        self.label.setStyleSheet("background: transparent;")
        movie = QMovie("assets/lost_soul.gif")
        movie.setScaledSize(QSize(self.GIF_SIZE, self.GIF_SIZE))
        self.label.setMovie(movie)
        movie.start()
        container_layout.addWidget(self.label, alignment=Qt.AlignCenter)

        layout.addWidget(bloody_container, alignment=Qt.AlignCenter)

        # Progress bar (unchanged)
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setFixedHeight(24)
        self.progress.setStyleSheet("""
            QProgressBar {
                background: #1a050a;
                color: #fff0c0;
                border: 2px solid #900d09;
                border-radius: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff3500, stop:0.5 #ff9900, stop:1 #e4aa1a
                );
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.progress)

    def setRange(self, minimum: int, maximum: int):
        self.progress.setRange(minimum, maximum)

    def setValue(self, value: int):
        self.progress.setValue(value)
