"""
UI Screens Package - Screen management and routing

This package contains screen implementations for different UI states in P(Doom).
Screens are responsible for rendering specific parts of the game interface while
maintaining consistent contracts through the base Screen protocol.

Current implementations:
- GameHudScreen: Main game HUD (resources, actions, upgrades, overlays)
- Function-based screens: main_menu, loading, audio_menu (migrated from ui.py)

Screen responsibilities:
- Render specific UI state to pygame surface
- Handle screen-specific input events
- Update animations and time-based state
- Maintain consistent interface through Screen protocol

Design principles:
- Lightweight screens with minimal logic
- Delegation to existing systems (ui.py, OverlayManager)
- No behavioural changes during refactoring
- UK spelling in documentation and comments
"""

from .base import Screen
from .game_hud import GameHudScreen

# Function-based screen implementations (migrated from ui.py)
from .main_menu import draw_main_menu
from .loading import draw_loading_screen
from .audio_menu import draw_audio_menu

__all__ = [
    'Screen',
    'GameHudScreen',
    # Function exports for backwards compatibility
    'draw_main_menu',
    'draw_loading_screen',
    'draw_audio_menu'
]