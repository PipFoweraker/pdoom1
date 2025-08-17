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
    
    def render_main_menu(self, screen, w, h, selected_item, sound_manager=None) -> None:
        """
        Render the main menu screen.
        
        Delegates to the main menu screen implementation while maintaining
        identical behaviour to the original ui.draw_main_menu function.
        
        Args:
            screen: pygame surface to render to
            w: Screen width
            h: Screen height
            selected_item: index of currently selected menu item
            sound_manager: optional SoundManager instance for sound toggle button
        """
        from .screens.main_menu import draw_main_menu
        draw_main_menu(screen, w, h, selected_item, sound_manager)
    
    def render_loading(self, screen, w, h, progress=0, status_text="Loading...", font=None) -> None:
        """
        Render the loading screen with progress indicator.
        
        Delegates to the loading screen implementation while maintaining
        identical behaviour to the original ui.draw_loading_screen function.
        
        Args:
            screen: pygame surface to render to
            w: Screen width
            h: Screen height
            progress: loading progress (0.0 to 1.0)
            status_text: text to display for loading status
            font: optional font for status text
        """
        from .screens.loading import draw_loading_screen
        draw_loading_screen(screen, w, h, progress, status_text, font)
    
    def render_audio_menu(self, screen, w, h, selected_item, audio_settings, sound_manager) -> None:
        """
        Render the audio settings menu.
        
        Delegates to the audio menu screen implementation while maintaining
        identical behaviour to the original ui.draw_audio_menu function.
        
        Args:
            screen: pygame surface to render to
            w: Screen width
            h: Screen height
            selected_item: index of currently selected menu item
            audio_settings: dictionary of current audio settings
            sound_manager: SoundManager instance for current state
        """
        from .screens.audio_menu import draw_audio_menu
        draw_audio_menu(screen, w, h, selected_item, audio_settings, sound_manager)
    
    def render_seed_selection(self, screen, w, h, selected_item, seed_input="", sound_manager=None) -> None:
        """
        Render the seed selection screen.
        
        Delegates to the seed selection screen implementation while maintaining
        identical behaviour to the original ui.draw_seed_selection function.
        
        Args:
            screen: pygame surface to render to
            w: Screen width
            h: Screen height
            selected_item: index of currently selected item (0=Weekly, 1=Custom)
            seed_input: current custom seed input text
            sound_manager: optional SoundManager instance for sound toggle button
        """
        from .screens.seed_selection import draw_seed_selection
        draw_seed_selection(screen, w, h, selected_item, seed_input, sound_manager)
    
    # Additional access methods for advanced usage
    
    @property
    def overlay_manager(self) -> OverlayManager:
        """
        Access to the internal overlay manager for advanced operations.
        
        Note: Direct access to internal components may change in future versions.
        Prefer using the facade methods when possible.
        """
        return self._overlay_manager