"""
UI Screens Package - Screen management and routing

This package contains screen implementations for different UI states in P(Doom).
Screens are responsible for rendering specific parts of the game interface while
maintaining consistent contracts through the base Screen protocol.

Current implementations:
- GameHudScreen: Main game HUD (resources, actions, upgrades, overlays)
- MainMenuScreen: Main menu interface (TODO: stub for future implementation)
- LoadingScreen: Progress and loading display (TODO: stub for future implementation)  
- AudioMenuScreen: Audio settings menu (TODO: stub for future implementation)

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
from .main_menu import MainMenuScreen
from .loading import LoadingScreen
from .audio_menu import AudioMenuScreen

__all__ = [
    'Screen',
    'GameHudScreen', 
    'MainMenuScreen',
    'LoadingScreen',
    'AudioMenuScreen'
]