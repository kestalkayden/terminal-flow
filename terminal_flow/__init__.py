"""
terminal-flow: A colorful terminal user interface application that displays ASCII text files
with dynamic rainbow animations, visual effects, and interactive runtime controls.

This package provides the core framework for terminal-based ASCII art display
with modular animation modes, complete color systems, and zero external dependencies.

Key modules:
    - curses_main: Pure curses CLI entry point with enhanced argparse interface and interactive controls
    - modes: Animation mode implementations (wave, spin, pulse, flux, morph)
    - colors: Complete color system with RGB/HSV generation, schemes, and curses adapter
    - text: ASCII art file loading, cycling, and management with TextLoader

Integration points:
    - Pure Python curses for zero-dependency terminal control with 256-color support
    - Built-in text/ directory with 11 ASCII art files for immediate usage
    - Runtime controls: arrow keys for navigation, C/c for colors, M/m for modes
    - Mathematical wave field simulation for morph mode animation

See Also:
    - curses_main.py: Pure curses CLI interface with interactive controls
    - text/loader.py: TextLoader class for file management
    - colors/: Complete color system implementation
"""

__version__ = "0.1.0"
__author__ = "kestalkayden"
__email__ = "kestalkayden@gmail.com"

# Package metadata
__all__ = ["__version__", "__author__", "__email__"]