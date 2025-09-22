"""
Color scheme configuration interface for terminal-flow.

Provides configuration loading, validation, and color scheme creation
for pure curses implementation with comprehensive error handling.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional, Any
from dataclasses import dataclass, field

from .schemes import BaseColorScheme, PrismColors, CustomColors, create_color_scheme


@dataclass
class ColorConfig:
    """
    Color configuration data structure.

    Holds all color-related configuration parameters with validation
    and default values for comprehensive color scheme management.
    """
    scheme_type: str = "prism"
    colors: Optional[List[Union[str, Tuple[int, int, int]]]] = None
    saturation: float = 1.0
    value: float = 1.0
    animation_speed: float = 1.0
    fps: int = 10  # Default to low definition for better performance
    cache_enabled: bool = True
    cache_size: int = 100
    custom_schemes: Dict[str, List[Union[str, Tuple[int, int, int]]]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration values after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate all configuration parameters.

        Raises:
            ValueError: If any configuration value is invalid
        """
        # Validate scheme type
        valid_schemes = ["prism", "custom"]
        if self.scheme_type not in valid_schemes:
            raise ValueError(f"Invalid scheme_type '{self.scheme_type}'. Must be one of: {valid_schemes}")

        # Validate numeric ranges
        if not 0.0 <= self.saturation <= 1.0:
            raise ValueError(f"saturation must be 0.0-1.0, got {self.saturation}")

        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"value must be 0.0-1.0, got {self.value}")

        if self.animation_speed <= 0.0:
            raise ValueError(f"animation_speed must be positive, got {self.animation_speed}")

        if self.fps <= 0:
            raise ValueError(f"fps must be positive, got {self.fps}")

        if self.cache_size < 1:
            raise ValueError(f"cache_size must be at least 1, got {self.cache_size}")

        # Validate custom scheme requirements
        if self.scheme_type == "custom":
            if not self.colors and not self.custom_schemes:
                raise ValueError("Custom scheme requires either 'colors' or 'custom_schemes' to be specified")

            if self.colors and len(self.colors) < 2:
                raise ValueError("Custom scheme colors must have at least 2 colors")


