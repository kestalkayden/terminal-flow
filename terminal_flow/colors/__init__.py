"""
Color system for terminal-flow rainbow animations.

Foundation module for color scheme implementations providing dynamic
rainbow color generation and management for terminal ASCII art display.

Planned implementations:
    - PrismColors: Full spectrum rainbow color schemes
    - CustomColors: User-defined color palette support
    - ColorGenerator: Dynamic color transition algorithms

Integration points:
    - Used by main.py CLI --colors option
    - Interfaces with modes module for animation color application
    - Coordinates with curses library for terminal color rendering

See Also:
    - main.py:22-27: Color scheme selection CLI option
    - modes/__init__.py: Animation mode integration
"""

from .generator import ColorGenerator
from .schemes import BaseColorScheme, PrismColors, CustomColors, create_color_scheme
from .animator import ColorFrameCache, ColorAnimator, BatchColorApplicator
from .config import ColorConfig, ColorSchemeLoader, load_color_scheme, load_color_config, parse_custom_colors

__all__ = [
    "ColorGenerator",
    "BaseColorScheme",
    "PrismColors",
    "CustomColors",
    "create_color_scheme",
    "ColorFrameCache",
    "ColorAnimator",
    "BatchColorApplicator",
    "ColorConfig",
    "ColorSchemeLoader",
    "load_color_scheme",
    "load_color_config",
    "parse_custom_colors"
]