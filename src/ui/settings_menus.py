"""
Settings and Configuration Menu System for P(Doom)

This module provides a comprehensive settings system with the following structure:
- Main Settings Menu: Audio, Gameplay, Accessibility, Keybindings
- Game Config Menu: Create/select custom game configurations 
- Seed Management: Integrated with game configs for community sharing

Design Philosophy:
- Clear separation between game settings (affect how you play) and game configs (affect what you play)
- Support for community sharing via config + seed combinations
- Extensible system for adding new settings categories
- Consistent with P(Doom)'s bureaucratic theme
"""

import pygame
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from src.services.config_manager import config_manager, get_current_config
from src.ui.visual_feedback import ButtonState, visual_feedback


class SettingsCategory(Enum):
    """Categories of settings available to the player."""
    AUDIO = "audio"
    GAMEPLAY = "gameplay" 
    ACCESSIBILITY = "accessibility"
    KEYBINDINGS = "keybindings"


class GameConfigMode(Enum):
    """Modes for game configuration management."""
    SELECT = "select"  # Choose from existing configs
    CREATE = "create"  # Create new config
    EDIT = "edit"     # Edit existing config
    SEED = "seed"     # Set custom seed for config


def draw_settings_main_menu(screen: pygame.Surface, w: int, h: int, selected_item: int) -> None:
    """
    Draw the main settings menu with categories.
    
    Args:
        screen: Pygame surface to draw on
        w, h: Screen dimensions
        selected_item: Currently selected menu item
    """
    # Clear background
    screen.fill((40, 45, 55))
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h * 0.06), bold=True)
    title_text = title_font.render("INSTITUTIONAL SETTINGS", True, (220, 240, 255))
    title_x = w // 2 - title_text.get_width() // 2
    title_y = int(h * 0.12)
    screen.blit(title_text, (title_x, title_y))
    
    # Subtitle
    subtitle_font = pygame.font.SysFont('Consolas', int(h * 0.025))
    subtitle_text = subtitle_font.render("Configure Laboratory Operations & Protocols", True, (180, 200, 220))
    subtitle_x = w // 2 - subtitle_text.get_width() // 2
    subtitle_y = title_y + title_text.get_height() + 10
    screen.blit(subtitle_text, (subtitle_x, subtitle_y))
    
    # Menu items with descriptions
    settings_options = [
        ("? Audio Settings", "Configure sound effects and volume levels"),
        ("[GAME] Gameplay Settings", "Adjust difficulty and game mechanics"),
        ("? Accessibility", "Visual and interaction accessibility options"),
        ("?? Keybindings", "Customize keyboard shortcuts and controls"),
        ("? Back to Main Menu", "Return to the main menu")
    ]
    
    # Button layout
    button_width = int(w * 0.6)
    button_height = int(h * 0.08)
    start_y = int(h * 0.35)
    spacing = int(h * 0.095)
    center_x = w // 2
    
    for i, (option_text, description) in enumerate(settings_options):
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
            screen, button_rect, option_text, button_state, 
            style='bureaucratic'
        )
        
        # Draw description text below button
        if i == selected_item:
            desc_font = pygame.font.SysFont('Consolas', int(h * 0.02))
            desc_text = desc_font.render(description, True, (200, 220, 240))
            desc_x = center_x - desc_text.get_width() // 2
            desc_y = button_y + button_height + 5
            screen.blit(desc_text, (desc_x, desc_y))


def draw_game_config_menu(screen: pygame.Surface, w: int, h: int, 
                         mode: GameConfigMode, selected_item: int,
                         available_configs: List[str] = None,
                         current_config_name: str = None,
                         custom_seed: str = "") -> None:
    """
    Draw the game configuration menu for creating/selecting game configs.
    
    Args:
        screen: Pygame surface to draw on
        w, h: Screen dimensions  
        mode: Current configuration mode
        selected_item: Currently selected item
        available_configs: List of available configuration names
        current_config_name: Name of currently active config
        custom_seed: Custom seed if being set
    """
    screen.fill((35, 40, 50))
    
    # Title based on mode
    title_font = pygame.font.SysFont('Consolas', int(h * 0.055), bold=True)
    if mode == GameConfigMode.SELECT:
        title = "LABORATORY CONFIGURATION SELECTION"
        subtitle = "Choose your research parameters & experimental conditions"
    elif mode == GameConfigMode.CREATE:
        title = "CREATE NEW CONFIGURATION"
        subtitle = "Design custom laboratory parameters for community sharing"
    elif mode == GameConfigMode.SEED:
        title = "SET EXPERIMENTAL SEED"
        subtitle = "Configure randomization parameters for reproducible experiments"
    else:
        title = "LABORATORY CONFIGURATION"
        subtitle = "Manage experimental parameters"
        
    title_text = title_font.render(title, True, (220, 240, 255))
    title_x = w // 2 - title_text.get_width() // 2
    title_y = int(h * 0.1)
    screen.blit(title_text, (title_x, title_y))
    
    subtitle_font = pygame.font.SysFont('Consolas', int(h * 0.022))
    subtitle_text = subtitle_font.render(subtitle, True, (180, 200, 220))
    subtitle_x = w // 2 - subtitle_text.get_width() // 2
    subtitle_y = title_y + title_text.get_height() + 8
    screen.blit(subtitle_text, (subtitle_x, subtitle_y))
    
    if mode == GameConfigMode.SELECT:
        _draw_config_selection(screen, w, h, selected_item, available_configs, current_config_name)
    elif mode == GameConfigMode.SEED:
        _draw_seed_input(screen, w, h, custom_seed)
    # Add other modes as needed


