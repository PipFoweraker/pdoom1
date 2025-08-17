"""
UI Package for P(Doom) - Modular UI Components and Overlay Management

This package provides the UI layer for P(Doom), featuring:
- Modular overlay management with z-order control
- UI components and primitives
- Screen management and routing
- Visual feedback systems

The overlay manager has been moved here from the top level but is re-exported
for backward compatibility.
"""

from .overlay_manager import OverlayManager, UIElement, ZLayer, UIState
from .overlay_manager import create_dialog, create_tooltip, create_modal
from .facade import UIFacade

# Backwards compatibility: re-export screen functions during migration
# TODO: Remove these after internal migration to UIFacade is complete
from .screens.main_menu import draw_main_menu
from .screens.loading import draw_loading_screen  
from .screens.audio_menu import draw_audio_menu
from .screens.seed_selection import draw_seed_selection

__all__ = [
    'OverlayManager',
    'UIElement', 
    'ZLayer',
    'UIState',
    'create_dialog',
    'create_tooltip', 
    'create_modal',
    'UIFacade',
    # Backwards compatibility exports - TODO: Remove after migration
    'draw_main_menu',
    'draw_loading_screen',
    'draw_audio_menu',
    'draw_seed_selection'
]