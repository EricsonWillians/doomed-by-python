"""Performance monitoring utilities for debugging."""

import time
import psutil
import os
from typing import Dict, List
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

class PerformanceMonitor(QObject):
    """Monitor application performance metrics."""
    
    stats_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = psutil.Process(os.getpid())
        self.frame_times: List[float] = []
        self.last_frame_time = time.time()
        self.paint_count = 0
        self.timer_count = 0
        
        # Monitor timer
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._update_stats)
        self.monitor_timer.start(1000)  # Update every second
    
    def record_frame(self):
        """Record a frame render time."""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.frame_times.append(frame_time)
        self.last_frame_time = current_time
        
        # Keep only last 60 frames
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
    
    def record_paint_event(self):
        """Record a paint event."""
        self.paint_count += 1
    
    def record_timer_event(self):
        """Record a timer event."""
        self.timer_count += 1
    
    def _update_stats(self):
        """Update and emit performance statistics."""
        try:
            # Calculate FPS
            if self.frame_times:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            else:
                fps = 0
            
            # Get memory usage
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Get CPU usage
            cpu_percent = self.process.cpu_percent()
            
            stats = {
                'fps': round(fps, 1),
                'memory_mb': round(memory_mb, 1),
                'cpu_percent': round(cpu_percent, 1),
                'paint_events_per_sec': self.paint_count,
                'timer_events_per_sec': self.timer_count,
                'frame_count': len(self.frame_times)
            }
            
            # Reset counters
            self.paint_count = 0
            self.timer_count = 0
            
            self.stats_updated.emit(stats)
            
        except Exception as e:
            print(f"Performance monitoring error: {e}")

# Global performance monitor instance
perf_monitor = PerformanceMonitor()