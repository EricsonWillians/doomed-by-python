import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap, QImage, QMovie
from PyQt5.QtCore import Qt, QTimer, QSize
from PIL import Image, ImageDraw, ImageFilter
import sys, os
from typing import Tuple

from typing import Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def generate_dark_hell(width: int, height: int) -> Image.Image:
    """
    Generate a seamless, evil hellscape tile for UI backgrounds.
    Features: deep reds, black branching cracks, glowing embers, scorched edges, subtle heat haze.
    Optionally uses Perlin noise for "lava veins" if the 'noise' library is installed.

    Args:
        width (int): Tile width (px)
        height (int): Tile height (px)
    Returns:
        PIL.Image (RGBA): Hell tile, ready for QImage/QPixmap or OpenGL texture.

    Appearance:
    - Base: Deep red, uneven and moody
    - Cracks: Jagged, black, branching (drawn with randomness for organic look)
    - Lava veins: Glowing, with natural randomness
    - Embers: Red/orange, blurred for glow
    - Vignette: Corners darker, focus in center
    - Subtle blue plasma flicker: Adds unnatural, infernal vibe
    """
    arr = np.zeros((height, width, 4), dtype=np.uint8)
    y_grid, x_grid = np.ogrid[:height, :width]

    # 1. Base hell color (deep dark red, uneven using sine/cos fields)
    base_r = 18 + 38 * (np.sin(2 * np.pi * y_grid / height + np.sin(2 * np.pi * x_grid / width)) + 1)
    chaos = 22 * (np.sin(2 * np.pi * x_grid / width * 2 + y_grid * 0.13) + np.sin(2 * np.pi * y_grid / height * 2 + x_grid * 0.09))
    r = np.clip(base_r + chaos + 54, 8, 35)
    g = 3 + 7 * np.sin((x_grid + y_grid) * 0.13)
    b = 2 + 3 * np.cos((x_grid - y_grid) * 0.08)
    arr[..., 0] = np.clip(r, 0, 255).astype(np.uint8)
    arr[..., 1] = np.clip(g, 0, 255).astype(np.uint8)
    arr[..., 2] = np.clip(b, 0, 255).astype(np.uint8)
    arr[..., 3] = 255

    # 2. Lava veins (if 'noise' is available, else skip)
    try:
        from noise import pnoise2
        scale = 0.08
        for y in range(height):
            for x in range(width):
                v: float = pnoise2(
                    x * scale, y * scale,
                    octaves=3,
                    repeatx=width, repeaty=height,
                    base=42
                )
                if v > 0.19:
                    arr[y, x, 0] = min(255, arr[y, x, 0] + int(95 * v))
                    arr[y, x, 1] = min(255, arr[y, x, 1] + int(32 * v))
    except ImportError:
        pass

    # 3. Black cracks (drawn with branching)
    cracks = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(cracks)
    n_cracks = np.random.randint(7, 12)
    for _ in range(n_cracks):
        x0, y0 = np.random.randint(0, width), np.random.randint(0, height)
        length = np.random.randint(width // 2, width)
        angle = np.random.uniform(-1.2, 1.2) * np.pi
        thickness = np.random.randint(2, 5)
        points = []
        for l in range(length):
            dx = (x0 + int(l * np.cos(angle + np.sin(l * 0.13) * 1.1))) % width
            dy = (y0 + int(l * np.sin(angle + np.cos(l * 0.12) * 1.1))) % height
            points.append((dx, dy))
            # Occasional branch
            if l > 10 and np.random.rand() < 0.018:
                branch_len = np.random.randint(7, 18)
                branch_angle = angle + np.random.uniform(-1.3, 1.3)
                for bl in range(branch_len):
                    bx = (dx + int(bl * np.cos(branch_angle))) % width
                    by = (dy + int(bl * np.sin(branch_angle))) % height
                    draw.ellipse([bx-thickness//2, by-thickness//2, bx+thickness//2, by+thickness//2], fill=255)
        if len(points) > 1:
            draw.line(points, fill=255, width=thickness)
    cracks = cracks.filter(ImageFilter.MaxFilter(3))
    cracks_np = np.array(cracks)
    arr[cracks_np > 128] = (0, 0, 0, 255)
    # Add scorched halo around cracks
    for offset in [(-1,0), (1,0), (0,-1), (0,1)]:
        mask = np.roll(cracks_np > 128, offset, axis=(0,1))
        arr[mask, 0] = (arr[mask, 0] // 2).astype(np.uint8)
        arr[mask, 1] = (arr[mask, 1] // 2).astype(np.uint8)
        arr[mask, 2] = (arr[mask, 2] // 2).astype(np.uint8)

    # 4. Embers (red/orange, blurred for "glow", but not playful)
    embers = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    emb_draw = ImageDraw.Draw(embers)
    n_embers = max(1, width * height // 1020)
    for _ in range(n_embers):
        fx = np.random.randint(0, width)
        fy = np.random.randint(0, height)
        fr = np.random.randint(2, 7)
        color = (
            np.random.randint(190, 255),   # R
            np.random.randint(22, 64),     # G
            np.random.randint(0, 12),      # B
            np.random.randint(80, 180)     # A (transparent)
        )
        emb_draw.ellipse([fx-fr, fy-fr, fx+fr, fy+fr], fill=color)
    embers = embers.filter(ImageFilter.GaussianBlur(radius=3.1))
    emb_np = np.array(embers)
    mask = emb_np[..., 3] > 0
    arr[mask] = emb_np[mask]

    # 5. Add subtle blue "demonic plasma" flicker for depth (random hot spots)
    flicker = (np.random.rand(height, width) > 0.998)
    arr[flicker, 2] = np.clip(arr[flicker, 2] + 56, 0, 255)

    # 6. Heat haze: blurred overlay
    haze = Image.fromarray(arr, "RGBA").filter(ImageFilter.GaussianBlur(radius=2.0))
    haze_np = np.array(haze)
    arr[..., 0] = np.clip(0.76 * arr[..., 0] + 0.24 * haze_np[..., 0], 0, 255).astype(np.uint8)
    arr[..., 1] = np.clip(0.80 * arr[..., 1] + 0.20 * haze_np[..., 1], 0, 255).astype(np.uint8)
    arr[..., 2] = np.clip(0.77 * arr[..., 2] + 0.23 * haze_np[..., 2], 0, 255).astype(np.uint8)

    # 7. Vignette for depth
    yy, xx = np.ogrid[:height, :width]
    cx, cy = width / 2, height / 2
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    vignette = 0.63 + 0.37 * np.cos(np.pi * dist / (0.93 * max(width, height)))
    for c in range(3):
        arr[..., c] = np.clip(arr[..., c] * vignette, 0, 255).astype(np.uint8)

    return Image.fromarray(arr, "RGBA")


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
