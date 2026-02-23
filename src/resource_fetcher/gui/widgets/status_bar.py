"""Status bar widget for GUI."""

import logging
import tkinter as tk
from datetime import datetime
from enum import Enum
from tkinter import scrolledtext, ttk

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Log levels for status bar."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class StatusBar(ttk.Frame):
    """Status bar with log display."""

    def __init__(self, master: tk.Widget) -> None:
        """Initialize status bar.

        Args:
            master: Parent widget.
        """
        super().__init__(master, relief=tk.SUNKEN, padding=5)

        self._create_widgets()
        logger.debug("StatusBar initialized")

    def _create_widgets(self) -> None:
        """Create status bar widgets."""
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            anchor=tk.W,
        )
        self.status_label.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        # Log text area
        log_frame = ttk.LabelFrame(self, text="Log", padding=5)
        log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Consolas", 9),
            state=tk.DISABLED,
            wrap=tk.WORD,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for coloring
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("SUCCESS", foreground="green")
        self.log_text.tag_config("timestamp", foreground="gray")

    def set_status(self, message: str) -> None:
        """Set status message.

        Args:
            message: Status message to display.
        """
        self.status_var.set(message)

        timestamp = datetime.now().strftime("%H:%M:%S")
        self._log_message(LogLevel.INFO, f"[{timestamp}] {message}")

    def log(
        self,
        level: LogLevel,
        message: str,
    ) -> None:
        """Log a message.

        Args:
            level: Log level.
            message: Log message.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log_message(level, f"[{timestamp}] [{level.value}] {message}")
        logger.log(
            logging.getLevelName(level.value),
            message,
        )

    def _log_message(self, level: LogLevel, message: str) -> None:
        """Add message to log text area.

        Args:
            level: Log level for coloring.
            message: Message to add.
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", level.value)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear(self) -> None:
        """Clear log text area."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        logger.debug("Log cleared")

    def log_info(self, message: str) -> None:
        """Log info message.

        Args:
            message: Message to log.
        """
        self.log(LogLevel.INFO, message)

    def warning(self, message: str) -> None:
        """Log warning message.

        Args:
            message: Message to log.
        """
        self.log(LogLevel.WARNING, message)

    def error(self, message: str) -> None:
        """Log error message.

        Args:
            message: Message to log.
        """
        self.log(LogLevel.ERROR, message)

    def success(self, message: str) -> None:
        """Log success message.

        Args:
            message: Message to log.
        """
        self.log(LogLevel.SUCCESS, message)
