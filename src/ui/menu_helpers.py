'''
Menu helper utilities for consistent menu behavior across P(Doom).

Quick win refactoring to reduce duplication in menu click handling.
'''

import pygame
from typing import Tuple, List, Optional, Callable


def get_menu_button_collision(
    mouse_pos: Tuple[int, int], 
    menu_items: List[str], 
    w: int, 
    h: int,
    button_width_ratio: float = 0.4,
    button_height_ratio: float = 0.08,
    start_y_ratio: float = 0.35,
    spacing_ratio: float = 0.1
) -> Optional[int]:
    '''
    Check if mouse position collides with any menu button.
    
    Args:
        mouse_pos: (x, y) mouse coordinates
        menu_items: List of menu item strings
        w, h: Screen dimensions
        button_width_ratio: Button width as ratio of screen width
        button_height_ratio: Button height as ratio of screen height  
        start_y_ratio: Starting Y position as ratio of screen height
        spacing_ratio: Vertical spacing as ratio of screen height
        
    Returns:
        Index of clicked menu item, or None if no collision
    '''
    button_width = int(w * button_width_ratio)
    button_height = int(h * button_height_ratio)
    start_y = int(h * start_y_ratio)
    spacing = int(h * spacing_ratio)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    for i, item in enumerate(menu_items):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            return i
    
    return None


def handle_menu_navigation(
    key: int,
    current_selection: int,
    menu_items: List[str],
    on_select: Optional[Callable[[int], None]] = None
) -> int:
    '''
    Handle keyboard navigation for menus with consistent behavior.
    
    Args:
        key: pygame key constant
        current_selection: Currently selected menu index
        menu_items: List of menu items
        on_select: Optional callback for when item is selected with Enter/Space
        
    Returns:
        New selection index
    '''
    if key in [pygame.K_UP, pygame.K_LEFT]:
        return (current_selection - 1) % len(menu_items)
    elif key in [pygame.K_DOWN, pygame.K_RIGHT]:
        return (current_selection + 1) % len(menu_items)
    elif key in [pygame.K_RETURN, pygame.K_SPACE] and on_select:
        on_select(current_selection)
        return current_selection
    
    return current_selection


def handle_mouse_wheel_menu_navigation(
    wheel_y: int,
    current_selection: int,
    menu_items: List[str]
) -> int:
    '''
    Handle mouse wheel navigation for menus with consistent behavior.
    
    Args:
        wheel_y: Mouse wheel Y direction (positive = up, negative = down)
        current_selection: Currently selected menu index
        menu_items: List of menu items
        
    Returns:
        New selection index
    '''
    if wheel_y > 0:  # Mouse wheel up
        return (current_selection - 1) % len(menu_items)
    elif wheel_y < 0:  # Mouse wheel down
        return (current_selection + 1) % len(menu_items)
    
    return current_selection
