#!/usr/bin/env python3
"""
Pure curses main entry point for terminal-flow.

Provides high-performance ambient display animation using curses library
with zero external dependencies and immediate startup. Features include
five animation modes (wave, spin, pulse, flux, morph), interactive
runtime controls, and advanced wave field simulation for organic motion.

Key classes:
    - WaveField: 2D wave field simulation for smooth wave propagation

Key functions:
    - animate_text_wave: Horizontal wave animation with gradient support
    - animate_text_spin: Polar coordinate rotation animation
    - animate_text_pulse: Ripple effects pulsing outward from center
    - animate_text_flux: Uniform color cycling across all characters
    - animate_text_morph: 3D wave field with mathematical wave generation
    - calculate_content_bounds: ASCII art centering with content detection

Integration points:
    - Uses TextLoader for file management and cycling
    - Uses ColorGenerator for monochromatic gradients and rainbow sequences
    - Uses CursesColorAdapter for RGB to terminal color mapping

See Also:
    - colors.generator: For wave field color generation algorithms
    - text.loader: For ASCII art file loading and management
"""

import curses
import time
import random
import argparse
import sys
import os
import math
from pathlib import Path

from .text import TextLoader
from .colors.generator import ColorGenerator
from .colors.curses_adapter import get_default_adapter, get_default_sequence
from .modes.wave import animate_text_wave
from .modes.spin import animate_text_spin
from .modes.pulse import animate_text_pulse
from .modes.flux import animate_text_flux
from .modes.morph import animate_text_morph




def calculate_content_bounds(lines):
    """
    Calculate the actual content bounds of ASCII art, excluding empty lines.

    Returns:
        (start_line, end_line, max_width) - bounds of actual content
    """
    if not lines:
        return 0, 0, 0

    # Find first and last non-empty lines
    start_line = 0
    end_line = len(lines) - 1

    for i, line in enumerate(lines):
        if line.strip():
            start_line = i
            break

    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            end_line = i
            break

    # Find maximum width of content
    max_width = 0
    for i in range(start_line, end_line + 1):
        max_width = max(max_width, len(lines[i]))

    return start_line, end_line, max_width



