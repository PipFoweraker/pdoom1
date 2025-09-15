"""Panel Component for P(Doom) UI System"""

import pygame
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class PanelStyle:
    """Styling configuration for panels."""
    bg_color: Tuple[int, int, int] = (50, 50, 50)
    border_color: Tuple[int, int, int] = (100, 100, 100)
    border_width: int = 1
    padding: Tuple[int, int] = (10, 10)
    title_color: Tuple[int, int, int] = (255, 255, 255)
    title_bg_color: Optional[Tuple[int, int, int]] = None


class Panel:
    """A reusable panel component for grouping UI elements."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 title: str = "", style: Optional[PanelStyle] = None):
        """
        Create a panel component.
        
        Args:
            x, y: Position of the panel
            width, height: Size of the panel
            title: Optional title for the panel
            style: Styling configuration
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.style = style or PanelStyle()
        self.visible = True
        
        # Child components
        self.children: list = []
        
        # Title rendering cache
        self._title_surface = None
        self._needs_redraw = True
    
    def add_child(self, child):
        """Add a child component to this panel."""
        self.children.append(child)
    
    def remove_child(self, child):
        """Remove a child component from this panel."""
        if child in self.children:
            self.children.remove(child)
    
    def handle_mouse_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for this panel and its children."""
        if not self.visible:
            return False
            
        # Check if event is within panel bounds
        if not self.rect.collidepoint(event.pos if hasattr(event, 'pos') else (0, 0)):
            return False
        
        # Let children handle the event first
        for child in self.children:
            if hasattr(child, 'handle_mouse_event'):
                if child.handle_mouse_event(event):
                    return True
        
        # Panel handled the event by containing it
        return True
    
    def _render_title(self, font: pygame.font.Font):
        """Render the panel title."""
        if self.title and (self._needs_redraw or self._title_surface is None):
            self._title_surface = font.render(self.title, True, self.style.title_color)
            self._needs_redraw = False
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the panel and its children."""
        if not self.visible:
            return
        
        # Draw background
        pygame.draw.rect(surface, self.style.bg_color, self.rect)
        
        # Draw border
        if self.style.border_width > 0:
            pygame.draw.rect(surface, self.style.border_color, self.rect, 
                           self.style.border_width)
        
        # Draw title if present
        if self.title:
            self._render_title(font)
            if self._title_surface:
                title_x = self.rect.x + self.style.padding[0]
                title_y = self.rect.y + self.style.padding[1]
                
                # Optional title background
                if self.style.title_bg_color:
                    title_bg_rect = pygame.Rect(
                        title_x - 2, title_y - 2,
                        self._title_surface.get_width() + 4,
                        self._title_surface.get_height() + 4
                    )
                    pygame.draw.rect(surface, self.style.title_bg_color, title_bg_rect)
                
                surface.blit(self._title_surface, (title_x, title_y))
        
        # Draw children
        for child in self.children:
            if hasattr(child, 'draw'):
                child.draw(surface, font)
