"""Main entry point for GUI application."""

import logging
import sys

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
        from resource_fetcher_gui.gui.widgets.main_window import MainWindow

        logger.info("GUI widgets imported successfully")

        # Create and run main window
        app = MainWindow(theme="cosmo")
        app.run()

        return 0

    except Exception as e:
        logger.exception("Fatal error starting GUI")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
