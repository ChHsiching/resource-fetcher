"""GUI widgets for Resource Fetcher."""

from resource_fetcher.gui.widgets.config_widget import ConfigWidget
from resource_fetcher.gui.widgets.main_window import MainWindow
from resource_fetcher.gui.widgets.status_bar import StatusBar
from resource_fetcher.gui.widgets.url_input_widget import URLInputWidget

__all__ = [
    "MainWindow",
    "URLInputWidget",
    "ConfigWidget",
    "StatusBar",
]
