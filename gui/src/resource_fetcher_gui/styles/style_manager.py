"""Centralized style management for GUI.

This module provides a StyleManager class that handles all styling
aspects of the application including themes, colors, fonts, and spacing.
It ensures consistent styling across all widgets and platforms.
"""

import sys
from tkinter import ttk

import ttkbootstrap as bootstrap


class StyleManager:
    """Manages application-wide styling.

    This class provides centralized style management including:
    - Theme selection and configuration
    - Color palette definitions
    - Platform-specific font stacks
    - Consistent spacing constants
    - Custom style overrides for ttkbootstrap
    """

    # Theme selection
    DEFAULT_THEME = "flatly"

    # Color palette (flatly base + refinements)
    # Chosen for high contrast and professional appearance
    COLORS = {
        "primary": "#2c3e50",  # Dark blue-gray
        "accent": "#3498db",  # Bright blue (custom)
        "success": "#27ae60",  # Dark green
        "error": "#e74c3c",  # Muted red
        "warning": "#f39c12",  # Orange
        "text": "#212529",  # Near black
        "text_secondary": "#6c757d",  # Gray
        "background": "#ffffff",  # White
        "border": "#dee2e6",  # Light gray
    }

    # Spacing constants
    # Provides consistent spacing rhythm throughout the UI
    SPACING = {
        "large": 12,  # Section gaps
        "medium": 8,  # Widget groups
        "small": 6,  # Related elements
        "tiny": 4,  # Tightly packed
    }

    @staticmethod
    def get_font(size: int = 9, bold: bool = False) -> tuple[str, int, str]:
        """Get platform-appropriate font.

        Selects fonts that match the platform's native appearance:
        - Windows: Segoe UI (standard Windows font)
        - macOS: SF Pro Text (standard macOS font)
        - Linux: Inter (modern, widely available)

        Args:
            size: Font size in points.
            bold: Whether font should be bold.

        Returns:
            Font tuple (family, size, weight).
        """
        if sys.platform == "darwin":
            family = "SF Pro Text"
        elif sys.platform == "win32":
            family = "Segoe UI"
        else:  # Linux
            family = "Inter"

        weight = "bold" if bold else "normal"
        return (family, size, weight)

    @staticmethod
    def get_monospace_font(size: int = 9) -> tuple[str, int]:
        """Get monospace font for logs and code.

        Selects the best monospace font for each platform:
        - Windows: Consolas (clear, readable)
        - macOS: Menlo (designed for code)
        - Linux: Courier New (widely available)

        Args:
            size: Font size in points.

        Returns:
            Font tuple (family, size).
        """
        if sys.platform == "darwin":
            family = "Menlo"
        elif sys.platform == "win32":
            family = "Consolas"
        else:
            family = "Courier New"

        return (family, size)

    @staticmethod
    def apply_custom_styles(style: ttk.Style) -> None:
        """Apply custom style overrides to ttkbootstrap theme.

        Makes subtle refinements to the default ttkbootstrap theme
        for a more polished, professional appearance.

        Changes are intentionally minimal to avoid "AI-generated" look:
        - Slightly more compact button padding
        - Consistent border width
        - Enhanced row height for Treeview
        - Professional font weights

        Args:
            style: ttk.Style instance from bootstrap.Window.
        """
        # Button refinements
        # More compact padding for better information density
        style.configure("TButton", padding=(12, 6), borderwidth=1)

        # Entry refinements
        # Consistent padding and minimal border
        style.configure("TEntry", padding=(6, 6), borderwidth=1)

        # LabelFrame refinements
        # Solid border for crisp appearance
        style.configure("TLabelframe", borderwidth=1, relief="solid")

        # LabelFrame labels (section headings)
        # Bold font for clear visual hierarchy
        style.configure("TLabelframe.Label", font=StyleManager.get_font(9, bold=True))

        # Treeview (song list) refinements
        # More row height for better readability
        style.configure("Treeview", rowheight=28, font=StyleManager.get_font(9))

        # Treeview headings
        # Bold font for clear column headers
        style.configure("Treeview.Heading", font=StyleManager.get_font(9, bold=True))

    @classmethod
    def initialize(cls, window: bootstrap.Window, theme: str = DEFAULT_THEME) -> ttk.Style:
        """Initialize styling for application.

        Applies the selected theme and custom style overrides.
        Call this once at application startup.

        Args:
            window: Bootstrap window instance.
            theme: Theme name to use (must be a valid ttkbootstrap theme).

        Returns:
            Configured ttk.Style instance.

        Example:
            >>> style = StyleManager.initialize(main_window, "flatly")
        """
        style = window.style
        cls.apply_custom_styles(style)
        return style
