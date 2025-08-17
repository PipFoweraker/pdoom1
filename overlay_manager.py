"""
DEPRECATED: This module has moved to pdoom1.ui.overlay_manager

This is a backwards-compatibility shim that re-exports the overlay manager
from its new location in the pdoom1.ui package. Please update your imports
to use the new location.

New import paths:
    from pdoom1.ui.overlay_manager import OverlayManager, UIElement, ZLayer, UIState
    from pdoom1.ui.overlay_manager import create_dialog, create_tooltip, create_modal
    
Or for convenience:
    from pdoom1.ui import OverlayManager, UIElement, ZLayer, UIState
    from pdoom1.ui import create_dialog, create_tooltip, create_modal
"""

import warnings
import sys

# Issue deprecation warning only once per process
if not hasattr(sys.modules[__name__], '_deprecation_warning_issued'):
    warnings.warn(
        "overlay_manager module has moved to pdoom1.ui.overlay_manager. "
        "Please update your imports to use the new location. "
        "This shim will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2
    )
    sys.modules[__name__]._deprecation_warning_issued = True

# Re-export everything from the new location
from pdoom1.ui.overlay_manager import *