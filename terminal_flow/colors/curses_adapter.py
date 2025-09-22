"""
Curses color adapter for terminal-flow color system.

Provides efficient mapping from RGB colors to curses color pairs
with optimized caching and terminal compatibility.
"""

import curses
import time
from typing import Dict, Tuple, List
from .generator import ColorGenerator


class CursesColorAdapter:
    """
    Adapter for converting RGB colors to curses color pairs.

    Provides efficient color mapping with caching and handles
    terminal color limitations gracefully.
    """

    def __init__(self, max_rgb_cache_size: int = 500):
        """Initialize curses color adapter."""
        self.color_pairs_initialized = False
        self.has_colors = False
        self.supports_256_colors = False
        self.rgb_to_pair_cache: Dict[Tuple[int, int, int], int] = {}
        self.rgb_cache_access_times: Dict[Tuple[int, int, int], float] = {}
        self.max_rgb_cache_size = max_rgb_cache_size
        self.max_pairs = 8  # Conservative for compatibility

    def _evict_oldest_rgb_cache(self) -> None:
        """Remove least recently used RGB cache entry."""
        if not self.rgb_cache_access_times:
            return

        oldest_rgb = min(self.rgb_cache_access_times.keys(),
                        key=lambda k: self.rgb_cache_access_times[k])
        del self.rgb_to_pair_cache[oldest_rgb]
        del self.rgb_cache_access_times[oldest_rgb]

        # Standard curses colors for mapping
        self.standard_colors = [
            (255, 0, 0),    # Red
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 255, 255),  # Cyan
            (0, 0, 255),    # Blue
            (255, 0, 255),  # Magenta
            (255, 255, 255), # White
            (128, 128, 128), # Gray
        ]

        self.curses_colors = [
            curses.COLOR_RED,
            curses.COLOR_YELLOW,
            curses.COLOR_GREEN,
            curses.COLOR_CYAN,
            curses.COLOR_BLUE,
            curses.COLOR_MAGENTA,
            curses.COLOR_WHITE,
            curses.COLOR_WHITE,  # Fallback for gray
        ]

    def initialize_colors(self) -> bool:
        """
        Initialize curses color pairs.

        Returns:
            True if colors are supported, False otherwise
        """
        if self.color_pairs_initialized:
            return self.has_colors

        if not curses.has_colors():
            self.has_colors = False
            self.color_pairs_initialized = True
            return False

        curses.start_color()

        # Detect 256-color support
        self.supports_256_colors = curses.COLORS >= 256
        if self.supports_256_colors:
            self.max_pairs = min(256, curses.COLOR_PAIRS)  # Use 256-color range
        else:
            self.max_pairs = 8  # Conservative for 8-color terminals

        # Use default background if supported
        if curses.can_change_color():
            curses.use_default_colors()
            bg = -1
        else:
            bg = curses.COLOR_BLACK

        # Initialize color pairs
        if self.supports_256_colors:
            # For 256-color terminals, initialize with standard colors but allow more
            for i in range(min(256, self.max_pairs)):
                if i == 0:
                    continue  # Skip color pair 0
                curses.init_pair(i, i % curses.COLORS, bg)
        else:
            # Initialize standard 8-color pairs for fallback
            for i, color in enumerate(self.curses_colors):
                if i < 8:
                    curses.init_pair(i + 1, color, bg)

        self.has_colors = True
        self.color_pairs_initialized = True
        return True

    def rgb_distance(self, rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
        """
        Calculate Euclidean distance between two RGB colors.

        Args:
            rgb1: First RGB color tuple
            rgb2: Second RGB color tuple

        Returns:
            Distance between colors
        """
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5

    def rgb_to_color_pair(self, rgb: Tuple[int, int, int]) -> int:
        """
        Convert RGB color to curses color pair number.

        Args:
            rgb: RGB color tuple (r, g, b) with values 0-255

        Returns:
            Curses color pair number (1-8)
        """
        # Check cache first
        if rgb in self.rgb_to_pair_cache:
            self.rgb_cache_access_times[rgb] = time.time()
            return self.rgb_to_pair_cache[rgb]

        if not self.has_colors:
            return 0  # No color support

        if self.supports_256_colors:
            # Use 256-color mapping
            r, g, b = rgb
            # Map to 6x6x6 color cube (colors 16-231)
            r6 = min(5, r * 6 // 256)
            g6 = min(5, g * 6 // 256)
            b6 = min(5, b * 6 // 256)
            color_256 = 16 + (36 * r6) + (6 * g6) + b6
            color_pair = min(color_256, self.max_pairs - 1)
        else:
            # Find closest standard color for 8-color terminals
            min_distance = float('inf')
            closest_index = 0

            for i, standard_color in enumerate(self.standard_colors):
                distance = self.rgb_distance(rgb, standard_color)
                if distance < min_distance:
                    min_distance = distance
                    closest_index = i

            color_pair = closest_index + 1

        # Evict oldest entries if cache is full
        if len(self.rgb_to_pair_cache) >= self.max_rgb_cache_size:
            self._evict_oldest_rgb_cache()

        # Cache result
        self.rgb_to_pair_cache[rgb] = color_pair
        self.rgb_cache_access_times[rgb] = time.time()
        return color_pair

    def get_color_attr(self, rgb: Tuple[int, int, int], bold: bool = True) -> int:
        """
        Get curses color attribute for RGB color.

        Args:
            rgb: RGB color tuple
            bold: Whether to apply bold attribute

        Returns:
            Curses color attribute for use with addstr()
        """
        if not self.has_colors:
            return curses.A_BOLD if bold else 0

        color_pair = self.rgb_to_color_pair(rgb)
        attr = curses.color_pair(color_pair)

        if bold:
            attr |= curses.A_BOLD

        return attr


class CursesRainbowSequence:
    """
    Optimized rainbow color sequence generator for curses.

    Pre-calculates color sequences to minimize per-frame overhead
    during animation loops.
    """

    def __init__(self, adapter: CursesColorAdapter):
        """
        Initialize rainbow sequence generator.

        Args:
            adapter: CursesColorAdapter instance
        """
        self.adapter = adapter
        self.cached_sequences: Dict[str, List[int]] = {}

    def generate_sequence(self, length: int, offset: float = 0.0,
                         bold: bool = True, color_scheme: str = None) -> List[int]:
        """
        Generate curses color attribute sequence for rainbow or monochromatic animation.

        Args:
            length: Number of colors in sequence
            offset: Animation offset (0.0-1.0)
            bold: Whether to apply bold attributes
            color_scheme: Color scheme name ('red', 'blue', etc.) or None for rainbow

        Returns:
            List of curses color attributes
        """
        # Create cache key
        cache_key = f"{length}_{offset:.3f}_{bold}_{color_scheme or 'rainbow'}"

        if cache_key in self.cached_sequences:
            return self.cached_sequences[cache_key]

        # Generate RGB sequence based on color scheme
        if color_scheme:
            rgb_sequence = ColorGenerator.generate_monochromatic_gradient(color_scheme, length, offset=offset)
        else:
            rgb_sequence = ColorGenerator.generate_rainbow_sequence(length, saturation=0.75, value=0.9, offset=offset)

        # Convert to curses attributes
        attr_sequence = []
        for rgb in rgb_sequence:
            attr = self.adapter.get_color_attr(rgb, bold=bold)
            attr_sequence.append(attr)

        # Cache result (limit cache size)
        if len(self.cached_sequences) < 100:
            self.cached_sequences[cache_key] = attr_sequence

        return attr_sequence

    def clear_cache(self):
        """Clear cached color sequences."""
        self.cached_sequences.clear()


def create_curses_adapter() -> CursesColorAdapter:
    """
    Factory function to create and initialize curses color adapter.

    Returns:
        Initialized CursesColorAdapter instance
    """
    adapter = CursesColorAdapter()
    adapter.initialize_colors()
    return adapter


# Module-level convenience instances
_default_adapter = None
_default_sequence = None


def get_default_adapter() -> CursesColorAdapter:
    """Get default curses color adapter (singleton)."""
    global _default_adapter
    if _default_adapter is None:
        _default_adapter = create_curses_adapter()
    return _default_adapter


def get_default_sequence() -> CursesRainbowSequence:
    """Get default rainbow sequence generator (singleton)."""
    global _default_sequence
    if _default_sequence is None:
        _default_sequence = CursesRainbowSequence(get_default_adapter())
    return _default_sequence