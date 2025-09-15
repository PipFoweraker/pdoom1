"""
UIFacade for P(Doom) - Central routing system for UI screens.

Provides a unified interface for rendering different game screens while maintaining
modular architecture. Routes screen rendering to appropriate modules.
"""

import pygame
from typing import Optional, Any
from .screens.game import render_game_screen


class UIFacade:
    """
    Central facade for UI rendering and management.
    
    Routes rendering calls to appropriate screen modules and manages
    the overall UI state and transitions.
    """
    
    def __init__(self):
        """Initialize the UI facade."""
        self.current_screen = None
        self.transition_state = None
        
    def render_game(self, screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
        """
        Render the main in-game screen.
        
        Args:
            screen: The pygame surface to render on
            game_state: Current game state object
            w: Screen width
            h: Screen height
        """
        # Check if 3-column layout is enabled
        use_three_column = False
        if hasattr(game_state, 'config') and game_state.config:
            ui_config = game_state.config.get('ui', {})
            use_three_column = ui_config.get('enable_three_column_layout', False)
        
        if use_three_column:
            # Use new 3-column layout
            render_game_screen(screen, game_state, w, h)
        else:
            # Fall back to legacy UI
            self._render_legacy_game_screen(screen, game_state, w, h)
    
    def _render_legacy_game_screen(self, screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
        """Render using the legacy UI system."""
        # Import legacy function
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from ui import draw_ui
        draw_ui(screen, game_state, w, h)
    
    def render_main_menu(self, screen: pygame.Surface, w: int, h: int, **kwargs) -> None:
        """
        Render the main menu screen.
        
        Args:
            screen: The pygame surface to render on
            w: Screen width
            h: Screen height
            **kwargs: Additional menu-specific parameters
        """
        # Import legacy function for now - will be migrated later
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from ui import draw_main_menu
        draw_main_menu(screen, w, h, **kwargs)
    
    def render_end_game_menu(self, screen: pygame.Surface, w: int, h: int, 
                           game_state: Any, **kwargs) -> None:
        """
        Render the end game menu screen.
        
        Args:
            screen: The pygame surface to render on
            w: Screen width
            h: Screen height
            game_state: Final game state
            **kwargs: Additional menu-specific parameters
        """
        # Import legacy function for now - will be migrated later
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from ui import draw_end_game_menu
        draw_end_game_menu(screen, w, h, game_state, **kwargs)
    
    def render_settings(self, screen: pygame.Surface, w: int, h: int, **kwargs) -> None:
        """
        Render the settings screen.
        
        Args:
            screen: The pygame surface to render on
            w: Screen width
            h: Screen height
            **kwargs: Additional settings-specific parameters
        """
        # Import legacy function for now - will be migrated later
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from ui import draw_pre_game_settings
        draw_pre_game_settings(screen, w, h, **kwargs)
    
    def set_current_screen(self, screen_name: str) -> None:
        """
        Set the current active screen.
        
        Args:
            screen_name: Name of the screen to set as current
        """
        self.current_screen = screen_name
    
    def get_current_screen(self) -> Optional[str]:
        """Get the name of the currently active screen."""
        return self.current_screen


def should_use_three_column_layout() -> bool:
    """
    Check if the 3-column layout should be used.
    
    Returns:
        bool: True if 3-column layout is enabled in configuration
    """
    try:
        from src.core.config_manager import config_manager
        ui_config = config_manager.get('ui', {})
        return ui_config.get('enable_three_column_layout', True)  # Default to True for v0.2.1
    except ImportError:
        # Fallback if config system not available
        return True


# Global UI facade instance
ui_facade = UIFacade()