"""
Configuration module for FAHRPC
Handles loading, validating, and managing config.json
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger('FAHRPC')
DEFAULT_CONFIG = {
    "discord": {
        "client_id": "1457701520673079501",
        "buttons": [
            {"label": "Start Folding", "url": "https://foldingathome.org/start-folding/"},
            {"label": "Github", "url": "https://github.com/Bandokii/FAHRPC"}
        ]
    },
    "foldingathome": {
        "web_url": "http://localhost:7396/",
        "stats_url": "https://v8-5.foldingathome.org/stats",
        "update_interval": 15
    },
    "temperature": {
        "thresholds": {"low": 65, "medium": 75},
        "colors": {"low": "green", "medium": "orange", "high": "red"}
    },
    "display": {
        "start_hidden": True,
        "show_header": True,
        "icon_file": "FAHRPC.png"
    },
    "hardware": {
        "nvidia": {"enabled": True, "strip_prefix": "NVIDIA GeForce "},
        "amd": {"enabled": True, "strip_prefix": "AMD Radeon "}
    },
    "logging": {
        "error_log_file": "fah_error_log.txt",
        "suppress_asyncio_warnings": True
    }
}

def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries.
    
    Args:
        base: Base dictionary (lower priority)
        override: Override dictionary (higher priority)
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def validate_config(config: Dict[str, Any]) -> tuple[bool, list[str]]:
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

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration from JSON file with fallback to defaults.
    
    Creates default config file if it doesn't exist and validates on load.
    
    Args:
        config_path: Path to config.json file
        
    Returns:
        Merged configuration dictionary
        
    Raises:
        SystemExit: If config validation fails
    """
    try:
        with open(config_path, 'r') as f:
            user_config = json.load(f)
            merged = merge_dicts(DEFAULT_CONFIG, user_config)
            
            # Validate configuration
            is_valid, errors = validate_config(merged)
            if not is_valid:
                for error in errors:
                    print(f"[CONFIG ERROR] {error}")
                raise SystemExit(1)
            
            return merged
    except FileNotFoundError:
        print(f"Config file '{config_path}' not found. Creating default config...")
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return DEFAULT_CONFIG
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}")
        print("Using default configuration.")
        return DEFAULT_CONFIG

def get_config() -> Dict[str, Any]:
    """
    Get the global configuration instance.
    
    Returns:
        Configuration dictionary
    """
    return load_config()
