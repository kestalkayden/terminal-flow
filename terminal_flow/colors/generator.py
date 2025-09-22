"""
Color generation utilities for terminal-flow rainbow animations.

Provides RGB/HSV color space utilities and rainbow/prism color generation algorithms
optimized for real-time terminal animation with pure curses integration.
"""

import colorsys
from typing import Tuple, List, Union


class ColorGenerator:
    """
    Core color generation utilities for rainbow and custom color schemes.

    Provides HSV-based rainbow color generation, RGB color space utilities,
    and color interpolation functions optimized for real-time animation.
    """

    @staticmethod
    def hsv_to_rgb(hue: float, saturation: float = 1.0, value: float = 1.0) -> Tuple[int, int, int]:
        """
        Convert HSV color values to RGB integers.

        Args:
            hue: Hue value 0.0-1.0 (0=red, 0.33=green, 0.67=blue, 1.0=red)
            saturation: Saturation 0.0-1.0 (0=grayscale, 1.0=vivid colors)
            value: Value/brightness 0.0-1.0 (0=black, 1.0=full brightness)

        Returns:
            RGB tuple as (red, green, blue) integers 0-255
        """
        # Clamp values to valid range
        hue = max(0.0, min(1.0, hue))
        saturation = max(0.0, min(1.0, saturation))
        value = max(0.0, min(1.0, value))

        rgb_float = colorsys.hsv_to_rgb(hue, saturation, value)
        return tuple(int(c * 255) for c in rgb_float)

    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """
        Convert RGB tuple to hex color string.

        Args:
            rgb: RGB tuple as (red, green, blue) integers 0-255

        Returns:
            Hex color string (e.g., "#ff0000")
        """
        r, g, b = rgb
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def generate_rainbow_color(position: float, saturation: float = 1.0, value: float = 1.0) -> Tuple[int, int, int]:
        """
        Generate rainbow color at specified spectrum position.

        Creates smooth rainbow color transitions across the full spectrum.
        Position 0.0 starts at red, cycles through orange, yellow, green,
        cyan, blue, magenta, and returns to red at 1.0.

        Args:
            position: Position in spectrum 0.0-1.0
            saturation: Color saturation 0.0-1.0 (default: 1.0 for vivid colors)
            value: Brightness 0.0-1.0 (default: 1.0 for full brightness)

        Returns:
            RGB tuple as (red, green, blue) integers 0-255
        """
        # Normalize position to 0.0-1.0 range
        position = position % 1.0
        return ColorGenerator.hsv_to_rgb(position, saturation, value)

    @staticmethod
    def generate_rainbow_color_hex(position: float, saturation: float = 1.0, value: float = 1.0) -> str:
        """
        Generate rainbow color as hex string.

        Convenience method that combines generate_rainbow_color() and rgb_to_hex().

        Args:
            position: Position in spectrum 0.0-1.0
            saturation: Color saturation 0.0-1.0
            value: Brightness 0.0-1.0

        Returns:
            Hex color string ready for terminal styling
        """
        rgb = ColorGenerator.generate_rainbow_color(position, saturation, value)
        return ColorGenerator.rgb_to_hex(rgb)

    @staticmethod
    def interpolate_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """
        Interpolate between two RGB colors.

        Creates smooth color transitions between two colors using linear interpolation.

        Args:
            color1: Starting RGB color (red, green, blue) 0-255
            color2: Ending RGB color (red, green, blue) 0-255
            factor: Interpolation factor 0.0-1.0 (0.0=color1, 1.0=color2)

        Returns:
            Interpolated RGB color as (red, green, blue) integers 0-255
        """
        factor = max(0.0, min(1.0, factor))

        r = int(color1[0] + (color2[0] - color1[0]) * factor)
        g = int(color1[1] + (color2[1] - color1[1]) * factor)
        b = int(color1[2] + (color2[2] - color1[2]) * factor)

        return (r, g, b)

    @staticmethod
    def generate_gradient_colors(start_color: Tuple[int, int, int], end_color: Tuple[int, int, int], steps: int) -> List[Tuple[int, int, int]]:
        """
        Generate gradient color sequence between two colors.

        Creates a smooth color gradient with specified number of steps.
        Useful for pre-calculating color sequences for animation.

        Args:
            start_color: Starting RGB color (red, green, blue) 0-255
            end_color: Ending RGB color (red, green, blue) 0-255
            steps: Number of gradient steps (minimum 2)

        Returns:
            List of RGB color tuples forming smooth gradient
        """
        if steps < 2:
            return [start_color, end_color]

        gradient = []
        for i in range(steps):
            factor = i / (steps - 1)
            color = ColorGenerator.interpolate_colors(start_color, end_color, factor)
            gradient.append(color)

        return gradient

    @staticmethod
    def generate_rainbow_sequence(length: int, saturation: float = 1.0, value: float = 1.0, offset: float = 0.0) -> List[Tuple[int, int, int]]:
        """
        Generate rainbow color sequence for text animation.

        Creates a sequence of rainbow colors distributed evenly across the spectrum.
        Optimized for coloring sequences of characters in ASCII art animation.

        Args:
            length: Number of colors to generate
            saturation: Color saturation 0.0-1.0
            value: Brightness 0.0-1.0
            offset: Starting position offset 0.0-1.0 for animation cycling

        Returns:
            List of RGB color tuples for text character styling
        """
        if length <= 0:
            return []

        colors = []
        for i in range(length):
            position = (i / length + offset) % 1.0
            color = ColorGenerator.generate_rainbow_color(position, saturation, value)
            colors.append(color)

        return colors

    @staticmethod
    def generate_rainbow_sequence_hex(length: int, saturation: float = 1.0, value: float = 1.0, offset: float = 0.0) -> List[str]:
        """
        Generate rainbow color sequence as hex strings.

        Convenience method for generating rainbow sequences ready for terminal styling.

        Args:
            length: Number of colors to generate
            saturation: Color saturation 0.0-1.0
            value: Brightness 0.0-1.0
            offset: Starting position offset 0.0-1.0 for animation cycling

        Returns:
            List of hex color strings for terminal styling
        """
        rgb_colors = ColorGenerator.generate_rainbow_sequence(length, saturation, value, offset)
        return [ColorGenerator.rgb_to_hex(rgb) for rgb in rgb_colors]

    @staticmethod
    def generate_monochromatic_gradient(color_name: str, length: int, offset: float = 0.0) -> List[Tuple[int, int, int]]:
        """
        Generate monochromatic gradient sequence for specified color.

        Creates a gradient from dark to light shades of the specified color,
        providing smooth color transitions for animation.

        Args:
            color_name: Color name ('red', 'blue', 'green', 'yellow', 'purple', 'cyan', 'gray', 'pink')
            length: Number of colors to generate
            offset: Starting position offset 0.0-1.0 for animation cycling

        Returns:
            List of RGB color tuples forming monochromatic gradient
        """
        if length <= 0:
            return []

        # Define color gradients (dark to light)
        color_gradients = {
            'red': [(150, 20, 20), (200, 30, 30), (255, 0, 0), (255, 50, 50), (255, 80, 80)],
            'blue': [(30, 30, 150), (0, 50, 200), (0, 0, 255), (50, 100, 255), (100, 150, 255)],
            'green': [(0, 80, 0), (0, 255, 0), (128, 255, 128)],
            'yellow': [(128, 128, 0), (255, 255, 0), (255, 255, 128)],
            'purple': [(80, 0, 80), (128, 0, 128), (200, 128, 200)],
            'cyan': [(0, 80, 80), (0, 255, 255), (128, 255, 255)],
            'gray': [(64, 64, 64), (128, 128, 128), (192, 192, 192)],
            'pink': [(180, 100, 140), (220, 130, 170), (255, 160, 190), (255, 192, 203), (255, 200, 210)],
            'orange': [(180, 60, 0), (215, 110, 0), (255, 140, 0), (255, 180, 40), (255, 195, 80)]
        }

        if color_name not in color_gradients:
            # Fallback to rainbow if unknown color
            return ColorGenerator.generate_rainbow_sequence(length, offset=offset)

        gradient_colors = color_gradients[color_name]

        # Create extended gradient with smooth transitions
        extended_gradient = []
        steps_per_segment = max(10, length // 2)

        for i in range(len(gradient_colors) - 1):
            start_color = gradient_colors[i]
            end_color = gradient_colors[i + 1]
            segment = ColorGenerator.generate_gradient_colors(start_color, end_color, steps_per_segment)
            if i > 0:
                segment = segment[1:]  # Avoid duplication
            extended_gradient.extend(segment)

        # Generate colors for text with offset
        colors = []
        for i in range(length):
            position = (i / length + offset) * len(extended_gradient)
            gradient_index = int(position) % len(extended_gradient)
            colors.append(extended_gradient[gradient_index])

        return colors