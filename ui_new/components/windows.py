"""
Window and panel components with headers for P(Doom) UI.

Provides reusable window and panel components including those with draggable headers.
Replaces dynamic imports of draw_window_with_header function.
"""

import pygame
from typing import Tuple, Optional
from .colours import (
    BUTTON_NORMAL_BG, BUTTON_HOVER_BG, BUTTON_PRESSED_BG,
    BUTTON_NORMAL_BORDER, BUTTON_HOVER_BORDER, BUTTON_PRESSED_BORDER,
    BUTTON_TEXT_COLOUR, BACKGROUND_COLOUR, TEXT_COLOUR
)

# Local font manager stub to avoid circular imports
class _FontManagerStub:
    def get_font(self, size, bold=False): 
        return pygame.font.Font(None, size) if pygame.get_init() else None
    def get_normal_font(self, h): 
        return self.get_font(max(12, int(h * 0.025)))

font_manager = _FontManagerStub()


def draw_window_with_header(screen: pygame.Surface, 
                          rect: pygame.Rect,
                          title: str, 
                          content: Optional[str] = None,
                          minimized: bool = False,
                          font: Optional[pygame.font.Font] = None) -> Tuple[pygame.Rect, Optional[pygame.Rect]]:
    """
    Draw a window with a header and optional minimize button.
    
    Maintains compatibility with legacy draw_window_with_header function signature.
    
    Args:
        screen: The surface to draw on
        rect: Window rectangle (pygame.Rect)
        title: Window title text
        content: Optional content text to display in window body
        minimized: Whether the window is minimized
        font: Optional font for title text
        
    Returns:
        Tuple of (header_rect, minimize_button_rect or None)
    """
    x, y, width, height = rect.x, rect.y, rect.width, rect.height
    
    if font is None:
        font = font_manager.get_normal_font(screen.get_height())
        
    # Use fixed header height for compatibility
    header_height = 30
    
    # Safety check: if font is still None (pygame not initialized), create a default font
    if font is None:
        try:
            font = pygame.font.Font(None, int(screen.get_height() * 0.025))
        except pygame.error:
            # If even default font fails, return early with dummy rects
            header_rect = pygame.Rect(x, y, width, header_height)
            minimize_rect = pygame.Rect(x + width - header_height + 4, y + 2, header_height - 4, header_height - 4)
            return header_rect, minimize_rect
    
    if minimized:
        # Only draw header when minimized
        height = header_height
    
    # Draw window background
    window_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, BACKGROUND_COLOUR, window_rect)
    pygame.draw.rect(screen, BUTTON_NORMAL_BORDER, window_rect, 2)
    
    # Draw header background
    header_rect = pygame.Rect(x, y, width, header_height)
    pygame.draw.rect(screen, BUTTON_NORMAL_BG, header_rect)
    pygame.draw.rect(screen, BUTTON_NORMAL_BORDER, header_rect, 1)
    
    # Draw title text
    title_surface = font.render(title, True, BUTTON_TEXT_COLOUR)
    title_x = x + 8
    title_y = y + (header_height - title_surface.get_height()) // 2
    screen.blit(title_surface, (title_x, title_y))
    
    # Draw minimize button
    button_size = header_height - 4
    minimize_rect = pygame.Rect(x + width - button_size - 2, y + 2, button_size, button_size)
    pygame.draw.rect(screen, BUTTON_HOVER_BG, minimize_rect)
    pygame.draw.rect(screen, BUTTON_HOVER_BORDER, minimize_rect, 1)
    
    # Draw minimize icon (horizontal line)
    line_y = minimize_rect.centery
    line_start = minimize_rect.left + 4
    line_end = minimize_rect.right - 4
    pygame.draw.line(screen, BUTTON_TEXT_COLOUR, 
                    (line_start, line_y), (line_end, line_y), 2)
    
    # Draw content if provided and not minimized
    if content and not minimized:
        content_y = y + header_height + 8
        content_x = x + 8
        
        # Simple multiline text rendering
        lines = content.split('\n')
        line_height = font.get_height() + 2
        
        for i, line in enumerate(lines):
            if content_y + i * line_height < y + height - 8:  # Don't overflow window
                line_surface = font.render(line, True, TEXT_COLOUR)
                screen.blit(line_surface, (content_x, content_y + i * line_height))
    
    return header_rect, minimize_rect


