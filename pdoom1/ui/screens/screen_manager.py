"""Screen Manager for P(Doom)

Manages screen transitions and provides a facade over main.py's screen system.
"""

from typing import Dict, Optional, Any, List, Tuple
import pygame
from .base_screen import BaseScreen, ScreenResult


class ScreenManager:
    """Manages game screens and transitions between them.
    
    Provides a clean interface for screen management while maintaining
    compatibility with the existing main.py screen system.
    """
    
    def __init__(self):
        """Initialise the screen manager."""
        self.screens: Dict[str, BaseScreen] = {}
        self.current_screen: Optional[BaseScreen] = None
        self.screen_stack: List[str] = []  # For back navigation
        self.pending_transition: Optional[Tuple[str, Dict[str, Any]]] = None
        
    def register_screen(self, screen: BaseScreen):
        """Register a screen with the manager.
        
        Args:
            screen: Screen instance to register
        """
        self.screens[screen.get_screen_id()] = screen
        
    def get_screen(self, screen_id: str) -> Optional[BaseScreen]:
        """Get a registered screen by ID.
        
        Args:
            screen_id: ID of screen to retrieve
            
        Returns:
            Screen instance or None if not found
        """
        return self.screens.get(screen_id)
        
    def set_current_screen(self, screen_id: str, transition_data: Optional[Dict[str, Any]] = None, push_to_stack: bool = True):
        """Set the current active screen.
        
        Args:
            screen_id: ID of screen to activate
            transition_data: Data to pass to the new screen
            push_to_stack: Whether to push current screen to navigation stack
        """
        # Deactivate current screen
        if self.current_screen:
            if push_to_stack:
                self.screen_stack.append(self.current_screen.get_screen_id())
            self.current_screen.deactivate()
            
        # Activate new screen
        new_screen = self.screens.get(screen_id)
        if new_screen:
            new_screen.activate(transition_data)
            self.current_screen = new_screen
        else:
            print(f"Warning: Screen '{screen_id}' not found")
            
    def go_back(self) -> bool:
        """Return to previous screen in stack.
        
        Returns:
            True if successfully went back, False if stack is empty
        """
        if not self.screen_stack:
            return False
            
        previous_screen_id = self.screen_stack.pop()
        self.set_current_screen(previous_screen_id, push_to_stack=False)
        return True
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for current screen.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.current_screen:
            return False
            
        result = self.current_screen.handle_event(event)
        if result:
            self._process_screen_result(result)
            return True
            
        return False
        
    def update(self, dt: float):
        """Update current screen.
        
        Args:
            dt: Delta time since last update in seconds
        """
        if not self.current_screen:
            return
            
        result = self.current_screen.update(dt)
        if result:
            self._process_screen_result(result)
            
        # Process any pending transitions
        if self.pending_transition:
            screen_id, data = self.pending_transition
            self.pending_transition = None
            self.set_current_screen(screen_id, data)
            
    def render(self, surface: pygame.Surface, screen_width: int, screen_height: int):
        """Render current screen.
        
        Args:
            surface: Surface to render to
            screen_width: Current screen width
            screen_height: Current screen height
        """
        if self.current_screen:
            self.current_screen.render(surface, screen_width, screen_height)
            
    def get_current_screen_id(self) -> Optional[str]:
        """Get ID of current screen.
        
        Returns:
            Current screen ID or None if no screen active
        """
        return self.current_screen.get_screen_id() if self.current_screen else None
        
    def clear_navigation_stack(self):
        """Clear the navigation stack."""
        self.screen_stack.clear()
        
    def _process_screen_result(self, result: Tuple[ScreenResult, str, Dict[str, Any]]):
        """Process a screen result and handle transitions.
        
        Args:
            result: Tuple of (result_type, next_screen_id, data)
        """
        result_type, next_screen_id, data = result
        
        if result_type == ScreenResult.TRANSITION:
            # Schedule transition for next update to avoid issues during event handling
            self.pending_transition = (next_screen_id, data)
        elif result_type == ScreenResult.BACK:
            self.go_back()
        elif result_type == ScreenResult.EXIT:
            # This would need to be handled at application level
            pass
        # CONTINUE requires no action
