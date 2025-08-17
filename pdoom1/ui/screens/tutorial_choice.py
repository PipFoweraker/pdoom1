"""
Tutorial choice screen for P(Doom) - Select tutorial mode

This module provides the tutorial choice screen for players to decide whether
to enable tutorial guidance for their game session.
"""

import pygame
from visual_feedback import visual_feedback, ButtonState, draw_low_poly_button


def draw_tutorial_choice(screen, w, h, selected_item):
    """
    Draw the tutorial choice screen.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected item (0=Yes, 1=No)
    """
    # Clear background
    screen.fill((50, 50, 50))
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    menu_font = pygame.font.SysFont('Consolas', int(h*0.03))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.025))
    
    # Title
    title_surf = title_font.render("Tutorial Mode?", True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.15)
    screen.blit(title_surf, (title_x, title_y))
    
    # Description
    desc_text = "Would you like to play with tutorial guidance?"
    desc_surf = desc_font.render(desc_text, True, (200, 200, 200))
    desc_x = w // 2 - desc_surf.get_width() // 2
    desc_y = title_y + title_surf.get_height() + 20
    screen.blit(desc_surf, (desc_x, desc_y))
    
    # Tutorial options
    tutorial_items = ["Yes - Enable Tutorial", "No - Regular Mode"]
    
    # Button layout
    button_width = int(w * 0.4)
    button_height = int(h * 0.08)
    start_y = int(h * 0.4)
    spacing = int(h * 0.12)
    center_x = w // 2
    
    for i, item in enumerate(tutorial_items):
        # Calculate button position
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.FOCUSED
        else:
            button_state = ButtonState.NORMAL
        
        # Draw button with text
        draw_low_poly_button(screen, button_rect, item, button_state)
    
    # Instructions
    inst_font = pygame.font.SysFont('Consolas', int(h*0.025))
    instructions = [
        "Use arrow keys or mouse to navigate, Enter/Space to confirm",
        "Tutorial mode provides helpful guidance for new players"
    ]
    
    inst_y = int(h * 0.8)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 5