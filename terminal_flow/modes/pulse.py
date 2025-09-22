"""
Pulse animation mode for terminal-flow.

Provides ripple pulse animation with distance-based coloring using the shared
animation framework.
"""

import math
from ..animation_base import BaseAnimationMode


class PulseMode(BaseAnimationMode):
    """
    Pulse animation mode with ripple effects from center.

    Colors pulse outward from the center of the ASCII art in ripple effects,
    creating waves that radiate from the center point.
    """

    def __init__(self):
        super().__init__('pulse')
        self.pulse_offset = 0.0
        self.center_row = 0
        self.center_col = 0

    def initialize_mode_variables(self):
        """Initialize pulse-specific animation variables."""
        self.pulse_offset = 0.0
        self.center_row = self.start_row + self.content_height // 2
        self.center_col = self.start_col + self.content_width // 2

    def update_animation_state(self, animation_speed, update_interval):
        """Update pulse animation offset."""
        self.pulse_offset += animation_speed * update_interval * 2.0  # Pulse speed
        if self.pulse_offset >= 1.0:
            self.pulse_offset -= 1.0

    def on_resize(self):
        """Update center point when terminal is resized."""
        self.center_row = self.start_row + self.content_height // 2
        self.center_col = self.start_col + self.content_width // 2

    def on_file_change(self):
        """Update center point when file changes."""
        self.center_row = self.start_row + self.content_height // 2
        self.center_col = self.start_col + self.content_width // 2

    def draw_frame(self):
        """Draw pulse animation frame with distance-based ripples."""
        max_rows, max_cols = self.stdscr.getmaxyx()

        # Draw animated text with pulse colors
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

                # Calculate distance from center
                dy = row - self.center_row
                dx = col - self.center_col
                distance = math.sqrt(dx * dx + dy * dy)

                # Normalize distance to 0-1 range and subtract pulse offset for outward pulse
                max_distance = math.sqrt(self.content_width * self.content_width + self.content_height * self.content_height) / 2
                normalized_distance = distance / max_distance if max_distance > 0 else 0
                color_position = (normalized_distance - self.pulse_offset) % 1.0

                # Get color from pre-computed palette (optimized)
                attr = self.get_color_from_palette(color_position)

                try:
                    self.stdscr.addstr(row, col, char, attr)
                except:  # curses.error
                    pass  # Ignore screen boundary errors


# Legacy function wrapper for backward compatibility
def animate_text_pulse(stdscr, text_files, animation_speed=1.0, update_interval=0.1,
                      cycle_interval=10.0, color_scheme=None, starting_file_index=0):
    """
    Main curses animation loop for pulse rainbow text with file cycling.

    Legacy wrapper around PulseMode class for backward compatibility.
    """
    pulse_mode = PulseMode()
    return pulse_mode.run(stdscr, text_files, animation_speed, update_interval,
                         cycle_interval, color_scheme, starting_file_index)