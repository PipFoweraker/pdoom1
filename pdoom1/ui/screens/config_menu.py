"""
Configuration menu screen for P(Doom) - Display and select game configurations

This module provides the configuration selection menu for choosing between
different game configuration presets.
"""

import pygame
from visual_feedback import visual_feedback, ButtonState, draw_low_poly_button


def draw_config_menu(screen, w, h, selected_item, configs, current_config_name):
    """
    Draw the configuration selection menu.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected config item
        configs: list of available config names
        current_config_name: name of currently active config
    """
    # Clear screen with grey background
    screen.fill((64, 64, 64))
    
    # Fonts for menu - scale based on screen size
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    menu_font = pygame.font.SysFont('Consolas', int(h*0.035))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.025))
    
    # Title at top
    title_surf = title_font.render("Configuration Selection", True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.1)
    screen.blit(title_surf, (title_x, title_y))
    
    # Current config indicator
    current_surf = desc_font.render(f"Current: {current_config_name}", True, (200, 200, 200))
    current_x = w // 2 - current_surf.get_width() // 2
    current_y = title_y + title_surf.get_height() + 10
    screen.blit(current_surf, (current_x, current_y))
    
    # Menu items (configs + back button)
    all_items = configs + ["← Back to Main Menu"]
    
    button_width = int(w * 0.4)
    button_height = int(h * 0.06)
    start_y = int(h * 0.25)
    
    for i, item in enumerate(all_items):
        y = start_y + i * int(button_height + h * 0.02)
        x = w // 2 - button_width // 2
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.SELECTED
        elif item == current_config_name:
            button_state = ButtonState.ACTIVE  # Different color for current config
        else:
            button_state = ButtonState.NORMAL
        
        # Draw button
        draw_low_poly_button(screen, x, y, button_width, button_height, 
                           item, menu_font, button_state)
    
    # Instructions at bottom
    instructions = [
        "↑/↓ or mouse to navigate",
        "Enter or click to select configuration",
        "Escape to go back"
    ]
    
    for i, inst in enumerate(instructions):
        inst_surf = desc_font.render(inst, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        inst_y = int(h * 0.8) + i * int(h * 0.04)
        screen.blit(inst_surf, (inst_x, inst_y))