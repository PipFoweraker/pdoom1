"""
Fix for Action List Text Display Issues (#315, #257)

This patch addresses several text rendering problems in the action list:
1. Text overflow in small button rects
2. Inconsistent font sizing between modes  
3. Long action names not properly truncated
4. Poor readability in compact UI mode

Issues: #315, #257
"""

import pygame
from typing import Tuple, Dict, Any

def truncate_text_for_rect(text: str, font: pygame.font.Font, max_width: int, ellipsis: str = "...") -> str:
    """
    Truncate text to fit within a given width, adding ellipsis if needed.
    
    Args:
        text: Text to truncate
        font: Font to measure with
        max_width: Maximum width in pixels
        ellipsis: String to append when truncating
        
    Returns:
        str: Truncated text that fits within max_width
    """
    if font.size(text)[0] <= max_width:
        return text
    
    # Binary search for the longest text that fits
    ellipsis_width = font.size(ellipsis)[0]
    available_width = max_width - ellipsis_width
    
    if available_width <= 0:
        return ellipsis[:max_width//font.size("X")[0]] if max_width > 0 else ""
    
    left, right = 0, len(text)
    best_fit = ""
    
    while left <= right:
        mid = (left + right) // 2
        candidate = text[:mid]
        
        if font.size(candidate)[0] <= available_width:
            best_fit = candidate
            left = mid + 1
        else:
            right = mid - 1
    
    return best_fit + ellipsis if best_fit else ellipsis


def get_optimal_action_text(action: Dict[str, Any], original_idx: int, rect_width: int, font_size: int = 16) -> Tuple[str, int]:
    """
    Get optimally formatted action text that fits in the button rect.
    
    Args:
        action: Action dictionary with 'name' key
        original_idx: Original action index for shortcut key
        rect_width: Available width in pixels
        font_size: Base font size to use
        
    Returns:
        Tuple[str, int]: (formatted_text, actual_font_size)
    """
    action_name = action.get("name", f"Action {original_idx + 1}")
    
    # Try different text formats in order of preference
    font = pygame.font.SysFont('Consolas', font_size, bold=True)
    
    # Format 1: Full text with shortcut key
    if original_idx < 9:
        from src.services.keybinding_manager import keybinding_manager
        shortcut_key = keybinding_manager.get_action_display_key(f"action_{original_idx + 1}")
        full_text = f"[{shortcut_key}] {action_name}"
        
        if font.size(full_text)[0] <= rect_width - 10:  # 10px margin
            return full_text, font_size
    
    # Format 2: Just action name
    if font.size(action_name)[0] <= rect_width - 10:
        return action_name, font_size
    
    # Format 3: Truncated action name
    truncated = truncate_text_for_rect(action_name, font, rect_width - 10)
    if truncated and len(truncated) > 3:  # Don't show if too short
        return truncated, font_size
    
    # Format 4: Try smaller font
    smaller_font_size = max(10, font_size - 2)
    smaller_font = pygame.font.SysFont('Consolas', smaller_font_size, bold=True)
    
    if font.size(action_name)[0] <= rect_width - 10:
        return action_name, smaller_font_size
    
    # Format 5: Truncated with smaller font  
    truncated_small = truncate_text_for_rect(action_name, smaller_font, rect_width - 10)
    return truncated_small, smaller_font_size


def get_optimal_compact_text(action: Dict[str, Any], action_index: int, rect_width: int, rect_height: int) -> Dict[str, Any]:
    """
    Get optimal text rendering parameters for compact UI mode.
    
    Args:
        action: Action dictionary
        action_index: Action index for shortcut
        rect_width: Button width
        rect_height: Button height
        
    Returns:
        dict: Parameters for text rendering (icon_size, key_size, text_truncation)
    """
    # Scale icon and key sizes based on button size
    min_dimension = min(rect_width, rect_height)
    
    return {
        'icon_size': max(12, int(min_dimension * 0.35)),  # Slightly smaller for better text fit
        'key_size': max(8, int(min_dimension * 0.18)),   # Smaller shortcut key text
        'icon_font': 'Consolas',
        'key_font': 'Consolas',
        'icon_bold': True,
        'key_bold': True
    }