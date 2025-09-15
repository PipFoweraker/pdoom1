"""
User interface modules.

This module provides compatibility imports for the UI system during the
monolith breakdown transition. Individual modules can be imported directly:

- src.ui.dialogs: Dialog box functions
- src.ui.panels: Panel and context window functions  
- src.ui.context: Context information utilities
- src.ui.rendering: Text and graphics utilities
- src.ui.components: Small UI components
- src.ui.layout: Layout and positioning utilities
"""

# Re-export all functions from the main ui.py for now (compatibility layer)
# TODO: Remove this once all imports are updated to modular structure
# NOTE: Avoiding direct imports from extracted modules to prevent circular imports
from ui import *