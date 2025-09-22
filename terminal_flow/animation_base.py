"""
Base animation framework for terminal-flow animation modes.

Provides shared infrastructure for all animation modes including curses setup,
file cycling, input handling, and common state management.
"""

import curses
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple

from .text import TextLoader
from .colors.curses_adapter import get_default_adapter, get_default_sequence


class BaseAnimationMode(ABC):
    """
    Abstract base class for animation modes that handles shared infrastructure.

    Eliminates 400+ lines of duplicate code across animation modes by providing:
    - Curses setup and teardown
    - File cycling and state management
    - Input handling with mode switching
    - Color scheme management
    - Frame rate control
    - Screen management
    """

    def __init__(self, mode_name: str):
        """
        Initialize base animation mode.

        Args:
            mode_name: Name of this animation mode (e.g., 'wave', 'spin')
        """
        self.mode_name = mode_name

        # Animation modes list
        self.modes = ['wave', 'spin', 'pulse', 'flux', 'morph']

        # Color schemes list
        self.color_schemes = [None, 'red', 'blue', 'green', 'yellow', 'purple', 'cyan', 'gray', 'pink', 'orange']

        # State variables
        self.current_file_index = 0
        self.last_file_change = 0.0
        self.current_color_scheme = None
        self.current_color_index = 0
        self.current_mode_index = 0
        self.last_update_time = 0.0

        # Content state
        self.lines = []
        self.content_start = 0
        self.content_end = 0
        self.content_width = 0
        self.content_height = 0
        self.start_row = 0
        self.start_col = 0

        # Curses objects
        self.stdscr = None
        self.color_adapter = None
        self.sequence_generator = None
        self.loader = None

        # Performance optimization: Pre-computed color palette
        self.color_palette = []
        self.palette_size = 360  # High resolution color palette

    def setup_curses(self, stdscr):
        """Initialize curses settings and color adapters."""
        self.stdscr = stdscr

        # Curses setup
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input
        stdscr.timeout(1)  # Minimal timeout

        # Initialize color adapter
        self.color_adapter = get_default_adapter()
        self.sequence_generator = get_default_sequence()

        # Pre-compute color palette for performance
        self._generate_color_palette()

    def setup_state(self, text_files, color_scheme, starting_file_index):
        """Initialize animation state and load initial file."""
        if not text_files:
            self.stdscr.addstr(0, 0, "No text files found!")
            self.stdscr.refresh()
            self.stdscr.getch()
            return False

        # File cycling state
        self.current_file_index = starting_file_index
        self.last_file_change = time.time()
        self.loader = TextLoader("")  # Empty dir since we have file paths

        # Color scheme cycling state
        self.current_color_scheme = color_scheme if color_scheme in self.color_schemes else None
        self.current_color_index = self.color_schemes.index(self.current_color_scheme)

        # Mode cycling state
        self.current_mode_index = self.modes.index(self.mode_name)

        # Load initial file and calculate bounds
        self.load_file(text_files)

        self.last_update_time = time.time()

        return True

    def load_file(self, text_files):
        """Load current file and calculate content bounds."""
        current_content = self.loader.load_file(text_files[self.current_file_index])
        self.lines = current_content.split('\n')

        self.calculate_content_bounds()

    def calculate_content_bounds(self):
        """Calculate content bounds and center ASCII art on screen."""
        max_rows, max_cols = self.stdscr.getmaxyx()

        # Calculate the actual content bounds of ASCII art, excluding empty lines
        if not self.lines:
            self.content_start, self.content_end, self.content_width = 0, 0, 0
            self.content_height = 0
            self.start_row = 0
            self.start_col = 0
            return

        # Find first and last non-empty lines
        start_line = 0
        end_line = len(self.lines) - 1

        for i, line in enumerate(self.lines):
            if line.strip():
                start_line = i
                break

        for i in range(len(self.lines) - 1, -1, -1):
            if self.lines[i].strip():
                end_line = i
                break

        # Find maximum width of content
        max_width = 0
        for i in range(start_line, end_line + 1):
            max_width = max(max_width, len(self.lines[i]))

        self.content_start = start_line
        self.content_end = end_line
        self.content_width = max_width
        self.content_height = self.content_end - self.content_start + 1
        self.start_row = max(0, (max_rows - self.content_height) // 2) - self.content_start
        self.start_col = max(0, (max_cols - self.content_width) // 2)

    def handle_input(self, text_files) -> Optional[Dict[str, Any]]:
        """
        Handle common input events.

        Returns:
            Dict with mode switch info if mode switch requested, None otherwise
        """
        key = self.stdscr.getch()

        if key == curses.KEY_RESIZE:
            self.calculate_content_bounds()
            self.on_resize()
            self.stdscr.clear()

        elif key == ord('q') or key == ord('Q') or key == 27:  # ESC
            return {}  # Signal exit

        elif key == curses.KEY_RIGHT:  # Next file manually
            self.current_file_index = (self.current_file_index + 1) % len(text_files)
            self.load_file(text_files)
            self.on_file_change()
            self.last_file_change = time.time()
            self.stdscr.clear()

        elif key == curses.KEY_LEFT:  # Previous file manually
            self.current_file_index = (self.current_file_index - 1) % len(text_files)
            self.load_file(text_files)
            self.on_file_change()
            self.last_file_change = time.time()
            self.stdscr.clear()

        elif key == ord('c') or key == ord('C'):  # Cycle color schemes
            self.current_color_index = (self.current_color_index + 1) % len(self.color_schemes)
            self.current_color_scheme = self.color_schemes[self.current_color_index]
            self.on_color_change()
            self.stdscr.clear()

        elif key == ord('m') or key == ord('M'):  # Switch animation mode
            self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
            next_mode = self.modes[self.current_mode_index]
            return {
                'next_mode': next_mode,
                'current_file_index': self.current_file_index,
                'current_color_scheme': self.current_color_scheme
            }

        return None

    def check_auto_file_cycling(self, text_files, cycle_interval):
        """Handle automatic file cycling if enabled."""
        current_time = time.time()
        if cycle_interval > 0 and current_time - self.last_file_change >= cycle_interval and len(text_files) > 1:
            self.current_file_index = (self.current_file_index + 1) % len(text_files)
            self.load_file(text_files)
            self.on_file_change()
            self.last_file_change = current_time
            self.stdscr.clear()

    def control_frame_rate(self, update_interval):
        """Control frame rate timing."""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        if delta_time < update_interval:
            time.sleep(update_interval - delta_time)
        self.last_update_time = time.time()

    def refresh_screen(self):
        """Refresh screen with double buffering."""
        self.stdscr.noutrefresh()
        curses.doupdate()

    def clear_screen(self):
        """Clear screen (erase is gentler than clear)."""
        self.stdscr.erase()

    # Abstract methods that each animation mode must implement

    @abstractmethod
    def initialize_mode_variables(self):
        """Initialize mode-specific variables (e.g., animation_offset, rotation_angle)."""
        pass

    @abstractmethod
    def update_animation_state(self, animation_speed, update_interval):
        """Update mode-specific animation state each frame."""
        pass

    @abstractmethod
    def draw_frame(self):
        """Draw the current animation frame."""
        pass

    # Optional callback methods for mode-specific handling

    def on_resize(self):
        """Called when terminal is resized. Override for mode-specific handling."""
        pass

    def on_file_change(self):
        """Called when file changes. Override for mode-specific handling."""
        pass

    def on_color_change(self):
        """Called when color scheme changes. Override for mode-specific handling."""
        self._generate_color_palette()

    def _generate_color_palette(self):
        """Pre-compute color palette for performance optimization."""
        if not self.sequence_generator:
            return

        # Generate high-resolution color palette
        color_attrs = self.sequence_generator.generate_sequence(
            self.palette_size,
            offset=0.0,
            bold=True,
            color_scheme=self.current_color_scheme
        )
        self.color_palette = color_attrs

    def get_color_from_palette(self, position: float) -> int:
        """
        Get color attribute from pre-computed palette.

        Args:
            position: Color position from 0.0 to 1.0

        Returns:
            Curses color attribute
        """
        if not self.color_palette:
            return 1  # curses.A_BOLD fallback

        # Map position to palette index
        index = int(position * (len(self.color_palette) - 1)) % len(self.color_palette)
        return self.color_palette[index]

    # Main animation loop

    def run(self, stdscr, text_files, animation_speed=1.0, update_interval=0.1,
            cycle_interval=10.0, color_scheme=None, starting_file_index=0):
        """
        Main animation loop that handles all shared infrastructure.

        Args:
            stdscr: curses screen object
            text_files: List of text file paths to cycle through
            animation_speed: Speed multiplier for animation
            update_interval: Time between frame updates
            cycle_interval: Time between file switches in seconds
            color_scheme: Initial color scheme
            starting_file_index: Starting file index

        Returns:
            Dict with next mode info if mode switch requested, None for normal exit
        """
        # Setup
        self.setup_curses(stdscr)

        if not self.setup_state(text_files, color_scheme, starting_file_index):
            return None

        self.initialize_mode_variables()

        # Main animation loop
        while True:
            # Handle input
            input_result = self.handle_input(text_files)
            if input_result is not None:
                if input_result:  # Mode switch requested
                    input_result.update({
                        'animation_speed': animation_speed,
                        'update_interval': update_interval,
                        'cycle_interval': cycle_interval
                    })
                    return input_result
                else:  # Exit requested
                    break

            # Check for automatic file cycling
            self.check_auto_file_cycling(text_files, cycle_interval)

            # Frame rate control
            self.control_frame_rate(update_interval)

            # Update animation state
            self.update_animation_state(animation_speed, update_interval)

            # Clear and draw frame
            self.clear_screen()
            self.draw_frame()
            self.refresh_screen()

        return None