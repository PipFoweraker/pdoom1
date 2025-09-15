"""
Backwards-compatible facade for overlay manager imports.

This module provides compatibility imports so existing code continues to work
while we gradually migrate to the new UI structure.
"""

# Import from the new location but expose with old interface
from pdoom1.ui.overlay_manager import (
    OverlayManager,
    UIElement, 
    ZLayer,
    UIState,
    create_dialog,
    create_tooltip, 
    create_modal
)

# Keep all the same exports so existing imports don't break
__all__ = [
    'OverlayManager',
    'UIElement',
    'ZLayer', 
    'UIState',
    'create_dialog',
    'create_tooltip',
    'create_modal'
]
