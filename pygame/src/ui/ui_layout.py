'''
UI Layout and State Module

This module provides UI layout and state management functions for the P(Doom) UI system.
Extracted from the main ui.py monolith as part of the Phase 3 refactoring effort.

Functions:
- draw_top_bar_info: Enhanced top bar with date, version, debug hotkeys
- draw_dev_mode_indicator: Developer mode indicator display
- draw_version_footer: Version display in footer area
- draw_version_header: Version display in header area
- draw_context_window: Bottom context window with detailed information
- UI state utility functions
'''

import pygame
from typing import Dict, Any, Optional, Tuple


def draw_dev_mode_indicator(screen: pygame.Surface, w: int, h: int, font: Optional[pygame.font.Font] = None) -> None:
    '''
    Draw developer mode indicator in top-left corner if DEV MODE is enabled.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for positioning
        font: optional font for dev mode text
    '''
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


def draw_version_footer(screen: pygame.Surface, w: int, h: int, font: Optional[pygame.font.Font] = None) -> None:
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


def draw_version_header(screen: pygame.Surface, w: int, h: int, font: Optional[pygame.font.Font] = None) -> None:
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


def draw_top_bar_info(screen: pygame.Surface, game_state: Any, w: int, h: int, small_font: pygame.font.Font, font: pygame.font.Font) -> None:
    '''
    Draw enhanced top bar with game date, version, and debug hotkeys.
    
    Args:
        screen: pygame screen surface
        game_state: current game state
        w, h: screen dimensions
        small_font, font: pygame font objects
    '''
    from src.services.version import get_display_version
    from src.services.config_manager import get_current_config
    
    top_y = int(h * 0.01)  # Very top of screen
    
    # 1. GAME DATE (Top Left)
    if hasattr(game_state, 'game_clock') and game_state.game_clock:
        date_text = f'Week of {game_state.game_clock.get_formatted_date()}'
        date_color = (180, 220, 255)  # Light blue
        date_surface = small_font.render(date_text, True, date_color)
        screen.blit(date_surface, (int(w * 0.02), top_y))
    
    # 2. VERSION NUMBER (Top Right)
    version_text = f'v{get_display_version()}'
    version_color = (200, 200, 200)  # Light gray
    version_surface = small_font.render(version_text, True, version_color)
    version_x = w - version_surface.get_width() - int(w * 0.02)
    screen.blit(version_surface, (version_x, top_y))
    
    # 3. DEBUG HOTKEYS (Top Center) - Configurable based on debug mode
    config = get_current_config()
    debug_mode = config.get('advanced', {}).get('debug_mode', True)  # Default to True for beta
    
    if debug_mode:
        # Debug hotkey hints in center
        hotkeys_text = '[H] Help  [C] Clear UI  [[] Screenshot  [M] Menu'
        hotkeys_color = (160, 160, 160)  # Dim gray so not distracting
        hotkeys_surface = small_font.render(hotkeys_text, True, hotkeys_color)
        hotkeys_x = (w - hotkeys_surface.get_width()) // 2
        screen.blit(hotkeys_surface, (hotkeys_x, top_y))


