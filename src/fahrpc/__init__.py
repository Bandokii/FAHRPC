"""
FAHRPC Modules Package
"""

from .config import load_config
from .discord_rpc import DiscordRPC
from .hardware import GPUMonitor
from .logger import setup_error_logging
from .scraper import FAHScraper
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
