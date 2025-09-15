"""UI Components for P(Doom)

Reusable UI components for building consistent interfaces.
"""

from typing import Dict, Any
import pygame

from .button import Button, ButtonState, ButtonStyle
from .panel import Panel, PanelStyle


class UIComponentManager:
    """Manages a collection of UI components."""
    
    def __init__(self):
        """Initialize the component manager."""
        self.components: Dict[str, Any] = {}
        self.draw_order: list = []
    
    def add_component(self, name: str, component: Any):
        """Add a component to be managed."""
        self.components[name] = component
        if name not in self.draw_order:
            self.draw_order.append(name)
    
    def remove_component(self, name: str):
        """Remove a component from management."""
        if name in self.components:
            del self.components[name]
        if name in self.draw_order:
            self.draw_order.remove(name)
    
    def get_component(self, name: str):
        """Get a component by name."""
        return self.components.get(name)
    
    def handle_mouse_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for all managed components."""
        # Process in reverse draw order (top to bottom)
        for name in reversed(self.draw_order):
            component = self.components.get(name)
            if component and hasattr(component, 'handle_mouse_event'):
                if component.handle_mouse_event(event):
                    return True
        return False
    
    def draw_all(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw all managed components in order."""
        for name in self.draw_order:
            component = self.components.get(name)
            if component and hasattr(component, 'draw'):
                component.draw(surface, font)