def draw_window_with_header_positioned(screen: pygame.Surface, 
                                     x: int, y: int, width: int, height: int,
                                     title: str, 
                                     minimizable: bool = True,
                                     header_height: Optional[int] = None) -> Tuple[pygame.Rect, Optional[pygame.Rect]]:
    """
    Draw a window with a header and optional minimize button using position parameters.
    
    Args:
        screen: The surface to draw on
        x, y: Window position
        width, height: Window dimensions
        title: Window title text
        minimizable: Whether to show minimize button
        header_height: Custom header height (default calculated from screen)
        
    Returns:
        Tuple of (header_rect, minimize_button_rect or None)
    """
    if header_height is None:
        header_height = int(screen.get_height() * 0.04)
    
    # Draw window background
    window_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, BACKGROUND_COLOUR, window_rect)
    pygame.draw.rect(screen, BUTTON_NORMAL_BORDER, window_rect, 2)
    
    # Draw header background
    header_rect = pygame.Rect(x, y, width, header_height)
    pygame.draw.rect(screen, BUTTON_NORMAL_BG, header_rect)
    pygame.draw.rect(screen, BUTTON_NORMAL_BORDER, header_rect, 1)
    
    # Draw title text
    font = font_manager.get_normal_font(screen.get_height())
    if font is None:
        try:
            font = pygame.font.Font(None, int(screen.get_height() * 0.025))
        except pygame.error:
            # If font creation fails, skip text rendering
            minimize_rect = None
            if minimizable:
                button_size = header_height - 4
                minimize_rect = pygame.Rect(x + width - button_size - 2, y + 2, button_size, button_size)
                pygame.draw.rect(screen, BUTTON_HOVER_BG, minimize_rect)
                pygame.draw.rect(screen, BUTTON_HOVER_BORDER, minimize_rect, 1)
                # Draw minimize icon (horizontal line)
                line_y = minimize_rect.centery
                line_start = minimize_rect.left + 4
                line_end = minimize_rect.right - 4
                pygame.draw.line(screen, BUTTON_TEXT_COLOUR, 
                                (line_start, line_y), (line_end, line_y), 2)
            return header_rect, minimize_rect
    title_surface = font.render(title, True, BUTTON_TEXT_COLOUR)
    title_x = x + 8
    title_y = y + (header_height - title_surface.get_height()) // 2
    screen.blit(title_surface, (title_x, title_y))
    
    # Draw minimize button if requested
    minimize_rect = None
    if minimizable:
        button_size = header_height - 4
        minimize_rect = pygame.Rect(x + width - button_size - 2, y + 2, button_size, button_size)
        pygame.draw.rect(screen, BUTTON_HOVER_BG, minimize_rect)
        pygame.draw.rect(screen, BUTTON_HOVER_BORDER, minimize_rect, 1)
        
        # Draw minimize icon (horizontal line)
        line_y = minimize_rect.centery
        line_start = minimize_rect.left + 4
        line_end = minimize_rect.right - 4
        pygame.draw.line(screen, BUTTON_TEXT_COLOUR, 
                        (line_start, line_y), (line_end, line_y), 2)
    
    return header_rect, minimize_rect


def draw_panel(screen: pygame.Surface,
               x: int, y: int, width: int, height: int,
               border_colour: Tuple[int, int, int] = BUTTON_NORMAL_BORDER,
               bg_colour: Tuple[int, int, int] = BACKGROUND_COLOUR,
               border_width: int = 2) -> pygame.Rect:
    """
    Draw a simple panel with background and border.
    
    Args:
        screen: The surface to draw on
        x, y: Panel position
        width, height: Panel dimensions
        border_colour: Border colour
        bg_colour: Background colour
        border_width: Border thickness
        
    Returns:
        The panel rectangle
    """
    panel_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, bg_colour, panel_rect)
    pygame.draw.rect(screen, border_colour, panel_rect, border_width)
    return panel_rect


def draw_dialog_background(screen: pygame.Surface,
                          dialog_rect: pygame.Rect,
                          alpha: int = 128) -> None:
    """
    Draw a semi-transparent background for modal dialogs.
    
    Args:
        screen: The surface to draw on
        dialog_rect: The dialog rectangle to leave uncovered
        alpha: Transparency level (0-255)
    """
    # Create semi-transparent overlay
    overlay = pygame.Surface(screen.get_size())
    overlay.set_alpha(alpha)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))


def draw_bordered_rect(screen: pygame.Surface,
                      rect: pygame.Rect,
                      bg_colour: Tuple[int, int, int],
                      border_colour: Tuple[int, int, int],
                      border_width: int = 1,
                      corner_radius: int = 0) -> None:
    """
    Draw a rectangle with background and border.
    
    Args:
        screen: The surface to draw on
        rect: Rectangle to draw
        bg_colour: Background colour
        border_colour: Border colour
        border_width: Border thickness
        corner_radius: Corner radius for rounded rectangles
    """
    if corner_radius > 0:
        pygame.draw.rect(screen, bg_colour, rect, border_radius=corner_radius)
        pygame.draw.rect(screen, border_colour, rect, border_width, border_radius=corner_radius)
    else:
        pygame.draw.rect(screen, bg_colour, rect)
        pygame.draw.rect(screen, border_colour, rect, border_width)