'''
UI Configuration Helper

Small, focused module for UI configuration access patterns.
Reduces repetitive config access code throughout the codebase.
'''
from typing import Any, Optional, Dict


def should_show_tooltips(game_state: Any) -> bool:
    '''
    Check if tooltips should be displayed based on configuration.
    
    Args:
        game_state: Game state object with config
        
    Returns:
        bool: True if tooltips should be shown (default: False)
    '''
    if not game_state or not hasattr(game_state, 'config'):
        return False
    
    return game_state.config.get('ui', {}).get('show_tooltips', False)


def get_ui_config(game_state: Any, key: str, default: Any = None) -> Any:
    '''
    Get a UI configuration value with safe fallback.
    
    Args:
        game_state: Game state object with config
        key: Configuration key to retrieve
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    '''
    if not game_state or not hasattr(game_state, 'config'):
        return default
    
    return game_state.config.get('ui', {}).get(key, default)
