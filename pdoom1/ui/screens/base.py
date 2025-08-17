"""
Base Screen Protocol for P(Doom) UI System

This module defines the base screen protocol that all UI screens should implement.
Screens are responsible for rendering specific parts of the game UI (main menu, HUD, 
loading screens, etc.) while maintaining consistent interfaces.

Design principles:
- Lightweight protocol with minimal requirements
- Consistent render contract across all screens
- UK spelling in documentation
"""

import pygame
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class Screen(ABC):
    """
    Base screen protocol for P(Doom) UI screens.
    
    All screen implementations should inherit from this class and implement
    the render method. Screens are responsible for drawing specific UI states
    (game HUD, main menu, loading, etc.) with consistent behaviour.
    
    The render contract ensures all screens can be used interchangeably
    through the UIFacade routing system.
    """
    
    @abstractmethod
    def render(self, screen: pygame.Surface, **kwargs) -> None:
        """
        Render this screen to the provided pygame surface.
        
        Args:
            screen: pygame surface to render to
            **kwargs: Screen-specific parameters (game_state, dimensions, etc.)
            
        Note:
            Implementations should be defensive about missing kwargs and
            provide sensible defaults where possible.
        """
        pass
    
    def update(self, dt: float) -> None:
        """
        Update screen animations and state.
        
        Args:
            dt: Delta time since last update in seconds
            
        Note:
            Default implementation does nothing. Override if screen
            needs animation or time-based updates.
        """
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events for this screen.
        
        Args:
            event: pygame event to handle
            
        Returns:
            bool: True if event was handled, False to pass to next handler
            
        Note:
            Default implementation does nothing. Override if screen
            needs to handle input events directly.
        """
        return False