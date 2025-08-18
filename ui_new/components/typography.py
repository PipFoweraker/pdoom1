"""
Typography utilities for P(Doom) UI.

Provides font management and text styling functions for consistent typography.
"""

import pygame
from typing import Tuple, Optional


class FontManager:
    """Manages font loading and sizing for the game UI."""
    
    def __init__(self):
        self.font_cache = {}
        self.base_font = 'Consolas'
        
    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        """Get a font with the specified size and weight."""
        key = (self.base_font, size, bold)
        if key not in self.font_cache:
            self.font_cache[key] = pygame.font.SysFont(self.base_font, size, bold=bold)
        return self.font_cache[key]
    
    def get_title_font(self, screen_h: int) -> pygame.font.Font:
        """Get the title font sized appropriately for screen height."""
        return self.get_font(int(screen_h * 0.045), bold=True)
    
    def get_big_font(self, screen_h: int) -> pygame.font.Font:
        """Get the big font sized appropriately for screen height."""
        return self.get_font(int(screen_h * 0.033))
    
    def get_normal_font(self, screen_h: int) -> pygame.font.Font:
        """Get the normal font sized appropriately for screen height."""
        return self.get_font(int(screen_h * 0.025))
    
    def get_small_font(self, screen_h: int) -> pygame.font.Font:
        """Get the small font sized appropriately for screen height."""
        return self.get_font(int(screen_h * 0.018))


# Global font manager instance
font_manager = FontManager()


def render_text(text: str, font: pygame.font.Font, colour: Tuple[int, int, int], 
                antialias: bool = True) -> pygame.Surface:
    """Render text with consistent styling."""
    return font.render(text, antialias, colour)


def render_multiline_text(text: str, font: pygame.font.Font, colour: Tuple[int, int, int],
                         max_width: int, line_spacing: int = 2) -> list:
    """Render multiline text, returning a list of surfaces."""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, colour)
        
        if test_surface.get_width() <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(font.render(' '.join(current_line), True, colour))
                current_line = [word]
            else:
                # Single word is too long, force it
                lines.append(font.render(word, True, colour))
    
    if current_line:
        lines.append(font.render(' '.join(current_line), True, colour))
    
    return lines


def get_text_size(text: str, font: pygame.font.Font) -> Tuple[int, int]:
    """Get the size of text when rendered with the given font."""
    return font.size(text)


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list:
    """Wrap text to fit within the specified width, returning list of lines."""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Single word is too long, force it
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines