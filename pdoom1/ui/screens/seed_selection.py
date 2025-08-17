"""
Seed Selection Screen for P(Doom)

This module contains the seed selection screen implementation migrated from ui.py.
Provides the seed selection interface with weekly and custom seed options.
"""

import pygame
from visual_feedback import ButtonState, draw_low_poly_button


def draw_seed_selection(screen, w, h, selected_item, seed_input="", sound_manager=None):
    """
    Draw the seed selection screen.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected item (0=Weekly, 1=Custom)
        seed_input: current custom seed input text
        sound_manager: optional SoundManager instance for sound toggle button
    """
    # Import helper function from ui.py as needed
    from ui import draw_mute_button_standalone
    
    # Clear background
    screen.fill((50, 50, 50))
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    menu_font = pygame.font.SysFont('Consolas', int(h*0.03))
    
    # Title
    title_surf = title_font.render("Select Seed", True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.15)
    screen.blit(title_surf, (title_x, title_y))
    
    # Seed options
    seed_items = ["Use Weekly Seed", "Use Custom Seed"]
    
    # Button layout
    button_width = int(w * 0.4)
    button_height = int(h * 0.08)
    start_y = int(h * 0.35)
    spacing = int(h * 0.12)
    center_x = w // 2
    
    for i, item in enumerate(seed_items):
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
    
    # If custom seed is selected, show input field
    if selected_item == 1:
        input_y = start_y + 2 * spacing
        input_width = int(w * 0.5)
        input_height = int(h * 0.06)
        input_x = center_x - input_width // 2
        input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
        
        # Draw input background
        pygame.draw.rect(screen, (80, 80, 80), input_rect)
        pygame.draw.rect(screen, (120, 120, 120), input_rect, 2)
        
        # Draw input text
        input_font = pygame.font.SysFont('Consolas', int(h*0.03))
        display_text = seed_input if seed_input else "Enter custom seed..."
        text_color = (255, 255, 255) if seed_input else (150, 150, 150)
        input_text_surf = input_font.render(display_text, True, text_color)
        text_x = input_rect.x + 10
        text_y = input_rect.centery - input_text_surf.get_height() // 2
        screen.blit(input_text_surf, (text_x, text_y))
    
    # Instructions
    inst_font = pygame.font.SysFont('Consolas', int(h*0.025))
    instructions = [
        "Use arrow keys to navigate, Enter to continue",
        "Custom seed: type your seed and press Enter"
    ]
    
    inst_y = int(h * 0.85)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 5
    
    # Draw sound toggle button if sound manager is available (Issue #89)
    if sound_manager:
        draw_mute_button_standalone(screen, sound_manager, w, h)