"""
User interface modules.

This module provides compatibility imports for the UI system during the
monolith breakdown transition. Individual modules can be imported directly:

- src.ui.dialogs: Dialog box functions (EXTRACTED)
- src.ui.panels: Panel and context window functions (EXTRACTED)
- src.ui.rendering: Text and graphics utilities (EXTRACTED) 
- src.ui.tutorials: Tutorial overlays and help systems (EXTRACTED)
- src.ui.context: Context information utilities
- src.ui.components: Small UI components
- src.ui.layout: Layout and positioning utilities
- src.ui.forms: Form and input dialogs (TODO)
- src.ui.game_ui: Core game UI functions (TODO) 
- src.ui.screens: Menu and screen functions (TODO)
"""

# Re-export all functions from the main ui.py for now (compatibility layer)
# TODO: Remove this once all imports are updated to modular structure
# NOTE: Avoiding direct imports from extracted modules to prevent circular imports
from ui import *

# Import extracted modules for direct access
from . import dialogs
from . import panels  
from . import rendering
from . import tutorials