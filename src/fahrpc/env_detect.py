# Cache project root in a global variable

# Sentinel object to distinguish between uninitialized and None
_PROJECT_ROOT = None

def get_project_root():
    global _PROJECT_ROOT
    if _PROJECT_ROOT is None:
        result = find_project_root()
        _PROJECT_ROOT = result if isinstance(result, Path) else None
    return _PROJECT_ROOT
import os
import sys
from pathlib import Path


def find_project_root():
    """
    Returns the current working directory as project root if pyproject.toml exists and its project.name matches 'fahrpc'.
    Returns None otherwise.
    """
    import tomllib
    cwd = Path(os.getcwd())
    pyproject_path = cwd / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with pyproject_path.open("rb") as f:
                pyproject = tomllib.load(f)
            project_name = pyproject.get("project", {}).get("name")
            if project_name == "fahrpc":
                return cwd
        except Exception:
            pass
    return None
