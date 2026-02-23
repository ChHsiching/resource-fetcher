"""URL input widget for GUI."""

import logging
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

import pyperclip

logger = logging.getLogger(__name__)


class URLInputWidget(ttk.LabelFrame):
    """Widget for URL input with validation and history."""

    def __init__(
        self,
        master: tk.Widget,
        on_url_change: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize URL input widget.

        Args:
            master: Parent widget.
            on_url_change: Callback when URL changes.
        """
        super().__init__(master, text="Input URL", padding=10)

        self.on_url_change = on_url_change
        self.url_history: list[str] = []

        self._create_widgets()
        logger.debug("URLInputWidget initialized")

    def _create_widgets(self) -> None:
        """Create URL input widgets."""
        # URL entry
        self.url_var = tk.StringVar()
        self.url_var.trace_add("write", self._on_url_changed)

        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill=tk.X, expand=True)

        self.url_entry = ttk.Entry(
            entry_frame,
            textvariable=self.url_var,
            font=("TkDefaultFont", 10),
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Paste button
        paste_btn = ttk.Button(
            entry_frame,
            text="Paste",
            command=self._paste_from_clipboard,
            width=8,
        )
        paste_btn.pack(side=tk.LEFT)

        # History dropdown
        history_frame = ttk.Frame(self)
        history_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(history_frame, text="History:").pack(side=tk.LEFT)

        self.history_combo = ttk.Combobox(
            history_frame,
            values=self.url_history,
            state="readonly",
            font=("TkDefaultFont", 9),
        )
        self.history_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.history_combo.bind("<<ComboboxSelected>>", self._on_history_selected)

    def _on_url_changed(self, *args: object) -> None:
        """Handle URL text change.

        Args:
            *args: Event arguments (unused).
        """
        url = self.url_var.get().strip()
        if self.on_url_change:
            self.on_url_change(url)

    def _paste_from_clipboard(self) -> None:
        """Paste URL from clipboard."""
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content:
                self.url_var.set(clipboard_content.strip())
                logger.debug("Pasted URL from clipboard")
        except Exception as e:
            logger.warning(f"Failed to paste from clipboard: {e}")

    def _on_history_selected(self, event: object) -> None:
        """Handle history selection.

        Args:
            event: Event object (unused).
        """
        selection = self.history_combo.get()
        if selection:
            self.url_var.set(selection)
            logger.debug(f"Selected URL from history: {selection}")

    def get_url(self) -> str:
        """Get current URL.

        Returns:
            Current URL string.
        """
        return self.url_var.get().strip()

    def set_url(self, url: str) -> None:
        """Set URL.

        Args:
            url: URL string to set.
        """
        self.url_var.set(url)

    def add_to_history(self, url: str) -> None:
        """Add URL to history.

        Args:
            url: URL to add.
        """
        url = url.strip()
        if url and url not in self.url_history:
            self.url_history.insert(0, url)
            # Keep only last 10 URLs
            self.url_history = self.url_history[:10]
            self.history_combo["values"] = self.url_history
            logger.debug(f"Added URL to history: {url}")

    def clear(self) -> None:
        """Clear URL input."""
        self.url_var.set("")

    def validate(self) -> tuple[bool, str]:
        """Validate URL.

        Returns:
            Tuple of (is_valid, error_message).
        """
        url = self.get_url()

        if not url:
            return False, "URL cannot be empty"

        if not url.startswith(("http://", "https://")):
            return False, "URL must start with http:// or https://"

        return True, ""
