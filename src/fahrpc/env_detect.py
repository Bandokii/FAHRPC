from pathlib import Path
import sys
import os

def is_running_from_global_install():
    """
    Detects if the app is running from a global installation (pipx/uv tool install)
    or a temporary uvx run, using correct cross-platform paths.
    Returns True if running from global or temporary install, False otherwise.
    """
    exe_path = Path(sys.executable).resolve()
    home = Path.home()

    # Platform-specific paths
    if sys.platform == "win32":
        local_bin = home / ".local" / "bin"
        cache_dir = home / "AppData" / "Local" / "uv" / "cache"
    else:  # Unix-Like (Linux, macOS)
        local_bin = home / ".local" / "bin"
        cache_dir = home / ".cache" / "uv"
        # Respect XDG_CACHE_HOME if set
        if "XDG_CACHE_HOME" in os.environ:
            cache_dir = Path(os.environ["XDG_CACHE_HOME"]) / "uv"

    # Check for pipx / uv tool install
    if local_bin in exe_path.parents:
        return True

    # Check for uvx temporary run
    if cache_dir in exe_path.parents:
        return True

    return False

def find_project_root():
    """
    Find the project root by looking for pyproject.toml or .venv in parent directories.
    Returns the directory containing pyproject.toml if found, else None.
    """
    current = Path(__file__).resolve().parent
    root = Path(current.root)

    while current != root:
        if (current / "pyproject.toml").exists():
            return current
        if (current / ".venv").is_dir():
            # Optional: consider .venv alone as indicator (common with uv)
            return current
        current = current.parent
    return None