def _draw_config_selection(screen: pygame.Surface, w: int, h: int, 
                          selected_item: int, available_configs: List[str],
                          current_config_name: str) -> None:
    """Draw the configuration selection interface."""
    if not available_configs:
        # No configs available
        font = pygame.font.SysFont('Consolas', int(h * 0.03))
        text = font.render("No configurations available. Creating default...", True, (255, 200, 200))
        text_x = w // 2 - text.get_width() // 2
        text_y = h // 2
        screen.blit(text, (text_x, text_y))
        return
    
    # Configuration list
    button_width = int(w * 0.7)
    button_height = int(h * 0.08)
    start_y = int(h * 0.25)
    spacing = int(h * 0.09)
    center_x = w // 2
    
    # Show available configs + option to create new + option to set seed
    options = available_configs + ["Create New Configuration", "Set Custom Seed", "? Back"]
    
    for i, option in enumerate(options):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.FOCUSED
        else:
            button_state = ButtonState.NORMAL
            
        # Special styling for current config
        display_text = option
        if i < len(available_configs):
            if option == current_config_name:
                display_text = f"? {option} (ACTIVE)"
                
        visual_feedback.draw_button(
            screen, button_rect, display_text, button_state,
            style='bureaucratic'
        )


def _draw_seed_input(screen: pygame.Surface, w: int, h: int, custom_seed: str) -> None:
    """Draw the custom seed input interface."""
    # Seed input box
    input_font = pygame.font.SysFont('Consolas', int(h * 0.035))
    label_font = pygame.font.SysFont('Consolas', int(h * 0.025))
    
    # Label
    label_text = label_font.render("EXPERIMENTAL SEED:", True, (200, 220, 240))
    label_x = w // 2 - label_text.get_width() // 2
    label_y = int(h * 0.35)
    screen.blit(label_text, (label_x, label_y))
    
    # Input box
    box_width = int(w * 0.5)
    box_height = int(h * 0.08)
    box_x = w // 2 - box_width // 2
    box_y = label_y + label_text.get_height() + 20
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
        "Enter custom seed for reproducible experiments",
        "Leave blank to use weekly challenge seed",
        "Press [ENTER] to continue, [ESC] to cancel"
    ]
    
    inst_font = pygame.font.SysFont('Consolas', int(h * 0.02))
    inst_y = box_y + box_height + 30
    for instruction in instructions:
        inst_text = inst_font.render(instruction, True, (180, 200, 220))
        inst_x = w // 2 - inst_text.get_width() // 2
        screen.blit(inst_text, (inst_x, inst_y))
        inst_y += inst_text.get_height() + 5


def handle_settings_main_menu_click(mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[SettingsCategory]:
    """
    Handle clicks on the main settings menu.
    
    Returns:
        SettingsCategory if a category was selected, None for back button
    """
    button_width = int(w * 0.6)
    button_height = int(h * 0.08)
    start_y = int(h * 0.35)
    spacing = int(h * 0.095)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    for i in range(5):  # 4 categories + back button
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            if i == 0:
                return SettingsCategory.AUDIO
            elif i == 1:
                return SettingsCategory.GAMEPLAY
            elif i == 2:
                return SettingsCategory.ACCESSIBILITY
            elif i == 3:
                return SettingsCategory.KEYBINDINGS
            elif i == 4:
                return None  # Back button
            break
    
    return None


def handle_game_config_click(mouse_pos: Tuple[int, int], w: int, h: int,
                           mode: GameConfigMode, available_configs: List[str]) -> Tuple[str, Any]:
    """
    Handle clicks on the game configuration menu.
    
    Returns:
        Tuple of (action, data) where action describes what was clicked
    """
    if mode == GameConfigMode.SELECT:
        button_width = int(w * 0.7)
        button_height = int(h * 0.08)
        start_y = int(h * 0.25)
        spacing = int(h * 0.09)
        center_x = w // 2
        
        mx, my = mouse_pos
        
        options = available_configs + ["Create New Configuration", "Set Custom Seed", "? Back"]
        
        for i, option in enumerate(options):
            button_x = center_x - button_width // 2
            button_y = start_y + i * spacing
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            if button_rect.collidepoint(mx, my):
                if i < len(available_configs):
                    return ("select_config", available_configs[i])
                elif option == "Create New Configuration":
                    return ("create_config", None)
                elif option == "Set Custom Seed":
                    return ("set_seed", None)
                elif option == "? Back":
                    return ("back", None)
                break
    
    return ("none", None)


def get_settings_navigation_info() -> Dict[str, Any]:
    """
    Get information about settings menu navigation structure.
    
    Returns:
        Dictionary with navigation information for breadcrumb display
    """
    return {
        "main_settings": {
            "title": "Settings",
            "categories": ["Audio", "Gameplay", "Accessibility", "Keybindings"]
        },
        "game_config": {
            "title": "Game Configuration", 
            "modes": ["Select", "Create", "Seed"]
        }
    }
