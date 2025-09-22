"""
Performance-optimized color animation system for terminal-flow.

Provides ColorAnimator and related classes for real-time color animation
with pre-calculated frames, caching, and batched operations targeting 30+ FPS.
Pure curses implementation without external dependencies.
"""

import time
from typing import List, Dict, Tuple, Optional, Union, Callable

from .schemes import BaseColorScheme


class ColorFrameCache:
    """
    High-performance color frame caching system.

    Caches pre-calculated color sequences to minimize computation overhead
    during real-time animation. Uses LRU-style eviction for memory management.
    """

    def __init__(self, max_cache_size: int = 100):
        """
        Initialize color frame cache.

        Args:
            max_cache_size: Maximum number of cached frame sequences
        """
        self.max_cache_size = max_cache_size
        self._cache: Dict[str, List[List[Tuple[int, int, int]]]] = {}
        self._access_times: Dict[str, float] = {}

    def get_cache_key(self, scheme_id: str, text_length: int, frame_count: int,
                     speed: float, **kwargs) -> str:
        """
        Generate cache key for color sequence.

        Args:
            scheme_id: Unique identifier for color scheme
            text_length: Number of characters in text
            frame_count: Number of animation frames
            speed: Animation speed multiplier
            **kwargs: Additional parameters for cache key

        Returns:
            Unique cache key string
        """
        extra_params = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{scheme_id}_{text_length}_{frame_count}_{speed}_{extra_params}"

    def get_frames(self, cache_key: str) -> Optional[List[List[Tuple[int, int, int]]]]:
        """
        Retrieve cached color frames.

        Args:
            cache_key: Cache key from get_cache_key()

        Returns:
            Cached color frame sequence or None if not found
        """
        if cache_key in self._cache:
            self._access_times[cache_key] = time.time()
            return self._cache[cache_key]
        return None

    def store_frames(self, cache_key: str, frames: List[List[Tuple[int, int, int]]]) -> None:
        """
        Store color frames in cache.

        Args:
            cache_key: Cache key from get_cache_key()
            frames: List of color frame sequences to cache
        """
        # Evict oldest entries if cache is full
        if len(self._cache) >= self.max_cache_size:
            self._evict_oldest()

        self._cache[cache_key] = frames
        self._access_times[cache_key] = time.time()

    def _evict_oldest(self) -> None:
        """Remove least recently used cache entry."""
        if not self._access_times:
            return

        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        del self._cache[oldest_key]
        del self._access_times[oldest_key]

    def clear(self) -> None:
        """Clear all cached frames."""
        self._cache.clear()
        self._access_times.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache size and other metrics
        """
        return {
            "cached_sequences": len(self._cache),
            "max_cache_size": self.max_cache_size,
            "cache_utilization": len(self._cache) / self.max_cache_size if self.max_cache_size > 0 else 0
        }


class ColorAnimator:
    """
    High-performance color animator for real-time text animation.

    Provides optimized color animation with frame pre-calculation, caching,
    and batched operations targeting 30+ FPS performance.
    """

    def __init__(self, color_scheme: BaseColorScheme, fps: int = 30,
                 enable_cache: bool = True, cache_size: int = 100):
        """
        Initialize color animator.

        Args:
            color_scheme: Color scheme to use for animation
            fps: Target frames per second (default: 30)
            enable_cache: Enable frame caching for performance (default: True)
            cache_size: Maximum number of cached frame sequences
        """
        self.color_scheme = color_scheme
        self.fps = fps
        self.frame_duration = 1.0 / fps
        self.enable_cache = enable_cache

        # Performance optimization components
        self._cache = ColorFrameCache(cache_size) if enable_cache else None
        self._current_frames: Optional[List[List[Tuple[int, int, int]]]] = None
        self._frame_index = 0
        self._last_frame_time = 0.0
        self._animation_speed = 1.0

        # Pre-calculation settings
        self._pre_calc_duration = 2.0  # Pre-calculate 2 seconds of animation
        self._text_length = 0

    def pre_calculate_frames(self, text_length: int, animation_speed: float = 1.0,
                           duration: Optional[float] = None) -> List[List[Tuple[int, int, int]]]:
        """
        Pre-calculate color animation frames for optimal performance.

        Generates a sequence of color frames that can be applied rapidly
        during animation without per-frame color computation overhead.

        Args:
            text_length: Number of characters in text to animate
            animation_speed: Speed multiplier for animation (default: 1.0)
            duration: Duration in seconds to pre-calculate (default: 2.0 seconds)

        Returns:
            List of color frame sequences, each containing colors for all characters
        """
        if duration is None:
            duration = self._pre_calc_duration

        frame_count = int(duration * self.fps)
        frames = []

        # Check cache first
        cache_key = None
        if self._cache:
            cache_key = self._cache.get_cache_key(
                scheme_id=self.color_scheme.__class__.__name__,
                text_length=text_length,
                frame_count=frame_count,
                speed=animation_speed
            )
            cached_frames = self._cache.get_frames(cache_key)
            if cached_frames:
                return cached_frames

        # Generate frames
        for frame_idx in range(frame_count):
            # Calculate animation offset for this frame
            time_offset = (frame_idx / self.fps) * animation_speed
            animation_offset = (time_offset * 0.5) % 1.0  # 0.5 = rotation speed factor

            # Generate colors for this frame
            frame_colors = self.color_scheme.get_colors_for_text(text_length, animation_offset)
            frames.append(frame_colors)

        # Cache the generated frames
        if self._cache and cache_key:
            self._cache.store_frames(cache_key, frames)

        return frames

    def initialize_animation(self, text_length: int, animation_speed: float = 1.0) -> None:
        """
        Initialize animation with pre-calculated frames.

        Args:
            text_length: Number of characters in text to animate
            animation_speed: Speed multiplier for animation
        """
        self._text_length = text_length
        self._animation_speed = animation_speed
        self._current_frames = self.pre_calculate_frames(text_length, animation_speed)
        self._frame_index = 0
        self._last_frame_time = time.time()

    def get_current_frame_colors(self) -> Optional[List[Tuple[int, int, int]]]:
        """
        Get colors for current animation frame.

        Returns:
            List of colors for current frame, or None if not initialized
        """
        if not self._current_frames:
            return None

        return self._current_frames[self._frame_index]

    def advance_frame(self, force: bool = False) -> bool:
        """
        Advance to next animation frame if enough time has elapsed.

        Args:
            force: Force frame advance regardless of timing

        Returns:
            True if frame was advanced, False otherwise
        """
        if not self._current_frames:
            return False

        current_time = time.time()
        time_elapsed = current_time - self._last_frame_time

        if force or time_elapsed >= self.frame_duration:
            self._frame_index = (self._frame_index + 1) % len(self._current_frames)
            self._last_frame_time = current_time
            return True

        return False

    def get_current_frame_colors_hex(self) -> Optional[List[str]]:
        """
        Get current frame colors as hex strings for curses styling.

        Returns:
            List of hex color strings for current frame, or None if not initialized
        """
        from .generator import ColorGenerator
        frame_colors = self.get_current_frame_colors()
        if not frame_colors:
            return None

        return [ColorGenerator.rgb_to_hex(color) for color in frame_colors]

    def animate_frame_auto(self) -> bool:
        """
        Automatically advance frame for animation timing.

        Convenience method that handles frame timing for curses implementation.

        Returns:
            True if animation frame was updated
        """
        return self.advance_frame()

    def set_animation_speed(self, speed: float) -> None:
        """
        Update animation speed and regenerate frames if needed.

        Args:
            speed: New animation speed multiplier
        """
        if speed != self._animation_speed and self._text_length > 0:
            self._animation_speed = speed
            # Regenerate frames with new speed
            self._current_frames = self.pre_calculate_frames(self._text_length, speed)
            self._frame_index = 0

    def get_performance_stats(self) -> Dict[str, Union[int, float]]:
        """
        Get animation performance statistics.

        Returns:
            Dictionary with performance metrics
        """
        stats = {
            "fps": self.fps,
            "frame_duration": self.frame_duration,
            "current_frame": self._frame_index,
            "total_frames": len(self._current_frames) if self._current_frames else 0,
            "animation_speed": self._animation_speed,
            "cache_enabled": self.enable_cache
        }

        if self._cache:
            stats.update(self._cache.get_cache_stats())

        return stats

    def clear_cache(self) -> None:
        """Clear all cached animation frames."""
        if self._cache:
            self._cache.clear()


class BatchColorApplicator:
    """
    Utility class for batched color operations for curses implementation.

    Provides optimized methods for preparing color data for curses styling.
    """

    @staticmethod
    def prepare_color_sequence_hex(colors: List[Tuple[int, int, int]],
                                 start_pos: int = 0) -> List[str]:
        """
        Convert RGB color sequence to hex strings for curses styling.

        Args:
            colors: List of RGB color tuples
            start_pos: Starting character position (for future use)

        Returns:
            List of hex color strings ready for terminal styling
        """
        from .generator import ColorGenerator
        return [ColorGenerator.rgb_to_hex(color) for color in colors]

    @staticmethod
    def prepare_color_map_hex(color_map: Dict[int, Tuple[int, int, int]]) -> Dict[int, str]:
        """
        Convert RGB color map to hex color map for curses styling.

        Args:
            color_map: Dictionary mapping character positions to RGB colors

        Returns:
            Dictionary mapping character positions to hex color strings
        """
        from .generator import ColorGenerator
        return {pos: ColorGenerator.rgb_to_hex(color) for pos, color in color_map.items()}