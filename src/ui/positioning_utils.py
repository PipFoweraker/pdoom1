'''
UI Positioning Utilities - Elegant Dynamic Layout System

This module provides dynamic UI positioning utilities that automatically adapt
to changes in the UI layout, screen sizes, and component counts.

PREFERRED APPROACH: Instead of hardcoding element counts or positions,
calculate positions dynamically based on actual rendered component rectangles.

Created: 2025-09-29 - Demo Hotfix Session
'''

from typing import Tuple, List, Optional
import pygame


def calculate_activity_log_position(game_state, w: int, h: int) -> Tuple[int, int]:
    '''
    Elegantly calculate activity log position based on actual action button layout.
    
    DESIGN PRINCIPLE: Position elements relative to actual rendered components,
    not estimated counts or hardcoded positions.
    
    Args:
        game_state: Game state containing filtered_action_rects
        w, h: Screen dimensions
        
    Returns:
        Tuple[int, int]: (log_x, log_y) coordinates for activity log
        
    Example Usage:
        log_x, log_y = calculate_activity_log_position(game_state, w, h)
    '''
    log_x = int(w * 0.04)  # Standard left margin
    
    # Check if we have actual action button rects to work with
    if (hasattr(game_state, 'filtered_action_rects') and 
        game_state.filtered_action_rects):
        
        # Find the bottom of the last visible action button
        last_button_bottom = max(rect.bottom for rect in game_state.filtered_action_rects)
        log_y = last_button_bottom + int(h * 0.015)  # 1.5% buffer below buttons
        
    else:
        # Graceful fallback if no action rects available
        log_y = int(h * 0.74)  # Original position
        
    return log_x, log_y


def calculate_dynamic_element_spacing(base_elements: List[pygame.Rect], 
                                    buffer_percent: float = 0.015) -> int:
    '''
    Calculate spacing for new UI elements based on existing element layout.
    
    Args:
        base_elements: List of existing UI element rectangles
        buffer_percent: Buffer as percentage of screen height
        
    Returns:
        int: Y-coordinate for next element placement
    '''
    if not base_elements:
        return 0
        
    return max(rect.bottom for rect in base_elements) + int(buffer_percent * 800)  # Assuming 800px height


def get_safe_positioning_zone(occupied_rects: List[pygame.Rect], 
                            screen_w: int, screen_h: int) -> pygame.Rect:
    '''
    Find safe area for new UI elements that doesn't overlap existing ones.
    
    Args:
        occupied_rects: List of rectangles already occupied by UI elements
        screen_w, screen_h: Screen dimensions
        
    Returns:
        pygame.Rect: Safe area for new element placement
    '''
    # Simple implementation - find area below all existing elements
    if occupied_rects:
        min_safe_y = max(rect.bottom for rect in occupied_rects) + 10
    else:
        min_safe_y = 50
        
    return pygame.Rect(0, min_safe_y, screen_w, screen_h - min_safe_y)


# Future UI positioning patterns to implement:
# - Dynamic panel sizing based on content
# - Responsive layout breakpoints  
# - Component collision detection
# - Automatic overflow handling