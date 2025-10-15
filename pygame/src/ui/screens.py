'''
Window, overlay, and screen rendering utilities for the P(Doom) game interface.

This module contains functions for drawing overlays, windows with headers,
version information, and loading screens.
'''

import pygame
from src.ui.text import wrap_text, draw_back_button


def draw_overlay(screen, title, content, scroll_offset, w, h, navigation_depth=0):
    '''
    Draw a scrollable overlay for displaying README or Player Guide content.
    
    Args:
        screen: pygame surface to draw on
        title: string title to display at top of overlay (can be None)
        content: full text content to display (can be None)
        scroll_offset: vertical scroll position in pixels
        w, h: screen width and height for responsive layout
        navigation_depth: current navigation depth for Back button display
    
    Returns:
        back_button_rect: Rectangle for Back button click detection (or None)
    
    Features:
    - Semi-transparent dark background overlay
    - Centered content area with border
    - Scrollable text with line wrapping
    - Scroll indicators (up/down arrows) when content exceeds view area  
    - Responsive text sizing based on screen dimensions
    - Clear navigation instructions
    - Defensive handling of None title/content values
    - Back button when navigation depth > 1
    
    The overlay handles long documents by breaking them into lines and showing
    only the visible portion based on scroll_offset. Users can scroll with
    arrow keys to view the full document.
    '''
    # Defensive handling for None values
    if title is None:
        title = 'Information Unavailable'
    if content is None:
        content = 'Content Not Available\n\nThe requested information could not be loaded at this time.\n\nPossible solutions:\n- Press Escape or Back to return to the previous screen\n- Try accessing this information again from the main menu\n- Check the Player Guide (F1) for general help\n\nIf this problem persists, it may indicate a technical issue.'
    # Overlay background - semi-transparent dark background
    overlay_surface = pygame.Surface((w, h))
    overlay_surface.set_alpha(240)
    overlay_surface.fill((20, 20, 30))
    screen.blit(overlay_surface, (0, 0))
    
    # Draw Back button if needed
    back_button_rect = draw_back_button(screen, w, h, navigation_depth)
    
    # Content area
    margin = int(w * 0.1)
    content_x = margin
    content_y = int(h * 0.1)
    content_width = w - 2 * margin
    content_height = int(h * 0.7)
    
    # Background for content area
    content_rect = pygame.Rect(content_x, content_y, content_width, content_height)
    pygame.draw.rect(screen, (40, 40, 50), content_rect, border_radius=15)
    pygame.draw.rect(screen, (100, 100, 150), content_rect, width=3, border_radius=15)
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h*0.04), bold=True)
    title_surf = title_font.render(title, True, (255, 255, 255))
    title_x = content_x + (content_width - title_surf.get_width()) // 2
    title_y = content_y + int(h * 0.02)
    screen.blit(title_surf, (title_x, title_y))
    
    # Content text area
    text_area_y = title_y + title_surf.get_height() + int(h * 0.03)
    text_area_height = content_height - (text_area_y - content_y) - int(h * 0.05)
    text_margin = int(w * 0.02)
    text_width = content_width - 2 * text_margin
    
    # Font for content
    content_font = pygame.font.SysFont('Consolas', int(h*0.02))
    line_height = content_font.get_height()
    
    # Split content into lines and handle scrolling
    lines = content.split('\n')
    visible_lines = int(text_area_height // line_height)
    start_line = scroll_offset // line_height
    end_line = min(start_line + visible_lines, len(lines))
    
    # Draw visible lines
    for i in range(start_line, end_line):
        if i < len(lines):
            line = lines[i]
            # Simple text wrapping for long lines
            wrapped_lines = wrap_text(line, content_font, text_width)
            
            for j, wrapped_line in enumerate(wrapped_lines):
                y_pos = text_area_y + (i - start_line + j) * line_height - (scroll_offset % line_height)
                if y_pos >= text_area_y and y_pos < text_area_y + text_area_height:
                    line_surf = content_font.render(wrapped_line, True, (220, 220, 220))
                    screen.blit(line_surf, (content_x + text_margin, y_pos))
    
    # Scroll indicators
    if scroll_offset > 0:
        # Up arrow
        arrow_font = pygame.font.SysFont('Consolas', int(h*0.03), bold=True)
        up_arrow = arrow_font.render('?', True, (255, 255, 255))
        screen.blit(up_arrow, (content_x + content_width - 30, text_area_y))
    
    if (start_line + visible_lines) < len(lines):
        # Down arrow
        arrow_font = pygame.font.SysFont('Consolas', int(h*0.03), bold=True)
        down_arrow = arrow_font.render('?', True, (255, 255, 255))
        screen.blit(down_arrow, (content_x + content_width - 30, text_area_y + text_area_height - 30))
    
    # Instructions at bottom
    instruction_font = pygame.font.SysFont('Consolas', int(h*0.025))
    instructions = 'Use arrow keys to scroll ? Press Escape or click to return to menu'
    inst_surf = instruction_font.render(instructions, True, (180, 200, 255))
    inst_x = w // 2 - inst_surf.get_width() // 2
    inst_y = content_y + content_height + int(h * 0.03)
    screen.blit(inst_surf, (inst_x, inst_y))
    
    return back_button_rect


def draw_window_with_header(screen, rect, title, content=None, minimized=False, font=None):
    '''
    Draw a window with a draggable header and minimize button.
    
    Args:
        screen: pygame surface to draw on
        rect: pygame.Rect defining window position and size
        title: window title text
        content: optional content to draw in window body
        minimized: whether window is in minimized state
        font: optional font for title text
        
    Returns:
        tuple: (header_rect, minimize_button_rect) for interaction handling
    '''
    if font is None:
        font = pygame.font.SysFont('Consolas', 16)
    
    # Window colors
    header_color = (60, 60, 80)
    header_border = (120, 120, 140)
    body_color = (40, 40, 55)
    body_border = (100, 100, 120)
    
    # Header dimensions
    header_height = 30
    header_rect = pygame.Rect(rect.x, rect.y, rect.width, header_height)
    
    # Draw header
    pygame.draw.rect(screen, header_color, header_rect)
    pygame.draw.rect(screen, header_border, header_rect, 2)
    
    # Draw title text
    title_surf = font.render(title, True, (255, 255, 255))
    title_x = header_rect.x + 8
    title_y = header_rect.y + (header_height - title_surf.get_height()) // 2
    screen.blit(title_surf, (title_x, title_y))
    
    # Draw minimize button (? or ? based on state)
    button_size = 20
    button_margin = 5
    minimize_button_rect = pygame.Rect(
        header_rect.right - button_size - button_margin,
        header_rect.y + (header_height - button_size) // 2,
        button_size, button_size
    )
    
    # Button background
    button_color = (80, 80, 100)
    pygame.draw.rect(screen, button_color, minimize_button_rect)
    pygame.draw.rect(screen, header_border, minimize_button_rect, 1)
    
    # Button icon
    icon_color = (255, 255, 255)
    if minimized:
        # Restore icon (?)
        icon_rect = pygame.Rect(
            minimize_button_rect.x + 4, minimize_button_rect.y + 4,
            minimize_button_rect.width - 8, minimize_button_rect.height - 8
        )
        pygame.draw.rect(screen, icon_color, icon_rect, 2)
    else:
        # Minimize icon (?)
        line_y = minimize_button_rect.centery
        line_start = minimize_button_rect.x + 4
        line_end = minimize_button_rect.right - 4
        pygame.draw.line(screen, icon_color, (line_start, line_y), (line_end, line_y), 2)
    
    # Draw body if not minimized
    if not minimized:
        body_rect = pygame.Rect(rect.x, rect.y + header_height, rect.width, rect.height - header_height)
        pygame.draw.rect(screen, body_color, body_rect)
        pygame.draw.rect(screen, body_border, body_rect, 2)
        
        # Draw content if provided
        if content:
            content_rect = pygame.Rect(
                body_rect.x + 8, body_rect.y + 8,
                body_rect.width - 16, body_rect.height - 16
            )
            if isinstance(content, str):
                # Simple text content
                lines = content.split('\n')
                line_height = font.get_height() + 2
                for i, line in enumerate(lines):
                    if i * line_height < content_rect.height:
                        text_surf = font.render(line, True, (255, 255, 255))
                        screen.blit(text_surf, (content_rect.x, content_rect.y + i * line_height))
    
    return header_rect, minimize_button_rect


def draw_version_footer(screen, w, h, font=None):
    '''
    Draw version information in the footer area.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for positioning
        font: optional font for version text
    '''
    try:
        from src.services.version import get_display_version
        version_text = get_display_version()
    except ImportError:
        version_text = 'dev'
    
    if font is None:
        font = pygame.font.SysFont('Consolas', max(12, int(h * 0.02)))
    
    # Position in bottom right corner with margin
    margin = int(h * 0.02)
    version_surf = font.render(version_text, True, (120, 120, 120))
    
    version_x = w - version_surf.get_width() - margin
    version_y = h - version_surf.get_height() - margin
    
    screen.blit(version_surf, (version_x, version_y))


def draw_version_header(screen, w, h, font=None):
    '''
    Draw version information in the header area (alternative placement).
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for positioning
        font: optional font for version text
    '''
    try:
        from src.services.version import get_display_version
        version_text = get_display_version()
    except ImportError:
        version_text = 'dev'
    
    if font is None:
        font = pygame.font.SysFont('Consolas', max(12, int(h * 0.02)))
    
    # Position in top right corner with margin
    margin = int(h * 0.02)
    version_surf = font.render(version_text, True, (120, 120, 120))
    
    version_x = w - version_surf.get_width() - margin
    version_y = margin
    
    screen.blit(version_surf, (version_x, version_y))


def draw_loading_screen(screen, w, h, progress=0, status_text='Loading...', font=None):
    '''
    Draw a loading screen with progress indicator and accessibility support.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height
        progress: loading progress (0.0 to 1.0)
        status_text: text to display for screen readers and status
        font: optional font for status text
        
    Returns:
        None
    
    Accessibility:
    - role='status' equivalent through clear status text
    - High contrast colors for visibility
    - Clear progress indication
    '''
    if font is None:
        font = pygame.font.SysFont('Consolas', max(16, int(h * 0.03)))
    
    # Dark background
    screen.fill((20, 20, 30))
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h * 0.06), bold=True)
    title_text = title_font.render('P(Doom)', True, (255, 255, 255))
    title_x = w // 2 - title_text.get_width() // 2
    title_y = int(h * 0.3)
    screen.blit(title_text, (title_x, title_y))
    
    # Subtitle
    subtitle_font = pygame.font.SysFont('Consolas', int(h * 0.025))
    subtitle_text = subtitle_font.render('Bureaucracy Strategy Prototype', True, (180, 180, 180))
    subtitle_x = w // 2 - subtitle_text.get_width() // 2
    subtitle_y = title_y + title_text.get_height() + 10
    screen.blit(subtitle_text, (subtitle_x, subtitle_y))
    
    # Progress bar
    bar_width = int(w * 0.4)
    bar_height = int(h * 0.02)
    bar_x = w // 2 - bar_width // 2
    bar_y = int(h * 0.5)
    
    # Progress bar background
    pygame.draw.rect(screen, (60, 60, 80), (bar_x, bar_y, bar_width, bar_height))
    
    # Progress bar fill
    fill_width = int(bar_width * max(0, min(1, progress)))
    if fill_width > 0:
        pygame.draw.rect(screen, (100, 150, 255), (bar_x, bar_y, fill_width, bar_height))
    
    # Progress bar border
    pygame.draw.rect(screen, (120, 120, 140), (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Status text
    status_surf = font.render(status_text, True, (200, 200, 200))
    status_x = w // 2 - status_surf.get_width() // 2
    status_y = bar_y + bar_height + 20
    screen.blit(status_surf, (status_x, status_y))
    
    # Progress percentage
    if progress > 0:
        percent_text = font.render(f'{int(progress * 100)}%', True, (150, 150, 150))
        percent_x = w // 2 - percent_text.get_width() // 2
        percent_y = status_y + status_surf.get_height() + 10
        screen.blit(percent_text, (percent_x, percent_y))