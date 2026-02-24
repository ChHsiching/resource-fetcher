"""Configuration widget for GUI."""

import logging
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import ttk

from resource_fetcher_gui.gui.core.config_service import DownloadConfig

logger = logging.getLogger(__name__)


class ConfigWidget(ttk.LabelFrame):
    """Widget for download configuration."""

    def __init__(
        self,
        master: tk.Widget,
        on_config_change: Callable[[DownloadConfig], None] | None = None,
    ) -> None:
        """Initialize configuration widget.

        Args:
            master: Parent widget.
            on_config_change: Callback when configuration changes.
        """
        super().__init__(master, text="Configuration", padding=10)

        self.on_config_change = on_config_change
        self._config = DownloadConfig()

        self._create_widgets()
        logger.debug("ConfigWidget initialized")

    def _create_widgets(self) -> None:
        """Create configuration widgets."""
        # Create two columns
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Output directory
        ttk.Label(left_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, pady=2)
        output_frame = ttk.Frame(left_frame)
        output_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 10))

        self.output_var = tk.StringVar(value=self._config.output_dir)
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_btn = ttk.Button(
            output_frame,
            text="Browse...",
            command=self._browse_output_dir,
            width=10,
        )
        browse_btn.pack(side=tk.LEFT)

        # Limit
        ttk.Label(left_frame, text="Download Limit (optional):").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.limit_var = tk.StringVar(value=str(self._config.limit) if self._config.limit else "")
        limit_entry = ttk.Entry(left_frame, textvariable=self.limit_var, width=15)
        limit_entry.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))

        # Timeout
        ttk.Label(left_frame, text="Timeout (seconds):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.timeout_var = tk.IntVar(value=self._config.timeout)
        timeout_spinbox = ttk.Spinbox(
            left_frame,
            from_=10,
            to=300,
            textvariable=self.timeout_var,
            width=15,
        )
        timeout_spinbox.grid(row=5, column=0, sticky=tk.W, pady=(0, 10))

        # Retries
        ttk.Label(left_frame, text="Retries:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.retries_var = tk.IntVar(value=self._config.retries)
        retries_spinbox = ttk.Spinbox(
            left_frame,
            from_=0,
            to=10,
            textvariable=self.retries_var,
            width=15,
        )
        retries_spinbox.grid(row=7, column=0, sticky=tk.W, pady=(0, 10))

        # Delay
        ttk.Label(right_frame, text="Delay (seconds):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.delay_var = tk.DoubleVar(value=self._config.delay)
        delay_spinbox = ttk.Spinbox(
            right_frame,
            from_=0.0,
            to=10.0,
            increment=0.1,
            textvariable=self.delay_var,
            width=15,
        )
        delay_spinbox.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))

        # Checkboxes
        self.overwrite_var = tk.BooleanVar(value=self._config.overwrite)
        overwrite_check = ttk.Checkbutton(
            right_frame,
            text="Overwrite existing files",
            variable=self.overwrite_var,
        )
        overwrite_check.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

        self.verbose_var = tk.BooleanVar(value=self._config.verbose)
        verbose_check = ttk.Checkbutton(
            right_frame,
            text="Verbose output",
            variable=self.verbose_var,
        )
        verbose_check.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))

        # Buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.grid(row=4, column=0, sticky=tk.W)

        reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset, width=10)
        reset_btn.pack(side=tk.LEFT, padx=(0, 5))

        apply_btn = ttk.Button(
            btn_frame,
            text="Apply",
            command=self._apply_config,
            width=10,
        )
        apply_btn.pack(side=tk.LEFT)

    def _browse_output_dir(self) -> None:
        """Browse for output directory."""
        from tkinter import filedialog

        current = self.output_var.get()
        if not current:
            current = str(Path.home())

        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=current,
            mustexist=True,
        )

        if directory:
            self.output_var.set(directory)
            logger.debug(f"Selected output directory: {directory}")

    def _apply_config(self) -> None:
        """Apply configuration changes."""
        self._config = self.get_config()
        if self.on_config_change:
            self.on_config_change(self.config)
        logger.info("Configuration applied")

    def get_config(self) -> DownloadConfig:
        """Get current configuration.

        Returns:
            Current DownloadConfig.
        """
        limit_str = self.limit_var.get().strip()
        limit = int(limit_str) if limit_str else None

        return DownloadConfig(
            output_dir=self.output_var.get(),
            limit=limit,
            overwrite=self.overwrite_var.get(),
            timeout=self.timeout_var.get(),
            retries=self.retries_var.get(),
            delay=self.delay_var.get(),
            verbose=self.verbose_var.get(),
        )

    def set_config(self, config: DownloadConfig) -> None:
        """Set configuration.

        Args:
            config: DownloadConfig to set.
        """
        self._config = config
        self.output_var.set(config.output_dir)
        self.limit_var.set(str(config.limit) if config.limit else "")
        self.timeout_var.set(config.timeout)
        self.retries_var.set(config.retries)
        self.delay_var.set(config.delay)
        self.overwrite_var.set(config.overwrite)
        self.verbose_var.set(config.verbose)

    def reset(self) -> None:
        """Reset to default configuration."""
        from resource_fetcher_gui.gui.core.config_service import ConfigService

        default_config = ConfigService.DEFAULT_CONFIG
        self.set_config(default_config)
        self._apply_config()
        logger.info("Configuration reset to defaults")
