import sys, os, tempfile, shutil
import numpy as np
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPixmap, QImage, QMovie
from PyQt5.QtCore import Qt, QTimer, QSize
from PIL import Image
from datetime import datetime

def generate_hell_tile_array(width, height, seed=None):
    """
    Generates a seamless "hellish" background tile (evil red, cracks, embers).
    - Runs ONCE at startup.
    - Deterministic if seed is provided.
    Returns: np.ndarray (height, width, 4) RGBA
    """
    if seed is not None:
        np.random.seed(seed)
    arr = np.zeros((height, width, 4), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            # Sinusoidal base (deep red, evil)
            r = 26 + 32 * np.sin(0.11 * y + 0.19 * x) + 38
            g = 7 + 9 * np.cos(0.19 * y + 0.13 * x)
            b = 2 + 6 * np.sin(0.09 * x - 0.11 * y)
            arr[y, x, 0] = np.clip(r, 0, 255)
            arr[y, x, 1] = np.clip(g, 0, 255)
            arr[y, x, 2] = np.clip(b, 0, 255)
            arr[y, x, 3] = 255
    # Add black cracks
    cracks = np.random.rand(5, 4) * np.array([[width, height, 2*np.pi, width/2]])
    for cx, cy, a, l in cracks:
        for t in range(int(l)):
            px = int((cx + t * np.cos(a + np.sin(t * 0.19))) % width)
            py = int((cy + t * np.sin(a + np.cos(t * 0.12))) % height)
            arr[py-1:py+2, px-1:px+2, :3] = 0
    # Add glowing embers
    for _ in range((width * height) // 640):
        ex, ey = np.random.randint(0, width), np.random.randint(0, height)
        radius = np.random.randint(2, 6)
        for dy in range(-radius, radius+1):
            for dx in range(-radius, radius+1):
                xx, yy = (ex+dx)%width, (ey+dy)%height
                dist = (dx*dx+dy*dy)**0.5
                if dist <= radius:
                    glow = int(220 - dist * 38 + np.random.randint(0, 8))
                    arr[yy, xx, 0] = np.clip(arr[yy, xx, 0] + glow, 0, 255)
                    arr[yy, xx, 1] = np.clip(arr[yy, xx, 1] + glow//3, 0, 255)
    # Vignette
    cy, cx = height/2, width/2
    for y in range(height):
        for x in range(width):
            d = ((x-cx)**2 + (y-cy)**2)**0.5
            fade = 0.85 + 0.15 * np.cos(np.pi * d / (0.7*max(width, height)))
            arr[y, x, :3] = (arr[y, x, :3].astype(np.float32) * fade).astype(np.uint8)
    return arr

def save_hell_tile_png(arr, path):
    img = Image.fromarray(arr, "RGBA")
    img.save(path)

def get_temp_tile_path(tag="doomed_by_python_tile"):
    tempdir = tempfile.gettempdir()
    # Use a name that is unique for the tile size, for robustness
    return os.path.join(tempdir, f"{tag}_{os.getpid()}.png")

def ensure_tile_file(tile_w, tile_h, seed=None, keep_existing=False):
    """
    If tile PNG exists, use it. Otherwise, generate and save.
    Returns the PNG path.
    """
    path = get_temp_tile_path()
    if keep_existing and os.path.isfile(path):
        return path
    arr = generate_hell_tile_array(tile_w, tile_h, seed)
    save_hell_tile_png(arr, path)
    return path

class DoomSoulWidget(QWidget):
    def __init__(self, skull_gif_path: str, parent=None, tile_w=96, tile_h=64):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self._tile_w, self._tile_h = tile_w, tile_h
        # Optionally: Use "seed of the day" for daily random backgrounds:
        day_seed = int(datetime.now().strftime('%Y%m%d'))
        self._tile_path = ensure_tile_file(tile_w, tile_h, seed=day_seed)
        self._tile_pixmap = QPixmap(self._tile_path)
        self._scroll = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

        self.skull_gif = QMovie(skull_gif_path)
        self.skull_gif.jumpToFrame(0)
        self.skull_frame = None
        self.skull_gif.frameChanged.connect(self.updateSkullFrame)
        self.skull_gif.start()

    def updateSkullFrame(self, idx):
        frame = self.skull_gif.currentPixmap().toImage().convertToFormat(QImage.Format_ARGB32)
        self.skull_frame = frame
        self.update()

    def _tick(self):
        self._scroll = (self._scroll + 2) % self._tile_w
        self.update()

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        # Tile and scroll the "hell river"
        for y in range(0, h, self._tile_h):
            for x in range(-self._scroll, w, self._tile_w):
                painter.drawPixmap(x, y, self._tile_pixmap)
        # Draw the animated skull, centered
        if self.skull_frame:
            size = int(min(w, h) * 0.82)
            skull = self.skull_frame.scaled(QSize(size, size), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            sx = (w - size) // 2
            sy = (h - size) // 2
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            painter.drawImage(sx, sy, skull)

    def closeEvent(self, event):
        # Clean up our temp file ONLY if we "own" it
        try:
            if os.path.isfile(self._tile_path):
                os.remove(self._tile_path)
        except Exception:
            pass
        event.accept()

if __name__ == "__main__":
    # Demo: run this as a standalone test
    app = QApplication(sys.argv)
    skull_gif = os.path.join(os.path.dirname(__file__), "assets", "lost_soul.gif")
    w = DoomSoulWidget(skull_gif)
    w.setWindowTitle("DOOM Soul Widget - Pre-generated Hell Tile (Super Optimized)")
    w.resize(320, 320)
    w.show()
    sys.exit(app.exec_())
