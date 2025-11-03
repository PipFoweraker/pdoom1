'''
UI layout utilities for P(Doom).

Consolidates common UI layout calculations and patterns that were
previously duplicated throughout main.py and ui.py.

Part of internal polish phase to reduce code duplication.
'''

import pygame
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class ButtonLayout:
    '''Standard button layout configuration.'''
    x: int
    y: int
    width: int
    height: int
    
    @property 
    def rect(self) -> pygame.Rect:
        '''Get pygame.Rect for this button layout.'''
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    @property
    def center_x(self) -> int:
        '''Get center X coordinate.'''
        return self.x + self.width // 2
    
    @property
    def center_y(self) -> int:
        '''Get center Y coordinate.'''
        return self.y + self.height // 2


@dataclass
class MenuLayoutConfig:
    '''Configuration for standard menu layouts.'''
    button_width_ratio: float = 0.4      # Button width as ratio of screen width
    button_height_ratio: float = 0.08    # Button height as ratio of screen height
    start_y_ratio: float = 0.35          # Starting Y position as ratio of screen height
    spacing_ratio: float = 0.1           # Vertical spacing as ratio of screen height
    centered: bool = True                # Whether to center buttons horizontally


class UILayoutManager:
    '''Manages common UI layout calculations and patterns.'''
    
    # Standard menu layouts used throughout the application
    STANDARD_MENU_LAYOUTS = {
        'main_menu': MenuLayoutConfig(0.4, 0.08, 0.35, 0.1),
        'submenu': MenuLayoutConfig(0.5, 0.08, 0.3, 0.1),
        'settings': MenuLayoutConfig(0.55, 0.07, 0.32, 0.085),
        'compact': MenuLayoutConfig(0.3, 0.06, 0.35, 0.08),
        'large': MenuLayoutConfig(0.6, 0.1, 0.25, 0.12)
    }
    
    @classmethod
    def calculate_menu_buttons(cls, w: int, h: int, num_buttons: int, 
                              layout_name: str = 'main_menu') -> List[ButtonLayout]:
        '''
        Calculate button layouts for a standard menu.
        
        Args:
            w, h: Screen dimensions
            num_buttons: Number of buttons to layout
            layout_name: Which layout configuration to use
            
        Returns:
            List of ButtonLayout objects for each button
        '''
        if layout_name not in cls.STANDARD_MENU_LAYOUTS:
            layout_name = 'main_menu'  # Fallback to default
            
        config = cls.STANDARD_MENU_LAYOUTS[layout_name]
        
        button_width = int(w * config.button_width_ratio)
        button_height = int(h * config.button_height_ratio)
        start_y = int(h * config.start_y_ratio)
        spacing = int(h * config.spacing_ratio)
        
        buttons = []
        for i in range(num_buttons):
            if config.centered:
                x = w // 2 - button_width // 2
            else:
                x = 0  # Left-aligned
                
            y = start_y + i * spacing
            buttons.append(ButtonLayout(x, y, button_width, button_height))
            
        return buttons
    
    @classmethod
    def calculate_button_at_position(cls, w: int, h: int, width_ratio: float, 
                                   height_ratio: float, x_ratio: float, 
                                   y_ratio: float) -> ButtonLayout:
        '''
        Calculate a single button layout at a specific position.
        
        Args:
            w, h: Screen dimensions
            width_ratio: Button width as ratio of screen width
            height_ratio: Button height as ratio of screen height  
            x_ratio: X position as ratio of screen width
            y_ratio: Y position as ratio of screen height
            
        Returns:
            ButtonLayout for the button
        '''
        return ButtonLayout(
            x=int(w * x_ratio),
            y=int(h * y_ratio),
            width=int(w * width_ratio),
            height=int(h * height_ratio)
        )
    
    @classmethod
    def calculate_centered_button(cls, w: int, h: int, width_ratio: float,
                                height_ratio: float, y_ratio: float) -> ButtonLayout:
        '''
        Calculate a centered button layout.
        
        Args:
            w, h: Screen dimensions
            width_ratio: Button width as ratio of screen width
            height_ratio: Button height as ratio of screen height
            y_ratio: Y position as ratio of screen height
            
        Returns:
            ButtonLayout for the centered button
        '''
        button_width = int(w * width_ratio)
        button_height = int(h * height_ratio)
        x = w // 2 - button_width // 2
        y = int(h * y_ratio)
        
        return ButtonLayout(x, y, button_width, button_height)
    
    @classmethod
    def find_clicked_button(cls, mouse_pos: Tuple[int, int], 
                          buttons: List[ButtonLayout]) -> int:
        '''
        Find which button was clicked based on mouse position.
        
        Args:
            mouse_pos: (x, y) tuple of mouse coordinates
            buttons: List of ButtonLayout objects to check
            
        Returns:
            Index of clicked button, or -1 if no button was clicked
        '''
        mx, my = mouse_pos
        
        for i, button in enumerate(buttons):
            if button.rect.collidepoint(mx, my):
                return i
                
        return -1
    
    @classmethod
    def get_safe_margin(cls, w: int, h: int, margin_ratio: float = 0.02) -> int:
        '''
        Calculate a safe margin based on screen size.
        
        Args:
            w, h: Screen dimensions
            margin_ratio: Margin as ratio of smaller screen dimension
            
        Returns:
            Margin size in pixels
        '''
        return int(min(w, h) * margin_ratio)


class ResponsiveLayout:
    '''Handles responsive layout calculations for different screen sizes.'''
    
    @staticmethod
    def scale_font_size(base_size: int, screen_h: int, reference_height: int = 800) -> int:
        '''
        Scale font size based on screen height.
        
        Args:
            base_size: Base font size for reference height
            screen_h: Current screen height
            reference_height: Reference screen height (default 800)
            
        Returns:
            Scaled font size
        '''
        scale_factor = screen_h / reference_height
        return max(12, int(base_size * scale_factor))  # Minimum readable size
    
    @staticmethod
    def get_responsive_spacing(screen_h: int, spacing_type: str = 'normal') -> int:
        '''
        Get responsive spacing based on screen height.
        
        Args:
            screen_h: Screen height
            spacing_type: 'tight', 'normal', 'loose'
            
        Returns:
            Spacing in pixels
        '''
        base_ratios = {
            'tight': 0.01,
            'normal': 0.02, 
            'loose': 0.04
        }
        
        ratio = base_ratios.get(spacing_type, 0.02)
        return int(screen_h * ratio)


# Convenience functions for common layout patterns
def create_standard_menu_layout(w: int, h: int, menu_items: List[str], 
                              layout_type: str = 'main_menu') -> List[ButtonLayout]:
    '''Create a standard menu layout for the given items.'''
    return UILayoutManager.calculate_menu_buttons(w, h, len(menu_items), layout_type)


def create_back_button_layout(w: int, h: int) -> ButtonLayout:
    '''Create layout for a standard back button in top-left corner.'''
    margin = UILayoutManager.get_safe_margin(w, h)
    return ButtonLayout(margin, margin, int(w * 0.1), int(h * 0.05))


def create_sound_button_layout(w: int, h: int) -> ButtonLayout:
    '''Create layout for a sound toggle button in bottom-right corner.'''
    button_size = int(min(w, h) * 0.06)
    margin = 20
    return ButtonLayout(
        w - button_size - margin,
        h - button_size - margin,
        button_size,
        button_size
    )


# Export the main classes and convenience functions
__all__ = [
    'ButtonLayout', 'MenuLayoutConfig', 'UILayoutManager', 'ResponsiveLayout',
    'create_standard_menu_layout', 'create_back_button_layout', 
    'create_sound_button_layout'
]
