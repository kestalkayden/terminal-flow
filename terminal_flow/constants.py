"""Shared constants for terminal-flow."""

# Canonical list of animation modes — single source of truth. Imported by the
# base class and both CLI front ends so the three can't drift out of sync.
ANIMATION_MODES = ("wave", "spin", "pulse", "flux", "morph")
