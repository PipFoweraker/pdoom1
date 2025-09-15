"""Base Screen Class for P(Doom)

Provides a foundation for all game screens with consistent interface.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import pygame
from enum import Enum


class ScreenResult(Enum):
    """Results that screens can return to indicate next action."""
    CONTINUE = "continue"  # Stay on current screen
    TRANSITION = "transition"  # Change to another screen
    EXIT = "exit"  # Exit application
    BACK = "back"  # Return to previous screen


class BaseScreen(ABC):
    """Base class for all game screens.
    
    Provides consistent interface for handling events, updating, and rendering.
    Each screen should inherit from this and implement the required methods.
    """
    
    def __init__(self, screen_id: str):
        """Initialise the screen.
        
        Args:
            screen_id: Unique identifier for this screen
        """
        self.screen_id = screen_id
        self.is_active = False
        self.transition_data: Optional[Dict[str, Any]] = None
        
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> Optional[Tuple[ScreenResult, str, Dict[str, Any]]]:
        """Handle a pygame event.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            Tuple of (result, next_screen_id, data) or None if no transition
            - result: What should happen next
            - next_screen_id: ID of screen to transition to (if TRANSITION)
            - data: Data to pass to next screen
        """
        pass
        
    @abstractmethod
    def update(self, dt: float) -> Optional[Tuple[ScreenResult, str, Dict[str, Any]]]:
        """Update screen logic.
        
        Args:
            dt: Delta time since last update in seconds
            
        Returns:
            Tuple of (result, next_screen_id, data) or None if no transition
        """
        pass
        
    @abstractmethod
    def render(self, surface: pygame.Surface, screen_width: int, screen_height: int):
        """Render the screen.
        
        Args:
            surface: Surface to render to
            screen_width: Current screen width
            screen_height: Current screen height
        """
        pass
        
    def activate(self, transition_data: Optional[Dict[str, Any]] = None):
        """Called when screen becomes active.
        
        Args:
            transition_data: Data passed from previous screen
        """
        self.is_active = True
        self.transition_data = transition_data
        
    def deactivate(self):
        """Called when screen becomes inactive."""
        self.is_active = False
        
    def get_screen_id(self) -> str:
        """Get the unique identifier for this screen."""
        return self.screen_id
