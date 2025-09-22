"""
Morph animation mode for terminal-flow.

Provides 3D wave field simulation with physics-like wave propagation using the shared
animation framework. Colors exhibit organic movement through complex mathematical
wave interference patterns.
"""

import time
from ..animation_base import BaseAnimationMode
from ..colors.generator import ColorGenerator


class WaveField:
    """
    2D wave field for smooth wave propagation animation.

    Creates coherent color regions that flow across ASCII art like ripples
    in water, replacing random per-character physics with spatial waves.
    """

    def __init__(self, rows, cols, max_tier):
        """
        Initialize wave field grid.

        Args:
            rows: Number of text rows
            cols: Maximum number of columns
            max_tier: Maximum wave height (maps to gradient length - 1)
        """
        self.rows = rows
        self.cols = cols
        self.max_tier = max_tier
        self.median_height = max_tier // 2

        # Wave height field (current wave heights)
        self.heights = [[float(self.median_height) for _ in range(cols)] for _ in range(rows)]

        # Pre-compute optimization constants
        self.center_row = rows // 2
        self.center_col = cols // 2

        # Pre-compute distance grid for radial waves (optimization)
        self.distance_grid = []
        for r in range(rows):
            row_distances = []
            for c in range(cols):
                import math
                distance = math.sqrt((r - self.center_row) ** 2 + (c - self.center_col) ** 2)
                row_distances.append(distance)
            self.distance_grid.append(row_distances)

    def get_height(self, row, col):
        """Get wave height at position (with bounds checking)."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.heights[row][col]
        return self.median_height

    def set_height(self, row, col, height):
        """Set wave height at position (with bounds checking and clamping)."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.heights[row][col] = max(0.0, min(float(self.max_tier), height))

    def get_tier(self, row, col):
        """Get color tier for position (integer version of height)."""
        height = self.get_height(row, col)
        return int(round(height))

    def propagate_waves(self, animation_speed=1.0, time_offset=0.0, content_bounds=None):
        """
        Generate continuous 3D wave field like a sound visualizer viewed from above.

        Creates overlapping mathematical wave functions that flow across the entire
        ASCII art continuously, like looking down at an undulating 3D surface.

        Args:
            animation_speed: Speed multiplier for wave animation
            time_offset: Time offset for wave calculations
            content_bounds: (start_row, end_row, line_lengths) for spatial optimization
        """
        import math

        # Spatial optimization: only calculate for content area if bounds provided
        if content_bounds:
            start_row, end_row, line_lengths = content_bounds
            row_range = range(start_row, min(end_row + 1, self.rows))
        else:
            row_range = range(self.rows)
            line_lengths = [self.cols] * self.rows

        # Multiple overlapping wave functions for complex interference patterns
        for r in row_range:
            # Optimize column range based on actual line length
            if content_bounds and r - (content_bounds[0] if content_bounds else 0) < len(line_lengths):
                col_limit = min(line_lengths[r - (content_bounds[0] if content_bounds else 0)], self.cols)
            else:
                col_limit = self.cols

            for c in range(col_limit):
                # Initialize at median
                total_height = self.median_height

                # Wave 1: Horizontal sine wave flowing right
                wave1 = math.sin((c * 0.3 + time_offset * 2.0)) * (self.max_tier * 0.15)

                # Wave 2: Vertical sine wave flowing down
                wave2 = math.sin((r * 0.25 + time_offset * 1.5)) * (self.max_tier * 0.12)

                # Wave 3: Diagonal wave flowing diagonally
                wave3 = math.sin((r + c) * 0.2 + time_offset * 1.8) * (self.max_tier * 0.1)

                # Wave 4: Radial wave from center (optimized with pre-computed distance)
                distance_from_center = self.distance_grid[r][c]
                wave4 = math.sin(distance_from_center * 0.4 - time_offset * 2.5) * (self.max_tier * 0.08)

                # Wave 5: Fast ripple texture
                wave5 = math.sin((r * 0.8 + c * 0.6) + time_offset * 4.0) * (self.max_tier * 0.05)

                # Combine all waves with interference
                total_height += wave1 + wave2 + wave3 + wave4 + wave5

                # Add some higher frequency detail
                detail = math.sin(r * 1.2 + c * 1.1 + time_offset * 3.0) * (self.max_tier * 0.03)
                total_height += detail

                # Clamp to valid range
                self.heights[r][c] = max(0.0, min(float(self.max_tier), total_height))


