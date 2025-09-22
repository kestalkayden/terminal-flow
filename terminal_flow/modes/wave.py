"""
Wave animation mode for terminal-flow.

Provides horizontal wave animation with gradient support using the shared
animation framework.
"""

from ..animation_base import BaseAnimationMode


class WaveMode(BaseAnimationMode):
    """
    Wave animation mode with horizontal wave motion.

    Creates flowing color waves that move horizontally across the ASCII art
    with customizable speed and color schemes.
    """

    def __init__(self):
        super().__init__('wave')
        self.animation_offset = 0.0

    def initialize_mode_variables(self):
        """Initialize wave-specific animation variables."""
        self.animation_offset = 0.0

    def update_animation_state(self, animation_speed, update_interval):
        """Update wave animation offset."""
        self.animation_offset += animation_speed * update_interval * 0.5
        if self.animation_offset >= 1.0:
            self.animation_offset -= 1.0

    def draw_frame(self):
        """Draw wave animation frame."""
        max_rows, max_cols = self.stdscr.getmaxyx()

        # Draw animated text
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

                # Calculate color position for this character (per-character calculation)
                position = (char_idx / len(line) + self.animation_offset + line_idx * 0.1) % 1.0

                # Get color from pre-computed palette (optimized)
                attr = self.get_color_from_palette(position)

                try:
                    self.stdscr.addstr(row, col, char, attr)
                except:  # curses.error
                    pass  # Ignore screen boundary errors


# Legacy function wrapper for backward compatibility
def animate_text_wave(stdscr, text_files, animation_speed=1.0, update_interval=0.1,
                     cycle_interval=10.0, color_scheme=None, starting_file_index=0):
    """
    Main curses animation loop for wave rainbow text with file cycling.

    Legacy wrapper around WaveMode class for backward compatibility.
    """
    wave_mode = WaveMode()
    return wave_mode.run(stdscr, text_files, animation_speed, update_interval,
                        cycle_interval, color_scheme, starting_file_index)