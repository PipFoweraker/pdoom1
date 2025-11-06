'''
Visual Feedback Utilities for P(Doom) UI

Provides standardized visual feedback for clickable elements including
button depression, gradient changes, hover effects, and accessibility support.

Inspired by low-bit, low-poly UI design with modern accessibility features.
'''

import pygame
from typing import Tuple, Optional, Dict
from enum import Enum


class ButtonState(Enum):
    '''States for interactive buttons'''
    NORMAL = 'normal'
    HOVER = 'hover'
    PRESSED = 'pressed'
    DISABLED = 'disabled'
    FOCUSED = 'focused'  # For keyboard navigation


class FeedbackStyle(Enum):
    '''Visual feedback styles for different UI elements'''
    BUTTON = 'button'
    ICON = 'icon'
    PANEL = 'panel'
    MENU_ITEM = 'menu_item'
    DIALOG = 'dialog'


class VisualFeedback:
    '''
    Centralized visual feedback system for UI elements.
    
    Provides consistent styling, animations, and accessibility features
    across all interactive elements in the game.
    '''
    
    def __init__(self):
        # Color schemes for different states
        self.color_schemes = {
            ButtonState.NORMAL: {
                'bg': (60, 80, 120),
                'border': (130, 130, 220),
                'text': (220, 220, 255),
                'shadow': (20, 20, 40)
            },
            ButtonState.HOVER: {
                'bg': (80, 100, 150),
                'border': (150, 150, 255),
                'text': (255, 255, 255),
                'shadow': (30, 30, 50),
                'glow': (200, 220, 255, 30)
            },
            ButtonState.PRESSED: {
                'bg': (40, 60, 100),
                'border': (100, 100, 180),
                'text': (200, 200, 240),
                'shadow': (10, 10, 20)
            },
            ButtonState.DISABLED: {
                'bg': (40, 40, 60),
                'border': (80, 80, 100),
                'text': (120, 120, 140),
                'shadow': (15, 15, 25)
            },
            ButtonState.FOCUSED: {
                'bg': (70, 90, 130),
                'border': (255, 255, 100),  # Yellow focus ring
                'text': (255, 255, 255),
                'shadow': (25, 25, 45),
                'focus_ring': (255, 255, 100, 80)
            }
        }
        
        # Animation parameters
        self.press_depth = 3
        self.hover_lift = 2
        self.border_width = 2
        self.focus_ring_width = 3
        self.corner_radius = 8
        
        # Font scaling for accessibility
        self.base_font_size = 16
        self.font_scale_factor = 1.0
        
    def draw_button(self, surface: pygame.Surface, rect: pygame.Rect, 
                   text: str, state: ButtonState, 
                   style: FeedbackStyle = FeedbackStyle.BUTTON,
                   custom_colors: Optional[Dict] = None) -> pygame.Rect:
        '''
        Draw a button with standardized visual feedback.
        
        Args:
            surface: pygame surface to draw on
            rect: button rectangle
            text: button text
            state: current button state
            style: visual style to apply
            custom_colors: optional color overrides
            
        Returns:
            pygame.Rect: actual drawn rectangle (may be offset for press effect)
        '''
        colors = custom_colors or self.color_schemes[state]
        
        # Calculate display rectangle with state effects
        display_rect = rect.copy()
        
        if state == ButtonState.PRESSED:
            # Button depression effect
            display_rect.x += self.press_depth
            display_rect.y += self.press_depth
        elif state == ButtonState.HOVER:
            # Subtle lift effect
            display_rect.y -= self.hover_lift
        
        # Draw shadow first (if not pressed)
        if state != ButtonState.PRESSED:
            shadow_rect = display_rect.copy()
            shadow_rect.x += self.press_depth
            shadow_rect.y += self.press_depth
            pygame.draw.rect(surface, colors['shadow'], shadow_rect, 
                           border_radius=self.corner_radius)
        
        # Draw glow effect for hover/focus
        if state in [ButtonState.HOVER, ButtonState.FOCUSED] and 'glow' in colors:
            glow_rect = display_rect.inflate(6, 6)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, colors['glow'], glow_surface.get_rect(), 
                           border_radius=self.corner_radius + 3)
            surface.blit(glow_surface, glow_rect.topleft)
        
        # Draw main button background
        pygame.draw.rect(surface, colors['bg'], display_rect, 
                        border_radius=self.corner_radius)
        
        # Draw border
        border_width = self.border_width
        if state == ButtonState.FOCUSED:
            border_width = self.focus_ring_width
            
        pygame.draw.rect(surface, colors['border'], display_rect, 
                        width=border_width, border_radius=self.corner_radius)
        
        # Draw focus ring for accessibility
        if state == ButtonState.FOCUSED and 'focus_ring' in colors:
            focus_rect = display_rect.inflate(8, 8)
            focus_surface = pygame.Surface((focus_rect.width, focus_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(focus_surface, colors['focus_ring'], focus_surface.get_rect(),
                           width=2, border_radius=self.corner_radius + 4)
            surface.blit(focus_surface, focus_rect.topleft)
        
        # Draw text with proper scaling and overflow handling
        if text:
            font_size = int(self.base_font_size * self.font_scale_factor)
            font = pygame.font.SysFont('Consolas', font_size, bold=(style == FeedbackStyle.BUTTON))
            
            # Check if text fits, if not try to make it fit
            available_width = display_rect.width - 10  # 5px margin on each side
            text_width = font.size(text)[0]
            
            final_text = text
            final_font = font
            
            if text_width > available_width:
                # Try smaller font first
                smaller_font_size = max(10, font_size - 2)
                smaller_font = pygame.font.SysFont('Consolas', smaller_font_size, bold=(style == FeedbackStyle.BUTTON))
                
                if smaller_font.size(text)[0] <= available_width:
                    final_text = text
                    final_font = smaller_font
                else:
                    # Truncate text with ellipsis
                    ellipsis = '...'
                    ellipsis_width = font.size(ellipsis)[0]
                    target_width = available_width - ellipsis_width
                    
                    if target_width > 0:
                        # Binary search for longest fitting text
                        left, right = 0, len(text)
                        best_fit = ''
                        
                        while left <= right:
                            mid = (left + right) // 2
                            candidate = text[:mid]
                            
                            if font.size(candidate)[0] <= target_width:
                                best_fit = candidate
                                left = mid + 1
                            else:
                                right = mid - 1
                        
                        final_text = best_fit + ellipsis if best_fit else ellipsis
                    else:
                        final_text = ellipsis[:max(1, available_width // font.size('X')[0])]
            
            text_surface = final_font.render(final_text, True, colors['text'])
            
            # Center text in button
            text_rect = text_surface.get_rect(center=display_rect.center)
            surface.blit(text_surface, text_rect)
        
        return display_rect
    
    def draw_icon_button(self, surface: pygame.Surface, rect: pygame.Rect,
                        icon_char: str, state: ButtonState,
                        tooltip: Optional[str] = None) -> pygame.Rect:
        '''
        Draw an icon button with visual feedback.
        
        Args:
            surface: pygame surface to draw on
            rect: button rectangle
            icon_char: character to use as icon
            state: current button state
            tooltip: optional tooltip text
            
        Returns:
            pygame.Rect: actual drawn rectangle
        '''
        colors = self.color_schemes[state]
        display_rect = self.draw_button(surface, rect, '', state, FeedbackStyle.ICON)
        
        # Draw icon character
        icon_font_size = int(min(rect.width, rect.height) * 0.5)
        icon_font = pygame.font.SysFont('Consolas', icon_font_size, bold=True)
        icon_surface = icon_font.render(icon_char, True, colors['text'])
        
        icon_rect = icon_surface.get_rect(center=display_rect.center)
        surface.blit(icon_surface, icon_rect)
        
        return display_rect
    
    def draw_panel(self, surface: pygame.Surface, rect: pygame.Rect,
                  title: Optional[str] = None, 
                  state: ButtonState = ButtonState.NORMAL,
                  minimizable: bool = False) -> Dict[str, pygame.Rect]:
        '''
        Draw a panel with optional title bar and controls.
        
        Args:
            surface: pygame surface to draw on
            rect: panel rectangle
            title: optional title text
            state: panel state (for visual feedback)
            minimizable: whether to show minimize button
            
        Returns:
            Dict[str, pygame.Rect]: rectangles for interactive elements
        '''
        colors = self.color_schemes[state]
        
        # Draw panel background
        bg_color = (40, 50, 70) if state == ButtonState.NORMAL else colors['bg']
        pygame.draw.rect(surface, bg_color, rect, border_radius=self.corner_radius)
        pygame.draw.rect(surface, colors['border'], rect, 
                        width=self.border_width, border_radius=self.corner_radius)
        
        interactive_rects = {}
        
        # Draw title bar if title provided
        if title:
            title_height = 30
            title_rect = pygame.Rect(rect.x, rect.y, rect.width, title_height)
            
            # Title bar background
            title_bg = (60, 70, 90) if state == ButtonState.NORMAL else colors['bg']
            pygame.draw.rect(surface, title_bg, title_rect, 
                           border_radius=0)  # Only round top corners
            pygame.draw.rect(surface, colors['border'], title_rect, 
                           width=self.border_width)
            
            # Title text
            title_font = pygame.font.SysFont('Consolas', int(self.base_font_size * 1.1), bold=True)
            title_surface = title_font.render(title, True, colors['text'])
            title_text_rect = title_surface.get_rect(centery=title_rect.centery, x=title_rect.x + 10)
            surface.blit(title_surface, title_text_rect)
            
            # Minimize button if requested
            if minimizable:
                min_button_size = title_height - 8
                min_button_rect = pygame.Rect(
                    title_rect.right - min_button_size - 4,
                    title_rect.y + 4,
                    min_button_size,
                    min_button_size
                )
                
                # Draw minimize button
                self.draw_icon_button(surface, min_button_rect, '?', ButtonState.NORMAL)
                interactive_rects['minimize'] = min_button_rect
        
        return interactive_rects
    
    def draw_menu_item(self, surface: pygame.Surface, rect: pygame.Rect,
                      text: str, state: ButtonState,
                      icon: Optional[str] = None,
                      shortcut: Optional[str] = None) -> pygame.Rect:
        '''
        Draw a menu item with keyboard shortcut support.
        
        Args:
            surface: pygame surface to draw on
            rect: menu item rectangle
            text: menu item text
            state: current state
            icon: optional icon character
            shortcut: optional keyboard shortcut text
            
        Returns:
            pygame.Rect: actual drawn rectangle
        '''
        colors = self.color_schemes[state]
        
        # Menu items have subtle styling
        if state == ButtonState.HOVER:
            pygame.draw.rect(surface, colors['bg'], rect, border_radius=4)
        elif state == ButtonState.FOCUSED:
            pygame.draw.rect(surface, colors['focus_ring'], rect, width=2, border_radius=4)
        
        # Draw icon if provided
        text_x = rect.x + 10
        if icon:
            icon_font = pygame.font.SysFont('Consolas', self.base_font_size, bold=True)
            icon_surface = icon_font.render(icon, True, colors['text'])
            icon_rect = icon_surface.get_rect(centery=rect.centery, x=text_x)
            surface.blit(icon_surface, icon_rect)
            text_x = icon_rect.right + 10
        
        # Draw main text
        font = pygame.font.SysFont('Consolas', self.base_font_size)
        text_surface = font.render(text, True, colors['text'])
        text_rect = text_surface.get_rect(centery=rect.centery, x=text_x)
        surface.blit(text_surface, text_rect)
        
        # Draw shortcut text (right-aligned)
        if shortcut:
            shortcut_font = pygame.font.SysFont('Consolas', self.base_font_size - 2)
            shortcut_surface = shortcut_font.render(shortcut, True, (150, 150, 180))
            shortcut_rect = shortcut_surface.get_rect(centery=rect.centery, right=rect.right - 10)
            surface.blit(shortcut_surface, shortcut_rect)
        
        return rect
    
    def highlight_error(self, surface: pygame.Surface, rect: pygame.Rect,
                       pulse_phase: float = 0.0) -> None:
        '''
        Draw error highlighting with pulsing red border.
        
        Args:
            surface: pygame surface to draw on
            rect: rectangle to highlight
            pulse_phase: animation phase (0.0 to 1.0)
        '''
        import math
        
        # Pulsing red highlight
        intensity = int(128 + 127 * math.sin(pulse_phase * 2 * math.pi))
        error_color = (255, intensity // 2, intensity // 2)
        
        # Draw pulsing border
        pygame.draw.rect(surface, error_color, rect, width=3, border_radius=self.corner_radius)
        
        # Optional: draw error glow
        if pulse_phase > 0.5:
            glow_rect = rect.inflate(6, 6)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_alpha = int(60 * (pulse_phase - 0.5) * 2)
            pygame.draw.rect(glow_surface, (*error_color, glow_alpha), glow_surface.get_rect(),
                           border_radius=self.corner_radius + 3)
            surface.blit(glow_surface, glow_rect.topleft)
    
    def set_font_scale(self, scale: float) -> None:
        '''Set font scaling factor for accessibility.'''
        self.font_scale_factor = max(0.5, min(2.0, scale))  # Clamp between 0.5x and 2.0x
    
    def get_accessible_color(self, base_color: Tuple[int, int, int], 
                            high_contrast: bool = False) -> Tuple[int, int, int]:
        '''
        Get an accessible version of a color with proper contrast.
        
        Args:
            base_color: original color
            high_contrast: whether to use high contrast mode
            
        Returns:
            Tuple[int, int, int]: accessible color
        '''
        if high_contrast:
            # High contrast mode: use white or black based on luminance
            r, g, b = base_color
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return (255, 255, 255) if luminance < 0.5 else (0, 0, 0)
        else:
            # Normal mode: ensure minimum contrast
            return base_color
    
    def draw_tooltip(self, surface: pygame.Surface, text: str, 
                    mouse_pos: Tuple[int, int], screen_w: int, screen_h: int) -> None:
        '''
        Draw an accessible tooltip near the mouse cursor.
        
        Args:
            surface: pygame surface to draw on
            text: tooltip text
            mouse_pos: current mouse position
            screen_w, screen_h: screen dimensions
        '''
        if not text:
            return
            
        # Calculate tooltip size
        font = pygame.font.SysFont('Consolas', int(self.base_font_size * 0.9))
        text_surface = font.render(text, True, (255, 255, 255))
        padding = 8
        tooltip_width = text_surface.get_width() + padding * 2
        tooltip_height = text_surface.get_height() + padding * 2
        
        # Position tooltip to avoid screen edges
        x, y = mouse_pos
        x += 15  # Offset from cursor
        y -= tooltip_height + 10
        
        # Keep tooltip on screen
        if x + tooltip_width > screen_w:
            x = screen_w - tooltip_width - 5
        if y < 0:
            y = mouse_pos[1] + 15
        if x < 0:
            x = 5
            
        tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        
        # Draw tooltip background
        pygame.draw.rect(surface, (40, 40, 60), tooltip_rect, border_radius=6)
        pygame.draw.rect(surface, (150, 150, 200), tooltip_rect, width=1, border_radius=6)
        
        # Draw text
        text_rect = text_surface.get_rect(center=tooltip_rect.center)
        surface.blit(text_surface, text_rect)


# Global instance for easy access
visual_feedback = VisualFeedback()


# Utility functions for common UI patterns

def draw_low_poly_button(surface: pygame.Surface, rect: pygame.Rect, 
                        text: str, state: ButtonState) -> pygame.Rect:
    '''Draw a button with low-poly/retro styling.'''
    return visual_feedback.draw_button(surface, rect, text, state)


def draw_gradient_background(surface: pygame.Surface, rect: pygame.Rect,
                           color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                           vertical: bool = True) -> None:
    '''Draw a subtle gradient background for panels.'''
    if vertical:
        for i in range(rect.height):
            ratio = i / rect.height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            
            line_rect = pygame.Rect(rect.x, rect.y + i, rect.width, 1)
            pygame.draw.rect(surface, (r, g, b), line_rect)
    else:
        for i in range(rect.width):
            ratio = i / rect.width
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            
            line_rect = pygame.Rect(rect.x + i, rect.y, 1, rect.height)
            pygame.draw.rect(surface, (r, g, b), line_rect)


def create_icon_from_text(text: str, size: int, color: Tuple[int, int, int]) -> pygame.Surface:
    '''Create a simple icon surface from text for low-poly styling.'''
    font = pygame.font.SysFont('Consolas', size, bold=True)
    return font.render(text, True, color)