"""Configuration management service for GUI."""

import dataclasses
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DownloadConfig:
    """Download configuration.

    Attributes:
        output_dir: Output directory for downloaded files
        limit: Optional limit on number of songs to download
        overwrite: Whether to overwrite existing files
        timeout: Request timeout in seconds
        retries: Number of retry attempts for failed downloads
        delay: Delay between downloads in seconds
        verbose: Enable verbose logging
    """

    output_dir: str = "./downloads"
    limit: int | None = None
    overwrite: bool = False
    timeout: int = 60
    retries: int = 3
    delay: float = 0.5
    verbose: bool = False


class ConfigService:
    """Service for managing application configuration.

    Handles loading, saving, and validation of configuration from JSON files.
    Configuration is stored in platform-specific locations:
    - Windows: %APPDATA%\\resource_fetcher\\config.json
    - Linux/macOS: ~/.config/resource_fetcher/config.json
    """

    DEFAULT_CONFIG = DownloadConfig()

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize configuration service.

        Args:
            config_path: Optional custom path to configuration file.
                        If not provided, uses default platform-specific path.
        """
        self.config_path = config_path or self._get_default_path()
        logger.debug(f"ConfigService initialized with path: {self.config_path}")

    def _get_default_path(self) -> Path:
        """Get default configuration path for current platform.

        Returns:
            Path to configuration file in platform-specific location.
        """
        if sys.platform == "win32":
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        else:
            base = Path.home() / ".config"

        return base / "resource_fetcher" / "config.json"

    def load_config(self) -> DownloadConfig:
        """Load configuration from file or return defaults.

        Attempts to load configuration from the configured path.
        If the file doesn't exist or is invalid, returns default configuration.

        Returns:
            DownloadConfig object with loaded or default values.
        """
        if not self.config_path.exists():
            logger.info(f"Config file not found at {self.config_path}, using defaults")
            return self.DEFAULT_CONFIG

        try:
            with open(self.config_path, encoding="utf-8") as f:
                data = json.load(f)

            # Validate and create config object
            config = self._validate_and_create_config(data)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in config file: {e}, using defaults")
            return self.DEFAULT_CONFIG
        except (TypeError, ValueError) as e:
            logger.warning(f"Invalid config data: {e}, using defaults")
            return self.DEFAULT_CONFIG
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}, using defaults")
            return self.DEFAULT_CONFIG

    def save_config(self, config: DownloadConfig) -> None:
        """Save configuration to file.

        Creates parent directories if they don't exist.
        Writes configuration as JSON with pretty formatting.

        Args:
            config: DownloadConfig object to save.
        """
        try:
            # Ensure parent directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert config to dictionary
            data = dataclasses.asdict(config)

            # Write to file with pretty formatting
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Configuration saved to {self.config_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def _validate_and_create_config(self, data: dict[str, Any]) -> DownloadConfig:
        """Validate configuration data and create DownloadConfig object.

        Args:
            data: Dictionary containing configuration values.

        Returns:
            DownloadConfig object with validated values.

        Raises:
            ValueError: If configuration data is invalid.
        """
        # Extract only valid fields
        valid_fields = {
            k: v
            for k, v in data.items()
            if k in DownloadConfig.__dataclass_fields__ and v is not None
        }

        # Type validation and coercion
        if "output_dir" in valid_fields:
            valid_fields["output_dir"] = str(valid_fields["output_dir"])

        if "limit" in valid_fields and valid_fields["limit"] is not None:
            try:
                valid_fields["limit"] = int(valid_fields["limit"])
                if valid_fields["limit"] <= 0:
                    raise ValueError("limit must be positive")
            except (ValueError, TypeError):
                logger.warning(f"Invalid limit value: {valid_fields['limit']}, ignoring")
                del valid_fields["limit"]

        if "timeout" in valid_fields:
            try:
                valid_fields["timeout"] = int(valid_fields["timeout"])
                if valid_fields["timeout"] <= 0:
                    raise ValueError("timeout must be positive")
            except (ValueError, TypeError):
                logger.warning(f"Invalid timeout value: {valid_fields['timeout']}, using default")
                valid_fields["timeout"] = self.DEFAULT_CONFIG.timeout

        if "retries" in valid_fields:
            try:
                valid_fields["retries"] = int(valid_fields["retries"])
                if valid_fields["retries"] < 0:
                    raise ValueError("retries must be non-negative")
            except (ValueError, TypeError):
                logger.warning(f"Invalid retries value: {valid_fields['retries']}, using default")
                valid_fields["retries"] = self.DEFAULT_CONFIG.retries

        if "delay" in valid_fields:
            try:
                valid_fields["delay"] = float(valid_fields["delay"])
                if valid_fields["delay"] < 0:
                    raise ValueError("delay must be non-negative")
            except (ValueError, TypeError):
                logger.warning(f"Invalid delay value: {valid_fields['delay']}, using default")
                valid_fields["delay"] = self.DEFAULT_CONFIG.delay

        if "overwrite" in valid_fields:
            valid_fields["overwrite"] = bool(valid_fields["overwrite"])

        if "verbose" in valid_fields:
            valid_fields["verbose"] = bool(valid_fields["verbose"])

        # Create config object with defaults for missing fields
        config_dict = dataclasses.asdict(self.DEFAULT_CONFIG)
        config_dict.update(valid_fields)

        return DownloadConfig(**config_dict)

    def get_default_config(self) -> DownloadConfig:
        """Get default configuration.

        Returns:
            Default DownloadConfig object.
        """
        return self.DEFAULT_CONFIG
