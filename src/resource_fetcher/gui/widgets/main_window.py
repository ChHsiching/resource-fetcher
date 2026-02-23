"""Main application window for Resource Fetcher GUI."""

import logging
import tkinter as tk
import tkinter.ttk as ttk

import ttkbootstrap as bootstrap

from resource_fetcher.gui.core.config_service import ConfigService, DownloadConfig
from resource_fetcher.gui.widgets.config_widget import ConfigWidget
from resource_fetcher.gui.widgets.status_bar import StatusBar
from resource_fetcher.gui.widgets.url_input_widget import URLInputWidget

logger = logging.getLogger(__name__)


class MainWindow(bootstrap.Window):
    """Main application window.

    This is the top-level window that contains all GUI components.
    Uses ttkbootstrap for modern theming.
    """

    def __init__(self, theme: str = "cosmo") -> None:
        """Initialize main window.

        Args:
            theme: ttkbootstrap theme name (default: "cosmo").
        """
        super().__init__(themename=theme)

        # Window configuration
        self.title("Resource Fetcher GUI")
        self.geometry("800x600")
        self.minsize(600, 400)

        # Initialize services
        self.config_service = ConfigService()

        # Center window on screen
        self.center_window()

        # Build UI
        self._create_widgets()
        self._load_config()

        logger.info(f"MainWindow initialized with theme: {theme}")

    def center_window(self) -> None:
        """Center window on screen."""
        self.update_idletasks()

        width = self.winfo_width()
        height = self.winfo_height()
        x_offset = (self.winfo_screenwidth() - width) // 2
        y_offset = (self.winfo_screenheight() - height) // 2

        self.geometry(f"{width}x{height}+{x_offset}+{y_offset}")

    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Main container with padding
        main_container = ttk.Frame(self, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        # URL Input Widget
        self.url_input = URLInputWidget(
            main_container,
            on_url_change=self._on_url_changed,
        )
        self.url_input.pack(fill=tk.X, pady=(0, 10))

        # Configuration Widget
        self.config_widget = ConfigWidget(
            main_container,
            on_config_change=self._on_config_changed,
        )
        self.config_widget.pack(fill=tk.X, pady=(0, 10))

        # Control buttons frame
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.download_btn = ttk.Button(
            control_frame,
            text="Download",
            command=self._on_download_clicked,
            width=15,
        )
        self.download_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_btn = ttk.Button(
            control_frame,
            text="Stop",
            command=self._on_stop_clicked,
            width=15,
            state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Progress placeholder label
        progress_frame = ttk.LabelFrame(main_container, text="Progress", padding=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        ttk.Label(
            progress_frame,
            text="Progress display will be implemented in Phase 3",
            font=("TkDefaultFont", 10, "italic"),
        ).pack(expand=True)

        # Status Bar
        self.status_bar = StatusBar(main_container)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Initial status message
        self.status_bar.set_status("Ready")

    def _load_config(self) -> None:
        """Load configuration from file."""
        config = self.config_service.load_config()
        self.config_widget.set_config(config)
        logger.info("Configuration loaded")

    def _on_url_changed(self, url: str) -> None:
        """Handle URL change.

        Args:
            url: New URL value.
        """
        # Validate and update download button state
        is_valid, _ = self.url_input.validate()
        state = tk.NORMAL if is_valid else tk.DISABLED
        self.download_btn.config(state=state)

    def _on_config_changed(self, config: DownloadConfig) -> None:
        """Handle configuration change.

        Args:
            config: New configuration.
        """
        logger.info("Configuration changed")
        self.status_bar.log_info("Configuration updated")

    def _on_download_clicked(self) -> None:
        """Handle download button click."""
        url = self.url_input.get_url()
        is_valid, error_msg = self.url_input.validate()

        if not is_valid:
            self.status_bar.error(f"Invalid URL: {error_msg}")
            return

        # TODO: Phase 4 - Use config for actual download
        _ = self.config_widget.get_config()

        # Add to history
        self.url_input.add_to_history(url)

        # Update UI state
        self.download_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        for child in self.config_widget.winfo_children():
            try:
                child.config(state=tk.DISABLED)
            except Exception:
                pass

        self.status_bar.log_info(f"Starting download from: {url}")

        # TODO: Phase 4 - Integrate with CLIWrapper for actual download
        self.after(2000, self._simulate_download_complete)

    def _on_stop_clicked(self) -> None:
        """Handle stop button click."""
        self.status_bar.warning("Download stopped")
        self._reset_ui_state()

    def _simulate_download_complete(self) -> None:
        """Simulate download completion (placeholder for Phase 4)."""
        self.status_bar.success("Download complete (simulation)")
        self._reset_ui_state()

    def _reset_ui_state(self) -> None:
        """Reset UI to ready state."""
        self.download_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        for child in self.config_widget.winfo_children():
            try:
                child.config(state=tk.NORMAL)
            except Exception:
                pass

    def run(self) -> None:
        """Start the main GUI event loop."""
        logger.info("Starting main event loop")
        self.mainloop()
