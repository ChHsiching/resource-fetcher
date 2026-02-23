"""Unit tests for ConfigService."""

import json
from pathlib import Path

from resource_fetcher.gui.core.config_service import ConfigService, DownloadConfig


class TestDownloadConfig:
    """Test DownloadConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = DownloadConfig()

        assert config.output_dir == "./downloads"
        assert config.limit is None
        assert config.overwrite is False
        assert config.timeout == 60
        assert config.retries == 3
        assert config.delay == 0.5
        assert config.verbose is False

    def test_custom_values(self) -> None:
        """Test configuration with custom values."""
        config = DownloadConfig(
            output_dir="/tmp/music",
            limit=10,
            overwrite=True,
            timeout=120,
            retries=5,
            delay=1.0,
            verbose=True,
        )

        assert config.output_dir == "/tmp/music"
        assert config.limit == 10
        assert config.overwrite is True
        assert config.timeout == 120
        assert config.retries == 5
        assert config.delay == 1.0
        assert config.verbose is True


class TestConfigService:
    """Test ConfigService functionality."""

    def test_init_with_custom_path(self, tmp_path: Path) -> None:
        """Test initialization with custom config path."""
        config_path = tmp_path / "custom_config.json"
        service = ConfigService(config_path=config_path)

        assert service.config_path == config_path

    def test_init_with_default_path(self) -> None:
        """Test initialization with default platform-specific path."""
        service = ConfigService()

        # Should get platform-specific path
        assert service.config_path.name == "config.json"
        assert "resource_fetcher" in str(service.config_path)

    def test_load_config_when_file_not_exists(self, tmp_path: Path) -> None:
        """Test loading config when file doesn't exist."""
        config_path = tmp_path / "nonexistent.json"
        service = ConfigService(config_path=config_path)

        config = service.load_config()

        # Should return default config
        assert config == ConfigService.DEFAULT_CONFIG

    def test_save_and_load_config(self, tmp_path: Path) -> None:
        """Test saving and loading configuration."""
        config_path = tmp_path / "test_config.json"
        service = ConfigService(config_path=config_path)

        # Save config
        original_config = DownloadConfig(
            output_dir="/tmp/music",
            timeout=120,
            retries=5,
        )
        service.save_config(original_config)

        # Verify file was created
        assert config_path.exists()

        # Load config
        loaded_config = service.load_config()

        # Verify loaded values match
        assert loaded_config.output_dir == "/tmp/music"
        assert loaded_config.timeout == 120
        assert loaded_config.retries == 5
        # Default values should be preserved
        assert loaded_config.limit is None
        assert loaded_config.overwrite is False

    def test_save_config_creates_directory(self, tmp_path: Path) -> None:
        """Test that save_config creates parent directory if needed."""
        config_path = tmp_path / "subdir" / "config.json"
        service = ConfigService(config_path=config_path)

        config = DownloadConfig(output_dir="./downloads")
        service.save_config(config)

        # Directory should be created
        assert config_path.parent.exists()
        assert config_path.exists()

    def test_load_config_with_valid_json(self, tmp_path: Path) -> None:
        """Test loading valid JSON configuration."""
        config_path = tmp_path / "valid_config.json"
        config_data = {
            "output_dir": "/tmp/music",
            "limit": 10,
            "overwrite": True,
            "timeout": 120,
            "retries": 5,
            "delay": 1.5,
            "verbose": True,
        }

        # Write JSON file
        config_path.write_text(json.dumps(config_data), encoding="utf-8")

        # Load config
        service = ConfigService(config_path=config_path)
        config = service.load_config()

        # Verify all values
        assert config.output_dir == "/tmp/music"
        assert config.limit == 10
        assert config.overwrite is True
        assert config.timeout == 120
        assert config.retries == 5
        assert config.delay == 1.5
        assert config.verbose is True

    def test_load_config_with_invalid_json(self, tmp_path: Path) -> None:
        """Test loading invalid JSON returns defaults."""
        config_path = tmp_path / "invalid_config.json"
        config_path.write_text("{ invalid json", encoding="utf-8")

        service = ConfigService(config_path=config_path)
        config = service.load_config()

        # Should return defaults
        assert config == ConfigService.DEFAULT_CONFIG

    def test_load_config_with_invalid_limit(self, tmp_path: Path) -> None:
        """Test that invalid limit value is ignored."""
        config_path = tmp_path / "invalid_limit.json"
        config_data = {"limit": -5}  # Invalid: must be positive

        config_path.write_text(json.dumps(config_data), encoding="utf-8")

        service = ConfigService(config_path=config_path)
        config = service.load_config()

        # Invalid limit should be ignored, default used
        assert config.limit is None

    def test_load_config_with_invalid_timeout(self, tmp_path: Path) -> None:
        """Test that invalid timeout uses default value."""
        config_path = tmp_path / "invalid_timeout.json"
        config_data = {"timeout": "invalid"}  # Invalid type

        config_path.write_text(json.dumps(config_data), encoding="utf-8")

        service = ConfigService(config_path=config_path)
        config = service.load_config()

        # Should use default timeout
        assert config.timeout == ConfigService.DEFAULT_CONFIG.timeout

    def test_load_config_with_partial_data(self, tmp_path: Path) -> None:
        """Test loading partial config uses defaults for missing fields."""
        config_path = tmp_path / "partial_config.json"
        config_data = {"output_dir": "/custom", "timeout": 90}

        config_path.write_text(json.dumps(config_data), encoding="utf-8")

        service = ConfigService(config_path=config_path)
        config = service.load_config()

        # Custom values
        assert config.output_dir == "/custom"
        assert config.timeout == 90
        # Default values for missing fields
        assert config.limit is None
        assert config.overwrite is False
        assert config.retries == 3
        assert config.delay == 0.5

    def test_get_default_config(self) -> None:
        """Test get_default_config returns default config."""
        service = ConfigService()

        config = service.get_default_config()

        assert config == ConfigService.DEFAULT_CONFIG

    def test_save_config_overwrites_existing(self, tmp_path: Path) -> None:
        """Test that save_config overwrites existing file."""
        config_path = tmp_path / "overwrite_test.json"
        service = ConfigService(config_path=config_path)

        # Save first config
        config1 = DownloadConfig(output_dir="/first", timeout=30)
        service.save_config(config1)

        # Save second config
        config2 = DownloadConfig(output_dir="/second", timeout=90)
        service.save_config(config2)

        # Load and verify second config
        loaded = service.load_config()
        assert loaded.output_dir == "/second"
        assert loaded.timeout == 90

    def test_config_serialization_roundtrip(self, tmp_path: Path) -> None:
        """Test that config can be saved and loaded without data loss."""
        config_path = tmp_path / "roundtrip.json"
        service = ConfigService(config_path=config_path)

        original = DownloadConfig(
            output_dir="/test/path",
            limit=42,
            overwrite=True,
            timeout=180,
            retries=7,
            delay=2.5,
            verbose=False,
        )

        # Save
        service.save_config(original)

        # Load
        loaded = service.load_config()

        # Verify all fields match
        assert loaded.output_dir == original.output_dir
        assert loaded.limit == original.limit
        assert loaded.overwrite == original.overwrite
        assert loaded.timeout == original.timeout
        assert loaded.retries == original.retries
        assert loaded.delay == original.delay
        assert loaded.verbose == original.verbose

    def test_load_config_with_zero_retries(self, tmp_path: Path) -> None:
        """Test that zero retries is accepted (non-negative)."""
        config_path = tmp_path / "zero_retries.json"
        config_data = {"retries": 0}

        config_path.write_text(json.dumps(config_data), encoding="utf-8")

        service = ConfigService(config_path=config_path)
        config = service.load_config()

        # Zero retries should be valid
        assert config.retries == 0

    def test_load_config_with_zero_delay(self, tmp_path: Path) -> None:
        """Test that zero delay is accepted (non-negative)."""
        config_path = tmp_path / "zero_delay.json"
        config_data = {"delay": 0}

        config_path.write_text(json.dumps(config_data), encoding="utf-8")

        service = ConfigService(config_path=config_path)
        config = service.load_config()

        # Zero delay should be valid
        assert config.delay == 0
