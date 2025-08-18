"""
Button components for P(Doom) UI.

Provides reusable button components with consistent styling and state management.
Integrates with the existing visual_feedback system while adding modular components.
"""

import pygame
from enum import Enum
from typing import Tuple, Optional, Dict, Any
from .colours import (
    BUTTON_NORMAL_BG, BUTTON_HOVER_BG, BUTTON_PRESSED_BG, BUTTON_DISABLED_BG,
    BUTTON_NORMAL_BORDER, BUTTON_HOVER_BORDER, BUTTON_PRESSED_BORDER, BUTTON_DISABLED_BORDER,
    BUTTON_TEXT_COLOUR, BUTTON_DISABLED_TEXT_COLOUR,
    END_TURN_NORMAL_BG, END_TURN_HOVER_BG, END_TURN_BORDER, END_TURN_TEXT_COLOUR,
    GLOW_COLOUR
)
from .typography import font_manager


class ButtonState(Enum):
    """Button visual states."""
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"
    FOCUSED = "focused"


class ButtonStyle(Enum):
    """Button style variants."""
    DEFAULT = "default"
    END_TURN = "end_turn"
    ACTION = "action"
    UPGRADE = "upgrade"
    ICON = "icon"


def get_button_colours(state: ButtonState, style: ButtonStyle = ButtonStyle.DEFAULT) -> Dict[str, Tuple[int, int, int]]:
    """Get the colour scheme for a button based on its state and style."""
    
    if style == ButtonStyle.END_TURN:
        return {
            ButtonState.NORMAL: {
                'bg': END_TURN_NORMAL_BG,
                'border': END_TURN_BORDER,
                'text': END_TURN_TEXT_COLOUR
            },
            ButtonState.HOVER: {
                'bg': END_TURN_HOVER_BG,
                'border': END_TURN_BORDER,
                'text': END_TURN_TEXT_COLOUR,
                'glow': GLOW_COLOUR
            },
            ButtonState.PRESSED: {
                'bg': BUTTON_PRESSED_BG,
                'border': BUTTON_PRESSED_BORDER,
                'text': END_TURN_TEXT_COLOUR
            },
            ButtonState.DISABLED: {
                'bg': BUTTON_DISABLED_BG,
                'border': BUTTON_DISABLED_BORDER,
                'text': BUTTON_DISABLED_TEXT_COLOUR
            }
        }.get(state, {
            'bg': END_TURN_NORMAL_BG,
            'border': END_TURN_BORDER,
            'text': END_TURN_TEXT_COLOUR
        })
    
    # Default button colours
    colour_map = {
        ButtonState.NORMAL: {
            'bg': BUTTON_NORMAL_BG,
            'border': BUTTON_NORMAL_BORDER,
            'text': BUTTON_TEXT_COLOUR
        },
        ButtonState.HOVER: {
            'bg': BUTTON_HOVER_BG,
            'border': BUTTON_HOVER_BORDER,
            'text': BUTTON_TEXT_COLOUR
        },
        ButtonState.PRESSED: {
            'bg': BUTTON_PRESSED_BG,
            'border': BUTTON_PRESSED_BORDER,
            'text': BUTTON_TEXT_COLOUR
        },
        ButtonState.DISABLED: {
            'bg': BUTTON_DISABLED_BG,
            'border': BUTTON_DISABLED_BORDER,
            'text': BUTTON_DISABLED_TEXT_COLOUR
        },
        ButtonState.FOCUSED: {
            'bg': BUTTON_HOVER_BG,
            'border': BUTTON_HOVER_BORDER,
            'text': BUTTON_TEXT_COLOUR
        }
    }
    
    return colour_map.get(state, colour_map[ButtonState.NORMAL])


