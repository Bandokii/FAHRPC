"""
Tray module for FAHRPC
Manages system tray icon and menu for window control
"""

import ctypes
import logging
import sys
import threading
from typing import Any, Dict

import pystray
from PIL import Image

logger = logging.getLogger('FAHRPC')

def set_console_visibility(visible: bool) -> None:
    """
    Toggle Windows console window visibility.

    Args:
        visible: True to show, False to hide console
    """
    if sys.platform == "win32":
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd != 0:
            ctypes.windll.user32.ShowWindow(hwnd, 1 if visible else 0)

class TrayIcon:
    """Manages the system tray icon and menu interactions."""

    def __init__(self, config: Dict[str, Any], restart_event: threading.Event,
                 stop_event: threading.Event) -> None:
        """
        Initialize Tray Icon.

        Args:
            config: Configuration dictionary
            restart_event: Threading event to trigger restart
            stop_event: Threading event to trigger shutdown
        """
        self.config = config
        self.restart_event = restart_event
        self.stop_event = stop_event
        self.icon = None
        self.thread = None

    def _load_icon_image(self) -> Image.Image:
        """
        Load icon image from file or create default.

        Returns:
            PIL Image object for tray icon
        """
        icon_file = self.config['display']['icon_file']
        try:
            return Image.open(icon_file)
        except Exception:
            return Image.new('RGB', (64, 64), color=(180, 0, 0))

    def _create_menu(self) -> tuple:
        """
        Create the tray menu with all available actions.

        Returns:
            Tuple of pystray.MenuItem objects
        """
        def on_show(icon, item):
            set_console_visibility(True)

        def on_hide(icon, item):
            set_console_visibility(False)

        def on_restart(icon, item):
            self.restart_event.set()

        def on_exit(icon, item):
            self.stop_event.set()
            icon.stop()

        return (
            pystray.MenuItem("Show Console", on_show),
            pystray.MenuItem("Hide Console", on_hide),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Restart FAHRPC", on_restart),
            pystray.MenuItem("Exit", on_exit),
        )

    def _run_icon(self) -> None:
        """Run the tray icon (blocking operation)."""
        icon_image = self._load_icon_image()
        menu = self._create_menu()
        self.icon = pystray.Icon("FAHRPC", icon_image, "FAHRPC", menu)
        self.icon.run()

    def start(self) -> None:
        """Start the tray icon in a separate daemon thread."""
        self.thread = threading.Thread(target=self._run_icon, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop the tray icon and cleanup."""
        if self.icon:
            self.icon.stop()
