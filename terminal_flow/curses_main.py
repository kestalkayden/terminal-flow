#!/usr/bin/env python3
"""
Pure curses main entry point for terminal-flow.

Provides high-performance ambient display animation using curses library
with zero external dependencies and immediate startup. Features include
five animation modes (wave, spin, pulse, flux, morph), interactive
runtime controls, and advanced wave field simulation for organic motion.

Key classes:
    - WaveField: 2D wave field simulation for smooth wave propagation


Integration points:
    - Uses TextLoader for file management and cycling
    - Uses CursesColorAdapter for RGB to terminal color mapping

See Also:
    - colors.generator: For wave field color generation algorithms
    - text.loader: For ASCII art file loading and management
"""

import curses
import random
import argparse
import sys
import os
from pathlib import Path

from .constants import ANIMATION_MODES
from .text import TextLoader
from .colors.curses_adapter import get_default_adapter, get_default_sequence


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
    parser.add_argument('--mode', type=str, default='wave', choices=ANIMATION_MODES,
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
