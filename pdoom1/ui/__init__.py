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

__all__ = [
    'OverlayManager',
    'UIElement', 
    'ZLayer',
    'UIState',
    'create_dialog',
    'create_tooltip', 
    'create_modal',
    'UIFacade'
]