"""
Spin animation mode for terminal-flow.

Provides polar coordinate rotation animation using the shared
animation framework.
"""

import math
from ..animation_base import BaseAnimationMode


class SpinMode(BaseAnimationMode):
    """
    Spin animation mode with polar coordinate rotation.

    Colors rotate around the center point of the ASCII art using polar coordinates
    for smooth circular color transitions.
    """

    def __init__(self):
        super().__init__('spin')
        self.rotation_angle = 0.0
        self.center_row = 0
        self.center_col = 0

    def initialize_mode_variables(self):
        """Initialize spin-specific animation variables."""
        self.rotation_angle = 0.0
        self.center_row = self.start_row + self.content_height // 2
        self.center_col = self.start_col + self.content_width // 2

    def update_animation_state(self, animation_speed, update_interval):
        """Update rotation angle."""
        self.rotation_angle += animation_speed * update_interval * math.pi  # Rotate in radians
        if self.rotation_angle >= 2 * math.pi:
            self.rotation_angle -= 2 * math.pi

    def on_resize(self):
        """Update center point when terminal is resized."""
        self.center_row = self.start_row + self.content_height // 2
        self.center_col = self.start_col + self.content_width // 2

    def on_file_change(self):
        """Update center point when file changes."""
        self.center_row = self.start_row + self.content_height // 2
        self.center_col = self.start_col + self.content_width // 2

    def draw_frame(self):
        """Draw spin animation frame with polar coordinates."""
        max_rows, max_cols = self.stdscr.getmaxyx()

        # Draw animated text with spin colors
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

                # Calculate polar coordinates from center
                dy = row - self.center_row
                dx = col - self.center_col

                # Calculate angle from center (0 to 2π)
                angle = math.atan2(dy, dx)

                # Normalize angle to 0-1 range and add rotation
                color_position = ((angle + self.rotation_angle) / (2 * math.pi)) % 1.0

                # Get color from pre-computed palette (optimized)
                attr = self.get_color_from_palette(color_position)

                try:
                    self.stdscr.addstr(row, col, char, attr)
                except:  # curses.error
                    pass  # Ignore screen boundary errors


# Legacy function wrapper for backward compatibility
def animate_text_spin(stdscr, text_files, animation_speed=1.0, update_interval=0.1,
                     cycle_interval=10.0, color_scheme=None, starting_file_index=0):
    """
    Main curses animation loop for spin rainbow text with file cycling.

    Legacy wrapper around SpinMode class for backward compatibility.
    """
    spin_mode = SpinMode()
    return spin_mode.run(stdscr, text_files, animation_speed, update_interval,
                        cycle_interval, color_scheme, starting_file_index)