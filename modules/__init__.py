"""
FAHRPC Modules Package
"""

from .config import load_config
from .logger import setup_error_logging
from .hardware import GPUMonitor
from .scraper import FAHScraper
from .discord_rpc import DiscordRPC
from .tray import TrayIcon, set_console_visibility

__all__ = [
    'load_config',
    'setup_error_logging',
    'GPUMonitor',
    'FAHScraper',
    'DiscordRPC',
    'TrayIcon',
    'set_console_visibility'
]
