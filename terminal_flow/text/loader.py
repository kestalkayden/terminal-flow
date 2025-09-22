"""
TextLoader for loading and managing ASCII art text files.

Provides file discovery, loading, and validation functionality for terminal-flow
ASCII art animations.
"""

from pathlib import Path
from typing import List, Optional


class TextLoader:
    """
    Loads and manages ASCII art text files for terminal-flow animations.

    Features:
        - Automatic .txt file discovery in specified directories
        - File content loading and validation
        - Support for empty directory initialization (for direct file path usage)
        - File counting and enumeration

    Usage:
        loader = TextLoader("/path/to/text/files")
        files = loader.discover_files()
        content = loader.load_file(files[0])
    """

    def __init__(self, text_dir: str = ""):
        """
        Initialize TextLoader with a directory path.

        Args:
            text_dir: Directory path containing .txt files. Can be empty string
                     if files will be provided directly to load_file().
        """
        self.text_dir = Path(text_dir) if text_dir else None
        self._file_count = 0

    def discover_files(self) -> List[Path]:
        """
        Discover all .txt files in the text directory.

        Returns:
            List of Path objects for discovered .txt files

        Raises:
            FileNotFoundError: If the text directory doesn't exist
            ValueError: If no text directory was provided
        """
        if not self.text_dir:
            raise ValueError("Cannot discover files without a text directory")

        if not self.text_dir.exists():
            raise FileNotFoundError(f"Text directory not found: {self.text_dir}")

        # Find all .txt files in the directory
        txt_files = list(self.text_dir.glob("*.txt"))
        txt_files.sort()  # Sort for consistent ordering

        self._file_count = len(txt_files)
        return txt_files

    def load_file(self, file_path: Path) -> str:
        """
        Load content from a text file.

        Args:
            file_path: Path to the .txt file to load

        Returns:
            String content of the file

        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If the file cannot be read
        """
        file_path = Path(file_path)  # Ensure it's a Path object

        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except IOError as e:
            raise IOError(f"Failed to read file {file_path}: {e}")

    @property
    def file_count(self) -> int:
        """
        Get the number of discovered files.

        Returns:
            Number of .txt files found by discover_files()
        """
        return self._file_count