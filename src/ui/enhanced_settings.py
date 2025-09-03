"""
Enhanced Settings System for P(Doom)

This module provides an improved settings interface that organizes options into logical categories:
- Audio Settings: Sound effects, volume, music
- Gameplay Settings: Difficulty, automation, display options  
- Accessibility: Visual aids, interaction options
- Game Configuration: Custom game configs and seeds

This replaces the simple audio-only settings with a comprehensive system.
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any
from src.features.visual_feedback import visual_feedback, ButtonState


def draw_settings_main_menu(screen: pygame.Surface, w: int, h: int, selected_item: int) -> None:
    """
    Draw the main settings menu with organized categories.
    
    Args:
        screen: Pygame surface to draw on
        w, h: Screen dimensions
        selected_item: Currently selected menu item
    """
    # Background
    screen.fill((40, 45, 55))
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h * 0.055), bold=True)
    title_text = title_font.render("SETTINGS & CONFIGURATION", True, (220, 240, 255))
    title_x = w // 2 - title_text.get_width() // 2
    title_y = int(h * 0.1)
    screen.blit(title_text, (title_x, title_y))
    
    # Subtitle
    subtitle_font = pygame.font.SysFont('Consolas', int(h * 0.025))
    subtitle_text = subtitle_font.render("Configure Laboratory Operations & Player Preferences", True, (180, 200, 220))
    subtitle_x = w // 2 - subtitle_text.get_width() // 2
    subtitle_y = title_y + title_text.get_height() + 10
    screen.blit(subtitle_text, (subtitle_x, subtitle_y))
    
    # Settings categories with descriptions
    settings_categories = [
        ("🔊 Audio Settings", "Sound effects, volume, and audio preferences"),
        ("⚙️ Game Configuration", "Custom game setups, seeds, and sharing"),
        ("🎮 Gameplay Settings", "Difficulty, automation, and display options"),
        ("♿ Accessibility", "Visual aids and interaction accommodations"),
        ("⌨️ Keybindings", "Customize keyboard shortcuts and controls"),
        ("← Back to Main Menu", "Return to the main menu")
    ]
    
    # Button layout
    button_width = int(w * 0.65)
    button_height = int(h * 0.07)
    start_y = int(h * 0.25)
    spacing = int(h * 0.08)
    center_x = w // 2
    
    for i, (category_text, description) in enumerate(settings_categories):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.FOCUSED
        else:
            button_state = ButtonState.NORMAL
        
        # Draw button using visual feedback system
        visual_feedback.draw_button(
            screen, button_rect, category_text, button_state,
            style='bureaucratic'
        )
        
        # Draw description text below button when focused
        if i == selected_item and i < len(settings_categories) - 1:  # Not for back button
            desc_font = pygame.font.SysFont('Consolas', int(h * 0.02))
            desc_text = desc_font.render(description, True, (200, 220, 240))
            desc_x = center_x - desc_text.get_width() // 2
            desc_y = button_y + button_height + 8
            screen.blit(desc_text, (desc_x, desc_y))


def draw_game_config_menu(screen: pygame.Surface, w: int, h: int, selected_item: int,
                         available_configs: List[Dict], current_config: str,
                         show_seed_input: bool = False, custom_seed: str = "") -> None:
    """
    Draw the game configuration menu for managing custom game setups.
    """
    screen.fill((35, 40, 50))
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h * 0.055), bold=True)
    title = "GAME CONFIGURATION"
    title_text = title_font.render(title, True, (220, 240, 255))
    title_x = w // 2 - title_text.get_width() // 2
    title_y = int(h * 0.08)
    screen.blit(title_text, (title_x, title_y))
    
    # Subtitle
    subtitle_font = pygame.font.SysFont('Consolas', int(h * 0.022))
    subtitle = "Create and manage custom game configurations for community sharing"
    subtitle_text = subtitle_font.render(subtitle, True, (180, 200, 220))
    subtitle_x = w // 2 - subtitle_text.get_width() // 2
    subtitle_y = title_y + title_text.get_height() + 8
    screen.blit(subtitle_text, (subtitle_x, subtitle_y))
    
    if show_seed_input:
        _draw_seed_input_section(screen, w, h, custom_seed)
    else:
        _draw_config_selection_section(screen, w, h, selected_item, available_configs, current_config)


def _draw_config_selection_section(screen: pygame.Surface, w: int, h: int, selected_item: int,
                                  available_configs: List[Dict], current_config: str) -> None:
    """Draw the configuration selection interface."""
    # Current config info
    info_font = pygame.font.SysFont('Consolas', int(h * 0.025))
    current_text = info_font.render(f"Current Configuration: {current_config}", True, (200, 255, 200))
    current_x = w // 2 - current_text.get_width() // 2
    current_y = int(h * 0.2)
    screen.blit(current_text, (current_x, current_y))
    
    # Configuration options
    button_width = int(w * 0.7)
    button_height = int(h * 0.06)
    start_y = int(h * 0.28)
    spacing = int(h * 0.07)
    center_x = w // 2
    
    # Build options list
    options = []
    for config in available_configs:
        display_name = config.get('display_name', config.get('name', 'Unknown'))
        if config.get('name') == current_config:
            display_name += " (ACTIVE)"
        options.append(display_name)
    
    options.extend([
        "📋 Create New Configuration",
        "🎲 Set Custom Seed",
        "📤 Export Current Config",
        "📥 Import Shared Config",
        "← Back to Settings"
    ])
    
    for i, option in enumerate(options):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.FOCUSED
        else:
            button_state = ButtonState.NORMAL
        
        visual_feedback.draw_button(
            screen, button_rect, option, button_state,
            style='bureaucratic'
        )


def _draw_seed_input_section(screen: pygame.Surface, w: int, h: int, custom_seed: str) -> None:
    """Draw the custom seed input interface."""
    # Instruction text
    inst_font = pygame.font.SysFont('Consolas', int(h * 0.025))
    inst_text = inst_font.render("Enter Custom Seed for Reproducible Experiments:", True, (200, 220, 240))
    inst_x = w // 2 - inst_text.get_width() // 2
    inst_y = int(h * 0.3)
    screen.blit(inst_text, (inst_x, inst_y))
    
    # Input box
    input_font = pygame.font.SysFont('Consolas', int(h * 0.035))
    box_width = int(w * 0.5)
    box_height = int(h * 0.08)
    box_x = w // 2 - box_width // 2
    box_y = inst_y + 50
    input_rect = pygame.Rect(box_x, box_y, box_width, box_height)
    
    # Draw input box
    pygame.draw.rect(screen, (60, 70, 85), input_rect, border_radius=8)
    pygame.draw.rect(screen, (130, 150, 200), input_rect, width=3, border_radius=8)
    
    # Draw seed text
    seed_text = input_font.render(custom_seed, True, (255, 255, 255))
    text_x = input_rect.x + 15
    text_y = input_rect.y + (input_rect.height - seed_text.get_height()) // 2
    screen.blit(seed_text, (text_x, text_y))
    
    # Instructions
    instructions = [
        "💡 Leave blank to use weekly challenge seed",
        "🔄 Seeds allow exact reproduction of game scenarios",
        "📤 Share config + seed combinations for community challenges",
        "",
        "Press [ENTER] to confirm • [ESC] to cancel"
    ]
    
    inst_small_font = pygame.font.SysFont('Consolas', int(h * 0.02))
    inst_y = box_y + box_height + 30
    for instruction in instructions:
        if instruction:  # Skip empty lines
            inst_text = inst_small_font.render(instruction, True, (180, 200, 220))
            inst_x = w // 2 - inst_text.get_width() // 2
            screen.blit(inst_text, (inst_x, inst_y))
        inst_y += inst_small_font.get_height() + 3


def draw_gameplay_settings_menu(screen: pygame.Surface, w: int, h: int, selected_item: int,
                               gameplay_settings: Dict[str, Any]) -> None:
    """
    Draw the gameplay settings menu.
    """
    screen.fill((40, 45, 55))
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h * 0.055), bold=True)
    title_text = title_font.render("GAMEPLAY SETTINGS", True, (220, 240, 255))
    title_x = w // 2 - title_text.get_width() // 2
    title_y = int(h * 0.1)
    screen.blit(title_text, (title_x, title_y))
    
    # Settings options
    button_width = int(w * 0.7)
    button_height = int(h * 0.06)
    start_y = int(h * 0.25)
    spacing = int(h * 0.08)
    center_x = w // 2
    
    # Build settings list from current config
    auto_delegation = gameplay_settings.get('auto_delegation', True)
    show_intel = gameplay_settings.get('show_opponent_intel', True)
    difficulty = gameplay_settings.get('difficulty_modifier', 1.0)
    event_freq = gameplay_settings.get('event_frequency', 1.0)
    
    settings_options = [
        f"Auto-Delegation: {'Enabled' if auto_delegation else 'Disabled'}",
        f"Show Opponent Intel: {'Yes' if show_intel else 'No'}",
        f"Difficulty Modifier: {difficulty:.1f}x",
        f"Event Frequency: {event_freq:.1f}x",
        "Reset to Defaults",
        "← Back to Settings"
    ]
    
    for i, option in enumerate(settings_options):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.FOCUSED
        else:
            button_state = ButtonState.NORMAL
        
        visual_feedback.draw_button(
            screen, button_rect, option, button_state,
            style='bureaucratic'
        )


def handle_settings_main_click(mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
    """
    Handle clicks on the main settings menu.
    
    Returns:
        Action string or None
    """
    button_width = int(w * 0.65)
    button_height = int(h * 0.07)
    start_y = int(h * 0.25)
    spacing = int(h * 0.08)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    actions = ["audio", "game_config", "gameplay", "accessibility", "keybindings", "back"]
    
    for i in range(6):  # 5 categories + back button
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            return actions[i]
    
    return None


def handle_game_config_click(mouse_pos: Tuple[int, int], w: int, h: int,
                           available_configs: List[Dict], show_seed_input: bool) -> Tuple[str, Any]:
    """
    Handle clicks on the game configuration menu.
    
    Returns:
        Tuple of (action, data)
    """
    if show_seed_input:
        # In seed input mode, only ESC handling
        return ("none", None)
    
    button_width = int(w * 0.7)
    button_height = int(h * 0.06)
    start_y = int(h * 0.28)
    spacing = int(h * 0.07)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    # Total options: configs + 5 action buttons
    total_options = len(available_configs) + 5
    
    for i in range(total_options):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            if i < len(available_configs):
                # Config selection
                return ("select_config", available_configs[i])
            elif i == len(available_configs):
                return ("create_config", None)
            elif i == len(available_configs) + 1:
                return ("set_seed", None)
            elif i == len(available_configs) + 2:
                return ("export_config", None)
            elif i == len(available_configs) + 3:
                return ("import_config", None)
            elif i == len(available_configs) + 4:
                return ("back", None)
            break
    
    return ("none", None)
