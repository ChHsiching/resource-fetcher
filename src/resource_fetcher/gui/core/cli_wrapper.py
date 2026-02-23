"""CLI wrapper for executing resource-fetcher as subprocess."""

import logging
import subprocess
import threading
from collections.abc import Callable
from pathlib import Path

from resource_fetcher.gui.core.config_service import DownloadConfig

logger = logging.getLogger(__name__)


class CLIWrapper:
    """Wrapper for executing CLI as subprocess.

    Manages subprocess lifecycle, captures output in real-time,
    and provides callbacks for progress tracking and completion.
    """

    def __init__(self, cli_path: Path) -> None:
        """Initialize CLI wrapper.

        Args:
            cli_path: Path to the CLI executable.
        """
        self.cli_path = cli_path
        self.current_process: subprocess.Popen[str] | None = None
        self.current_thread: threading.Thread | None = None

        logger.debug(f"CLIWrapper initialized with CLI path: {cli_path}")

    def execute_download(
        self,
        url: str,
        config: DownloadConfig,
        progress_callback: Callable[[str], None] | None = None,
        complete_callback: Callable[[int], None] | None = None,
    ) -> threading.Thread:
        """Execute download in background thread.

        Starts the CLI as a subprocess with appropriate arguments.
        Captures stdout/stderr in real-time and calls progress_callback for each line.
        Calls complete_callback with exit code when download finishes.

        Args:
            url: Album URL to download.
            config: Download configuration.
            progress_callback: Optional callback called with each line of CLI output.
            complete_callback: Optional callback called with exit code when done.

        Returns:
            Thread object running the download process.

        Raises:
            FileNotFoundError: If CLI executable doesn't exist.
            ValueError: If URL is invalid.
        """
        # Validate CLI path
        if not self.cli_path.exists():
            raise FileNotFoundError(f"CLI executable not found: {self.cli_path}")

        # Validate URL
        if not url or not url.startswith("http"):
            raise ValueError(f"Invalid URL: {url}")

        # Build command
        cmd = self._build_command(url, config)
        logger.debug(f"Executing command: {' '.join(cmd)}")

        def run_process() -> None:
            """Run subprocess in background thread."""
            try:
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    bufsize=1,  # Line buffered
                    errors="replace",  # Replace encoding errors instead of failing
                )

                # Read output line by line
                if self.current_process.stdout:
                    for line in self.current_process.stdout:
                        line = line.rstrip()
                        logger.debug(f"CLI output: {line}")
                        if progress_callback:
                            progress_callback(line)

                # Wait for process to complete
                exit_code = self.current_process.wait()
                logger.info(f"Download process completed with exit code: {exit_code}")

                if complete_callback:
                    complete_callback(exit_code)

            except Exception as e:
                logger.error(f"Error running download process: {e}")
                if complete_callback:
                    complete_callback(-1)  # Use -1 to indicate error
            finally:
                self.current_process = None
                self.current_thread = None

        # Start thread
        thread = threading.Thread(target=run_process, daemon=True)
        self.current_thread = thread
        thread.start()

        return thread

    def _build_command(self, url: str, config: DownloadConfig) -> list[str]:
        """Build CLI command from configuration.

        Args:
            url: Album URL to download.
            config: Download configuration.

        Returns:
            List of command arguments.
        """
        cmd = [
            str(self.cli_path),
            "--url",
            url,
            "--output",
            config.output_dir,
            "--timeout",
            str(config.timeout),
            "--retries",
            str(config.retries),
            "--delay",
            str(config.delay),
        ]

        # Optional arguments
        if config.limit is not None:
            cmd.extend(["--limit", str(config.limit)])

        if config.overwrite:
            cmd.append("--overwrite")

        if config.verbose:
            cmd.append("--verbose")

        return cmd

    def stop_download(self) -> bool:
        """Stop the currently running download.

        Attempts to terminate the subprocess if it's running.

        Returns:
            True if process was stopped, False if no process was running.
        """
        if self.current_process is None:
            logger.warning("No download process to stop")
            return False

        try:
            logger.info("Stopping download process...")
            self.current_process.terminate()

            # Give it a moment to terminate gracefully
            try:
                self.current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it didn't terminate
                logger.warning("Process did not terminate gracefully, forcing kill")
                self.current_process.kill()
                self.current_process.wait()

            logger.info("Download process stopped")
            return True

        except Exception as e:
            logger.error(f"Error stopping download: {e}")
            return False

    def is_running(self) -> bool:
        """Check if download is currently running.

        Returns:
            True if a download process is currently active, False otherwise.
        """
        if self.current_process is None:
            return False

        # Check if process is still alive
        return self.current_process.poll() is None

    def wait_for_completion(self, timeout: float | None = None) -> bool:
        """Wait for download to complete.

        Args:
            timeout: Optional timeout in seconds. If None, waits indefinitely.

        Returns:
            True if download completed, False if timeout occurred.
        """
        if self.current_thread is None:
            return True  # No thread means nothing to wait for

        try:
            self.current_thread.join(timeout=timeout)
            return not self.current_thread.is_alive()
        except Exception as e:
            logger.error(f"Error waiting for completion: {e}")
            return False