def draw_context_window(screen: pygame.Surface, context_info: Dict[str, Any], w: int, h: int, minimized: bool = False, config: Optional[Dict[str, Any]] = None) -> Tuple[Optional[pygame.Rect], Optional[pygame.Rect]]:
    '''
    Draw a context window at the bottom of the screen showing detailed information.
    
    Args:
        screen: pygame screen surface
        context_info: dict with 'title', 'description', 'details' keys
        w, h: screen dimensions
        minimized: whether the context window is minimized
        config: optional config dict for customization
        
    Returns:
        tuple: (context_rect, button_rect) for interaction handling
    '''
    if not context_info:
        return None, None  # No context to show
    
    # Get configuration settings - reduced height to save screen space
    if config and 'ui' in config and 'context_window' in config['ui']:
        ctx_config = config['ui']['context_window']
        expanded_height_percent = ctx_config.get('height_percent', 0.07)  # Reduced from 0.10 to 0.07
        minimized_height_percent = ctx_config.get('minimized_height_percent', 0.04)  # Reduced from 0.05 to 0.04
    else:
        # Default values if no config - bottom 6-7% of screen (much more compact)
        expanded_height_percent = 0.07
        minimized_height_percent = 0.04
    
    # Context window dimensions - positioned at bottom with configurable height
    window_height = int(h * minimized_height_percent) if minimized else int(h * expanded_height_percent)
    window_width = int(w * 0.98)
    window_x = int(w * 0.01)
    window_y = h - window_height - 5  # 5px margin from bottom
    
    # Background with rounded corners - 80's techno green theme
    context_rect = pygame.Rect(window_x, window_y, window_width, window_height)
    # Light readable techno green background
    pygame.draw.rect(screen, (40, 80, 40), context_rect, border_radius=8)  # Dark green base
    pygame.draw.rect(screen, (100, 200, 100), context_rect, width=2, border_radius=8)  # Bright green border
    
    # Header with title and minimize button - retro DOS style
    header_height = 22
    header_rect = pygame.Rect(window_x, window_y, window_width, header_height)
    pygame.draw.rect(screen, (60, 120, 60), header_rect, border_radius=8)  # Darker green header
    
    # Title - ALL CAPS DOS style
    title_font = pygame.font.SysFont('Courier', max(12, int(h*0.018)), bold=True)  # Courier for DOS feel
    title_color = (200, 255, 200)  # Bright green text
    title_text = title_font.render(str(context_info.get('title', 'CONTEXT')).upper(), True, title_color)
    screen.blit(title_text, (window_x + 8, window_y + 3))
    
    # Minimize/Maximize button - green theme
    button_size = 16
    button_x = window_x + window_width - button_size - 4
    button_y = window_y + 3
    button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
    
    # Button background
    pygame.draw.rect(screen, (80, 150, 80), button_rect, border_radius=3)  # Green button
    pygame.draw.rect(screen, (150, 255, 150), button_rect, width=1, border_radius=3)  # Bright green border
    
    # Button symbol
    symbol_font = pygame.font.SysFont('Courier', 10, bold=True)  # DOS font
    symbol = '-' if not minimized else '+'
    symbol_text = symbol_font.render(symbol, True, (200, 255, 200))  # Bright green text
    symbol_rect = symbol_text.get_rect(center=button_rect.center)
    screen.blit(symbol_text, symbol_rect)
    
    if not minimized:
        # Content area
        content_y = window_y + header_height + 3
        content_x = window_x + 8
        
        # Description - DOS style ALL CAPS
        desc_font = pygame.font.SysFont('Courier', max(10, int(h*0.016)))  # Courier for DOS, slightly larger
        description = str(context_info.get('description', ''))
        
        if description:
            # Convert to ALL CAPS for DOS terminal feel
            description = description.upper()
            
            # Simple word wrap for description
            words = description.split(' ')
            current_line = ''
            lines: list[str] = []
            max_chars_per_line = max(25, (window_width - 16) // 8)  # Adjusted for Courier font
            
            for word in words:
                test_line = current_line + (' ' if current_line else '') + word
                if len(test_line) <= max_chars_per_line:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            # Render description lines
            line_height = desc_font.get_height() + 1
            current_y = content_y
            
            for line in lines[:2]:  # Show up to 2 lines of description
                if current_y + line_height > window_y + window_height - 3:
                    break
                line_text = desc_font.render(line, True, (180, 255, 180))  # Bright green text
                screen.blit(line_text, (content_x, current_y))
                current_y += line_height
            
            # Move to details section
            current_y += 3  # Small gap
        else:
            current_y = content_y
        
        # Details section - DOS style
        details = context_info.get('details', [])
        if details and current_y < window_y + window_height - 15:
            detail_font = pygame.font.SysFont('Courier', max(9, int(h*0.014)))  # Courier for DOS
            
            # Horizontal layout for details to save space
            detail_x = content_x
            detail_y = current_y
            
            for detail in details[:4]:  # Show up to 4 details
                # Convert details to ALL CAPS
                detail_str = str(detail).upper()
                detail_text = detail_font.render(detail_str, True, (150, 220, 150))  # Medium green text
                
                # Check if detail fits on current line
                if detail_x + detail_text.get_width() + 20 > window_x + window_width - 10:
                    # Move to next line
                    detail_y += detail_font.get_height() + 1
                    detail_x = content_x
                    
                    # Check if we have room for another line
                    if detail_y + detail_font.get_height() > window_y + window_height - 3:
                        break
                
                screen.blit(detail_text, (detail_x, detail_y))
                detail_x += detail_text.get_width() + 20  # Space between details
    
    return context_rect, button_rect
