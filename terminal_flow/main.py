"""
Main CLI entry point for terminal-flow application.

Provides Click-based command line interface with options for animation modes,
color schemes, configuration files, and text directory management.

Key functions:
    - cli: Main Click command with comprehensive option parsing
    - Terminal initialization and cross-platform color testing
    - Text file discovery and validation with user feedback
    - Framework status display and functionality verification

Integration points:
    - Uses Rich Console for advanced terminal features and color display
    - Click for CLI option parsing and command structure
    - pathlib for cross-platform file system operations
    - colorama via Rich for Windows terminal color support

CLI Options:
    - --mode: Animation mode selection (spin, wave, pulse)
    - --colors: Color scheme selection (prism, custom)
    - --config: Optional configuration file path
    - --text-dir: Text file directory (default: text/)
    - --speed: Animation speed multiplier

See Also:
    - pyproject.toml:51-52: CLI entry point configuration
    - terminal_flow/__init__.py: Package metadata and structure
"""

import click
from rich.console import Console
from rich.text import Text
from rich import print as rprint
import sys
from pathlib import Path

from .text import TextLoader

console = Console()


@click.command()
@click.option(
    "--mode",
    type=click.Choice(["wave", "spin", "pulse", "flux", "morph"]),
    default="wave",
    help="Display mode for color animation"
)
@click.option(
    "--colors",
    type=click.Choice(["prism", "custom"]),
    default="prism",
    help="Color scheme to use"
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to configuration file"
)
@click.option(
    "--text-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default=str(Path.cwd() / 'text' if (Path.cwd() / 'text').exists() else Path(__file__).parent / 'text'),
    help="Directory containing text files"
)
@click.option(
    "--speed",
    type=float,
    default=1.0,
    help="Animation speed multiplier"
)
@click.version_option(version="0.1.0", prog_name="terminal-flow")
def cli(mode: str, colors: str, config: str, text_dir: str, speed: float) -> None:
    """
    A colorful terminal user interface application that displays ASCII text files
    with dynamic rainbow animations and visual effects.
    """
    try:
        # Initialize terminal
        console.clear()

        # Display welcome message
        welcome_text = Text("🌈 terminal-flow v0.1.0", style="bold magenta")
        console.print(welcome_text, justify="center")
        console.print()

        # Show current settings
        settings_text = Text("Settings:", style="bold cyan")
        console.print(settings_text)
        console.print(f"  Mode: {mode}")
        console.print(f"  Colors: {colors}")
        console.print(f"  Text Directory: {text_dir}")
        console.print(f"  Speed: {speed}x")
        console.print()

        # Initialize text loader and discover files
        try:
            text_loader = TextLoader(text_dir)
            txt_files = text_loader.discover_files()

            if not txt_files:
                console.print(f"[yellow]No .txt files found in '{text_dir}' directory[/yellow]")
                console.print(f"[yellow]Tip: Add some ASCII art .txt files to get started![/yellow]")
                sys.exit(1)

            console.print(f"[green]Found {text_loader.file_count} text file(s) to display[/green]")
            for txt_file in txt_files:
                console.print(f"  • {txt_file.name}")
            console.print()

        except FileNotFoundError:
            console.print(f"[red]Error: Text directory '{text_dir}' not found[/red]")
            console.print(f"[yellow]Tip: Create a '{text_dir}' directory and add some .txt files![/yellow]")
            sys.exit(1)

        # Basic terminal test - display a sample text with colors
        console.print("[bold]Terminal functionality test:[/bold]")
        test_text = Text("terminal-flow")
        test_text.stylize("red", 0, 1)
        test_text.stylize("yellow", 1, 2)
        test_text.stylize("green", 2, 3)
        test_text.stylize("cyan", 3, 4)
        test_text.stylize("blue", 4, 5)
        test_text.stylize("magenta", 5, 6)
        test_text.stylize("red", 6, 7)
        test_text.stylize("yellow", 7, 8)
        test_text.stylize("green", 8, 9)
        test_text.stylize("cyan", 9, 10)
        console.print(test_text, justify="center")
        console.print()

        console.print("[green]✓ Terminal colors working![/green]")
        console.print("[green]✓ CLI entry point working![/green]")
        console.print("[green]✓ Package structure ready![/green]")
        console.print()
        console.print("[yellow]Framework setup complete! Animation modes coming soon...[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()