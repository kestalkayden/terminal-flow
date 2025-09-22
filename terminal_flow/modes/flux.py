"""
Flux animation mode for terminal-flow.

Provides uniform color cycling animation where all characters cycle through
the same color spectrum using the shared animation framework.
"""

import curses
from ..animation_base import BaseAnimationMode


class FluxMode(BaseAnimationMode):
    """
    Flux animation mode with uniform color cycling.

    All characters cycle through the same color spectrum uniformly,
    creating a synchronized color-changing effect across the entire display.
    """

    def __init__(self):
        super().__init__('flux')
        self.flux_offset = 0.0

    def initialize_mode_variables(self):
        """Initialize flux-specific animation variables."""
        self.flux_offset = 0.0

    def update_animation_state(self, animation_speed, update_interval):
        """Update flux animation offset."""
        self.flux_offset += animation_speed * update_interval * 0.7  # Faster cycling through spectrum
        if self.flux_offset >= 1.0:
            self.flux_offset -= 1.0

    def draw_frame(self):
        """Draw flux animation frame with uniform color for all characters."""
        max_rows, max_cols = self.stdscr.getmaxyx()

        # Get single color for all characters from pre-computed palette (optimized)
        uniform_attr = self.get_color_from_palette(self.flux_offset) | curses.A_DIM

        # Draw animated text with uniform flux color
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

                try:
                    self.stdscr.addstr(row, col, char, uniform_attr)
                except:  # curses.error
                    pass  # Ignore screen boundary errors


# Legacy function wrapper for backward compatibility
def animate_text_flux(stdscr, text_files, animation_speed=1.0, update_interval=0.1,
                     cycle_interval=10.0, color_scheme=None, starting_file_index=0):
    """
    Main curses animation loop for flux rainbow text with file cycling.

    Legacy wrapper around FluxMode class for backward compatibility.
    """
    flux_mode = FluxMode()
    return flux_mode.run(stdscr, text_files, animation_speed, update_interval,
                        cycle_interval, color_scheme, starting_file_index)