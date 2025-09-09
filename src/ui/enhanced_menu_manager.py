"""
Enhanced Menu System for P(Doom)

This module provides updated menu handling that integrates:
- Fixed custom seed functionality
- Comprehensive game configuration system
- Reorganized settings (Audio, Gameplay, Accessibility)
- Community sharing features via config + seed packages

This replaces the broken menu handling in main.py with a robust, extensible system.
"""

import pygame
from typing import List, Optional, Tuple, Any
from enum import Enum

from src.ui.settings_menus import (
    SettingsCategory, GameConfigMode, 
    draw_settings_main_menu, draw_game_config_menu,
    handle_settings_main_menu_click, handle_game_config_click
)
from src.services.game_config_manager import game_config_manager
from src.services.config_manager import config_manager


class MenuState(Enum):
    """Enhanced menu states for the updated system."""
    MAIN_MENU = "main_menu"
    GAME_CONFIG = "game_config"
    SETTINGS_MAIN = "settings_main"
    SETTINGS_AUDIO = "settings_audio" 
    SETTINGS_GAMEPLAY = "settings_gameplay"
    SETTINGS_ACCESSIBILITY = "settings_accessibility"
    SETTINGS_KEYBINDINGS = "settings_keybindings"
    CUSTOM_SEED = "custom_seed"
    PRE_GAME = "pre_game"
    TUTORIAL_CHOICE = "tutorial_choice"
    

