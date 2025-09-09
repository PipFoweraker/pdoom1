"""
Text rendering and navigation utilities for the UI system.

This module provides text wrapping, rendering, and navigation button functionality.
"""

import pygame


def should_show_back_button(depth: int) -> bool:
    """
    Determine if a back button should be shown based on navigation depth.
    
    Args:
        depth: Current navigation depth
        
    Returns:
        bool: True if back button should be shown
    """
    return depth > 0


def draw_back_button(screen, w, h, navigation_depth, font=None):
    """
    Draw a back navigation button if appropriate for the current depth.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen dimensions
        navigation_depth: current navigation depth
        font: font to use for button text
        
    Returns:
        pygame.Rect: button rectangle if drawn, None otherwise
    """
    if not should_show_back_button(navigation_depth):
        return None
        
    if font is None:
        font = pygame.font.Font(None, 36)
    
    # Position back button in top-left corner with margin based on screen height
    margin = int(h * 0.02)  # 2% of height for consistent positioning
    back_text = font.render("? Back", True, (255, 255, 255))
    back_rect = pygame.Rect(margin, margin, back_text.get_width() + 20, back_text.get_height() + 10)
    
    # Draw button background
    pygame.draw.rect(screen, (50, 50, 50), back_rect)
    pygame.draw.rect(screen, (255, 255, 255), back_rect, 2)
    
    # Draw button text
    text_x = back_rect.x + 10
    text_y = back_rect.y + 5
    screen.blit(back_text, (text_x, text_y))
    
    return back_rect


def wrap_text(text, font, max_width):
    """
    Wrap text to fit within the given width using the provided font.
    
    Args:
        text: text to wrap
        font: pygame font object
        max_width: maximum width in pixels
        
    Returns:
        list: lines of wrapped text
    """
    if not text:
        return []
    
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        test_surface = font.render(test_line, True, (255, 255, 255))
        
        if test_surface.get_width() <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                # Single word is too long, force it
                lines.append(word)
    
    if current_line:
        lines.append(current_line)
    
    return lines


def render_text(text, font, max_width=None, color=(255,255,255), line_height_multiplier=1.35):
    """
    Render text with optional wrapping and return list of surfaces and total height.
    
    Args:
        text: text to render
        font: pygame font object
        max_width: maximum width for wrapping (None for no wrapping)
        color: text color tuple
        line_height_multiplier: multiplier for line height spacing
        
    Returns:
        tuple: (list of text surfaces, total height)
    """
    if max_width:
        lines = wrap_text(text, font, max_width)
    else:
        lines = text.split('\n')
    
    surfaces = []
    line_height = int(font.get_height() * line_height_multiplier)
    
    for line in lines:
        surface = font.render(line, True, color)
        surfaces.append(surface)
    
    total_height = len(surfaces) * line_height
    
    return surfaces, total_height