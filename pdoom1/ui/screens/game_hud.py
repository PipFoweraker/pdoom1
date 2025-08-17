"""
Game HUD Screen for P(Doom)

This module implements the GameHudScreen that renders the main game interface.
It acts as a thin wrapper over the existing ui.draw_ui function and delegates
overlay rendering to the OverlayManager.

This screen is responsible for:
- Drawing the main game HUD (resources, actions, upgrades, etc.)
- Coordinating with OverlayManager for UI overlays
- Maintaining the existing game UI behaviour with no logic changes
"""

import pygame
from typing import Optional
from .base import Screen


class GameHudScreen(Screen):
    """
    Screen implementation for the main game HUD.
    
    This screen wraps the existing ui.draw_ui functionality and delegates
    overlay rendering to the OverlayManager. It maintains the exact same
    rendering behaviour as the original implementation.
    
    The screen acts as a coordination layer between the core game UI drawing
    and the overlay system, with no changes to game logic or appearance.
    """
    
    def __init__(self, overlay_manager=None):
        """
        Initialise the GameHudScreen.
        
        Args:
            overlay_manager: Optional OverlayManager instance for rendering overlays.
                           If None, overlay rendering will be skipped.
        """
        self.overlay_manager = overlay_manager
    
    def render(self, screen: pygame.Surface, **kwargs) -> None:
        """
        Render the game HUD to the screen.
        
        Args:
            screen: pygame surface to render to
            **kwargs: Expected parameters:
                - game_state: GameState instance with current game data
                - w, h: Screen width and height
                
        The method first calls the existing ui.draw_ui function to draw
        the main HUD, then delegates to OverlayManager for overlay rendering.
        This maintains identical behaviour to the original rendering code.
        """
        # Import here to avoid circular dependencies
        from ui import draw_ui
        
        # Extract expected parameters with sensible defaults
        game_state = kwargs.get('game_state')
        w = kwargs.get('w', 1200)  # Default screen width
        h = kwargs.get('h', 800)   # Default screen height
        
        if game_state is None:
            # Cannot render HUD without game state
            return
        
        # Draw the main game UI using existing function
        # This maintains all existing game HUD behaviour and appearance
        draw_ui(screen, game_state, w, h)
        
        # Render overlay elements if overlay manager is available
        if self.overlay_manager is not None:
            self.overlay_manager.render_elements(screen)
    
    def update(self, dt: float) -> None:
        """
        Update screen animations and overlay state.
        
        Args:
            dt: Delta time since last update in seconds
            
        This delegates animation updates to the OverlayManager if available.
        """
        if self.overlay_manager is not None:
            self.overlay_manager.update_animations()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events for the game HUD.
        
        Args:
            event: pygame event to handle
            
        Returns:
            bool: True if event was handled by overlay system, False otherwise
            
        This delegates event handling to the OverlayManager for UI overlays.
        Game-specific event handling remains in the main game loop.
        """
        if self.overlay_manager is not None:
            # Note: This would need screen dimensions for proper handling
            # For now, use default dimensions - this may need adjustment
            # when integrating with the main event loop
            return self.overlay_manager.handle_mouse_event(event, 1200, 800) is not None
        return False