"""Entry point for `python -m terminal_flow` — runs the curses animator.

Mirrors the `terminal-flow` console script so both front doors behave identically.
"""

from .curses_main import main

if __name__ == "__main__":
    main()
