"""Theme constants for GUI styling.

This module contains constant definitions for colors, spacing,
and other theme-related values. These constants are used
throughout the application to ensure visual consistency.

Note: Many constants are defined in StyleManager for better
organization. This module is reserved for future expansion
if needed (e.g., animation constants, breakpoints, etc.).
"""

# Version info
__version__ = "1.0.0"

# Export key constants for convenience
from resource_fetcher_gui.styles.style_manager import StyleManager

# Commonly used constants (aliases for easier access)
DEFAULT_THEME = StyleManager.DEFAULT_THEME
COLORS = StyleManager.COLORS
SPACING = StyleManager.SPACING
