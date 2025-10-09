'''
Reusable UI components for the P(Doom) interface.

This module contains small, focused utility functions for drawing
common UI elements like tooltips, version info, and status indicators.
'''

import pygame
from typing import Tuple, Optional


def draw_dev_mode_indicator(screen, w: int, h: int, font=None):
    '''Draw developer mode indicator in top-left corner if DEV MODE is enabled.'''
    try:
        from src.services.dev_mode import get_dev_status_text
        dev_text = get_dev_status_text()
        
        if not dev_text:
            return  # DEV MODE not enabled
        
        if font is None:
            font = pygame.font.SysFont('Consolas', max(14, int(h * 0.022)), bold=True)
        
        # Create text with bright orange/yellow color for visibility
        dev_surf = font.render(f'[{dev_text}]', True, (255, 165, 0))
        
        # Position in top-left corner with margin
        margin = int(h * 0.015)
        screen.blit(dev_surf, (margin, margin))
        
    except ImportError:
        pass  # Silently fail if dev_mode module not available


def draw_version_footer(screen, w: int, h: int, font=None):
    '''Draw version information in the footer area.'''
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


def draw_version_header(screen, w: int, h: int, font=None):
    '''Draw version information in the header area (alternative placement).'''
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


def draw_tooltip(screen, text: str, mouse_pos: Tuple[int, int], w: int, h: int):
    '''Draw a tooltip at the mouse position with text.'''
    font = pygame.font.SysFont('Consolas', int(h*0.018))
    surf = font.render(text, True, (230,255,200))
    tw, th = surf.get_size()
    px, py = mouse_pos
    # Prevent tooltip going off screen
    if px+tw > w: px = w-tw-10
    if py+th > h: py = h-th-10
    pygame.draw.rect(screen, (40, 40, 80), (px, py, tw+12, th+12), border_radius=6)
    screen.blit(surf, (px+6, py+6))


def draw_loading_screen(screen, w: int, h: int, progress: float = 0, status_text: str = 'Loading...', font=None):
    '''Draw a loading screen with progress indicator and accessibility support.'''
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
        percent_text = subtitle_font.render(f'{int(progress * 100)}%', True, (150, 150, 150))
        percent_x = w // 2 - percent_text.get_width() // 2
        percent_y = status_y + status_surf.get_height() + 10
        screen.blit(percent_text, (percent_x, percent_y))


def should_show_ui_element(game_state, element_id: str) -> bool:
    '''Check if a UI element should be visible based on tutorial progress.'''
    # Import onboarding here to avoid circular imports
    from src.features.onboarding import onboarding
    
    # If tutorial is not active, show all elements
    if not onboarding.show_tutorial_overlay:
        return True
    
    # Check if element should be visible based on tutorial progress
    return onboarding.should_show_ui_element(element_id)


def draw_mute_button_standalone(screen, sound_manager, w: int, h: int):
    '''Draw mute/unmute button in bottom right corner (standalone version for menus)'''
    # Button position (bottom right) - made larger per issue #89
    button_size = int(min(w, h) * 0.06)  # Same size as main game mute button
    button_x = w - button_size - 20
    button_y = h - button_size - 20
    
    # Button colors
    if sound_manager and sound_manager.is_enabled():
        bg_color = (100, 200, 100)  # Green when sound is on
        icon_color = (255, 255, 255)
        symbol = '~'  # Musical note when sound is on
    else:
        bg_color = (200, 100, 100)  # Red when sound is off
        icon_color = (255, 255, 255) 
        symbol = 'X'  # Muted symbol when sound is off
    
    # Draw button background
    button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
    pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, width=2, border_radius=8)
    
    # Draw icon
    font_size = int(button_size * 0.6)
    font = pygame.font.SysFont('Arial', font_size)
    icon_surf = font.render(symbol, True, icon_color)
    icon_x = button_x + (button_size - icon_surf.get_width()) // 2
    icon_y = button_y + (button_size - icon_surf.get_height()) // 2
    screen.blit(icon_surf, (icon_x, icon_y))
