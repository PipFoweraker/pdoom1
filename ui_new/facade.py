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
        render_game_screen(screen, game_state, w, h)
    
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


# Global UI facade instance
ui_facade = UIFacade()