class EnhancedMenuManager:
    """Manages the enhanced menu system with proper state transitions."""
    
    def __init__(self):
        self.current_state = MenuState.MAIN_MENU
        self.selected_item = 0
        self.navigation_stack = []
        
        # Game config state
        self.config_mode = GameConfigMode.SELECT
        self.available_configs = []
        self.selected_config = None
        self.custom_seed = ""
        
        # Settings state
        self.settings_category = None
        
        # Initialize available configs
        self.refresh_available_configs()
    
    def refresh_available_configs(self):
        """Refresh the list of available configurations."""
        self.available_configs = game_config_manager.get_available_configs()
    
    def get_main_menu_items(self) -> List[str]:
        """Get the correct main menu items."""
        return [
            "Launch Lab",  # Quick start with current/default config
            "Game Config",  # Configure game parameters
            "Settings",     # Audio, gameplay, accessibility settings
            "Player Guide", # Documentation
            "Exit"
        ]
    
    def handle_main_menu_click(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """
        Handle clicks on the main menu.
        
        Returns:
            Action to take or None if no action
        """
        menu_items = self.get_main_menu_items()
        
        # Calculate button positions to match draw_main_menu layout
        button_width = int(w * 0.4)
        button_height = int(h * 0.08)
        start_y = int(h * 0.35)
        spacing = int(h * 0.1)
        center_x = w // 2
        
        mx, my = mouse_pos
        
        for i, item in enumerate(menu_items):
            button_x = center_x - button_width // 2
            button_y = start_y + i * spacing
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            if button_rect.collidepoint(mx, my):
                self.selected_item = i
                
                if i == 0:  # Launch Lab
                    return "launch_lab"
                elif i == 1:  # Game Config
                    self.push_state(MenuState.GAME_CONFIG)
                    self.config_mode = GameConfigMode.SELECT
                    return "enter_game_config"
                elif i == 2:  # Settings
                    self.push_state(MenuState.SETTINGS_MAIN)
                    return "enter_settings"
                elif i == 3:  # Player Guide
                    return "show_player_guide"
                elif i == 4:  # Exit
                    return "exit_game"
                break
        
        return None
    
    def handle_game_config_click(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """Handle clicks in the game configuration menu."""
        if self.config_mode == GameConfigMode.SELECT:
            action, data = handle_game_config_click(
                mouse_pos, w, h, self.config_mode, 
                [config["name"] for config in self.available_configs]
            )
            
            if action == "select_config":
                self.selected_config = data
                return "config_selected"
            elif action == "create_config":
                return "create_config"
            elif action == "set_seed":
                self.push_state(MenuState.CUSTOM_SEED)
                return "enter_seed_input"
            elif action == "back":
                self.pop_state()
                return "back_to_main"
        
        return None
    
    def handle_settings_main_click(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """Handle clicks in the main settings menu.""" 
        category = handle_settings_main_menu_click(mouse_pos, w, h)
        
        if category == SettingsCategory.AUDIO:
            self.push_state(MenuState.SETTINGS_AUDIO)
            return "enter_audio_settings"
        elif category == SettingsCategory.GAMEPLAY:
            self.push_state(MenuState.SETTINGS_GAMEPLAY)
            return "enter_gameplay_settings"
        elif category == SettingsCategory.ACCESSIBILITY:
            self.push_state(MenuState.SETTINGS_ACCESSIBILITY)
            return "enter_accessibility_settings"
        elif category == SettingsCategory.KEYBINDINGS:
            self.push_state(MenuState.SETTINGS_KEYBINDINGS)
            return "enter_keybindings"
        elif category is None:  # Back button
            self.pop_state()
            return "back_to_main"
        
        return None
    
    def handle_custom_seed_input(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle keyboard input for custom seed entry.
        
        Returns:
            Action to take or None
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Use entered seed or generate default
                if not self.custom_seed.strip():
                    from src.services.seed_manager import get_weekly_seed
                    self.custom_seed = get_weekly_seed()
                return "seed_confirmed"
            elif event.key == pygame.K_ESCAPE:
                self.custom_seed = ""
                self.pop_state()
                return "seed_cancelled"
            elif event.key == pygame.K_BACKSPACE:
                self.custom_seed = self.custom_seed[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.custom_seed += event.unicode
        
        return None
    
    def push_state(self, new_state: MenuState):
        """Push current state to navigation stack and change to new state."""
        self.navigation_stack.append(self.current_state)
        self.current_state = new_state
        self.selected_item = 0  # Reset selection
    
    def pop_state(self) -> bool:
        """
        Pop previous state from navigation stack.
        
        Returns:
            True if state was popped, False if stack was empty
        """
        if self.navigation_stack:
            self.current_state = self.navigation_stack.pop()
            self.selected_item = 0
            return True
        return False
    
    def get_navigation_depth(self) -> int:
        """Get current navigation depth for UI display."""
        return len(self.navigation_stack)
    
    def draw_current_menu(self, screen: pygame.Surface, w: int, h: int, **kwargs):
        """Draw the current menu based on state."""
        if self.current_state == MenuState.MAIN_MENU:
            # Use existing draw_main_menu function
            from ui import draw_main_menu
            draw_main_menu(screen, w, h, self.selected_item, kwargs.get('sound_manager'))
            
        elif self.current_state == MenuState.GAME_CONFIG:
            draw_game_config_menu(
                screen, w, h, self.config_mode, self.selected_item,
                self.available_configs, 
                config_manager.get_current_config_name(),
                self.custom_seed
            )
            
        elif self.current_state == MenuState.SETTINGS_MAIN:
            draw_settings_main_menu(screen, w, h, self.selected_item)
            
        elif self.current_state == MenuState.SETTINGS_AUDIO:
            # Use existing audio menu
            from ui import draw_audio_menu
            audio_settings = kwargs.get('audio_settings', {})
            draw_audio_menu(screen, w, h, self.selected_item, audio_settings, kwargs.get('sound_manager'))
            
        elif self.current_state == MenuState.CUSTOM_SEED:
            self._draw_custom_seed_input(screen, w, h)
    
    def _draw_custom_seed_input(self, screen: pygame.Surface, w: int, h: int):
        """Draw the custom seed input screen."""
        screen.fill((32, 32, 44))
        
        # Title
        title_font = pygame.font.SysFont('Consolas', 70, bold=True)
        title_text = title_font.render("P(Doom)", True, (240, 255, 220))
        title_x = (w - title_text.get_width()) // 2
        screen.blit(title_text, (title_x, h // 6))
        
        # Prompt
        font = pygame.font.SysFont('Consolas', 40)
        prompt_text = font.render("Enter Custom Seed:", True, (210, 210, 255))
        prompt_x = (w - prompt_text.get_width()) // 2
        screen.blit(prompt_text, (prompt_x, h // 3))
        
        # Input box
        box = pygame.Rect(w // 4, h // 2, w // 2, 60)
        pygame.draw.rect(screen, (60, 60, 110), box, border_radius=8)
        pygame.draw.rect(screen, (130, 130, 210), box, width=3, border_radius=8)
        
        # Seed text
        seed_text = font.render(self.custom_seed, True, (255, 255, 255))
        screen.blit(seed_text, (box.x + 10, box.y + 10))
        
        # Instructions
        small_font = pygame.font.SysFont('Consolas', 24)
        instructions = [
            "Leave blank for weekly challenge seed",
            "Press [Enter] to continue, [Esc] to cancel"
        ]
        
        y_offset = h // 2 + 100
        for instruction in instructions:
            inst_text = small_font.render(instruction, True, (255, 255, 180))
            inst_x = (w - inst_text.get_width()) // 2
            screen.blit(inst_text, (inst_x, y_offset))
            y_offset += 30
    
    def get_current_state_name(self) -> str:
        """Get current state name for debugging/logging."""
        return self.current_state.value
    
    def reset_to_main_menu(self):
        """Reset to main menu, clearing navigation stack."""
        self.current_state = MenuState.MAIN_MENU
        self.navigation_stack.clear()
        self.selected_item = 0
        self.custom_seed = ""


# Additional helper functions for menu integration

def create_game_with_config(config_name: str = None, seed: str = None) -> Tuple[Any, str]:
    """
    Create a new game with specified configuration and seed.
    
    Args:
        config_name: Name of configuration to use (None for current)
        seed: Custom seed (None for weekly seed)
        
    Returns:
        Tuple of (game_state, actual_seed_used)
    """
    # Import here to avoid circular imports
    from src.core.game_state import GameState
    from src.services.seed_manager import get_weekly_seed
    
    # Apply configuration if specified
    if config_name:
        config_data = None
        # Try user configs first
        config_data = game_config_manager.load_user_config(config_name)
        if not config_data and config_name in config_manager.list_available_configs():
            # Use built-in config
            config_manager.switch_config(config_name)
    
    # Set seed
    actual_seed = seed if seed else get_weekly_seed()
    
    # Create game state
    game_state = GameState(actual_seed)
    
    return game_state, actual_seed


def get_menu_transition_sound(from_state: str, to_state: str) -> Optional[str]:
    """
    Get appropriate sound effect for menu transitions.
    
    Returns:
        Sound effect name or None
    """
    if to_state == "game":
        return "game_start"
    elif "settings" in to_state:
        return "menu_enter"
    elif from_state != "main_menu" and to_state == "main_menu":
        return "menu_back"
    else:
        return "menu_navigate"