class MorphMode(BaseAnimationMode):
    """
    Morph animation mode with 3D wave field simulation.

    Colors exhibit physics-like behavior, starting at median values and
    transitioning with resistance toward extremes, creating organic movement
    through complex mathematical wave interference patterns.
    """

    def __init__(self):
        super().__init__('morph')
        self.wave_field = None
        self.gradient_length = 50  # Number of color tiers
        self.base_gradient = []
        self.cached_gradient_attrs = []  # Pre-computed curses attributes

    def initialize_mode_variables(self):
        """Initialize morph-specific animation variables."""
        # Generate base color gradient for current scheme
        if self.current_color_scheme:
            self.base_gradient = ColorGenerator.generate_monochromatic_gradient(
                self.current_color_scheme, self.gradient_length)
        else:
            self.base_gradient = ColorGenerator.generate_rainbow_sequence(
                self.gradient_length, saturation=0.75, value=0.9)

        # Pre-compute gradient colors to curses attributes for performance
        self._precompute_gradient_attrs()

        # Initialize wave field
        self.wave_field = WaveField(len(self.lines), self.content_width, self.gradient_length - 1)

    def update_animation_state(self, animation_speed, update_interval):
        """Update wave field propagation simulation."""
        if self.wave_field:
            # Wave field propagation simulation with continuous time
            current_time = time.time()

            # Calculate content bounds for spatial optimization
            content_bounds = self._get_content_bounds()

            self.wave_field.propagate_waves(animation_speed, current_time * animation_speed, content_bounds)

    def on_resize(self):
        """Reinitialize wave field when terminal is resized."""
        if self.wave_field:
            self.wave_field = WaveField(len(self.lines), self.content_width, self.gradient_length - 1)

    def on_file_change(self):
        """Reinitialize wave field when file changes."""
        if self.wave_field:
            self.wave_field = WaveField(len(self.lines), self.content_width, self.gradient_length - 1)

    def on_color_change(self):
        """Regenerate base gradient when color scheme changes."""
        if self.current_color_scheme:
            self.base_gradient = ColorGenerator.generate_monochromatic_gradient(
                self.current_color_scheme, self.gradient_length)
        else:
            self.base_gradient = ColorGenerator.generate_rainbow_sequence(
                self.gradient_length, saturation=0.75, value=0.9)

        # Re-compute cached gradient attributes
        self._precompute_gradient_attrs()

    def _precompute_gradient_attrs(self):
        """Pre-compute gradient colors to curses attributes for performance."""
        # Skip if color adapter not initialized yet (during mode switching)
        if not self.color_adapter:
            return

        self.cached_gradient_attrs = []
        for rgb_color in self.base_gradient:
            attr = self.color_adapter.get_color_attr(rgb_color, bold=True)
            self.cached_gradient_attrs.append(attr)

    def _get_content_bounds(self):
        """Calculate content bounds for spatial optimization."""
        line_lengths = []
        for line in self.lines:
            line_lengths.append(len(line))
        return (self.content_start, self.content_end, line_lengths)

    def draw_frame(self):
        """Draw morph animation frame with wave field simulation."""
        max_rows, max_cols = self.stdscr.getmaxyx()

        # Draw animated text with wave field colors
        for line_idx, line in enumerate(self.lines):
            if line_idx + self.start_row >= max_rows:
                break

            for char_idx, char in enumerate(line):
                # Skip whitespace characters entirely for performance
                if not char.strip():
                    continue

                col = self.start_col + char_idx
                row = self.start_row + line_idx

                if col >= max_cols or row >= max_rows:
                    continue

                # Get tier for this character and map to color
                if self.wave_field and char_idx < self.content_width:
                    tier = self.wave_field.get_tier(line_idx, char_idx)
                    if tier < len(self.cached_gradient_attrs):
                        # Use pre-computed color attribute for performance
                        attr = self.cached_gradient_attrs[tier]

                        try:
                            self.stdscr.addstr(row, col, char, attr)
                        except:  # curses.error
                            pass  # Ignore screen boundary errors
                    else:
                        # Fallback for invalid tier
                        try:
                            self.stdscr.addstr(row, col, char)
                        except:  # curses.error
                            pass
                else:
                    # Fallback if wave field not available
                    try:
                        self.stdscr.addstr(row, col, char)
                    except:  # curses.error
                        pass


# Legacy function wrapper for backward compatibility
def animate_text_morph(stdscr, text_files, animation_speed=1.0, update_interval=0.1,
                      cycle_interval=10.0, color_scheme=None, starting_file_index=0):
    """
    Main curses animation loop for morph rainbow text with file cycling.

    Legacy wrapper around MorphMode class for backward compatibility.
    """
    morph_mode = MorphMode()
    return morph_mode.run(stdscr, text_files, animation_speed, update_interval,
                         cycle_interval, color_scheme, starting_file_index)