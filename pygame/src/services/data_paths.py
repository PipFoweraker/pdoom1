'''
Cross-platform data directory management for PDoom1.

Provides consistent data storage location across Windows, macOS, and Linux.
Uses appdirs for platform-appropriate directories.
'''

import os
import sys
from pathlib import Path


def get_data_dir() -> Path:
    '''
    Get the platform-appropriate data directory for PDoom1.
    
    Returns:
        Path: Directory for storing user data (settings, scores, logs)
        
    Examples:
        Windows: %APPDATA%/PDoom1/
        macOS: ~/Library/Application Support/PDoom1/
        Linux: ~/.local/share/pdoom1/
    '''
    # Check for test override
    test_data_dir = os.environ.get('PDOOM1_TEST_DATA_DIR')
    if test_data_dir:
        data_dir = Path(test_data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    if sys.platform == 'win32':
        # Windows: Use APPDATA
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
        data_dir = Path(base) / 'PDoom1'
    elif sys.platform == 'darwin':
        # macOS: Use Application Support
        data_dir = Path.home() / 'Library' / 'Application Support' / 'PDoom1'
    else:
        # Linux/Unix: Use XDG Base Directory Specification
        xdg_data_home = os.environ.get('XDG_DATA_HOME', '')
        if xdg_data_home:
            data_dir = Path(xdg_data_home) / 'pdoom1'
        else:
            data_dir = Path.home() / '.local' / 'share' / 'pdoom1'
    
    # Ensure directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    
    return data_dir


def get_settings_file() -> Path:
    '''Get the full path to the settings file.'''
    return get_data_dir() / 'settings.json'


def get_leaderboard_file() -> Path:
    '''Get the full path to the local leaderboard file.'''
    return get_data_dir() / 'leaderboard.json'


def get_logs_dir() -> Path:
    '''Get the directory for log files.'''
    logs_dir = get_data_dir() / 'logs'
    logs_dir.mkdir(exist_ok=True)
    return logs_dir