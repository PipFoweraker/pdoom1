"""
shared/core/engine_interface.py

Abstract interface for game engine operations.
Allows game logic to work with both pygame and Godot.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class MessageCategory(Enum):
    """Message categories for UI display."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    EVENT = "event"
    ACTION = "action"

@dataclass
class DialogOption:
    """Option in a dialog box."""
    id: str
    text: str
    enabled: bool = True
    tooltip: Optional[str] = None

@dataclass
class DialogResult:
    """Result from showing a dialog."""
    option_id: str
    cancelled: bool = False

class IGameEngine(ABC):
    """
    Abstract interface for game engine operations.
    
    Both pygame and Godot implement this interface, allowing
    game logic to remain engine-agnostic.
    """
    
    # ========== Display Methods ==========
    
    @abstractmethod
    def display_message(self, message: str, category: MessageCategory) -> None:
        """
        Display a message to the player.
        
        Args:
            message: Message text
            category: Message category for styling
        """
        pass
    
    @abstractmethod
    def update_resource_display(self, resources: Dict[str, float]) -> None:
        """
        Update resource counters in UI.
        
        Args:
            resources: Dict of resource_name -> value
                e.g. {"money": 50000, "compute": 100, "safety": 10}
        """
        pass
    
    @abstractmethod
    def update_turn_display(self, turn: int) -> None:
        """Update turn counter display."""
        pass
    
    @abstractmethod
    def update_employee_display(self, employees: Dict[str, int]) -> None:
        """
        Update employee count display.
        
        Args:
            employees: Dict of employee_type -> count
        """
        pass
    
    # ========== Dialog Methods ==========
    
    @abstractmethod
    def show_dialog(
        self,
        title: str,
        description: str,
        options: List[DialogOption]
    ) -> DialogResult:
        """
        Show modal dialog and wait for player choice.
        
        Args:
            title: Dialog title
            description: Dialog description text
            options: List of available options
            
        Returns:
            DialogResult with selected option
        """
        pass
    
    @abstractmethod
    def show_event_popup(
        self,
        event_name: str,
        event_description: str,
        options: List[DialogOption]
    ) -> DialogResult:
        """
        Show event popup (similar to dialog but styled for events).
        
        Args:
            event_name: Event title
            event_description: Event description
            options: Available responses
            
        Returns:
            DialogResult with selected option
        """
        pass
    
    # ========== Audio Methods ==========
    
    @abstractmethod
    def play_sound(self, sound_id: str) -> None:
        """
        Play sound effect.
        
        Args:
            sound_id: Sound identifier (e.g. "hire", "upgrade", "event")
        """
        pass
    
    @abstractmethod
    def set_volume(self, volume: float) -> None:
        """
        Set audio volume.
        
        Args:
            volume: Volume level 0.0-1.0
        """
        pass
    
    # ========== Visual Feedback Methods ==========
    
    @abstractmethod
    def highlight_element(self, element_id: str, duration: float = 1.0) -> None:
        """
        Highlight UI element briefly.
        
        Args:
            element_id: Element to highlight
            duration: Highlight duration in seconds
        """
        pass
    
    @abstractmethod
    def show_tooltip(self, element_id: str, text: str) -> None:
        """
        Show tooltip for element.
        
        Args:
            element_id: Element to show tooltip for
            text: Tooltip text
        """
        pass
    
    # ========== State Query Methods ==========
    
    @abstractmethod
    def is_element_hovered(self, element_id: str) -> bool:
        """Check if UI element is currently hovered."""
        pass
    
    @abstractmethod
    def is_element_clicked(self, element_id: str) -> bool:
        """Check if UI element was clicked this frame."""
        pass
    
    # ========== Utility Methods ==========
    
    @abstractmethod
    def get_screen_size(self) -> Tuple[int, int]:
        """Get current screen dimensions."""
        pass
    
    @abstractmethod
    def request_refresh(self) -> None:
        """Request UI refresh (for state changes)."""
        pass


class MockEngine(IGameEngine):
    """
    Mock engine for testing game logic without pygame/Godot.
    Stores all operations for verification in tests.
    """
    
    def __init__(self):
        self.messages: List[Tuple[str, MessageCategory]] = []
        self.resources: Dict[str, float] = {}
        self.turn: int = 0
        self.employees: Dict[str, int] = {}
        self.sounds_played: List[str] = []
        self.dialogs_shown: List[Dict[str, Any]] = []
        self.dialog_responses: List[DialogResult] = []
        self._next_dialog_result: Optional[DialogResult] = None
    
    def display_message(self, message: str, category: MessageCategory) -> None:
        self.messages.append((message, category))
    
    def update_resource_display(self, resources: Dict[str, float]) -> None:
        self.resources.update(resources)
    
    def update_turn_display(self, turn: int) -> None:
        self.turn = turn
    
    def update_employee_display(self, employees: Dict[str, int]) -> None:
        self.employees.update(employees)
    
    def show_dialog(
        self,
        title: str,
        description: str,
        options: List[DialogOption]
    ) -> DialogResult:
        self.dialogs_shown.append({
            "title": title,
            "description": description,
            "options": [opt.id for opt in options]
        })
        
        # Return pre-configured result or first option
        if self._next_dialog_result:
            result = self._next_dialog_result
            self._next_dialog_result = None
            return result
        else:
            return DialogResult(option_id=options[0].id, cancelled=False)
    
    def show_event_popup(
        self,
        event_name: str,
        event_description: str,
        options: List[DialogOption]
    ) -> DialogResult:
        return self.show_dialog(event_name, event_description, options)
    
    def play_sound(self, sound_id: str) -> None:
        self.sounds_played.append(sound_id)
    
    def set_volume(self, volume: float) -> None:
        pass
    
    def highlight_element(self, element_id: str, duration: float = 1.0) -> None:
        pass
    
    def show_tooltip(self, element_id: str, text: str) -> None:
        pass
    
    def is_element_hovered(self, element_id: str) -> bool:
        return False
    
    def is_element_clicked(self, element_id: str) -> bool:
        return False
    
    def get_screen_size(self) -> Tuple[int, int]:
        return (1024, 768)
    
    def request_refresh(self) -> None:
        pass
    
    # Test helper methods
    def set_next_dialog_result(self, result: DialogResult) -> None:
        """Set result for next dialog (for testing)."""
        self._next_dialog_result = result
    
    def clear_history(self) -> None:
        """Clear all recorded operations."""
        self.messages.clear()
        self.sounds_played.clear()
        self.dialogs_shown.clear()