def draw_button(screen: pygame.Surface,
                rect: pygame.Rect,
                text: str,
                state: ButtonState = ButtonState.NORMAL,
                style: ButtonStyle = ButtonStyle.DEFAULT,
                custom_colours: Optional[Dict[str, Any]] = None) -> None:
    """
    Draw a button with the specified state and style.
    
    Args:
        screen: The surface to draw on
        rect: Button rectangle
        text: Button text
        state: Button state
        style: Button style variant
        custom_colours: Optional custom colour overrides
    """
    colours = get_button_colours(state, style)
    if custom_colours:
        colours.update(custom_colours)
    
    # Calculate offset for pressed state
    offset = 3 if state == ButtonState.PRESSED else 0
    draw_rect = pygame.Rect(rect.x, rect.y + offset, rect.width, rect.height - offset)
    
    # Draw button background
    pygame.draw.rect(screen, colours['bg'], draw_rect)
    pygame.draw.rect(screen, colours['border'], draw_rect, 2)
    
    # Draw glow effect for hover state if specified
    if 'glow' in colours:
        glow_rect = pygame.Rect(draw_rect.x - 2, draw_rect.y - 2, 
                               draw_rect.width + 4, draw_rect.height + 4)
        glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, colours['glow'], 
                        pygame.Rect(0, 0, glow_rect.width, glow_rect.height))
        screen.blit(glow_surface, glow_rect.topleft)
    
    # Draw button text
    font = font_manager.get_normal_font(screen.get_height())
    text_surface = font.render(text, True, colours['text'])
    text_rect = text_surface.get_rect(center=draw_rect.center)
    screen.blit(text_surface, text_rect)


def draw_icon_button(screen: pygame.Surface,
                    rect: pygame.Rect,
                    icon_text: str,
                    state: ButtonState = ButtonState.NORMAL) -> None:
    """
    Draw a small icon button (typically used for purchased upgrades).
    
    Args:
        screen: The surface to draw on
        rect: Button rectangle
        icon_text: Single character or short text for icon
        state: Button state
    """
    colours = get_button_colours(state)
    
    # Draw background circle or rounded rect
    center = rect.center
    radius = min(rect.width, rect.height) // 2 - 2
    pygame.draw.circle(screen, colours['bg'], center, radius)
    pygame.draw.circle(screen, colours['border'], center, radius, 2)
    
    # Draw icon text
    font = font_manager.get_small_font(screen.get_height())
    text_surface = font.render(icon_text, True, colours['text'])
    text_rect = text_surface.get_rect(center=center)
    screen.blit(text_surface, text_rect)


def draw_toggle_button(screen: pygame.Surface,
                      rect: pygame.Rect,
                      text: str,
                      is_toggled: bool,
                      state: ButtonState = ButtonState.NORMAL) -> None:
    """
    Draw a toggle button that can be in on/off state.
    
    Args:
        screen: The surface to draw on
        rect: Button rectangle
        text: Button text
        is_toggled: Whether the button is in toggled/active state
        state: Button interaction state
    """
    # Modify colours based on toggle state
    colours = get_button_colours(state)
    if is_toggled:
        # Make background slightly brighter when toggled
        bg_colour = tuple(min(255, c + 30) for c in colours['bg'])
        colours['bg'] = bg_colour
    
    draw_button(screen, rect, text, state, ButtonStyle.DEFAULT, colours)
    
    # Draw toggle indicator (small dot in corner)
    if is_toggled:
        indicator_pos = (rect.right - 8, rect.top + 8)
        pygame.draw.circle(screen, (100, 255, 100), indicator_pos, 3)


def is_button_hovered(mouse_pos: Tuple[int, int], button_rect: pygame.Rect) -> bool:
    """Check if the mouse is hovering over a button."""
    return button_rect.collidepoint(mouse_pos)


def is_button_clicked(mouse_pos: Tuple[int, int], button_rect: pygame.Rect,
                     mouse_button: int = 1) -> bool:
    """Check if a button was clicked (mouse button 1 = left click)."""
    return button_rect.collidepoint(mouse_pos)