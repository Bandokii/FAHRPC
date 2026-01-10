"""
FAHRPC - Folding@Home Discord Rich Presence
============================================

A Python application that displays your Folding@Home GPU folding progress
in Discord Rich Presence. Features real-time GPU monitoring, temperature
tracking, and automatic stat synchronization.

Modules:
    config      - Configuration loading and validation
    discord_rpc - Discord Rich Presence connection management
    hardware    - GPU detection and monitoring (Nvidia/AMD)
    logger      - Enhanced logging with timestamps and stack traces
    scraper     - Web scraping for FAH control interface and stats
    tray        - System tray icon and menu management
    main        - Application entry point and main loop

Usage:
    >>> from fahrpc import load_config, GPUMonitor, DiscordRPC
    >>> config = load_config()
    >>> gpu = GPUMonitor(config)
    >>> print(gpu.nvidia_count)

Author: Bandokii
AI Collaborator: GitHub Copilot
Version: 1.0.1
License: MIT
"""

__version__ = "1.0.1"
__author__ = "Bandokii"

from .config import APP_AUTHOR, APP_NAME, get_config_dir, get_log_path, load_config
from .discord_rpc import DiscordRPC
from .hardware import GPUMonitor
from .logger import setup_error_logging
from .scraper import FAHScraper
from .tray import TrayIcon, set_console_visibility

__all__ = [
    # Package metadata
    '__version__',
    '__author__',
    # Configuration
    'load_config',
    'get_config_dir',
    'get_log_path',
    'APP_NAME',
    'APP_AUTHOR',
    # Logging
    'setup_error_logging',
    # Hardware monitoring
    'GPUMonitor',
    # Web scraping
    'FAHScraper',
    # Discord integration
    'DiscordRPC',
    # System tray
    'TrayIcon',
    'set_console_visibility',
]
