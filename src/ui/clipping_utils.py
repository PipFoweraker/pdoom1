"""
UI Rectangle Clipping Utilities - Elegant Modular Solution

This module provides clean, reusable functions for handling UI element clipping
against context windows while maintaining accurate click detection.

Created: 2025-09-29 - Demo Hotfix Session (Elegant Modularization)
"""

from typing import List, Tuple, Union, Optional
import pygame


def clip_rectangles_for_context_window(
    rectangles: List[Union[pygame.Rect, Tuple[int, int, int, int]]], 
    context_top: int,
    buffer: int = 2
) -> List[Optional[pygame.Rect]]:
    """
    Elegantly clip UI rectangles to avoid overlap with context window.
    
    This ensures that stored rectangles match what's visually rendered,
    fixing click detection issues in a clean, modular way.
    
    Args:
        rectangles: List of rectangles to clip (pygame.Rect or tuples)
        context_top: Y-coordinate where context window starts
        buffer: Safety buffer in pixels
        
    Returns:
        List of clipped pygame.Rect objects, or None for completely hidden elements
    """
    clipped_rects = []
    
    for rect in rectangles:
        # Convert tuple to pygame.Rect if needed
        if isinstance(rect, tuple):
            rect = pygame.Rect(rect)
        elif rect is None:
            clipped_rects.append(None)
            continue
            
        # Clone the rectangle to avoid modifying original
        clipped_rect = rect.copy()
        
        # Clip height if it would overlap context window
        if clipped_rect.bottom > context_top:
            clipped_rect.height = max(0, context_top - clipped_rect.top - buffer)
            
        # Mark as None if completely clipped away
        if clipped_rect.height <= 0:
            clipped_rects.append(None)
        else:
            clipped_rects.append(clipped_rect)
            
    return clipped_rects


def get_safe_context_top(game_state, screen_height: int) -> int:
    """
    Elegantly determine context window top position with fallback.
    
    Args:
        game_state: Game state object
        screen_height: Screen height for fallback calculation
        
    Returns:
        Y-coordinate where context window starts
    """
    try:
        return game_state._get_context_window_top(screen_height)
    except (AttributeError, Exception):
        return int(screen_height * 0.90) - 5  # Elegant fallback


def apply_clipping_to_ui_elements(
    rectangles: List[Union[pygame.Rect, Tuple[int, int, int, int]]],
    game_state,
    screen_height: int
) -> List[Optional[pygame.Rect]]:
    """
    Complete clipping workflow for UI elements.
    
    Combines context window detection and rectangle clipping in one elegant call.
    
    Args:
        rectangles: UI element rectangles to clip
        game_state: Game state for context window detection
        screen_height: Screen height for calculations
        
    Returns:
        List of properly clipped rectangles matching visual rendering
    """
    context_top = get_safe_context_top(game_state, screen_height)
    return clip_rectangles_for_context_window(rectangles, context_top)