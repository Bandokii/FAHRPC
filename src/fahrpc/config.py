"""
Configuration Module for FAHRPC
==============================

Handles all configuration management including:
- Loading user configuration from platform-specific directories
- Merging user settings with sensible defaults
- Validating required configuration keys
- Creating default config files for new users

Configuration file locations (managed by platformdirs):
    Windows: %LOCALAPPDATA%\\Bandokii\\fahrpc\\config.json
    macOS:   ~/Library/Application Support/fahrpc/config.json
    Linux:   ~/.config/fahrpc/config.json

Example usage:
    >>> from fahrpc.config import load_config, get_config_dir
    >>> config = load_config()
    >>> print(config['discord']['client_id'])
    >>> print(get_config_dir())
"""

import json
import logging
from platformdirs import user_config_dir
from fahrpc.env_detect import is_running_from_global_install, find_project_root
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# Application Metadata
# ============================================================================
# These constants are used by platformdirs to determine config locations
# and are exported for use by other modules (logging, tray, etc.)

APP_NAME = "fahrpc"      # Application identifier (lowercase, no spaces)
APP_AUTHOR = "Bandokii"  # Author/organization name for directory structure

logger = logging.getLogger(APP_NAME.upper())


# ============================================================================
# Path Resolution Functions
# ============================================================================

def get_config_dir() -> Path:
    """
    Determine the config directory location:
    - If running from project root (pyproject.toml and config.json present), use project root.
    - Otherwise, use platformdirs user config directory.
    Returns:
        Path to the config directory (creates it if it doesn't exist)
    """
    project_root = find_project_root()
    if project_root is not None:
        # Only use project root if config.json and pyproject.toml are present
        config_json = project_root / "config.json"
        pyproject = project_root / "pyproject.toml"
        if config_json.exists() and pyproject.exists():
            config_dir = project_root
            config_dir.mkdir(parents=True, exist_ok=True)
            return config_dir

    # Otherwise, use user config dir (platformdirs)
    config_dir = Path(user_config_dir(APP_NAME, APP_AUTHOR))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """
    Get the full path to the config.json file.

    Returns:
        Path to config.json in the appropriate config directory
    """
    return get_config_dir() / 'config.json'


def get_log_path(filename: str = "fah_error_log.txt") -> Path:
    """
    Get the full path to a log file in the project directory.

    Args:
        filename: Name of the log file

    Returns:
        Path to the log file in the project directory
    """
    return get_config_dir() / filename


# ============================================================================
# Default Configuration
# ============================================================================
# This configuration is used when no config.json exists or as a base for
# merging with user settings. All values here are sensible defaults.

DEFAULT_CONFIG = {
    # Discord Rich Presence settings
    "discord": {
        "client_id": "1457701520673079501",  # FAHRPC Discord Application ID
        "buttons": [
            {"label": "Start Folding", "url": "https://foldingathome.org/start-folding/"},
            {"label": "GitHub", "url": "https://github.com/Bandokii/FAHRPC"}
        ]
    },
    # Folding@Home connection settings
    "foldingathome": {
        "web_url": "http://localhost:7396/",  # Only supports local Folding@Home client
        "stats_url": "https://v8-5.foldingathome.org/stats",  # Global stats page
        "update_interval": 15  # Seconds between Discord/console updates
    },
    # Temperature display thresholds and colors
    "temperature": {
        "thresholds": {"low": 65, "medium": 75},  # °C thresholds
        "colors": {"low": "green", "medium": "orange", "high": "red"}  # ANSI colors
    },
    # Display and UI settings
    "display": {
        "start_hidden": True,   # Hide console on startup (tray only)
        "show_header": True,    # Show ASCII art header
        "icon_file": "FAHRPC.png"  # Tray icon filename
    },
    # GPU monitoring settings
    "hardware": {
        "nvidia": {"enabled": True, "strip_prefix": "NVIDIA GeForce "},
        "amd": {"enabled": True, "strip_prefix": "AMD Radeon "}
    },
    # Logging settings
    "logging": {
        "error_log_file": "fah_error_log.txt",  # Log filename in config dir
        "suppress_asyncio_warnings": True  # Filter noisy async warnings
    }
}


# ============================================================================
# Configuration Helper Functions
# ============================================================================

def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries.

    User config values override defaults, but missing keys fall back to defaults.
    Nested dictionaries are merged recursively rather than replaced wholesale.

    Args:
        base: Base dictionary (lower priority - defaults)
        override: Override dictionary (higher priority - user config)

    Returns:
        Merged dictionary with all keys from both inputs
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate required config keys are present.

    Args:
        config: Configuration dictionary to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    required_keys = {
        'discord.client_id': ['discord', 'client_id'],
        'foldingathome.web_url': ['foldingathome', 'web_url'],
        'temperature.thresholds': ['temperature', 'thresholds'],
        'hardware': ['hardware'],
        'logging.error_log_file': ['logging', 'error_log_file']
    }

    errors = []
    for key_name, key_path in required_keys.items():
        value = config
        try:
            for path in key_path:
                value = value[path]
        except (KeyError, TypeError):
            errors.append(f"Missing required config key: {key_name}")

    return len(errors) == 0, errors

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from JSON file with fallback to defaults.

    Creates default config file if it doesn't exist and validates on load.

    Args:
        config_path: Path to config.json file (uses default location if None)

    Returns:
        Merged configuration dictionary

    Raises:
        SystemExit: If config validation fails
    """
    # Use platform-appropriate config path if not specified
    if config_path is None:
        config_path = str(get_config_path())

    logger.debug(f"[CONFIG] Loading configuration from: {config_path}")

    try:
        with open(config_path, 'r') as f:
            logger.debug("[CONFIG] Config file found, parsing JSON")
            user_config = json.load(f)
            logger.debug(f"[CONFIG] User config keys: {list(user_config.keys())}")
            merged = merge_dicts(DEFAULT_CONFIG, user_config)
            logger.debug("[CONFIG] Configuration merged successfully")

            # Validate configuration
            is_valid, errors = validate_config(merged)
            if not is_valid:
                logger.error(f"[CONFIG] Configuration validation failed: {errors}")
                for error in errors:
                    print(f"[CONFIG ERROR] {error}")
                raise SystemExit(1)

            logger.info("[CONFIG] Configuration loaded and validated successfully")
            logger.debug(f"[CONFIG] Foldingathome endpoint: {merged['foldingathome']['web_url']}")
            logger.debug(f"[CONFIG] Discord client ID: {merged['discord']['client_id']}")
            logger.debug(f"[CONFIG] Update interval: {merged['foldingathome']['update_interval']}s")
            logger.debug(f"[CONFIG] Nvidia enabled: {merged['hardware']['nvidia']['enabled']}")
            logger.debug(f"[CONFIG] AMD enabled: {merged['hardware']['amd']['enabled']}")
            return merged
    except FileNotFoundError:
        logger.info(f"[CONFIG] Config file not found at {config_path}")
        logger.info("[CONFIG] Creating default configuration")
        print(f"Config file not found. Creating default config at: {config_path}")
        # Ensure parent directory exists
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"[CONFIG] Created config directory: {Path(config_path).parent}")
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
            logger.info("[CONFIG] Default configuration file written")
        return DEFAULT_CONFIG
    except json.JSONDecodeError as e:
        logger.error(f"[CONFIG] JSON parsing error: {e}", exc_info=True)
        print(f"Error parsing config file: {e}")
        print("Using default configuration.")
        logger.info("[CONFIG] Falling back to default configuration")
        return DEFAULT_CONFIG
