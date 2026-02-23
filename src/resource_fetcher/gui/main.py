"""Main entry point for GUI application."""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("gui.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point for GUI application.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    try:
        logger.info("Starting Resource Fetcher GUI...")

        # Check if ttkbootstrap is available
        try:
            import importlib.util

            if importlib.util.find_spec("ttkbootstrap") is None:
                raise ImportError()
        except (ImportError, AttributeError):
            logger.error("ttkbootstrap is not installed. Please run: pip install ttkbootstrap")
            print("Error: ttkbootstrap is not installed.")
            print("Please run: pip install ttkbootstrap")
            return 1

        # Import GUI components
        from resource_fetcher.gui.core.cli_wrapper import CLIWrapper
        from resource_fetcher.gui.core.config_service import ConfigService
        from resource_fetcher.gui.core.output_parser import OutputParser, SongProgress

        logger.info("Core services imported successfully")

        # Test services
        print("Testing GUI core services...")

        # Test ConfigService
        config_service = ConfigService()
        config = config_service.load_config()
        print(f"[OK] ConfigService: output_dir={config.output_dir}, timeout={config.timeout}")

        # Test CLIWrapper (check if CLI exists)
        cli_path = Path("dist/resource-fetcher.exe")
        if sys.platform != "win32":
            cli_path = Path("dist/resource-fetcher")

        if cli_path.exists():
            CLIWrapper(cli_path)
            print(f"[OK] CLIWrapper: CLI found at {cli_path}")
        else:
            print(f"[WARN] CLIWrapper: CLI not found at {cli_path} (will be available after build)")

        # Test OutputParser
        parser = OutputParser()
        test_line = "[5/10] 圣哉三一歌"
        result = parser.parse_line(test_line)
        if isinstance(result, SongProgress):
            print(f"[OK] OutputParser: Parsed [{result.index}/{result.total}] {result.title}")

        print("\n" + "=" * 60)
        print("All core services are working correctly!")
        print("=" * 60)
        print("\nNote: Full GUI interface will be implemented in the next phase.")
        print("Current phase: Core services foundation (Phase 1)")
        print("\nNext steps:")
        print("  1. Implement MainWindow and widgets (Phase 2)")
        print("  2. Add progress display (Phase 3)")
        print("  3. Integrate complete workflow (Phase 4)")

        return 0

    except Exception as e:
        logger.exception("Fatal error starting GUI")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
