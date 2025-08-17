"""
Audio Menu Screen for P(Doom)

This module contains the audio settings menu implementation migrated from ui.py.
Provides audio settings interface with volume controls, accessibility-friendly
audio controls, and integration with sound manager for real-time feedback.
"""

import pygame
from visual_feedback import ButtonState, draw_low_poly_button


def draw_audio_menu(screen, w, h, selected_item, audio_settings, sound_manager):
    """
    Draw the audio settings menu.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height
        selected_item: index of currently selected menu item
        audio_settings: dictionary of current audio settings
        sound_manager: SoundManager instance for current state
    """
    # Background
    screen.fill((40, 45, 55))
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h*0.055), bold=True)
    title_surf = title_font.render("Audio Settings", True, (220, 240, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.12)
    screen.blit(title_surf, (title_x, title_y))
    
    # Menu items
    menu_font = pygame.font.SysFont('Consolas', int(h*0.03))
    button_width = int(w * 0.6)
    button_height = int(h * 0.06)
    start_y = int(h * 0.25)
    spacing = int(h * 0.08)
    center_x = w // 2
    
    # Audio menu items with current values
    master_status = "Enabled" if audio_settings.get('master_enabled', True) else "Disabled"
    sfx_volume = audio_settings.get('sfx_volume', 80)
    
    menu_items = [
        f"Master Sound: {master_status}",
        f"SFX Volume: {sfx_volume}%",
        "Sound Effects Settings",
        "Test Sound",
        "← Back to Main Menu"
    ]
    
    for i, item in enumerate(menu_items):
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
    inst_font = pygame.font.SysFont('Consolas', int(h*0.02))
    instructions = [
        "Use arrow keys to navigate, Enter/Space to select",
        "Left/Right arrows adjust volume settings",
        "Escape to return to main menu"
    ]
    
    inst_y = int(h * 0.75)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 3
    
    # Additional info about sound effects
    if selected_item == 2:
        info_font = pygame.font.SysFont('Consolas', int(h*0.018))
        info_text = "Individual sound toggles: Click to cycle through sound effects"
        info_surf = info_font.render(info_text, True, (150, 200, 150))
        info_x = w // 2 - info_surf.get_width() // 2
        info_y = int(h * 0.85)
        screen.blit(info_surf, (info_x, info_y))