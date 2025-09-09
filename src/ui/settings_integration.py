"""
Settings Integration Layer for P(Doom)

This module provides a compatibility layer that integrates the enhanced settings system
with the existing main.py structure. It allows gradual migration to the new system
without breaking existing functionality.
"""

import pygame
from typing import Optional, Tuple
from src.ui.enhanced_settings import (
    draw_settings_main_menu, draw_game_config_menu, draw_gameplay_settings_menu,
    handle_settings_main_click, handle_game_config_click
)
from src.services.config_manager import config_manager, get_current_config
from src.services.game_config_manager import game_config_manager


class SettingsState:
    """Manages settings menu state for integration with main.py"""
    
    def __init__(self):
        self.current_menu = "main"  # main, audio, game_config, gameplay, accessibility, keybindings
        self.selected_item = 0
        self.show_seed_input = False
        self.custom_seed = ""
        self.available_configs = []
        self.refresh_configs()
    
    def refresh_configs(self):
        """Refresh available configurations list."""
        self.available_configs = game_config_manager.get_available_configs()
    
    def enter_settings(self):
        """Enter the main settings menu."""
        self.current_menu = "main"
        self.selected_item = 0
    
    def enter_audio_settings(self):
        """Enter audio settings (use existing system)."""
        self.current_menu = "audio"
        self.selected_item = 0
        return "sounds_menu"  # Return state for main.py
    
    def enter_game_config(self):
        """Enter game configuration menu."""
        self.current_menu = "game_config"
        self.selected_item = 0
        self.show_seed_input = False
        self.refresh_configs()
    
    def enter_gameplay_settings(self):
        """Enter gameplay settings menu."""
        self.current_menu = "gameplay"
        self.selected_item = 0
    
    def enter_seed_input(self):
        """Enter custom seed input mode."""
        self.show_seed_input = True
        self.custom_seed = ""
    
    def exit_seed_input(self):
        """Exit custom seed input mode."""
        self.show_seed_input = False
        self.custom_seed = ""
    
    def handle_main_settings_click(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """Handle clicks in main settings menu."""
        action = handle_settings_main_click(mouse_pos, w, h)
        
        if action == "audio":
            return self.enter_audio_settings()
        elif action == "game_config":
            self.enter_game_config()
            return "game_config_menu"
        elif action == "gameplay":
            self.enter_gameplay_settings()
            return "gameplay_settings_menu"
        elif action == "accessibility":
            # TODO: Implement accessibility settings
            return "accessibility_menu"
        elif action == "keybindings":
            return "keybinding_menu"  # Use existing keybinding system
        elif action == "back":
            return "main_menu"
        
        return None
    
    def handle_game_config_click(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """Handle clicks in game configuration menu."""
        if self.show_seed_input:
            return None  # Seed input is handled by keyboard
        
        action, data = handle_game_config_click(mouse_pos, w, h, self.available_configs, self.show_seed_input)
        
        if action == "select_config":
            # Switch to selected config
            config_name = data.get('name')
            if config_name and config_name in config_manager.list_available_configs():
                config_manager.switch_config(config_name)
                return "config_changed"
        elif action == "create_config":
            return "create_config_menu"
        elif action == "set_seed":
            self.enter_seed_input()
            return "seed_input_mode"
        elif action == "export_config":
            return "export_config_dialog"
        elif action == "import_config":
            return "import_config_dialog"
        elif action == "back":
            self.enter_settings()
            return "settings_main_menu"
        
        return None
    
    def handle_seed_input_keyboard(self, event: pygame.event.Event) -> Optional[str]:
        """Handle keyboard input for custom seed entry."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Process the seed
                if not self.custom_seed.strip():
                    from src.services.seed_manager import get_weekly_seed
                    self.custom_seed = get_weekly_seed()
                self.exit_seed_input()
                return "seed_confirmed"
            elif event.key == pygame.K_ESCAPE:
                self.exit_seed_input()
                return "seed_cancelled"
            elif event.key == pygame.K_BACKSPACE:
                self.custom_seed = self.custom_seed[:-1]
            elif event.unicode and event.unicode.isprintable():
                if len(self.custom_seed) < 50:  # Reasonable limit
                    self.custom_seed += event.unicode
        
        return None
    
    def draw_current_menu(self, screen: pygame.Surface, w: int, h: int, **kwargs):
        """Draw the current settings menu."""
        if self.current_menu == "main":
            draw_settings_main_menu(screen, w, h, self.selected_item)
        elif self.current_menu == "game_config":
            current_config_name = config_manager.get_current_config_name()
            draw_game_config_menu(
                screen, w, h, self.selected_item, self.available_configs,
                current_config_name, self.show_seed_input, self.custom_seed
            )
        elif self.current_menu == "gameplay":
            current_config = get_current_config()
            gameplay_settings = current_config.get('gameplay', {})
            draw_gameplay_settings_menu(screen, w, h, self.selected_item, gameplay_settings)
        # Other menus use existing systems
    
    def get_current_menu_type(self) -> str:
        """Get the current menu type for state management."""
        return self.current_menu
    
    def is_seed_input_mode(self) -> bool:
        """Check if currently in seed input mode."""
        return self.show_seed_input
    
    def get_custom_seed(self) -> str:
        """Get the current custom seed."""
        return self.custom_seed


# Global instance for use in main.py
settings_state = SettingsState()


def integrate_with_existing_main():
    """
    Integration helper for gradual adoption in main.py.
    
    This provides a transition path from the current menu system to the enhanced one.
    """
    integration_map = {
        # Map old states to new system
        "sounds_menu": settings_state.enter_audio_settings,
        "settings_main": settings_state.enter_settings,
        
        # New states
        "game_config_menu": settings_state.enter_game_config,
        "gameplay_settings_menu": settings_state.enter_gameplay_settings,
    }
    
    return integration_map


def get_enhanced_settings_keyboard_handler():
    """
    Get keyboard handler for enhanced settings.
    
    Returns a function that can be called from main.py keyboard event handling.
    """
    def handle_keyboard(event: pygame.event.Event, current_state: str) -> Optional[str]:
        if current_state == "game_config_menu" and settings_state.is_seed_input_mode():
            return settings_state.handle_seed_input_keyboard(event)
        # Add other keyboard handlers as needed
        return None
    
    return handle_keyboard


def get_enhanced_settings_mouse_handler():
    """
    Get mouse handler for enhanced settings.
    
    Returns a function that can be called from main.py mouse event handling.
    """
    def handle_mouse(mouse_pos: Tuple[int, int], w: int, h: int, current_state: str) -> Optional[str]:
        if current_state == "settings_main":
            return settings_state.handle_main_settings_click(mouse_pos, w, h)
        elif current_state == "game_config_menu":
            return settings_state.handle_game_config_click(mouse_pos, w, h)
        # Add other mouse handlers as needed
        return None
    
    return handle_mouse


def get_enhanced_settings_renderer():
    """
    Get renderer for enhanced settings.
    
    Returns a function that can be called from main.py rendering loop.
    """
    def render_settings(screen: pygame.Surface, w: int, h: int, current_state: str, **kwargs):
        if current_state in ["settings_main", "game_config_menu", "gameplay_settings_menu"]:
            settings_state.draw_current_menu(screen, w, h, **kwargs)
            return True  # Rendered by enhanced system
        return False  # Use existing system
    
    return render_settings
