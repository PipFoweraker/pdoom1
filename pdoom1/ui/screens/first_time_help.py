"""
First time help screen for P(Doom) - Display first-time mechanic help

This module provides the first-time help popup for showing contextual
help when players encounter new game mechanics.
"""

import pygame
from ui import wrap_text


def draw_first_time_help(screen, help_content, w, h, mouse_pos=None):
    """
    Draw a small help popup for first-time mechanics.
    
    Args:
        screen: pygame surface to draw on
        help_content: dict with title and content for the help popup
        w, h: screen width and height
        mouse_pos: current mouse position for hover effects (optional)
    """
    if not help_content or not isinstance(help_content, dict):
        return None
        
    # Small popup dimensions
    popup_width = int(w * 0.4)
    popup_height = int(h * 0.25)
    popup_x = w - popup_width - 20  # Top right corner
    popup_y = 20
    
    # Popup background
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    pygame.draw.rect(screen, (60, 80, 100), popup_rect, border_radius=10)
    pygame.draw.rect(screen, (150, 200, 255), popup_rect, width=3, border_radius=10)
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.025), bold=True)
    content_font = pygame.font.SysFont('Consolas', int(h*0.02))
    
    # Title
    title_text = title_font.render(help_content.get('title', 'Tip'), True, (255, 255, 100))
    screen.blit(title_text, (popup_x + 10, popup_y + 10))
    
    # Content with word wrapping
    content = help_content.get('content', '')
    content_width = popup_width - 20
    wrapped_content = wrap_text(content, content_font, content_width)
    
    for i, line in enumerate(wrapped_content[:6]):  # Max 6 lines
        line_surface = content_font.render(line, True, (255, 255, 255))
        screen.blit(line_surface, (popup_x + 10, popup_y + 40 + i * 20))
    
    # Close button (X) with hover effect
    close_button_size = 20
    close_button_x = popup_x + popup_width - close_button_size - 5
    close_button_y = popup_y + 5
    close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)
    
    # Check for hover effect
    close_button_color = (200, 100, 100)  # Default red
    close_text_color = (255, 255, 255)    # Default white
    
    if mouse_pos and close_button_rect.collidepoint(mouse_pos):
        close_button_color = (255, 120, 120)  # Brighter red on hover
        close_text_color = (255, 255, 100)    # Yellow text on hover
    
    pygame.draw.rect(screen, close_button_color, close_button_rect, border_radius=3)
    
    close_font = pygame.font.SysFont('Consolas', int(h*0.02), bold=True)
    close_text = close_font.render("×", True, close_text_color)
    close_text_rect = close_text.get_rect(center=close_button_rect.center)
    screen.blit(close_text, close_text_rect)
    
    # Add dismiss instructions at bottom of popup
    dismiss_font = pygame.font.SysFont('Consolas', int(h*0.015))
    dismiss_text = dismiss_font.render("Press Esc to dismiss, Enter to accept", True, (180, 180, 180))
    dismiss_y = popup_y + popup_height - 25
    screen.blit(dismiss_text, (popup_x + 10, dismiss_y))
    
    return close_button_rect