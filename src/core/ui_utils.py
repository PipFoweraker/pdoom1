"""
UI positioning utilities extracted from game_state.py

This module contains all the UI rectangle calculation and positioning methods
that were cluttering the main GameState class. These are pure functions that
calculate screen positions and sizes based on screen dimensions.
"""

from typing import List, Optional, Tuple, Any
import pygame


def get_action_rects(w: int, h: int) -> List[pygame.Rect]:
    """Calculate action button rectangles based on screen dimensions."""
    action_rects = []
    actions_per_column = 9
    action_start_x = int(w * 0.15)
    action_start_y = int(h * 0.15)
    action_width = int(w * 0.28)
    action_height = int(h * 0.065)
    
    for idx in range(actions_per_column * 2):  # Two columns
        col = idx // actions_per_column
        row = idx % actions_per_column
        x = action_start_x + col * (action_width + int(w * 0.02))
        y = action_start_y + row * (action_height + int(h * 0.005))
        action_rects.append(pygame.Rect(x, y, action_width, action_height))
    
    return action_rects


def get_upgrade_rects(w: int, h: int) -> List[Optional[pygame.Rect]]:
    """Calculate upgrade button rectangles based on screen dimensions."""
    upgrade_rects = []
    upgrade_width = int(w * 0.028)
    upgrade_height = int(h * 0.05)
    upgrades_start_x = int(w * 0.72)
    upgrades_start_y = int(h * 0.12)
    
    for idx in range(16):  # Max 16 upgrades in 4x4 grid
        row = idx // 4
        col = idx % 4
        x = upgrades_start_x + col * (upgrade_width + int(w * 0.005))
        y = upgrades_start_y + row * (upgrade_height + int(h * 0.01))
        upgrade_rects.append(pygame.Rect(x, y, upgrade_width, upgrade_height))
    
    return upgrade_rects


def get_upgrade_icon_rect(upgrade_idx: int, w: int, h: int) -> Optional[Tuple[int, int, int, int]]:
    """Get the rectangle for a specific upgrade icon."""
    if upgrade_idx < 0:
        return None
    
    upgrade_width = int(w * 0.028)
    upgrade_height = int(h * 0.05)
    upgrades_start_x = int(w * 0.72)
    upgrades_start_y = int(h * 0.12)
    
    row = upgrade_idx // 4
    col = upgrade_idx % 4
    x = upgrades_start_x + col * (upgrade_width + int(w * 0.005))
    y = upgrades_start_y + row * (upgrade_height + int(h * 0.01))
    
    return (x, y, upgrade_width, upgrade_height)


def get_context_window_top(h: int) -> int:
    """Calculate the top position of the context window."""
    return int(h * 0.37)


def get_endturn_rect(w: int, h: int) -> Tuple[int, int, int, int]:
    """Calculate the End Turn button rectangle."""
    return (int(w*0.39), int(h*0.74), int(w*0.22), int(h*0.07))  # Moved up to account for context window


def get_mute_button_rect(w: int, h: int) -> Tuple[int, int, int, int]:
    """Calculate the mute button rectangle."""
    button_size = int(min(w, h) * 0.04)
    button_x = w - button_size - 20
    button_y = h - button_size - 20
    return (button_x, button_y, button_size, button_size)


def get_activity_log_minimize_button_rect(w: int, h: int) -> Tuple[int, int, int, int]:
    """Calculate the activity log minimize button rectangle."""
    base_x, base_y = get_activity_log_base_position(w, h)
    button_size = 20
    log_width = int(w * 0.33)
    return (base_x + log_width - button_size - 5, base_y + 5, button_size, button_size)


def get_activity_log_expand_button_rect(w: int, h: int) -> Tuple[int, int, int, int]:
    """Calculate the activity log expand button rectangle."""
    base_x, base_y = get_activity_log_base_position(w, h)
    button_size = 20
    log_width = int(w * 0.33)
    
    # Position relative to minimized state
    return (base_x + log_width - button_size - 5, base_y + 25, button_size, button_size)


def get_activity_log_rect(w: int, h: int) -> Tuple[int, int, int, int]:
    """Calculate the activity log rectangle."""
    base_x, base_y = get_activity_log_base_position(w, h)
    log_width = int(w * 0.33)
    log_height = int(h * 0.15)
    return (base_x, base_y, log_width, log_height)


def get_activity_log_base_position(w: int, h: int) -> Tuple[int, int]:
    """Calculate the base position for the activity log."""
    return (int(w * 0.04), int(h * 0.74))


def get_activity_log_current_position(w: int, h: int) -> Tuple[int, int]:
    """Calculate the current position for the activity log (could be dragged)."""
    # For now, return base position - dragging would modify this in the future
    return get_activity_log_base_position(w, h)


def validate_rect(rect: Any, context: str = "") -> bool:
    """Validate that a rectangle is properly formatted."""
    if rect is None:
        return False
    
    try:
        if len(rect) != 4:
            # Note: Could add logging here if needed
            return False
        
        x, y, w, h = rect
        if not all(isinstance(val, (int, float)) for val in rect):
            # Note: Could add logging here if needed
            return False
            
        return True
    except Exception:
        # Note: Could add logging here if needed
        return False


def get_ui_element_rects(screen_w: int = 1200, screen_h: int = 800) -> List[Tuple[int, int, int, int]]:
    """Get rectangles for all major UI elements for collision detection."""
    ui_rects = []
    
    # Action buttons area
    action_start_x = int(screen_w * 0.15)
    action_start_y = int(screen_w * 0.15)
    action_area_width = int(screen_w * 0.58)  # Two columns + gap
    action_area_height = int(screen_h * 0.65)
    ui_rects.append((action_start_x, action_start_y, action_area_width, action_area_height))
    
    # Upgrades area
    upgrades_x = int(screen_w * 0.72)
    upgrades_y = int(screen_h * 0.12)
    upgrades_width = int(screen_w * 0.15)
    upgrades_height = int(screen_h * 0.25)
    ui_rects.append((upgrades_x, upgrades_y, upgrades_width, upgrades_height))
    
    # Context window
    context_x = int(screen_w * 0.72)
    context_y = get_context_window_top(screen_h)
    context_width = int(screen_w * 0.25)
    context_height = int(screen_h * 0.45)
    ui_rects.append((context_x, context_y, context_width, context_height))
    
    # Activity log
    log_rect = get_activity_log_rect(screen_w, screen_h)
    ui_rects.append(log_rect)
    
    # End turn button
    endturn_rect = get_endturn_rect(screen_w, screen_h)
    ui_rects.append(endturn_rect)
    
    return ui_rects
