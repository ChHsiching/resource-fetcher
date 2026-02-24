"""Unit tests for CLIWrapper."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from resource_fetcher_gui.gui.core.cli_wrapper import CLIWrapper
from resource_fetcher_gui.gui.core.config_service import DownloadConfig


class TestCLIWrapper:
    """Test CLIWrapper functionality."""

    def test_init_with_path(self, tmp_path: Path) -> None:
        """Test initialization with CLI path."""
        cli_path = tmp_path / "cli.exe"
        wrapper = CLIWrapper(cli_path)

        assert wrapper.cli_path == cli_path
        assert wrapper.current_process is None
        assert wrapper.current_thread is None

    @pytest.fixture
    def valid_cli_file(self, tmp_path: Path) -> Path:
        """Create a fake CLI executable file for testing."""
        cli_path = tmp_path / "resource-fetcher"
        cli_path.write_text("#!/bin/bash\\necho 'fake CLI'")
        cli_path.chmod(0o755)
        return cli_path

    def test_execute_download_with_nonexistent_cli(self) -> None:
        """Test execute_download raises FileNotFoundError if CLI doesn't exist."""
        wrapper = CLIWrapper(Path("nonexistent.exe"))
        config = DownloadConfig()

        with pytest.raises(FileNotFoundError, match="CLI executable not found"):
            wrapper.execute_download("http://example.com", config)

    def test_execute_download_with_invalid_url(self, valid_cli_file: Path) -> None:
        """Test execute_download raises ValueError for invalid URL."""
        wrapper = CLIWrapper(valid_cli_file)
        config = DownloadConfig()

        with pytest.raises(ValueError, match="Invalid URL"):
            wrapper.execute_download("not-a-url", config)

        with pytest.raises(ValueError, match="Invalid URL"):
            wrapper.execute_download("", config)

    def test_build_command_with_basic_config(self, valid_cli_file: Path) -> None:
        """Test building command with basic configuration."""
        wrapper = CLIWrapper(valid_cli_file)
        config = DownloadConfig(
            output_dir="/tmp/music",
            timeout=60,
            retries=3,
            delay=0.5,
        )

        cmd = wrapper._build_command("http://example.com/album", config)

        assert str(valid_cli_file) in cmd
        assert "--url" in cmd
        assert "http://example.com/album" in cmd
        assert "--output" in cmd
        assert "/tmp/music" in cmd
        assert "--timeout" in cmd
        assert "60" in cmd
        assert "--retries" in cmd
        assert "3" in cmd
        assert "--delay" in cmd
        assert "0.5" in cmd

    def test_build_command_with_limit(self, valid_cli_file: Path) -> None:
        """Test building command with download limit."""
        wrapper = CLIWrapper(valid_cli_file)
        config = DownloadConfig(limit=10)

        cmd = wrapper._build_command("http://example.com", config)

        assert "--limit" in cmd
        assert "10" in cmd

    def test_build_command_with_overwrite(self, valid_cli_file: Path) -> None:
        """Test building command with overwrite flag."""
        wrapper = CLIWrapper(valid_cli_file)
        config = DownloadConfig(overwrite=True)

        cmd = wrapper._build_command("http://example.com", config)

        assert "--overwrite" in cmd

    def test_build_command_with_verbose(self, valid_cli_file: Path) -> None:
        """Test building command with verbose flag."""
        wrapper = CLIWrapper(valid_cli_file)
        config = DownloadConfig(verbose=True)

        cmd = wrapper._build_command("http://example.com", config)

        assert "--verbose" in cmd

    def test_build_command_without_optional_flags(self, valid_cli_file: Path) -> None:
        """Test building command without optional flags."""
        wrapper = CLIWrapper(valid_cli_file)
        config = DownloadConfig()  # Default values

        cmd = wrapper._build_command("http://example.com", config)

        # These should NOT be in command
        assert "--limit" not in cmd
        assert "--overwrite" not in cmd
        assert "--verbose" not in cmd

    @patch("subprocess.Popen")
    def test_execute_download_starts_process(
        self, mock_popen: MagicMock, valid_cli_file: Path
    ) -> None:
        """Test that execute_download starts subprocess."""
        # Mock the Popen process
        mock_process = MagicMock()
        mock_process.wait.return_value = 0
        mock_process.poll.return_value = 0  # Process has exited
        mock_process.stdout = iter([])
        mock_popen.return_value = mock_process

        wrapper = CLIWrapper(valid_cli_file)
        config = DownloadConfig()

        # Mock progress_callback to avoid threading issues in test
        progress_calls = []

        def progress_callback(line: str) -> None:
            progress_calls.append(line)

        def complete_callback(exit_code: int) -> None:
            pass

        thread = wrapper.execute_download(
            "http://example.com", config, progress_callback, complete_callback
        )

        # Verify subprocess.Popen was called
        assert mock_popen.called
        args = mock_popen.call_args[0][0]
        assert args[0] == str(valid_cli_file)
        assert "http://example.com" in args

        # Wait a bit for thread to complete
        thread.join(timeout=1)

    @patch("subprocess.Popen")
    def test_stop_download_terminates_process(
        self, mock_popen: MagicMock, valid_cli_file: Path
    ) -> None:
        """Test that stop_download terminates the process."""
        # Mock a running process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        mock_process.wait.return_value = None
        mock_popen.return_value = mock_process

        wrapper = CLIWrapper(valid_cli_file)
        DownloadConfig()

        # Start download (will create mock process)
        with patch.object(wrapper, "current_process", mock_process):
            result = wrapper.stop_download()

            # Verify terminate was called
            assert result is True
            mock_process.terminate.assert_called_once()

    def test_stop_download_when_no_process(self, valid_cli_file: Path) -> None:
        """Test stop_download returns False when no process running."""
        wrapper = CLIWrapper(valid_cli_file)

        result = wrapper.stop_download()

        assert result is False

    @patch("subprocess.Popen")
    def test_is_running_returns_true_when_process_active(
        self, mock_popen: MagicMock, valid_cli_file: Path
    ) -> None:
        """Test is_running returns True when process is active."""
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Still running
        mock_popen.return_value = mock_process

        wrapper = CLIWrapper(valid_cli_file)

        with patch.object(wrapper, "current_process", mock_process):
            assert wrapper.is_running() is True

    def test_is_running_returns_false_when_no_process(self, valid_cli_file: Path) -> None:
        """Test is_running returns False when no process."""
        wrapper = CLIWrapper(valid_cli_file)

        assert wrapper.is_running() is False

    @patch("subprocess.Popen")
    def test_is_running_returns_false_when_process_exited(
        self, mock_popen: MagicMock, valid_cli_file: Path
    ) -> None:
        """Test is_running returns False when process has exited."""
        mock_process = MagicMock()
        mock_process.poll.return_value = 0  # Exited with code 0
        mock_popen.return_value = mock_process

        wrapper = CLIWrapper(valid_cli_file)

        with patch.object(wrapper, "current_process", mock_process):
            assert wrapper.is_running() is False

    @patch("subprocess.Popen")
    def test_wait_for_completion_with_timeout(
        self, mock_popen: MagicMock, valid_cli_file: Path
    ) -> None:
        """Test wait_for_completion with timeout."""
        mock_process = MagicMock()
        mock_process.wait.return_value = None
        mock_process.poll.return_value = 0
        mock_popen.return_value = mock_process

        wrapper = CLIWrapper(valid_cli_file)
        config = DownloadConfig()

        # Start download
        def progress_callback(line: str) -> None:
            pass

        def complete_callback(exit_code: int) -> None:
            pass

        wrapper.execute_download("http://example.com", config, progress_callback, complete_callback)

        # Wait for completion with short timeout
        result = wrapper.wait_for_completion(timeout=5)

        # Thread should complete quickly
        assert result is True

    @patch("subprocess.Popen")
    def test_wait_for_completion_without_thread(self, valid_cli_file: Path) -> None:
        """Test wait_for_completion when no thread exists."""
        wrapper = CLIWrapper(valid_cli_file)

        # No thread running
        result = wrapper.wait_for_completion()

        assert result is True
