"""
Color scheme implementations for terminal-flow rainbow animations.

Provides PrismColors and CustomColors classes for managing different color schemes
with pure curses integration and real-time animation optimization.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Union, Optional

from .generator import ColorGenerator


class BaseColorScheme(ABC):
    """
    Abstract base class for color schemes.

    Defines the interface that all color schemes must implement for
    consistent integration with animation modes.
    """

    @abstractmethod
    def get_colors_for_text(self, text_length: int, offset: float = 0.0) -> List[Tuple[int, int, int]]:
        """
        Generate colors for text of specified length.

        Args:
            text_length: Number of characters to generate colors for
            offset: Animation offset 0.0-1.0 for cycling effects

        Returns:
            List of RGB color tuples for each character
        """
        pass

    @abstractmethod
    def get_colors_hex(self, text_length: int, offset: float = 0.0) -> List[str]:
        """
        Generate hex color strings for text of specified length.

        Args:
            text_length: Number of characters to generate colors for
            offset: Animation offset 0.0-1.0 for cycling effects

        Returns:
            List of hex color strings for each character
        """
        pass


class PrismColors(BaseColorScheme):
    """
    Full spectrum rainbow color scheme implementation.

    Generates smooth rainbow color transitions across the full spectrum
    using HSV color space for vivid, animated rainbow effects.
    """

    def __init__(self, saturation: float = 1.0, value: float = 1.0):
        """
        Initialize prism color scheme.

        Args:
            saturation: Color saturation 0.0-1.0 (default: 1.0 for vivid colors)
            value: Brightness 0.0-1.0 (default: 1.0 for full brightness)
        """
        self.saturation = max(0.0, min(1.0, saturation))
        self.value = max(0.0, min(1.0, value))

    def get_colors_for_text(self, text_length: int, offset: float = 0.0) -> List[Tuple[int, int, int]]:
        """
        Generate rainbow colors for text characters.

        Creates smooth rainbow color sequence distributed evenly across
        the spectrum, optimized for character-by-character text styling.

        Args:
            text_length: Number of characters to generate colors for
            offset: Animation offset 0.0-1.0 for rotating rainbow effect

        Returns:
            List of RGB color tuples for each character
        """
        return ColorGenerator.generate_rainbow_sequence(
            length=text_length,
            saturation=self.saturation,
            value=self.value,
            offset=offset
        )

    def get_colors_hex(self, text_length: int, offset: float = 0.0) -> List[str]:
        """
        Generate rainbow hex colors for text characters.

        Creates smooth rainbow color sequence as hex strings for terminal styling.

        Args:
            text_length: Number of characters to generate colors for
            offset: Animation offset 0.0-1.0 for rotating rainbow effect

        Returns:
            List of hex color strings for each character
        """
        return ColorGenerator.generate_rainbow_sequence_hex(
            length=text_length,
            saturation=self.saturation,
            value=self.value,
            offset=offset
        )

    def get_spectrum_preview(self, length: int = 20) -> List[Tuple[int, int, int]]:
        """
        Generate color preview of the rainbow spectrum.

        Useful for displaying color scheme previews or testing.

        Args:
            length: Number of preview colors to generate

        Returns:
            List of RGB color tuples showing spectrum range
        """
        return self.get_colors_for_text(length, 0.0)


class CustomColors(BaseColorScheme):
    """
    User-defined custom color palette scheme implementation.

    Supports custom color palettes with smooth transitions between
    defined colors using interpolation and gradient generation.
    """

    def __init__(self, colors: List[Union[Tuple[int, int, int], str]]):
        """
        Initialize custom color scheme.

        Args:
            colors: List of colors as RGB tuples or hex strings
                   Minimum 2 colors required for gradient generation
        """
        if len(colors) < 2:
            raise ValueError("Custom color scheme requires at least 2 colors")

        self.colors = self._normalize_colors(colors)

    def _normalize_colors(self, colors: List[Union[Tuple[int, int, int], str]]) -> List[Tuple[int, int, int]]:
        """
        Convert all color inputs to normalized RGB tuples.

        Args:
            colors: Mixed list of color representations

        Returns:
            List of RGB tuples (red, green, blue) 0-255
        """
        normalized = []

        for color in colors:
            if isinstance(color, tuple) and len(color) == 3:
                # Already RGB tuple
                r, g, b = color
                normalized.append((max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b)))))
            elif isinstance(color, str):
                # Hex string - parse manually
                if color.startswith('#'):
                    hex_color = color[1:]
                else:
                    hex_color = color

                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    normalized.append((r, g, b))
                else:
                    raise ValueError(f"Invalid hex color format: {color}")
            else:
                raise ValueError(f"Unsupported color format: {color}")

        return normalized

    def get_colors_for_text(self, text_length: int, offset: float = 0.0) -> List[Tuple[int, int, int]]:
        """
        Generate custom palette colors for text characters.

        Creates smooth color transitions across the custom palette,
        cycling through all defined colors with gradient interpolation.

        Args:
            text_length: Number of characters to generate colors for
            offset: Animation offset 0.0-1.0 for cycling through palette

        Returns:
            List of RGB color tuples for each character
        """
        if text_length <= 0:
            return []

        # Calculate total palette length including gradients between colors
        total_palette_length = len(self.colors) * 10  # 10 steps between each color pair

        # Generate extended color palette with gradients
        extended_palette = []
        for i in range(len(self.colors)):
            start_color = self.colors[i]
            end_color = self.colors[(i + 1) % len(self.colors)]
            gradient = ColorGenerator.generate_gradient_colors(start_color, end_color, 10)
            extended_palette.extend(gradient[:-1])  # Exclude last to avoid duplication

        # Generate colors for text with offset
        text_colors = []
        for i in range(text_length):
            # Calculate position in extended palette with offset
            position = (i / text_length + offset) * len(extended_palette)
            palette_index = int(position) % len(extended_palette)
            rgb_color = extended_palette[palette_index]
            text_colors.append(rgb_color)

        return text_colors

    def get_colors_hex(self, text_length: int, offset: float = 0.0) -> List[str]:
        """
        Generate custom palette hex colors for text characters.

        Args:
            text_length: Number of characters to generate colors for
            offset: Animation offset 0.0-1.0 for cycling through palette

        Returns:
            List of hex color strings for each character
        """
        rgb_colors = self.get_colors_for_text(text_length, offset)
        return [ColorGenerator.rgb_to_hex(rgb) for rgb in rgb_colors]

    def get_palette_preview(self) -> List[Tuple[int, int, int]]:
        """
        Get preview of the custom color palette.

        Returns:
            List of RGB color tuples showing original palette colors
        """
        return self.colors.copy()

    @classmethod
    def from_hex_strings(cls, hex_colors: List[str]) -> 'CustomColors':
        """
        Create custom color scheme from hex color strings.

        Args:
            hex_colors: List of hex color strings like ["#ff0000", "#00ff00", "#0000ff"]

        Returns:
            CustomColors instance with specified hex colors
        """
        return cls(hex_colors)

    @classmethod
    def from_rgb_tuples(cls, rgb_colors: List[Tuple[int, int, int]]) -> 'CustomColors':
        """
        Create custom color scheme from RGB tuples.

        Args:
            rgb_colors: List of RGB tuples like [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

        Returns:
            CustomColors instance with specified RGB colors
        """
        return cls(rgb_colors)


def create_color_scheme(scheme_type: str, **kwargs) -> BaseColorScheme:
    """
    Factory function for creating color schemes.

    Args:
        scheme_type: Type of scheme ("prism" or "custom")
        **kwargs: Additional arguments for scheme initialization

    Returns:
        Configured color scheme instance

    Raises:
        ValueError: If scheme_type is not supported
    """
    if scheme_type == "prism":
        saturation = kwargs.get("saturation", 1.0)
        value = kwargs.get("value", 1.0)
        return PrismColors(saturation=saturation, value=value)

    elif scheme_type == "custom":
        colors = kwargs.get("colors")
        if colors is None:
            raise ValueError("Custom color scheme requires 'colors' parameter")
        return CustomColors(colors)

    else:
        raise ValueError(f"Unsupported color scheme type: {scheme_type}")