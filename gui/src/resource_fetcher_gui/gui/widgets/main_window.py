"""Main application window for Resource Fetcher GUI."""

import logging
import sys
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path

import ttkbootstrap as bootstrap

from resource_fetcher_gui.gui.core.cli_wrapper import CLIWrapper
from resource_fetcher_gui.gui.core.config_service import ConfigService, DownloadConfig
from resource_fetcher_gui.gui.core.output_parser import OutputParser, SongProgress
from resource_fetcher_gui.gui.widgets.config_widget import ConfigWidget
from resource_fetcher_gui.gui.widgets.progress_widget import ProgressWidget
from resource_fetcher_gui.gui.widgets.status_bar import StatusBar
from resource_fetcher_gui.gui.widgets.url_input_widget import URLInputWidget
from resource_fetcher_gui.styles import StyleManager

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
        self.cli_wrapper: CLIWrapper | None = None
        self.output_parser = OutputParser()

        # Determine CLI path
        cli_path = Path("dist/resource-fetcher.exe")
        if sys.platform != "win32":
            cli_path = Path("dist/resource-fetcher")

        if cli_path.exists():
            self.cli_wrapper = CLIWrapper(cli_path)
            logger.info(f"CLI wrapper initialized with: {cli_path}")
        else:
            logger.warning(f"CLI not found at {cli_path} (will be available after build)")

        # Center window on screen
        self.center_window()

        # Initialize styling
        StyleManager.initialize(self, theme)

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

        # Progress Widget
        self.progress_widget = ProgressWidget(main_container)
        self.progress_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

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

        if not self.cli_wrapper:
            self.status_bar.error("CLI executable not found. Please build the project first.")
            return

        config = self.config_widget.get_config()

        # Add to history
        self.url_input.add_to_history(url)

        # Clear previous progress
        self.progress_widget.clear()
        self.output_parser.reset()

        # Update UI state
        self.download_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        for child in self.config_widget.winfo_children():
            try:
                child.config(state=tk.DISABLED)
            except Exception:
                pass

        self.status_bar.log_info(f"Starting download from: {url}")

        # Start download in background thread
        self.cli_wrapper.execute_download(
            url,
            config,
            progress_callback=self._on_progress,
            complete_callback=self._on_download_complete,
        )

    def _on_progress(self, line: str) -> None:
        """Handle CLI output progress.

        Args:
            line: Line of CLI output.
        """
        # Parse output
        result = self.output_parser.parse_line(line)

        if isinstance(result, SongProgress):
            # Update progress widget from main thread
            self.after(0, lambda: self.progress_widget.update_progress(result))
            self.after(0, lambda: self.progress_widget.scroll_to_bottom())

        # Also log the line
        self.status_bar.log_info(line.strip())

    def _on_download_complete(self, exit_code: int) -> None:
        """Handle download completion.

        Args:
            exit_code: Process exit code.
        """
        if exit_code == 0:
            self.status_bar.success("Download completed successfully!")
        else:
            failed = self.progress_widget.get_failed_songs()
            if failed:
                self.status_bar.error(
                    f"Download completed with errors. {len(failed)} songs failed."
                )
                for title in failed:
                    self.status_bar.error(f"  - {title}")
            else:
                self.status_bar.error(f"Download failed with exit code {exit_code}")

        self._reset_ui_state()

    def _on_stop_clicked(self) -> None:
        """Handle stop button click."""
        if self.cli_wrapper and self.cli_wrapper.is_running():
            self.cli_wrapper.stop_download()
            self.status_bar.warning("Download stopped by user")
        else:
            self.status_bar.warning("No download in progress")

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
