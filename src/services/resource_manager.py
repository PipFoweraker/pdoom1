"""
Resource Manager - Handles asset loading for both development and PyInstaller environments

This module provides functionality for:
- Detecting PyInstaller bundled environment
- Resolving asset paths for both development and distribution
- Centralizing resource loading logic
- Maintaining compatibility across deployment methods
"""

import os
import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource for both development and PyInstaller environments.
    
    Args:
        relative_path: Path relative to project root (e.g., 'assets/lab_names.csv')
        
    Returns:
        str: Absolute path to the resource
        
    Examples:
        >>> get_resource_path('assets/lab_names.csv')
        '/path/to/project/assets/lab_names.csv'  # Development
        >>> get_resource_path('assets/lab_names.csv') 
        '/tmp/_MEI123/assets/lab_names.csv'      # PyInstaller bundle
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = str(getattr(sys, '_MEIPASS'))
    else:
        # Development environment - use current working directory
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def get_asset_path(asset_file: str) -> str:
    """
    Get path to asset file in assets/ directory.
    
    Args:
        asset_file: Filename in assets directory (e.g., 'lab_names.csv')
        
    Returns:
        str: Full path to asset file
    """
    return get_resource_path(f"assets/{asset_file}")


def get_config_path(config_file: str) -> str:
    """
    Get path to config file in configs/ directory.
    
    Args:
        config_file: Config filename (e.g., 'default.template.json')
        
    Returns:
        str: Full path to config file
    """
    return get_resource_path(f"configs/{config_file}")


def resource_exists(relative_path: str) -> bool:
    """
    Check if a resource exists.
    
    Args:
        relative_path: Path relative to project root
        
    Returns:
        bool: True if resource exists, False otherwise
    """
    try:
        path = get_resource_path(relative_path)
        return os.path.exists(path)
    except Exception:
        return False


def is_bundled_environment() -> bool:
    """
    Check if running in a PyInstaller bundle.
    
    Returns:
        bool: True if running in PyInstaller bundle, False in development
    """
    return hasattr(sys, '_MEIPASS')


def get_user_data_directory() -> Path:
    """
    Get user data directory for saves, configs, and logs.
    This is always in the user's home directory, never bundled.
    
    Returns:
        Path: User data directory path
    """
    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('APPDATA', Path.home()))
    else:  # macOS/Linux
        base_dir = Path.home() / '.local' / 'share'
    
    return base_dir / 'PDoom'


# Initialize user data directory on import
def _ensure_user_data_directory():
    """Ensure user data directory exists"""
    user_dir = get_user_data_directory()
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (user_dir / 'configs').mkdir(exist_ok=True)
    (user_dir / 'saves').mkdir(exist_ok=True)
    (user_dir / 'logs').mkdir(exist_ok=True)
    (user_dir / 'leaderboards').mkdir(exist_ok=True)


# Initialize on module import
_ensure_user_data_directory()
