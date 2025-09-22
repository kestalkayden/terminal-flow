"""
Animation modes for terminal-flow display effects with runtime mode switching.

Complete module housing five animation mode implementations with mathematical
algorithms for dynamic visual effects on ASCII art terminal display.

Animation modes:
    - Wave: Horizontal rainbow wave effects flowing across ASCII art
    - Spin: Polar coordinate color rotation around center point
    - Pulse: Ripple effects pulsing outward from center with configurable patterns
    - Flux: Uniform color cycling across all characters simultaneously
    - Morph: 3D wave field animation with mathematical wave propagation

Key features:
    - Runtime mode switching with M/m keys (wave → spin → pulse → flux → morph)
    - Integration with 10 color schemes (rainbow + 9 monochromatic gradients)
    - State preservation during mode transitions
    - Performance optimization with frame caching and batched operations

Integration points:
    - Implemented in curses_main.py with mode_switching_wrapper
    - Interfaces with complete color system for scheme application
    - Coordinates with TextLoader for ASCII art content rendering
    - Interactive controls for immediate mode switching

See Also:
    - curses_main.py: Mode implementations and switching logic
    - colors/: Complete color system integration
    - animation_base.py: BaseAnimationMode framework
"""

# Mode implementations will be added here
__all__ = []