"""
Panel drawing functions for the P(Doom) game interface.

This module contains large UI panel functions including context windows,
scoreboards, event panels, and other complex display elements.
"""

import pygame
from typing import Dict, Any, Optional, Tuple


def draw_context_window(screen: pygame.Surface, context_info: Dict[str, Any], w: int, h: int, minimized: bool = False, config: Optional[Dict[str, Any]] = None) -> Tuple[Optional[pygame.Rect], Optional[pygame.Rect]]:
    """
    Draw a context window at the bottom of the screen showing detailed information.
    
    Args:
        screen: pygame screen surface
        context_info: dict with 'title', 'description', 'details' keys
        w, h: screen dimensions
        minimized: whether the context window is minimized
        config: optional config dict for customization
    """
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
            lines = []
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
            
            for i, detail in enumerate(details[:4]):  # Show up to 4 details
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


def draw_scoreboard(screen: pygame.Surface, game_state, w: int, h: int, seed: str) -> None:
    """
    Draw the game over scoreboard with final statistics.
    
    Args:
        screen: pygame screen surface
        game_state: current game state object
        w, h: screen dimensions
        seed: game seed string
    """
    # Scoreboard after game over
    font = pygame.font.SysFont('Consolas', int(h*0.035))
    title = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    big = pygame.font.SysFont('Consolas', int(h*0.05))
    small = pygame.font.SysFont('Consolas', int(h*0.02))

    # Box
    pygame.draw.rect(screen, (40,40,70), (w//6, h//7, w*2//3, h*3//5), border_radius=24)
    pygame.draw.rect(screen, (130, 190, 255), (w//6, h//7, w*2//3, h*3//5), width=5, border_radius=24)

    # Headline
    screen.blit(title.render("GAME OVER", True, (255,0,0)), (w//2 - int(w*0.09), h//7 + int(h*0.05)))
    msg = game_state.messages[-1] if game_state.messages else ""
    screen.blit(big.render(msg, True, (255,220,220)), (w//6 + int(w*0.04), h//7 + int(h*0.16)))

    # Score details
    lines = [
        f"Survived until Turn: {game_state.turn}",
        f"Final Staff: {game_state.staff}",
        f"Final Money: ${game_state.money}",
        f"Final Reputation: {game_state.reputation}",
        f"Final p(Doom): {game_state.doom}",
        f"Seed: {seed}",
        f"High Score (turns): {game_state.highscore}"
    ]
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, (240,255,255)), (w//6 + int(w*0.04), h//7 + int(h*0.27) + i*int(h*0.05)))
    screen.blit(small.render("Click anywhere to restart.", True, (255,255,180)), (w//2 - int(w*0.1), h//7 + int(h*0.5)))
