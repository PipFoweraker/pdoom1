'''
Low-level text and graphics rendering utilities for UI components.

This module contains fundamental rendering functions used across the UI system
for text wrapping, rendering, and drawing basic interface elements.
'''

import pygame
from typing import List, Tuple, Optional


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    '''
    Splits the text into multiple lines so that each line fits within max_width.
    Returns a list of strings, each representing a line.
    Improved to handle overflow with better word breaking.
    '''
    lines = []
    # Use textwrap to split into words, then try to pack as many as possible per line
    words = text.split(' ')
    curr_line = ''
    for word in words:
        test_line = curr_line + (' ' if curr_line else '') + word
        if font.size(test_line)[0] <= max_width:
            curr_line = test_line
        else:
            if curr_line:
                lines.append(curr_line)
                curr_line = word
            else:
                # Handle very long words that don't fit on a line
                # Break them using character-level wrapping as fallback
                if font.size(word)[0] > max_width:
                    # Character-level breaking for extremely long words
                    for i in range(1, len(word) + 1):
                        if font.size(word[:i])[0] > max_width:
                            if i > 1:
                                lines.append(word[:i-1])
                                word = word[i-1:]
                            break
                curr_line = word
    if curr_line:
        lines.append(curr_line)
    return lines


def render_text(text: str, font: pygame.font.Font, max_width: Optional[int] = None, color: Tuple[int, int, int] = (255,255,255), line_height_multiplier: float = 1.35) -> Tuple[List[Tuple[pygame.Surface, Tuple[int, int]]], pygame.Rect]:
    '''Render text with optional word wrapping and consistent line height. Returns [(surface, (x_offset, y_offset)), ...], bounding rect.'''
    lines = [text]
    if max_width:
        lines = wrap_text(text, font, max_width)
    surfaces = [font.render(line, True, color) for line in lines]
    
    # Use consistent line height for better visual spacing
    font_height = font.get_height()
    line_height = int(font_height * line_height_multiplier)
    
    widths = [surf.get_width() for surf in surfaces]
    total_width = max(widths) if widths else 0
    total_height = line_height * len(lines) if lines else 0
    
    # Calculate offsets with consistent line spacing
    offsets = [(0, i * line_height) for i in range(len(lines))]
    return list(zip(surfaces, offsets)), pygame.Rect(0, 0, total_width, total_height)


def draw_resource_icon(screen: pygame.Surface, icon_type: str, x: int, y: int, size: int = 16) -> None:
    '''
    Draw 8-bit style resource icons.
    
    Args:
        screen: pygame surface to draw on
        icon_type: 'money', 'research', 'papers', 'compute'
        x, y: position to draw at
        size: icon size in pixels
    '''
    if icon_type == 'money':
        # Stylized $ sign in 8-bit style
        # Vertical line
        pygame.draw.rect(screen, (255, 230, 60), (x + size//2 - 1, y, 2, size))
        # Top horizontal
        pygame.draw.rect(screen, (255, 230, 60), (x + 2, y + 2, size - 4, 2))
        # Middle horizontal (shorter)
        pygame.draw.rect(screen, (255, 230, 60), (x + 3, y + size//2 - 1, size - 6, 2))
        # Bottom horizontal
        pygame.draw.rect(screen, (255, 230, 60), (x + 2, y + size - 4, size - 4, 2))
        
    elif icon_type == 'research':
        # Light bulb icon
        # Bulb top (round)
        pygame.draw.circle(screen, (150, 200, 255), (x + size//2, y + size//3), size//3)
        # Bulb base (rectangle)
        pygame.draw.rect(screen, (150, 200, 255), (x + size//2 - 2, y + size//2, 4, size//3))
        # Filament lines
        pygame.draw.line(screen, (100, 150, 200), (x + size//2 - 2, y + size//3), (x + size//2 + 2, y + size//3))
        pygame.draw.line(screen, (100, 150, 200), (x + size//2 - 1, y + size//3 + 2), (x + size//2 + 1, y + size//3 + 2))
        
    elif icon_type == 'papers':
        # Paper/document icon
        # Main rectangle
        pygame.draw.rect(screen, (255, 200, 100), (x + 2, y + 2, size - 6, size - 4))
        # Border
        pygame.draw.rect(screen, (200, 150, 50), (x + 2, y + 2, size - 6, size - 4), 1)
        # Text lines
        for i in range(3):
            line_y = y + 5 + i * 3
            pygame.draw.line(screen, (200, 150, 50), (x + 4, line_y), (x + size - 6, line_y))
            
    elif icon_type == 'compute':
        # Exponential/power symbol (like e^x or 2^n)
        # Draw '2' 
        pygame.draw.rect(screen, (100, 255, 150), (x + 2, y + 2, 4, 2))
        pygame.draw.rect(screen, (100, 255, 150), (x + 6, y + 4, 2, 3))
        pygame.draw.rect(screen, (100, 255, 150), (x + 2, y + 7, 6, 2))
        # Draw superscript 'n'
        pygame.draw.rect(screen, (100, 255, 150), (x + 10, y + 2, 2, 4))
        pygame.draw.rect(screen, (100, 255, 150), (x + 12, y + 3, 1, 1))
        pygame.draw.rect(screen, (100, 255, 150), (x + 13, y + 4, 2, 2))
