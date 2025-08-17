"""
Turn transition screen for P(Doom) - Display turn processing overlay

This module provides the turn transition overlay that shows during turn
processing with visual effects and progress indicators.
"""

import pygame


def draw_turn_transition_overlay(screen, w, h, timer, duration):
    """
    Draw a turn transition overlay with darkening/lightening effect.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height
        timer: current timer value (counts down from duration to 0)
        duration: total duration of the transition
    """
    if timer <= 0 or duration <= 0:
        return
    
    # Calculate transition progress (0.0 to 1.0)
    progress = 1.0 - (timer / duration)
    
    # Create overlay surface
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(128)  # Semi-transparent
    
    # Calculate overlay color based on progress
    # Start dark, then lighten, then back to normal
    if progress < 0.5:
        # First half: darken
        darkness = int(100 * (progress * 2))  # 0 to 100
        overlay.fill((darkness, darkness, darkness))
    else:
        # Second half: lighten back to normal
        lightness = int(100 * (2 - progress * 2))  # 100 to 0
        overlay.fill((lightness, lightness, lightness))
    
    # Draw overlay
    screen.blit(overlay, (0, 0))
    
    # Add "Processing Turn..." text in center
    font = pygame.font.SysFont('Consolas', int(h * 0.04), bold=True)
    text_color = (255, 255, 255) if progress < 0.5 else (50, 50, 50)  # White on dark, dark on light
    text_surf = font.render("Processing Turn...", True, text_color)
    text_x = w // 2 - text_surf.get_width() // 2
    text_y = h // 2 - text_surf.get_height() // 2
    screen.blit(text_surf, (text_x, text_y))
    
    # Add progress indicator
    progress_width = int(w * 0.3)
    progress_height = 8
    progress_x = w // 2 - progress_width // 2
    progress_y = text_y + text_surf.get_height() + 20
    
    # Background bar
    progress_bg = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
    pygame.draw.rect(screen, (100, 100, 100), progress_bg)
    
    # Progress bar
    progress_fill_width = int(progress_width * progress)
    progress_fill = pygame.Rect(progress_x, progress_y, progress_fill_width, progress_height)
    progress_color = (100, 200, 100)  # Green progress bar
    pygame.draw.rect(screen, progress_color, progress_fill)