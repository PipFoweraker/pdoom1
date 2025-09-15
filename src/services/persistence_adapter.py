"""Persistence Adapter for Legacy File Migration

This module provides simple adapters to gradually migrate from legacy file paths
to the new data directory system without breaking existing code.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from src.services.data_directory import get_data_manager

# Legacy file mappings for common files
LEGACY_FILES = {
    'onboarding_progress.json': 'onboarding_progress.json',
    'tutorial_settings.json': 'tutorial_settings.json', 
    'local_highscore.json': 'leaderboards/local_highscore.json',
    'configs/default.json': 'configs/default.json'
}


def get_file_path(filename: str) -> Path:
    """
    Get the appropriate path for a file, handling legacy migration.
    
    This is a drop-in replacement for constructing file paths in the game.
    Instead of: open("onboarding_progress.json", "r")
    Use:        open(get_file_path("onboarding_progress.json"), "r")
    """
    data_manager = get_data_manager()
    
    # Check if this is a known legacy file
    if filename in LEGACY_FILES:
        new_filename = LEGACY_FILES[filename]
        return data_manager.migrate_file_if_needed(new_filename)
    
    # For new files, use the new data directory directly
    return data_manager.get_data_path(filename)


def load_json_file(filename: str, default: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Load a JSON file with legacy path support.
    
    Args:
        filename: Name of the JSON file
        default: Default value if file doesn't exist or can't be read
        
    Returns:
        Parsed JSON data or default value
    """
    if default is None:
        default = {}
        
    file_path = get_file_path(filename)
    
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        # Log error but don't crash
        import logging
        logging.warning(f"Could not load {filename}: {e}")
    
    return default


def save_json_file(filename: str, data: Dict[str, Any], 
                   create_directories: bool = True) -> bool:
    """
    Save data to a JSON file with legacy path support.
    
    Args:
        filename: Name of the JSON file
        data: Data to save
        create_directories: Whether to create parent directories
        
    Returns:
        True if successful, False otherwise
    """
    file_path = get_file_path(filename)
    
    try:
        if create_directories:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
        
    except (PermissionError, OSError) as e:
        # Log error but don't crash
        import logging
        logging.error(f"Could not save {filename}: {e}")
        return False


# Convenience functions for common files
def get_onboarding_progress() -> Dict[str, Any]:
    """Load onboarding progress with migration support."""
    return load_json_file('onboarding_progress.json', {
        'tutorial_enabled': True,
        'is_first_time': True,
        'completed_steps': [],
        'seen_mechanics': [],
        'tutorial_dismissed': False
    })


def save_onboarding_progress(progress: Dict[str, Any]) -> bool:
    """Save onboarding progress with migration support."""
    return save_json_file('onboarding_progress.json', progress)


def get_tutorial_settings() -> Dict[str, Any]:
    """Load tutorial settings with migration support."""
    return load_json_file('tutorial_settings.json', {
        'tutorial_enabled': True,
        'tutorial_shown_milestones': [],
        'first_game_launch': True
    })


def save_tutorial_settings(settings: Dict[str, Any]) -> bool:
    """Save tutorial settings with migration support."""
    return save_json_file('tutorial_settings.json', settings)


def get_local_highscore() -> Dict[str, Any]:
    """Load local highscore with migration support."""
    return load_json_file('local_highscore.json', {})


def save_local_highscore(scores: Dict[str, Any]) -> bool:
    """Save local highscore with migration support."""
    return save_json_file('local_highscore.json', scores)
