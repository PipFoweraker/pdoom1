"""Button Component for P(Doom) UI System"""

import pygame
from typing import Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum


class ButtonState(Enum):
    """States for button components."""
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"


@dataclass
class ButtonStyle:
    """Styling configuration for buttons."""
    bg_color: Tuple[int, int, int] = (60, 60, 60)
    hover_color: Tuple[int, int, int] = (80, 80, 80)
    pressed_color: Tuple[int, int, int] = (40, 40, 40)
    disabled_color: Tuple[int, int, int] = (40, 40, 40)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    disabled_text_color: Tuple[int, int, int] = (128, 128, 128)
    border_color: Optional[Tuple[int, int, int]] = None
    border_width: int = 0
    padding: Tuple[int, int] = (8, 4)
    font_size: int = 16


class Button:
    """A reusable button component."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, callback: Optional[Callable] = None,
                 style: Optional[ButtonStyle] = None):
        """
        Create a button component.
        
        Args:
            x, y: Position of the button
            width, height: Size of the button
            text: Button text
            callback: Function to call when clicked
            style: Styling configuration
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.style = style or ButtonStyle()
        self.state = ButtonState.NORMAL
        self.enabled = True
        self.visible = True
        
        # Cache the rendered text
        self._text_surface = None
        self._text_rect = None
        self._needs_redraw = True
    
    def handle_mouse_event(self, event: pygame.event.Event) -> bool:
        """
        Handle mouse events for this button.
        
        Returns:
            True if the event was handled, False otherwise
        """
        if not self.enabled or not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.state = ButtonState.PRESSED
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos) and self.state == ButtonState.PRESSED:
                if self.callback:
                    self.callback()
                self.state = ButtonState.HOVER
                return True
            else:
                self.state = ButtonState.NORMAL
                
        elif event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if self.state != ButtonState.PRESSED:
                    self.state = ButtonState.HOVER
            else:
                self.state = ButtonState.NORMAL
                
        return False
    
    def _render_text(self, font: pygame.font.Font):
        """Render the button text."""
        if self._needs_redraw or self._text_surface is None:
            color = (self.style.disabled_text_color if not self.enabled 
                    else self.style.text_color)
            self._text_surface = font.render(self.text, True, color)
            
            # Center the text in the button
            text_rect = self._text_surface.get_rect()
            self._text_rect = text_rect
            self._text_rect.center = self.rect.center
            
            self._needs_redraw = False
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the button."""
        if not self.visible:
            return
            
        # Choose background color based on state
        if not self.enabled:
            bg_color = self.style.disabled_color
        elif self.state == ButtonState.PRESSED:
            bg_color = self.style.pressed_color
        elif self.state == ButtonState.HOVER:
            bg_color = self.style.hover_color
        else:
            bg_color = self.style.bg_color
        
        # Draw background
        pygame.draw.rect(surface, bg_color, self.rect)
        
        # Draw border if specified
        if self.style.border_color and self.style.border_width > 0:
            pygame.draw.rect(surface, self.style.border_color, self.rect, 
                           self.style.border_width)
        
        # Render and draw text
        self._render_text(font)
        if self._text_surface:
            surface.blit(self._text_surface, self._text_rect)
    
    def set_text(self, text: str):
        """Change the button text."""
        if text != self.text:
            self.text = text
            self._needs_redraw = True
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the button."""
        if enabled != self.enabled:
            self.enabled = enabled
            self.state = ButtonState.NORMAL if enabled else ButtonState.DISABLED
            self._needs_redraw = True
