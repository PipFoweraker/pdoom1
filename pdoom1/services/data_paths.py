"""
Cross-platform data directory management for PDoom1.

Provides consistent data storage location across Windows, macOS, and Linux.
Uses appdirs for platform-appropriate directories.
"""

import os
import sys
from pathlib import Path


def get_data_dir() -> Path:
    """
    Get the platform-appropriate data directory for PDoom1.
    
    Returns:
        Path: Directory for storing user data (settings, scores, logs)
        
    Examples:
        Windows: %APPDATA%/pdoom1/
        macOS: ~/Library/Application Support/pdoom1/
        Linux: ~/.local/share/pdoom1/
    """
    # Check for data directory override (highest precedence)
    data_dir_override = os.environ.get("PDOOM1_DATA_DIR")
    if data_dir_override:
        data_dir = Path(data_dir_override)
        ensure_dir(data_dir)
        return data_dir
    
    # Check for test override
    test_data_dir = os.environ.get("PDOOM1_TEST_DATA_DIR")
    if test_data_dir:
        data_dir = Path(test_data_dir)
        ensure_dir(data_dir)
        return data_dir
    
    if sys.platform == "win32":
        # Windows: Use APPDATA with fallback
        base = os.environ.get("APPDATA")
        if not base:
            base = str(Path.home() / "AppData" / "Roaming")
        data_dir = Path(base) / "pdoom1"
    elif sys.platform == "darwin":
        # macOS: Use Application Support
        data_dir = Path.home() / "Library" / "Application Support" / "pdoom1"
    else:
        # Linux/Unix: Use XDG Base Directory Specification
        xdg_data_home = os.environ.get("XDG_DATA_HOME", "")
        if xdg_data_home:
            data_dir = Path(xdg_data_home) / "pdoom1"
        else:
            data_dir = Path.home() / ".local" / "share" / "pdoom1"
    
    # Ensure directory exists
    ensure_dir(data_dir)
    
    return data_dir


def ensure_dir(path: Path) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
    """
    path.mkdir(parents=True, exist_ok=True)


def get_save_dir() -> Path:
    """Get the directory for save files."""
    save_dir = get_data_dir() / "saves"
    ensure_dir(save_dir)
    return save_dir


def get_log_dir() -> Path:
    """Get the directory for log files."""
    log_dir = get_data_dir() / "logs"
    ensure_dir(log_dir)
    return log_dir


def get_settings_file() -> Path:
    """Get the full path to the settings file."""
    return get_data_dir() / "settings.json"


def get_leaderboard_file() -> Path:
    """Get the full path to the local leaderboard file."""
    return get_data_dir() / "leaderboard.json"


def get_logs_dir() -> Path:
    """Get the directory for log files."""
    return get_log_dir()  # Alias for backwards compatibility