import sys, os, tempfile, shutil
import numpy as np
from PyQt5.QtWidgets import QWidget, QApplication, QSizePolicy
from PyQt5.QtGui import QPainter, QPixmap, QImage, QMovie
from PyQt5.QtCore import Qt, QTimer, QSize
from PIL import Image
from datetime import datetime

# Import performance settings with fallback
try:
    from src.performance import perf_settings
except ImportError:
    class FallbackPerfSettings:
        def get(self, key, default=None):
            defaults = {
                'animation_fps': 20, 
                'enable_antialiasing': False,
                'skull_scaling_quality': 'fast'
            }
            return defaults.get(key, default)
        def get_timer_interval(self):
            return 50
    perf_settings = FallbackPerfSettings()

def generate_hell_tile_array(width, height, seed=None):
    """
    Optimized hellish background tile generation using vectorized operations.
    Returns: np.ndarray (height, width, 4) RGBA
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Create coordinate grids for vectorized operations
    y_coords, x_coords = np.mgrid[0:height, 0:width]
    
    # Vectorized sinusoidal base calculations
    r = np.clip(26 + 32 * np.sin(0.11 * y_coords + 0.19 * x_coords) + 38, 0, 255)
    g = np.clip(7 + 9 * np.cos(0.19 * y_coords + 0.13 * x_coords), 0, 255)
    b = np.clip(2 + 6 * np.sin(0.09 * x_coords - 0.11 * y_coords), 0, 255)
    
    # Create the array
    arr = np.zeros((height, width, 4), dtype=np.uint8)
    arr[:, :, 0] = r
    arr[:, :, 1] = g
    arr[:, :, 2] = b
    arr[:, :, 3] = 255
    
    # Simplified crack generation (fewer cracks for performance)
    cracks = np.random.rand(3, 4) * np.array([[width, height, 2*np.pi, width/3]])
    for cx, cy, a, l in cracks:
        t_vals = np.arange(0, int(l), 2)  # Skip every other point for performance
        px = ((cx + t_vals * np.cos(a + np.sin(t_vals * 0.19))) % width).astype(int)
        py = ((cy + t_vals * np.sin(a + np.cos(t_vals * 0.12))) % height).astype(int)
        # Vectorized crack drawing
        for i in range(len(px)):
            y_slice = slice(max(0, py[i]-1), min(height, py[i]+2))
            x_slice = slice(max(0, px[i]-1), min(width, px[i]+2))
            arr[y_slice, x_slice, :3] = 0
    
    # Reduced ember count for performance
    ember_count = (width * height) // 1280  # Half the original count
    for _ in range(ember_count):
        ex, ey = np.random.randint(0, width), np.random.randint(0, height)
        radius = np.random.randint(2, 4)  # Smaller radius
        y_slice = slice(max(0, ey-radius), min(height, ey+radius+1))
        x_slice = slice(max(0, ex-radius), min(width, ex+radius+1))
        
        # Vectorized ember glow
        dy, dx = np.mgrid[y_slice, x_slice] - np.array([[ey], [ex]])
        dist = np.sqrt(dx*dx + dy*dy)
        mask = dist <= radius
        glow = (220 - dist * 38).astype(int)
        
        arr[y_slice, x_slice, 0] = np.where(mask, 
                                           np.clip(arr[y_slice, x_slice, 0] + glow, 0, 255),
                                           arr[y_slice, x_slice, 0])
        arr[y_slice, x_slice, 1] = np.where(mask,
                                           np.clip(arr[y_slice, x_slice, 1] + glow//3, 0, 255),
                                           arr[y_slice, x_slice, 1])
    
    # Vectorized vignette
    cy, cx = height/2, width/2
    d = np.sqrt((x_coords-cx)**2 + (y_coords-cy)**2)
    fade = 0.85 + 0.15 * np.cos(np.pi * d / (0.7*max(width, height)))
    arr[:, :, :3] = (arr[:, :, :3].astype(np.float32) * fade[:, :, np.newaxis]).astype(np.uint8)
    
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
    def __init__(self, skull_gif_path: str, parent=None, tile_w=96, tile_h=64, animated_background=False):
        super().__init__(parent)
        self.setMinimumSize(180, 180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tile_w, self._tile_h = tile_w, tile_h
        self._animated_background = animated_background
        
        # Only generate tile if animated background is enabled
        if self._animated_background:
            day_seed = int(datetime.now().strftime('%Y%m%d'))
            self._tile_path = ensure_tile_file(tile_w, tile_h, seed=day_seed)
            self._tile_pixmap = QPixmap(self._tile_path)
        else:
            self._tile_path = None
            self._tile_pixmap = None
        
        self._scroll = 0
        self._cached_skull = None
        self._cached_skull_size = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        if self._animated_background:
            self._timer.start(perf_settings.get_timer_interval())

        self.skull_gif = QMovie(skull_gif_path)
        self.skull_gif.jumpToFrame(0)
        self.skull_frame = None
        self.skull_gif.frameChanged.connect(self.updateSkullFrame)
        self.skull_gif.start()

    def updateSkullFrame(self, idx):
        # Cache the frame conversion to avoid repeated operations
        frame = self.skull_gif.currentPixmap().toImage().convertToFormat(QImage.Format_ARGB32)
        self.skull_frame = frame
        # Invalidate cached skull when frame changes
        self._cached_skull = None
        self.update()

    def _tick(self):
        if self._animated_background:
            self._scroll = (self._scroll + 1) % self._tile_w  # Slower scroll for performance
            # Only update every other frame to reduce CPU usage
            if self._scroll % 2 == 0:
                self.update()

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, perf_settings.get('enable_antialiasing', False))
        
        if self._animated_background and self._tile_pixmap:
            # Optimized tiling - only draw visible area
            visible_rect = event.rect()
            start_x = ((visible_rect.x() - self._scroll) // self._tile_w) * self._tile_w + self._scroll
            start_y = (visible_rect.y() // self._tile_h) * self._tile_h
            end_x = visible_rect.right() + self._tile_w
            end_y = visible_rect.bottom() + self._tile_h
            
            for y in range(start_y, end_y, self._tile_h):
                for x in range(start_x - self._scroll, end_x, self._tile_w):
                    painter.drawPixmap(x, y, self._tile_pixmap)
        else:
            # Fast black background fill
            painter.fillRect(event.rect(), Qt.black)
        
        # Draw the animated skull with caching
        if self.skull_frame:
            size = int(min(w, h) * 0.82)
            
            # Use cached scaled skull if size hasn't changed
            if self._cached_skull is None or self._cached_skull_size != size:
                transform_mode = Qt.SmoothTransformation if perf_settings.get('skull_scaling_quality') == 'smooth' else Qt.FastTransformation
                self._cached_skull = self.skull_frame.scaled(
                    QSize(size, size), Qt.KeepAspectRatio, transform_mode
                )
                self._cached_skull_size = size
            
            sx = (w - size) // 2
            sy = (h - size) // 2
            painter.drawImage(sx, sy, self._cached_skull)

    def setAnimatedBackground(self, enabled):
        """Enable or disable the animated background."""
        self._animated_background = enabled
        
        if enabled:
            # Generate tile if not already done
            if not self._tile_pixmap:
                day_seed = int(datetime.now().strftime('%Y%m%d'))
                self._tile_path = ensure_tile_file(self._tile_w, self._tile_h, seed=day_seed)
                self._tile_pixmap = QPixmap(self._tile_path)
            # Start animation timer
            if not self._timer.isActive():
                self._timer.start(33)
        else:
            # Stop animation timer
            self._timer.stop()
        
        self.update()

    def closeEvent(self, event):
        # Clean up our temp file ONLY if we "own" it
        try:
            if self._tile_path and os.path.isfile(self._tile_path):
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
