"""
Import manager for main.py to organize and optimize imports.

This module consolidates all imports for main.py in a cleaner, more maintainable way.
Part of the internal polish phase to improve code organization.
"""

# Standard library imports

# Third-party imports
import pygame

# Core game imports
from src.core.game_state import GameState

# UI system imports
from ui import (
    draw_scoreboard, draw_main_menu, draw_overlay
)
from ui_new.facade import ui_facade
from src.ui.overlay_manager import OverlayManager

# Service imports
from src.services.bug_reporter import BugReporter
from src.services.version import get_display_version
from src.services.config_manager import (
    initialize_config_system, get_current_config, config_manager
)
from src.services.sound_manager import SoundManager

# Feature imports
from src.features.onboarding import onboarding
from src.features.event_system import EventAction

# Menu system imports
from src.ui.menu_handlers.menu_system import (
    NavigationManager, MenuClickHandler, MenuKeyboardHandler,
    get_weekly_seed, load_markdown_file
)


def initialize_systems():
    """Initialize all game systems and return configuration."""
    # Initialize config system on startup
    initialize_config_system()
    current_config = get_current_config()
    
    # Initialize global sound manager for menu use
    global_sound_manager = SoundManager()
    
    # Ensure audio section exists in config
    if 'audio' not in current_config:
        current_config['audio'] = {}
    if 'sound_enabled' not in current_config['audio']:
        current_config['audio']['sound_enabled'] = True
        
    if current_config.get('audio', {}).get('sound_enabled', True):
        global_sound_manager.set_enabled(True)
    else:
        global_sound_manager.set_enabled(False)
    
    return current_config, global_sound_manager


def initialize_display(current_config):
    """Initialize pygame display based on configuration."""
    pygame.init()
    
    # Set up initial screen for loading
    info = pygame.display.Info()
    ui_config = current_config.get('ui', {})
    window_scale = ui_config.get('window_scale', 0.8)
    fullscreen_enabled = ui_config.get('fullscreen', False)
    
    if fullscreen_enabled:
        screen_w = info.current_w
        screen_h = info.current_h
        screen = pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN)
    else:
        screen_w = int(1200 * window_scale)
        screen_h = int(800 * window_scale)
        screen = pygame.display.set_mode((screen_w, screen_h))
    
    pygame.display.set_caption(f"P(Doom): Bureaucracy Strategy Game {get_display_version()}")
    
    return screen, screen_w, screen_h


# Export commonly used functions and classes
__all__ = [
    # Core modules
    'pygame', 'GameState', 'ui_facade',
    
    # UI functions (selected commonly used ones)
    'draw_main_menu', 'draw_scoreboard', 'draw_overlay',
    
    # Services
    'BugReporter', 'get_display_version', 'config_manager',
    'SoundManager', 'OverlayManager',
    
    # Features
    'onboarding', 'EventAction',
    
    # Menu system
    'NavigationManager', 'MenuClickHandler', 'MenuKeyboardHandler',
    'get_weekly_seed', 'load_markdown_file',
    
    # Initialization functions
    'initialize_systems', 'initialize_display'
]
