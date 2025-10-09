'''
Modern UI Positioning System for UI_new Environment

This module implements the dynamic positioning approach documented in 
UI_DYNAMIC_POSITIONING.md for the new modular UI system.

Usage in UI_new:
    from src.ui.ui_new.positioning import calculate_element_position
    pos = calculate_element_position(element_type, game_state, screen_dims)
'''

from typing import Tuple, Dict, Any, List
import pygame

# Import the core utilities
from src.ui.positioning_utils import (
    calculate_activity_log_position,
    calculate_dynamic_element_spacing,
    get_safe_positioning_zone
)


class ModernUIPositioning:
    '''
    Modern UI positioning system for UI_new environment.
    
    Implements dynamic positioning patterns that automatically adapt
    to layout changes, screen sizes, and component variations.
    '''
    
    def __init__(self):
        self.cached_positions: Dict[str, Tuple[int, int]] = {}
        self.layout_version = 0
    
    def get_element_position(self, element_type: str, game_state: Any, 
                           w: int, h: int, **kwargs) -> Tuple[int, int]:
        '''
        Get position for a UI element using dynamic calculation.
        
        Args:
            element_type: Type of UI element ('activity_log', 'context_panel', etc.)
            game_state: Game state with component rectangles
            w, h: Screen dimensions
            **kwargs: Additional positioning parameters
            
        Returns:
            Tuple[int, int]: (x, y) coordinates for element
        '''
        if element_type == 'activity_log':
            return calculate_activity_log_position(game_state, w, h)
            
        elif element_type == 'context_panel':
            # Position context panel in bottom-right, above END TURN
            return self._calculate_context_panel_position(game_state, w, h)
            
        elif element_type == 'upgrade_panel':
            # Position upgrade panel in right column
            return self._calculate_upgrade_panel_position(game_state, w, h)
            
        else:
            # Fallback to safe positioning
            return int(w * 0.04), int(h * 0.5)
    
    def _calculate_context_panel_position(self, game_state: Any, 
                                        w: int, h: int) -> Tuple[int, int]:
        '''Calculate context panel position dynamically.'''
        # Position in bottom-right, accounting for END TURN button
        panel_width = int(w * 0.25)
        panel_height = int(h * 0.3)
        
        x = w - panel_width - int(w * 0.02)  # Right margin
        y = h - panel_height - int(h * 0.15)  # Above END TURN area
        
        return x, y
    
    def _calculate_upgrade_panel_position(self, game_state: Any,
                                        w: int, h: int) -> Tuple[int, int]:
        '''Calculate upgrade panel position dynamically.'''
        # Position in right column, below competitors panel
        competitors_bottom = int(h * 0.27)  # Competitors panel bottom approx
        
        x = int(w * 0.65)
        y = competitors_bottom + int(h * 0.02)  # Small buffer
        
        return x, y

# Singleton instance for UI_new
ui_positioning = ModernUIPositioning()


# Convenience functions for UI_new
def get_activity_log_pos(game_state: Any, w: int, h: int) -> Tuple[int, int]:
    '''Get activity log position for UI_new layouts.'''
    return ui_positioning.get_element_position('activity_log', game_state, w, h)


def get_context_panel_pos(game_state: Any, w: int, h: int) -> Tuple[int, int]:
    '''Get context panel position for UI_new layouts.'''
    return ui_positioning.get_element_position('context_panel', game_state, w, h)


def get_upgrade_panel_pos(game_state: Any, w: int, h: int) -> Tuple[int, int]:
    '''Get upgrade panel position for UI_new layouts.'''
    return ui_positioning.get_element_position('upgrade_panel', game_state, w, h)