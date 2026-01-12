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
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from platformdirs import user_config_dir

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
    from fahrpc.env_detect import get_project_root
    project_root = get_project_root()
    if project_root is not None:
        config_json = project_root / "config.json"
        pyproject = project_root / "pyproject.toml"
        if config_json.exists() and pyproject.exists():
            return project_root
    # Fallback: use platformdirs config dir
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


def load_default_config() -> Dict[str, Any]:
    default_path = os.path.join(os.path.dirname(__file__), "data", "default_config.json")
    with open(default_path, "r") as f:
        return json.load(f)

DEFAULT_CONFIG = load_default_config()
def diff_dicts(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively return only the keys in user that differ from default.
    """
    diff = {}
    for key, value in user.items():
        if key not in default:
            diff[key] = value
        elif isinstance(value, dict) and isinstance(default[key], dict):
            subdiff = diff_dicts(default[key], value)
            if subdiff:
                diff[key] = subdiff
        elif value != default[key]:
            diff[key] = value
    return diff


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
        logger.info("[CONFIG] Creating minimal configuration file")
        print(f"Config file not found. Creating minimal config at: {config_path}")
        # Ensure parent directory exists
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        # Save an empty config file (user can fill in overrides)
        with open(config_path, 'w') as f:
            json.dump({}, f, indent=2)
            logger.info("[CONFIG] Empty configuration file written")
        return DEFAULT_CONFIG

    except json.JSONDecodeError as e:
        logger.error(f"[CONFIG] JSON parsing error: {e}", exc_info=True)
        print(f"Error parsing config file: {e}")
        print("Using default configuration.")
        logger.info("[CONFIG] Falling back to default configuration")
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """
    Save only the keys that differ from defaults to config.json.
    """
    if config_path is None:
        config_path = str(get_config_path())
    diff = diff_dicts(DEFAULT_CONFIG, config)
    Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(diff, f, indent=2)