def animate_text_spin(stdscr, text_files, animation_speed=1.0, update_interval=0.1, cycle_interval=10.0, color_scheme=None, starting_file_index=0):
    """
    Main curses animation loop for spin rainbow text with file cycling.

    Colors rotate around the center point of the ASCII art using polar coordinates.

    Args:
        stdscr: curses screen object
        text_files: List of text file paths to cycle through
        animation_speed: Speed multiplier for animation
        update_interval: Time between frame updates
        cycle_interval: Time between file switches in seconds

    Returns:
        Dict with next mode info if mode switch requested, None for normal exit
    """
    # Curses setup
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.timeout(1)  # Minimal timeout

    # Initialize color adapter
    color_adapter = get_default_adapter()
    sequence_generator = get_default_sequence()

    if not text_files:
        stdscr.addstr(0, 0, "No text files found!")
        stdscr.refresh()
        stdscr.getch()
        return None

    # File cycling state
    current_file_index = starting_file_index
    last_file_change = time.time()
    loader = TextLoader("")  # Empty dir since we have file paths

    # Color scheme cycling state
    color_schemes = [None, 'red', 'blue', 'green', 'yellow', 'purple', 'cyan', 'gray', 'pink', 'orange']
    current_color_scheme = color_scheme if color_scheme in color_schemes else None
    current_color_index = color_schemes.index(current_color_scheme)

    # Mode cycling state
    modes = ['wave', 'spin', 'pulse', 'flux', 'morph']
    current_mode = 'spin'  # This function is spin
    current_mode_index = modes.index(current_mode)

    # Load initial file
    current_content = loader.load_file(text_files[current_file_index])
    lines = current_content.split('\n')
    max_rows, max_cols = stdscr.getmaxyx()

    # Calculate content bounds and center properly
    content_start, content_end, content_width = calculate_content_bounds(lines)
    content_height = content_end - content_start + 1
    start_row = max(0, (max_rows - content_height) // 2) - content_start
    start_col = max(0, (max_cols - content_width) // 2)

    # Calculate center point for rotation
    center_row = start_row + content_height // 2
    center_col = start_col + content_width // 2

    last_update_time = time.time()
    rotation_angle = 0.0

    while True:
        # Handle input
        key = stdscr.getch()
        if key == curses.KEY_RESIZE:
            max_rows, max_cols = stdscr.getmaxyx()
            content_start, content_end, content_width = calculate_content_bounds(lines)
            content_height = content_end - content_start + 1
            start_row = max(0, (max_rows - content_height) // 2) - content_start
            start_col = max(0, (max_cols - content_width) // 2)
            center_row = start_row + content_height // 2
            center_col = start_col + content_width // 2
            stdscr.clear()
        elif key == ord('q') or key == ord('Q') or key == 27:  # ESC
            break
        elif key == curses.KEY_RIGHT:  # Next file manually
            current_file_index = (current_file_index + 1) % len(text_files)
            current_content = loader.load_file(text_files[current_file_index])
            lines = current_content.split('\n')
            content_start, content_end, content_width = calculate_content_bounds(lines)
            content_height = content_end - content_start + 1
            start_row = max(0, (max_rows - content_height) // 2) - content_start
            start_col = max(0, (max_cols - content_width) // 2)
            center_row = start_row + content_height // 2
            center_col = start_col + content_width // 2
            last_file_change = time.time()
            stdscr.clear()
        elif key == curses.KEY_LEFT:  # Previous file manually
            current_file_index = (current_file_index - 1) % len(text_files)
            current_content = loader.load_file(text_files[current_file_index])
            lines = current_content.split('\n')
            content_start, content_end, content_width = calculate_content_bounds(lines)
            content_height = content_end - content_start + 1
            start_row = max(0, (max_rows - content_height) // 2) - content_start
            start_col = max(0, (max_cols - content_width) // 2)
            last_file_change = time.time()
            stdscr.clear()
        elif key == ord('c') or key == ord('C'):  # Cycle color schemes
            current_color_index = (current_color_index + 1) % len(color_schemes)
            current_color_scheme = color_schemes[current_color_index]
            stdscr.clear()
        elif key == ord('m') or key == ord('M'):  # Switch animation mode
            current_mode_index = (current_mode_index + 1) % len(modes)
            next_mode = modes[current_mode_index]
            return {
                'next_mode': next_mode,
                'current_file_index': current_file_index,
                'current_color_scheme': current_color_scheme,
                'animation_speed': animation_speed,
                'update_interval': update_interval,
                'cycle_interval': cycle_interval
            }

        # Check for automatic file cycling
        current_time = time.time()
        if cycle_interval > 0 and current_time - last_file_change >= cycle_interval and len(text_files) > 1:
            current_file_index = (current_file_index + 1) % len(text_files)
            current_content = loader.load_file(text_files[current_file_index])
            lines = current_content.split('\n')
            content_start, content_end, content_width = calculate_content_bounds(lines)
            content_height = content_end - content_start + 1
            start_row = max(0, (max_rows - content_height) // 2) - content_start
            start_col = max(0, (max_cols - content_width) // 2)
            center_row = start_row + content_height // 2
            center_col = start_col + content_width // 2
            last_file_change = current_time
            stdscr.clear()

        # Frame rate control
        current_time = time.time()
        delta_time = current_time - last_update_time
        if delta_time < update_interval:
            time.sleep(update_interval - delta_time)
        last_update_time = time.time()

        # Update rotation angle
        rotation_angle += animation_speed * update_interval * math.pi  # Rotate in radians
        if rotation_angle >= 2 * math.pi:
            rotation_angle -= 2 * math.pi

        # Clear screen (erase is gentler than clear)
        stdscr.erase()

        # Draw animated text with spin colors
        for line_idx, line in enumerate(lines):
            if line_idx + start_row >= max_rows:
                break

            for char_idx, char in enumerate(line):
                col = start_col + char_idx
                row = start_row + line_idx

                if col >= max_cols or row >= max_rows:
                    continue

                if char.strip():  # Only color non-whitespace
                    # Calculate polar coordinates from center
                    dy = row - center_row
                    dx = col - center_col

                    # Calculate angle from center (0 to 2π)
                    angle = math.atan2(dy, dx)

                    # Normalize angle to 0-1 range and add rotation
                    color_position = ((angle + rotation_angle) / (2 * math.pi)) % 1.0

                    # Generate color sequence for this character
                    color_attrs = sequence_generator.generate_sequence(
                        1,  # Single character
                        offset=color_position,
                        bold=True,
                        color_scheme=current_color_scheme
                    )

                    attr = color_attrs[0] if color_attrs else curses.A_BOLD

                    try:
                        stdscr.addstr(row, col, char, attr)
                    except curses.error:
                        pass  # Ignore screen boundary errors
                else:
                    # Draw whitespace without color
                    try:
                        stdscr.addstr(row, col, char)
                    except curses.error:
                        pass

        # Refresh screen (double buffering)
        stdscr.noutrefresh()
        curses.doupdate()







def main():
    """Pure curses main entry point."""
    # Try root text/ first (development), fall back to package text/ (pipx install)
    root_text_dir = Path.cwd() / 'text'
    package_text_dir = Path(__file__).parent / 'text'
    default_text_dir = root_text_dir if root_text_dir.exists() else package_text_dir

    parser = argparse.ArgumentParser(description="Spin-TUI: Colorful terminal ASCII art animation")
    parser.add_argument('--text-dir', type=str, default=str(default_text_dir),
                       help='Directory containing ASCII art text files')
    parser.add_argument('--speed', type=float, default=1.0,
                       help='Animation speed multiplier (default: 1.0)')
    parser.add_argument('--mode', type=str, default='wave', choices=['wave', 'spin', 'pulse', 'flux', 'morph'],
                       help='Animation mode (default: wave)')
    parser.add_argument('--color', type=str, choices=['red', 'blue', 'green', 'yellow', 'purple', 'cyan', 'gray', 'pink', 'orange'],
                       help='Color gradient scheme (default: prism rainbow when not specified)')
    parser.add_argument('--file', type=str,
                       help='Specific file to display (e.g., --file sample for sample.txt)')
    parser.add_argument('--cycle', nargs='?', const=30.0, type=float,
                       help='Enable file cycling. Optional: seconds between changes (default: 30.0)')

    # FPS preset flags
    fps_group = parser.add_mutually_exclusive_group()
    fps_group.add_argument('--uld', action='store_true',
                          help='Ultra-low definition: 5 FPS (minimal CPU)')
    fps_group.add_argument('--ld', action='store_true',
                          help='Low definition: 10 FPS (default, efficient)')
    fps_group.add_argument('--md', action='store_true',
                          help='Medium definition: 30 FPS (smooth)')
    fps_group.add_argument('--hd', action='store_true',
                          help='High definition: 60 FPS (maximum smoothness)')

    args = parser.parse_args()

    # Determine FPS setting
    if args.uld:
        fps = 5
    elif args.md:
        fps = 30
    elif args.hd:
        fps = 60
    else:  # Default to --ld (10 FPS)
        fps = 10

    update_interval = 1.0 / fps

    # Check terminal support
    if not os.isatty(1) or os.environ.get('TERM') == 'dumb':
        print("Error: This application requires a TTY with curses support.")
        sys.exit(1)

    # Load text content and determine file selection behavior
    try:
        loader = TextLoader(args.text_dir)
        all_files = loader.discover_files()

        if not all_files:
            print(f"Error: No .txt files found in {args.text_dir}")
            sys.exit(1)

        # Always load all files for navigation, but determine starting file and cycling behavior
        selected_files = list(all_files)
        starting_file_index = 0
        cycle_interval = 0.0  # 0 = no cycling

        if args.file:
            # Try to find specific file to start with
            target_filename = args.file if args.file.endswith('.txt') else f"{args.file}.txt"

            for i, file_path in enumerate(selected_files):
                if file_path.name == target_filename:
                    starting_file_index = i
                    break
            else:
                print(f"Warning: {target_filename} not found, starting with random file")
                starting_file_index = random.randint(0, len(selected_files) - 1)
        else:
            # No specific file requested - start at random file
            starting_file_index = random.randint(0, len(selected_files) - 1)

        # Set cycling interval if cycling is enabled
        if args.cycle is not None:
            cycle_interval = args.cycle

    except Exception as e:
        print(f"Error loading text files: {e}")
        sys.exit(1)

    # Start curses animation with mode switching support
    try:
        # Import mode classes for persistent instances
        from .modes.wave import WaveMode
        from .modes.spin import SpinMode
        from .modes.pulse import PulseMode
        from .modes.flux import FluxMode
        from .modes.morph import MorphMode

        # Create persistent mode instances to maintain state
        mode_instances = {
            'wave': WaveMode(),
            'spin': SpinMode(),
            'pulse': PulseMode(),
            'flux': FluxMode(),
            'morph': MorphMode()
        }

        # Start with initial mode
        current_mode = args.mode
        current_file_index = starting_file_index
        current_color_scheme = args.color

        def mode_switching_wrapper(stdscr):
            nonlocal current_mode, current_file_index, current_color_scheme

            while True:
                # Get mode instance for current mode
                mode_instance = mode_instances.get(current_mode, mode_instances['wave'])

                # Ensure mode instance has the current color scheme and regenerate palette
                if mode_instance.current_color_scheme != current_color_scheme:
                    mode_instance.current_color_scheme = current_color_scheme
                    if current_color_scheme in mode_instance.color_schemes:
                        mode_instance.current_color_index = mode_instance.color_schemes.index(current_color_scheme)
                    mode_instance.on_color_change()  # Regenerate color palette

                # Run mode instance
                result = mode_instance.run(stdscr, selected_files, args.speed, update_interval, cycle_interval, current_color_scheme, current_file_index)

                # Check if mode switch was requested
                if result is None:
                    # Normal exit (q pressed)
                    break
                else:
                    # Mode switch requested - update state
                    current_mode = result['next_mode']
                    current_file_index = result['current_file_index']
                    current_color_scheme = result['current_color_scheme']
                    # Continue loop with new mode

        curses.wrapper(mode_switching_wrapper)
    except curses.error as e:
        print(f"Curses error: {e}")
        print("Terminal might not support required curses features.")
        sys.exit(1)
    except KeyboardInterrupt:
        pass  # Clean exit on Ctrl+C


if __name__ == "__main__":
    main()