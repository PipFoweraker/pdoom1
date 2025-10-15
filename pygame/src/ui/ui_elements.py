'''
UI element drawing functions for P(Doom) - Employee blobs, buttons, and UI widgets

This module contains drawing functions for interactive UI elements including:
- Employee visualization (blobs with animations)
- Button components (mute, back buttons)
- Basic UI widgets and controls

Extracted from ui.py as part of Phase 3 UI modularization.
'''

import pygame
from typing import Any, Optional, Tuple, List


def draw_employee_blobs(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    '''
    Draw animated employee blobs (circles representing staff members).
    
    Handles positioning, animation, visual effects, and employee state display.
    Includes productivity halos, type differentiation, and dynamic repositioning.
    '''
    if not hasattr(game_state, 'employee_blobs') or not game_state.employee_blobs:
        return
    
    # Update blob positions dynamically to avoid UI elements
    # This is called every frame to ensure continuous repositioning
    game_state._update_blob_positions_dynamically(w, h)
    
    # Handle initial positioning for new blobs that haven't been positioned yet
    for i, blob in enumerate(game_state.employee_blobs):
        # Initialize position for new blobs or those that need repositioning
        if blob.get('needs_position_update', False):
            new_x, new_y = game_state._calculate_blob_position(i, w, h)
            blob['target_x'] = new_x
            blob['target_y'] = new_y
            # If blob is already animated in, update current position too
            if blob['animation_progress'] >= 1.0:
                blob['x'] = new_x
                blob['y'] = new_y
            blob['needs_position_update'] = False
    
    # Update blob animations for new employees - now appearing directly instead of sliding in
    for blob in game_state.employee_blobs:
        if blob['animation_progress'] < 1.0:
            blob['animation_progress'] = min(1.0, blob['animation_progress'] + 0.2)  # Faster fade-in
            # Fade in at target position instead of sliding from edge
            blob['x'] = blob['target_x']  # Appear directly at target position
    
    # Draw each blob
    for blob in game_state.employee_blobs:
        x, y = int(blob['x']), int(blob['y'])
        
        # Skip if still animating in and off-screen
        if x < 0:
            continue
            
        # Draw halo for productive employees (those with compute)
        if blob['has_compute']:
            # Glowing halo effect
            halo_radius = 35
            for i in range(3):
                alpha = 80 - i * 20
                halo_color = (100, 255, 150, alpha)
                # Create a surface for the halo with alpha
                halo_surface = pygame.Surface((halo_radius * 2, halo_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(halo_surface, halo_color, (halo_radius, halo_radius), halo_radius - i * 3)
                screen.blit(halo_surface, (x - halo_radius, y - halo_radius))
        
        # Draw the main blob (employee or manager)
        blob_radius = 20
        
        # Different colors for managers vs employees
        if blob.get('type') == 'manager':
            blob_color = (100, 255, 100) if blob['has_compute'] else (80, 200, 80)  # Green for managers
        else:
            blob_color = (150, 200, 255) if blob['has_compute'] else (100, 150, 200)  # Blue for employees
        
        # Main blob body
        pygame.draw.circle(screen, blob_color, (x, y), blob_radius)
        pygame.draw.circle(screen, (255, 255, 255), (x, y), blob_radius, 2)
        
        # Simple face (eyes)
        eye_offset = 6
        eye_radius = 3
        pygame.draw.circle(screen, (50, 50, 100), (x - eye_offset, y - 4), eye_radius)
        pygame.draw.circle(screen, (50, 50, 100), (x + eye_offset, y - 4), eye_radius)
        
        # Productivity indicator (small dot)
        if blob['productivity'] > 0:
            pygame.draw.circle(screen, (100, 255, 100), (x, y + 8), 4)


def draw_mute_button(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    '''Draw mute/unmute button in bottom right corner'''
    # Button position (bottom right) - made larger per issue #89
    button_size = int(min(w, h) * 0.06)  # Increased from 0.04 to 0.06 for better visibility
    button_x = w - button_size - 20
    button_y = h - button_size - 20
    
    # Button colors
    if hasattr(game_state, 'sound_manager') and game_state.sound_manager and game_state.sound_manager.is_enabled():
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


def draw_mute_button_standalone(screen: pygame.Surface, sound_manager: Any, w: int, h: int) -> None:
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


def draw_back_button(screen: pygame.Surface, w: int, h: int, navigation_depth: int, font: Optional[pygame.font.Font] = None) -> Optional[pygame.Rect]:
    '''
    Draw a Back button when navigation depth >= 1.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for positioning
        navigation_depth: current navigation depth from navigation stack
        font: optional font for the button text
    
    Returns:
        pygame.Rect: The button rectangle for click detection, or None if not rendered
    '''
    if navigation_depth < 1:
        return None
    
    if font is None:
        font = pygame.font.SysFont('Consolas', max(16, int(h * 0.025)))
    
    # Position button in top-left corner with margin
    margin = int(h * 0.02)
    button_text = '< Back'
    text_surf = font.render(button_text, True, (255, 255, 255))
    
    # Button styling
    padding = int(h * 0.01)
    button_width = text_surf.get_width() + padding * 2
    button_height = text_surf.get_height() + padding * 2
    button_rect = pygame.Rect(margin, margin, button_width, button_height)
    
    # Draw button background with subtle styling
    pygame.draw.rect(screen, (60, 60, 80), button_rect)
    pygame.draw.rect(screen, (120, 120, 140), button_rect, 2)
    
    # Center text in button
    text_x = button_rect.x + (button_rect.width - text_surf.get_width()) // 2
    text_y = button_rect.y + (button_rect.height - text_surf.get_height()) // 2
    screen.blit(text_surf, (text_x, text_y))
    
    return button_rect


def draw_tooltip(screen: pygame.Surface, text: str, mouse_pos: Tuple[int, int], w: int, h: int) -> None:
    '''
    Draw a tooltip near the mouse position with the given text.
    
    Args:
        screen: pygame surface to draw on
        text: tooltip text to display
        mouse_pos: current mouse position (x, y)
        w, h: screen dimensions for boundary checking
    '''
    font = pygame.font.SysFont('Consolas', int(h*0.018))
    surf = font.render(text, True, (230,255,200))
    tw, th = surf.get_size()
    px, py = mouse_pos
    
    # Prevent tooltip going off screen
    if px+tw > w: 
        px = w-tw-10
    if py+th > h: 
        py = h-th-10
    
    # Draw tooltip background with rounded corners
    pygame.draw.rect(screen, (40, 40, 80), (px, py, tw+12, th+12), border_radius=6)
    screen.blit(surf, (px+6, py+6))


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    '''
    Splits the text into multiple lines so that each line fits within max_width.
    Returns a list of strings, each representing a line.
    Improved to handle overflow with better word breaking.
    '''
    lines: list[str] = []
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
                # Single word too long - break it up
                while font.size(word)[0] > max_width and word:
                    # Find maximum characters that fit
                    for i in range(len(word)-1, 0, -1):
                        if font.size(word[:i])[0] <= max_width:
                            lines.append(word[:i])
                            word = word[i:]
                            break
                    else:
                        # Even single character doesn't fit
                        lines.append(word[0])
                        word = word[1:]
                curr_line = word
    if curr_line:
        lines.append(curr_line)
    
    return lines
