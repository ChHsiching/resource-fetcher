"""GUI styles module.

This package provides centralized style management for the Resource Fetcher GUI.
It includes theme selection, color palettes, font stacks, and spacing constants.

Example usage:
    from resource_fetcher_gui.styles import StyleManager, DEFAULT_THEME, COLORS, SPACING

    # Apply theme to window
    style = StyleManager.initialize(main_window, DEFAULT_THEME)

    # Get platform-appropriate font
    font = StyleManager.get_font(size=9, bold=True)

    # Access spacing constants
    padding = SPACING["medium"]
"""

from resource_fetcher_gui.styles.style_manager import StyleManager
from resource_fetcher_gui.styles.theme_constants import COLORS, DEFAULT_THEME, SPACING

__all__ = ["StyleManager", "COLORS", "DEFAULT_THEME", "SPACING"]
