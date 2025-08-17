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
    
    def render_config_menu(self, screen, w, h, selected_item, available_configs, current_config_name) -> None:
        """
        Render the configuration menu screen.
        
        Delegates to the config menu screen implementation while maintaining
        identical behaviour to the original ui.draw_config_menu function.
        
        Args:
            screen: pygame surface to render to
            w: Screen width
            h: Screen height
            selected_item: index of currently selected config item
            available_configs: list of available config names
            current_config_name: name of currently active config
        """
        from .screens.config_menu import draw_config_menu
        draw_config_menu(screen, w, h, selected_item, available_configs, current_config_name)
    
    def render_pre_game_settings(self, screen, w, h, settings, selected_item, sound_manager=None) -> None:
        """
        Render the pre-game settings screen.
        
        Delegates to the pre-game settings screen implementation while maintaining
        identical behaviour to the original ui.draw_pre_game_settings function.
        
        Args:
            screen: pygame surface to render to
            w: Screen width
            h: Screen height
            settings: dictionary of current settings values
            selected_item: index of currently selected setting
            sound_manager: optional SoundManager instance for sound toggle button
        """
        from .screens.pre_game_settings import draw_pre_game_settings
        draw_pre_game_settings(screen, w, h, settings, selected_item, sound_manager)
    
    def render_tutorial_choice(self, screen, w, h, selected_item) -> None:
        """
        Render the tutorial choice screen.
        
        Delegates to the tutorial choice screen implementation while maintaining
        identical behaviour to the original ui.draw_tutorial_choice function.
        
        Args:
            screen: pygame surface to render to
            w: Screen width
            h: Screen height
            selected_item: index of currently selected item (0=Yes, 1=No)
        """
        from .screens.tutorial_choice import draw_tutorial_choice
        draw_tutorial_choice(screen, w, h, selected_item)
    
    def render_seed_prompt(self, screen, seed_input, weekly_seed) -> None:
        """
        Render the seed prompt screen.
        
        Delegates to the seed prompt screen implementation while maintaining
        identical behaviour to the original ui.draw_seed_prompt function.
        
        Args:
            screen: pygame surface to render to
            seed_input: current seed input text
            weekly_seed: weekly challenge seed suggestion
        """
        from .screens.seed_prompt import draw_seed_prompt
        draw_seed_prompt(screen, seed_input, weekly_seed)
    
    def render_overlay(self, screen, title, content, scroll, w, h, nav_depth) -> None:
        """
        Render the overlay screen.
        
        Delegates to the overlay screen implementation while maintaining
        identical behaviour to the original ui.draw_overlay function.
        
        Args:
            screen: pygame surface to render to
            title: string title to display at top of overlay
            content: full text content to display
            scroll: vertical scroll position in pixels
            w: Screen width
            h: Screen height
            nav_depth: current navigation depth for Back button display
        """
        from .screens.overlay import draw_overlay
        return draw_overlay(screen, title, content, scroll, w, h, nav_depth)
    
    def render_bug_report_form(self, screen, data, selected_field, w, h) -> None:
        """
        Render the bug report form screen.
        
        Delegates to the bug report screen implementation while maintaining
        identical behaviour to the original ui.draw_bug_report_form function.
        
        Args:
            screen: pygame surface to render to
            data: dict containing form field values
            selected_field: index of currently selected field
            w: Screen width
            h: Screen height
        """
        from .screens.bug_report import draw_bug_report_form
        return draw_bug_report_form(screen, data, selected_field, w, h)
    
    def render_bug_report_success(self, screen, message, w, h) -> None:
        """
        Render the bug report success screen.
        
        Delegates to the bug report screen implementation while maintaining
        identical behaviour to the original ui.draw_bug_report_success function.
        
        Args:
            screen: pygame surface to render to
            message: success message to display
            w: Screen width
            h: Screen height
        """
        from .screens.bug_report import draw_bug_report_success
        draw_bug_report_success(screen, message, w, h)
    
    def render_end_game_menu(self, screen, w, h, selected_item, game_state, seed) -> None:
        """
        Render the end game menu screen.
        
        Delegates to the end game menu screen implementation while maintaining
        identical behaviour to the original ui.draw_end_game_menu function.
        
        Args:
            screen: pygame surface to render to
            w: Screen width
            h: Screen height
            selected_item: index of currently selected menu item
            game_state: GameState object for displaying final stats
            seed: Game seed used for this session
        """
        from .screens.end_game_menu import draw_end_game_menu
        draw_end_game_menu(screen, w, h, selected_item, game_state, seed)
    
    def render_high_score_screen(self, screen, w, h, game_state, seed, submit_cb=None) -> None:
        """
        Render the high score screen.
        
        Delegates to the high score screen implementation while maintaining
        identical behaviour to the original ui.draw_high_score_screen function.
        
        Args:
            screen: pygame surface to render to
            w: Screen width
            h: Screen height
            game_state: current game state with final scores
            seed: game seed used for this run
            submit_cb: optional callback for leaderboard submission
        """
        from .screens.high_score import draw_high_score_screen
        draw_high_score_screen(screen, w, h, game_state, seed, submit_cb)
    
    def render_turn_transition_overlay(self, screen, w, h, timer, duration) -> None:
        """
        Render the turn transition overlay.
        
        Delegates to the turn transition screen implementation while maintaining
        identical behaviour to the original ui.draw_turn_transition_overlay function.
        
        Args:
            screen: pygame surface to render to
            w: Screen width
            h: Screen height
            timer: current timer value (counts down from duration to 0)
            duration: total duration of the transition
        """
        from .screens.turn_transition import draw_turn_transition_overlay
        draw_turn_transition_overlay(screen, w, h, timer, duration)
    
    def render_first_time_help(self, screen, help_content, w, h, mouse_pos=None) -> None:
        """
        Render the first time help popup.
        
        Delegates to the first time help screen implementation while maintaining
        identical behaviour to the original ui.draw_first_time_help function.
        
        Args:
            screen: pygame surface to render to
            help_content: dict with title and content for the help popup
            w: Screen width
            h: Screen height
            mouse_pos: current mouse position for hover effects (optional)
        """
        from .screens.first_time_help import draw_first_time_help
        return draw_first_time_help(screen, help_content, w, h, mouse_pos)
    
    # Additional access methods for advanced usage
    
    @property
    def overlay_manager(self) -> OverlayManager:
        """
        Access to the internal overlay manager for advanced operations.
        
        Note: Direct access to internal components may change in future versions.
        Prefer using the facade methods when possible.
        """
        return self._overlay_manager