"""
Tray Module for FAHRPC
=====================

Manages the Windows system tray icon and context menu for application control.

Features:
    - System tray icon with custom PNG image
    - Right-click context menu for quick actions
    - Show/Hide console window toggle
    - Restart and Exit application controls
    - Daemon thread operation (doesn't block main loop)

Menu Options:
    - Show Console: Reveals the console window
    - Hide Console: Hides the console window
    - Restart FAHRPC: Restarts the main logic loop
    - Exit: Cleanly shuts down the application

Example usage:
    >>> from fahrpc.tray import TrayIcon, set_console_visibility
    >>> tray = TrayIcon(config, restart_event, stop_event)
    >>> tray.start()  # Runs in background thread
    >>> set_console_visibility(False)  # Hide console
"""

import ctypes
import logging
import sys
import threading
from pathlib import Path
from typing import Any, Dict

import pystray
from PIL import Image

from fahrpc.config import APP_NAME

logger = logging.getLogger(APP_NAME.upper())

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
        icon_filename = self.config['display']['icon_file']

        # Try multiple locations in order:
        # 1. Relative to current working directory (most common)
        # 2. Absolute path if specified
        # 3. Relative to src/fahrpc module root
        # 4. Relative to project root (three levels up from tray.py)
        possible_paths = [
            Path.cwd() / icon_filename,  # Current working directory
            Path(icon_filename).resolve(),  # Absolute path
            Path(__file__).parent / icon_filename,  # Same directory as tray.py
            Path(__file__).parent.parent / icon_filename,  # src/fahrpc/../ (src/)
            Path(__file__).parent.parent.parent / icon_filename,  # Project root
        ]

        # Remove duplicates while preserving order
        seen = set()
        unique_paths = []
        for p in possible_paths:
            p_str = str(p.resolve())
            if p_str not in seen:
                seen.add(p_str)
                unique_paths.append(p)

        for icon_path in unique_paths:
            try:
                if icon_path.exists():
                    logger.debug(f"Loading icon from: {icon_path}")
                    return Image.open(icon_path)
            except Exception as e:
                logger.error(f"Failed to load icon from {icon_path}: {e}", exc_info=True)
                continue

        # Fallback: create a red circle icon
        searched_paths = [str(p) for p in unique_paths]
        logger.error(f"Could not find icon file '{icon_filename}' in any search path. Searched: {searched_paths}")
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
        self.icon = pystray.Icon(APP_NAME.upper(), icon_image, APP_NAME.upper(), menu)
        self.icon.run()

    def start(self) -> None:
        """Start the tray icon in a separate daemon thread."""
        self.thread = threading.Thread(target=self._run_icon, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop the tray icon and cleanup."""
        if self.icon:
            self.icon.stop()
