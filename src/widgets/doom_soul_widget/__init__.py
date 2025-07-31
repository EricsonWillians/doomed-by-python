# doom_soul_widget.py
# Author: Ericson Willians
# Standalone PyQt5 widget for a "DOOM Lost Soul" over a scrolling hell tile, optimized for low CPU

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QMovie, QImage
from PyQt5.QtCore import Qt, QTimer, QSize
from PIL import Image, ImageDraw, ImageFilter
import os

def make_hell_tile(width=96, height=64):
    """Generate a single seamless hell tile, *once*, as a PIL image."""
    img = Image.new("RGBA", (width, height), (24, 7, 5, 255))
    draw = ImageDraw.Draw(img)

    # Evil veins (red, jagged lines)
    for _ in range(8):
        points = [(0, int(height/2 + (height/3) * (0.4-0.8*(_%2))))]
        for x in range(0, width, 7):
            y = int(height/2 + (height/3) * (0.5 - 1.0 * (_%2)) + 8 * (1-(_%2))*((x*13+_)%7)/7)
            points.append((x, y))
        draw.line(points, fill=(140+_, 18, 5), width=2)
    # Black cracks
    for _ in range(3):
        x = width // 4 + _*width//5
        draw.line([(x, 2), (x+5, height-2)], fill=(0,0,0), width=3)
    # Embers
    for _ in range(18):
        x, y = (int(width * 0.12 + _*width//19), int(height * 0.3 + (_*height//21)%height))
        draw.ellipse([x, y, x+4, y+4], fill=(255, 100, 0, 170))

    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    # Subtle vignette
    for y in range(height):
        for x in range(width):
            dx, dy = (x - width/2), (y - height/2)
            dist = (dx*dx + dy*dy)**0.5 / (width/2)
            f = 0.8 + 0.18*(1 - dist)
            r,g,b,a = img.getpixel((x,y))
            img.putpixel((x, y), (int(r*f), int(g*f), int(b*f), a))
    return img

class DoomSoulWidget(QWidget):
    def __init__(self, skull_gif_path, parent=None, tile_w=96, tile_h=64, scroll_speed=2):
        super().__init__(parent)
        self.setMinimumSize(180, 180)
        self.tile_w, self.tile_h = tile_w, tile_h
        # Pre-render tile and convert to QPixmap
        tile_img = make_hell_tile(tile_w, tile_h)
        self.tile_qpix = QPixmap.fromImage(
            QImage(tile_img.tobytes("raw", "RGBA"), tile_w, tile_h, QImage.Format_RGBA8888)
        )
        self.scroll = 0
        self.scroll_speed = scroll_speed

        # Setup GIF
        self.skull_gif = QMovie(skull_gif_path)
        self.skull_gif.frameChanged.connect(self.update)
        self.skull_gif.start()

        # Timer to scroll only background
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scroll)
        self.timer.start(33)  # ~30 FPS, but only blits

    def _scroll(self):
        self.scroll = (self.scroll + self.scroll_speed) % self.tile_w
        self.update()

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        p = QPainter(self)
        # Scroll background by simply tiling the QPixmap
        for y in range(0, h, self.tile_h):
            for x in range(-self.scroll, w, self.tile_w):
                p.drawPixmap(x, y, self.tile_qpix)
        # Draw the animated skull GIF, centered and large
        frame = self.skull_gif.currentPixmap()
        size = int(min(w, h)*0.85)
        if not frame.isNull():
            scaled = frame.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (w - scaled.width()) // 2
            y = (h - scaled.height()) // 2
            p.drawPixmap(x, y, scaled)

if __name__ == "__main__":
    # Demo launcher
    app = QApplication(sys.argv)
    assets = os.path.join(os.path.dirname(__file__), "assets")
    skull_gif = os.path.join(assets, "lost_soul.gif")
    w = DoomSoulWidget(skull_gif)
    w.setWindowTitle("Doomed by Python - Optimized Lost Soul Widget")
    w.resize(320, 320)
    w.show()
    sys.exit(app.exec_())
