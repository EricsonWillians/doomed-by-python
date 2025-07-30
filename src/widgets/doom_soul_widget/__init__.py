import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap, QImage, QMovie
from PyQt5.QtCore import Qt, QTimer, QSize
from PIL import Image, ImageDraw, ImageFilter
import sys, os

def generate_dark_hell(width, height):
    from PIL import Image
    import numpy as np
    arr = np.zeros((height, width, 3), dtype=np.uint8)

    # Deep, noisy dark red base
    for y in range(height):
        for x in range(width):
            base = 30 + 45 * np.sin(y * 0.17 + np.sin(x * 0.09))
            chaos = 40 * np.sin(x * 0.07 + y * 0.10) + 12 * np.random.randn()
            r = np.clip(base + chaos + 75, 18, 32)  # Lower max for darker feel
            g = int(4 + 6 * np.sin((x + y) * 0.13))
            b = int(3 + 2 * np.cos((x - y) * 0.08))
            arr[y, x] = (int(np.clip(r, 0, 255)), int(np.clip(g, 0, 255)), int(np.clip(b, 0, 255)))

    # Black cracks: organic, fewer, thick, sharp
    for _ in range(np.random.randint(2, 5)):
        x0, y0 = np.random.randint(0, width), np.random.randint(0, height)
        length = np.random.randint(width//2, width)
        angle = np.random.uniform(-1.2, 1.2) * np.pi
        for l in range(length):
            x = int(x0 + l * np.cos(angle + np.sin(l*0.11)*0.8)) % width
            y = int(y0 + l * np.sin(angle + np.cos(l*0.08)*0.7)) % height
            rr = np.random.randint(3, 7)
            yy, xx = np.ogrid[:height, :width]
            mask = (yy-y)**2 + (xx-x)**2 <= rr**2
            arr[mask] = (0, 0, 0)

    # Embers (very few, hot, orange-red)
    for _ in range(width * height // 800):
        fx = np.random.randint(0, width)
        fy = np.random.randint(0, height)
        fr = np.random.randint(2, 6)
        arr[max(0,fy-fr):min(height,fy+fr), max(0,fx-fr):min(width,fx+fr), 0] = 110 + np.random.randint(0, 35)
        arr[max(0,fy-fr):min(height,fy+fr), max(0,fx-fr):min(width,fx+fr), 1] = 10 + np.random.randint(0, 40)
        arr[max(0,fy-fr):min(height,fy+fr), max(0,fx-fr):min(width,fx+fr), 2] = np.random.randint(0, 10)


    img = Image.fromarray(arr, "RGB")
    return img


class DoomSoulWidget(QWidget):
    def __init__(self, skull_gif_path, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self._tile_w, self._tile_h = 96, 64
        img = generate_dark_hell(self._tile_w, self._tile_h)
        data = img.tobytes("raw", "RGBA")
        self._tile_img = QImage(data, self._tile_w, self._tile_h, QImage.Format_RGBA8888)
        self._tile_pixmap = QPixmap.fromImage(self._tile_img)
        self._scroll = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

        # Skull GIF with alpha, loaded via QMovie
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

        # Composite the animated GIF frame with alpha, centered
        if self.skull_frame:
            size = int(min(w, h) * 0.82)
            skull = self.skull_frame.scaled(QSize(size, size), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            sx = (w - size) // 2
            sy = (h - size) // 2
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            painter.drawImage(sx, sy, skull)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    skull_gif = os.path.join(os.path.dirname(__file__), "assets", "lost_soul.gif")
    w = DoomSoulWidget(skull_gif)
    w.setWindowTitle("DOOM Soul Widget - True Hell River")
    w.resize(320, 320)
    w.show()
    sys.exit(app.exec_())
