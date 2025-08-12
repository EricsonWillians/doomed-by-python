"""Performance optimization settings and utilities."""

import os
from typing import Dict, Any

class PerformanceSettings:
    """Centralized performance configuration."""
    
    # Default performance settings
    DEFAULT_SETTINGS = {
        'animation_fps': 20,  # Reduced from 30+ FPS
        'blood_texture_cache_size': 60,  # Number of cached blood frames
        'skull_scaling_quality': 'fast',  # 'fast' or 'smooth'
        'enable_antialiasing': False,  # Disable for better performance
        'background_animation_enabled': True,
        'sprite_frame_caching': True,
        'reduce_paint_events': True,
        'optimize_visibility_checks': True,
    }
    
    def __init__(self):
        self.settings = self.DEFAULT_SETTINGS.copy()
        self._load_from_env()
    
    def _load_from_env(self):
        """Load performance settings from environment variables."""
        env_mappings = {
            'DOOMED_ANIMATION_FPS': ('animation_fps', int),
            'DOOMED_CACHE_SIZE': ('blood_texture_cache_size', int),
            'DOOMED_SCALING_QUALITY': ('skull_scaling_quality', str),
            'DOOMED_ANTIALIASING': ('enable_antialiasing', lambda x: x.lower() == 'true'),
            'DOOMED_BACKGROUND_ANIM': ('background_animation_enabled', lambda x: x.lower() == 'true'),
        }
        
        for env_var, (setting_key, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    self.settings[setting_key] = converter(value)
                except (ValueError, TypeError):
                    pass  # Keep default value on conversion error
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a performance setting value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a performance setting value."""
        self.settings[key] = value
    
    def get_timer_interval(self) -> int:
        """Get optimized timer interval in milliseconds."""
        fps = self.get('animation_fps', 20)
        return max(16, 1000 // fps)  # Minimum 16ms (60 FPS max)

# Global performance settings instance
perf_settings = PerformanceSettings()