class ColorSchemeLoader:
    """
    Color scheme configuration loader and factory.

    Handles loading configuration from files, CLI parameters, and environment
    with hierarchical configuration merging and comprehensive validation.
    """

    def __init__(self):
        """Initialize color scheme loader."""
        self.default_config = ColorConfig()

    def load_from_cli(self, colors: str = "prism", speed: float = 1.0, **kwargs) -> ColorConfig:
        """
        Load color configuration from CLI parameters for curses implementation.

        Args:
            colors: Color scheme name ("prism" or "custom")
            speed: Animation speed multiplier
            **kwargs: Additional configuration parameters

        Returns:
            ColorConfig instance with CLI parameters applied

        Raises:
            ValueError: If CLI parameters are invalid
        """
        config_dict = {
            "scheme_type": colors,
            "animation_speed": speed
        }
        config_dict.update(kwargs)

        return ColorConfig(**config_dict)

    def load_from_file(self, config_path: Union[str, Path]) -> ColorConfig:
        """
        Load color configuration from JSON configuration file.

        Args:
            config_path: Path to JSON configuration file

        Returns:
            ColorConfig instance loaded from file

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If configuration file is invalid
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file {config_path}: {e}")

        # Extract color-specific configuration
        color_config = config_data.get("colors", {})

        return ColorConfig(**color_config)

    def merge_configs(self, base_config: ColorConfig, override_config: ColorConfig) -> ColorConfig:
        """
        Merge two configurations with override priority.

        Args:
            base_config: Base configuration (lower priority)
            override_config: Override configuration (higher priority)

        Returns:
            Merged ColorConfig instance
        """
        merged_dict = {}

        # Start with base config
        for field_name in base_config.__dataclass_fields__:
            merged_dict[field_name] = getattr(base_config, field_name)

        # Override with non-default values from override config
        for field_name in override_config.__dataclass_fields__:
            override_value = getattr(override_config, field_name)
            default_value = getattr(self.default_config, field_name)

            # Only override if the value is different from default
            if override_value != default_value:
                merged_dict[field_name] = override_value

        return ColorConfig(**merged_dict)

    def create_color_scheme(self, config: ColorConfig) -> BaseColorScheme:
        """
        Create color scheme instance from configuration.

        Args:
            config: ColorConfig instance with validated parameters

        Returns:
            BaseColorScheme instance ready for animation

        Raises:
            ValueError: If color scheme cannot be created from configuration
        """
        if config.scheme_type == "prism":
            return PrismColors(
                saturation=config.saturation,
                value=config.value
            )

        elif config.scheme_type == "custom":
            colors = config.colors
            if not colors:
                raise ValueError("Custom color scheme requires colors to be specified")

            return CustomColors(colors)

        else:
            raise ValueError(f"Unsupported scheme type: {config.scheme_type}")

    def load_and_create_scheme(self, colors: str = "prism",
                              speed: float = 1.0,
                              config_file: Optional[Union[str, Path]] = None,
                              **kwargs) -> Tuple[BaseColorScheme, ColorConfig]:
        """
        Complete workflow: load configuration and create color scheme for curses.

        Args:
            colors: CLI color scheme parameter
            speed: Animation speed multiplier
            config_file: Optional configuration file path
            **kwargs: Additional CLI parameters

        Returns:
            Tuple of (color_scheme, final_config)
        """
        # Start with CLI configuration
        cli_config = self.load_from_cli(colors, speed, **kwargs)

        # Load file configuration if provided
        if config_file:
            try:
                file_config = self.load_from_file(config_file)
                # Merge with CLI taking precedence
                final_config = self.merge_configs(file_config, cli_config)
            except (FileNotFoundError, ValueError) as e:
                # Fall back to CLI-only config if file loading fails
                print(f"Warning: Could not load config file: {e}")
                final_config = cli_config
        else:
            final_config = cli_config

        # Create and return color scheme
        color_scheme = self.create_color_scheme(final_config)
        return color_scheme, final_config


def parse_custom_colors(colors_input: Union[str, List[str]]) -> List[Union[str, Tuple[int, int, int]]]:
    """
    Parse custom colors from various input formats.

    Supports hex strings, RGB tuples, and comma-separated lists.

    Args:
        colors_input: Color specification as string or list

    Returns:
        List of colors ready for CustomColors creation

    Raises:
        ValueError: If color format is invalid
    """
    if isinstance(colors_input, str):
        # Handle comma-separated color list
        if ',' in colors_input:
            color_strings = [c.strip() for c in colors_input.split(',')]
        else:
            color_strings = [colors_input.strip()]
    else:
        color_strings = colors_input

    parsed_colors = []
    for color_str in color_strings:
        color_str = color_str.strip()

        # Handle hex colors
        if color_str.startswith('#'):
            if len(color_str) not in [4, 7]:  # #RGB or #RRGGBB
                raise ValueError(f"Invalid hex color format: {color_str}")
            parsed_colors.append(color_str)

        # Handle RGB tuples as strings like "(255,0,0)"
        elif color_str.startswith('(') and color_str.endswith(')'):
            try:
                rgb_str = color_str.strip('()')
                r, g, b = map(int, rgb_str.split(','))
                if not all(0 <= c <= 255 for c in [r, g, b]):
                    raise ValueError(f"RGB values must be 0-255: {color_str}")
                parsed_colors.append((r, g, b))
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid RGB tuple format: {color_str}")

        # Handle named colors (pass through for future processing)
        else:
            parsed_colors.append(color_str)

    if len(parsed_colors) < 2:
        raise ValueError("Custom colors require at least 2 colors")

    return parsed_colors


def create_example_config() -> Dict[str, Any]:
    """
    Create example configuration dictionary for curses implementation.

    Returns:
        Example configuration structure optimized for performance
    """
    return {
        "colors": {
            "scheme_type": "prism",
            "saturation": 1.0,
            "value": 1.0,
            "animation_speed": 1.0,
            "fps": 10,  # Lower default for better performance
            "cache_enabled": True,
            "cache_size": 50,  # Smaller cache for lower memory usage
            "custom_schemes": {
                "sunset": ["#ff6b35", "#f7931e", "#ffd23f", "#06ffa5", "#118ab2"],
                "ocean": ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087", "#f95d6a", "#ff7c43", "#ffa600"],
                "pastel": ["#ffd6ff", "#c8d6e5", "#3742fa", "#2ed573", "#ffa502"]
            }
        },
        "curses": {
            "update_interval": 0.1,  # 10 FPS default
            "use_erase": True,  # Use stdscr.erase() for flicker-free animation
            "enable_colors": True
        }
    }


# Module-level convenience functions
_loader = ColorSchemeLoader()

def load_color_scheme(colors: str = "prism", speed: float = 1.0, config_file: Optional[Union[str, Path]] = None, **kwargs) -> BaseColorScheme:
    """
    Convenience function to load and create color scheme for curses.

    Args:
        colors: Color scheme type ("prism" or "custom")
        speed: Animation speed multiplier
        config_file: Optional configuration file path
        **kwargs: Additional configuration parameters

    Returns:
        Ready-to-use BaseColorScheme instance
    """
    scheme, _ = _loader.load_and_create_scheme(colors, speed, config_file, **kwargs)
    return scheme

def load_color_config(colors: str = "prism", speed: float = 1.0, config_file: Optional[Union[str, Path]] = None, **kwargs) -> ColorConfig:
    """
    Convenience function to load color configuration only for curses.

    Args:
        colors: Color scheme type
        speed: Animation speed multiplier
        config_file: Optional configuration file path
        **kwargs: Additional configuration parameters

    Returns:
        Validated ColorConfig instance
    """
    _, config = _loader.load_and_create_scheme(colors, speed, config_file, **kwargs)
    return config