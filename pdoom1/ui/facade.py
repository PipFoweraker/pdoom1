"""
UI Facade for P(Doom) - Stable interface for UI operations

This module provides a thin facade over the UI subsystem to enable future
refactoring while maintaining a stable external interface. The facade
currently wraps OverlayManager but can be extended to route to different
UI components as the system evolves.

Design principles:
- Thin wrapper with minimal logic
- Stable interface for main game and other components  
- Enables future UI modularisation without breaking callers
- UK spelling in documentation and comments
"""

import pygame
from typing import Optional
from .overlay_manager import OverlayManager


class UIFacade:
    """
    Thin facade providing a stable interface to the UI subsystem.
    
    This class wraps the internal OverlayManager and proxies common UI operations.
    Future UI refactoring can modify the internal implementation while preserving
    this external interface for stability.
    
    Features:
    - Element registration and lifecycle management
    - Event handling (mouse and keyboard)
    - Rendering and animation updates
    - Window management (bring to front, minimization)
    """
    
    def __init__(self, overlay_manager=None):
        """
        Initialise the UI facade with an overlay manager.
        
        Args:
            overlay_manager: Existing OverlayManager instance to use.
                           If None, creates a new internal instance.
        """
        self._overlay_manager = overlay_manager if overlay_manager is not None else OverlayManager()
    
    def register_element(self, element) -> bool:
        """
        Register a UI element with the overlay system.
        
        Args:
            element: UIElement to register
            
        Returns:
            bool: True if successful, False if ID already exists
        """
        return self._overlay_manager.register_element(element)
    
    def unregister_element(self, element_id: str) -> bool:
        """
        Remove a UI element from the overlay system.
        
        Args:
            element_id: ID of element to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        return self._overlay_manager.unregister_element(element_id)
    
    def bring_to_front(self, element_id: str) -> bool:
        """
        Bring a UI element to the front of its layer.
        
        Args:
            element_id: ID of element to bring forward
            
        Returns:
            bool: True if successful, False if element not found
        """
        return self._overlay_manager.bring_to_front(element_id)
    
    def render_elements(self, screen: pygame.Surface) -> None:
        """
        Render all visible UI elements to the screen.
        
        Args:
            screen: pygame surface to render to
        """
        self._overlay_manager.render_elements(screen)
    
    def update_animations(self) -> None:
        """Update all UI element animations."""
        self._overlay_manager.update_animations()
    
    def handle_mouse_event(self, event: pygame.event.Event, screen_w: int, screen_h: int) -> Optional[str]:
        """
        Handle mouse events for UI elements.
        
        Args:
            event: pygame mouse event
            screen_w, screen_h: Screen dimensions
            
        Returns:
            Optional[str]: ID of element that handled the event, if any
        """
        return self._overlay_manager.handle_mouse_event(event, screen_w, screen_h)
    
    def handle_keyboard_event(self, event: pygame.event.Event) -> bool:
        """
        Handle keyboard events for UI navigation and accessibility.
        
        Args:
            event: pygame keyboard event
            
        Returns:
            bool: True if event was handled by UI, False otherwise
        """
        return self._overlay_manager.handle_keyboard_event(event)
    
    def toggle_minimize(self, element_id: str) -> bool:
        """
        Toggle the minimization state of a UI element.
        
        Args:
            element_id: ID of element to toggle
            
        Returns:
            bool: True if successful, False if element not found
        """
        return self._overlay_manager.toggle_minimize(element_id)
    
    def render_game(self, screen, game_state, w, h) -> None:
        """
        Render the game HUD and overlay elements.
        
        This method coordinates rendering of the main game interface by calling
        the existing ui.draw_ui function and then delegating overlay rendering
        to the OverlayManager. This maintains identical behaviour to the original
        rendering code with no logic changes.
        
        Args:
            screen: pygame surface to render to
            game_state: GameState instance with current game data
            w: Screen width
            h: Screen height
        """
        # Import here to avoid circular dependencies
        from ui import draw_ui
        
        # Draw the main game UI using existing function
        draw_ui(screen, game_state, w, h)
        
        # Render overlay elements through the overlay manager
        self._overlay_manager.render_elements(screen)
    
    # Additional access methods for advanced usage
    
    @property
    def overlay_manager(self) -> OverlayManager:
        """
        Access to the internal overlay manager for advanced operations.
        
        Note: Direct access to internal components may change in future versions.
        Prefer using the facade methods when possible.
        """
        return self._overlay_manager