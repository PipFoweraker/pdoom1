'''
Menu handling functions for P(Doom) main menu system.

This module contains all the menu interaction handlers that were previously
in main.py, extracted for better code organization and maintainability.
'''

import pygame
import json
from datetime import datetime, timezone
from src.features.onboarding import onboarding


def get_weekly_seed():
    '''Generate a weekly seed based on current date.'''
    # Example: YYYYWW (year and ISO week number)
    now = datetime.now(timezone.utc)
    return f'{now.year}{now.isocalendar()[1]}'


def load_markdown_file(filename):
    '''Load and return the contents of a markdown file'''
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f'Could not load {filename}'


def get_tutorial_settings():
    '''Get current tutorial settings from file.'''
    try:
        with open('tutorial_settings.json', 'r') as f:
            data = json.load(f)
        return {
            'tutorial_enabled': data.get('tutorial_enabled', True),
            'first_game_launch': data.get('first_game_launch', True)
        }
    except Exception:
        return {'tutorial_enabled': True, 'first_game_launch': True}


def create_settings_content(game_state=None):
    '''Create settings content for the settings overlay'''
    tutorial_status = 'Enabled' if onboarding.tutorial_enabled else 'Disabled'
    tutorial_completed = 'Yes' if not onboarding.is_first_time else 'No'
    hints_enabled = 'Enabled' if onboarding.are_hints_enabled() else 'Disabled'
    
    # Get hint status
    hint_status = onboarding.get_hint_status()
    seen_hints = [name for name, seen in hint_status.items() if seen]
    unseen_hints = [name for name, seen in hint_status.items() if not seen]
    
    return f'''# Settings
## Tutorial & Help System
- **Tutorial System**: {tutorial_status}
- **Tutorial Completed**: {tutorial_completed}
- **In-Game Hints**: {hints_enabled}
- **In-Game Help**: Press 'H' key anytime to access Player Guide

## Hints Status
- **Hints Seen**: {len(seen_hints)}
- **Hints Available**: {len(unseen_hints)}

## Configuration
- **Audio**: Toggle from main menu
- **Controls**: Keyboard shortcuts available in-game (press 'H')
- **Display**: Configured at game startup

## Advanced Options
If you want to reset your tutorial progress or hint status, you can delete the following files:
- `tutorial_settings.json` - Resets tutorial preferences
- `onboarding_progress.json` - Resets hint progress

## Version Info
Version: {game_state.get_display_version() if hasattr(game_state, 'get_display_version') else 'Unknown'}
'''


class NavigationManager:
    '''Manages navigation state stack for menu system.'''
    
    def __init__(self):
        self.navigation_stack = []
    
    def push_state(self, current_state, new_state):
        '''Push current state to navigation stack and return new state.'''
        self.navigation_stack.append(current_state)
        return new_state
    
    def pop_state(self, current_state):
        '''Pop from navigation stack and return previous state, or current if stack empty.'''
        if self.navigation_stack:
            return self.navigation_stack.pop()
        return current_state
    
    def get_depth(self):
        '''Get current navigation depth (number of states in stack).'''
        return len(self.navigation_stack)
    
    def clear(self):
        '''Clear the navigation stack.'''
        self.navigation_stack.clear()


class MenuClickHandler:
    '''Handles mouse clicks for various menu screens.'''
    
    @staticmethod
    def handle_main_menu_click(mouse_pos, w, h, menu_items):
        '''
        Handle mouse clicks on main menu items.
        
        Args:
            mouse_pos: Tuple of (x, y) mouse coordinates
            w, h: Screen width and height for button positioning
            menu_items: List of menu item names
            
        Returns:
            Dict with action and any additional data
        '''
        # Calculate menu button positions (must match draw_main_menu layout)
        button_width = int(w * 0.4)
        button_height = int(h * 0.08)
        start_y = int(h * 0.35)
        spacing = int(h * 0.1)
        center_x = w // 2
        
        mx, my = mouse_pos
        
        # Check each menu button for collision
        for i, item in enumerate(menu_items):
            button_x = center_x - button_width // 2
            button_y = start_y + i * spacing
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            if button_rect.collidepoint(mx, my):
                return {'action': 'menu_select', 'index': i, 'item': item}
        
        return {'action': 'none'}
    
    @staticmethod
    def handle_start_game_submenu_click(mouse_pos, w, h, submenu_items):
        '''Handle mouse clicks on start game submenu.'''
        # Calculate button positions (match the standard menu layout)
        button_width = int(w * 0.5)
        button_height = int(w * 0.08)
        start_y = int(h * 0.3)
        spacing = int(h * 0.1)
        center_x = w // 2
        
        mx, my = mouse_pos
        
        # Check each submenu button
        for i, item in enumerate(submenu_items):
            button_x = center_x - button_width // 2
            button_y = start_y + i * spacing
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            if button_rect.collidepoint(mx, my):
                return {'action': 'submenu_select', 'index': i, 'item': item}
        
        return {'action': 'none'}


class MenuKeyboardHandler:
    '''Handles keyboard navigation for various menu screens.'''
    
    @staticmethod
    def handle_main_menu_keyboard(key, selected_item, menu_items):
        '''
        Handle keyboard navigation in main menu.
        
        Args:
            key: pygame key constant from keydown event
            selected_item: Currently selected menu item index
            menu_items: List of menu items
            
        Returns:
            Dict with new_selected_item and action
        '''
        if key == pygame.K_UP:
            new_selected = (selected_item - 1) % len(menu_items)
            return {'new_selected_item': new_selected, 'action': 'navigate'}
        elif key == pygame.K_DOWN:
            new_selected = (selected_item + 1) % len(menu_items)
            return {'new_selected_item': new_selected, 'action': 'navigate'}
        elif key == pygame.K_RETURN:
            return {'new_selected_item': selected_item, 'action': 'select', 'index': selected_item}
        
        return {'new_selected_item': selected_item, 'action': 'none'}


class SettingsHandler:
    '''Handles pre-game settings interactions.'''
    
    @staticmethod
    def cycle_setting_value(setting_index, settings_dict, reverse=False):
        '''
        Cycle through available values for a setting.
        
        Args:
            setting_index: Index of the setting to cycle
            settings_dict: Dictionary of current settings
            reverse: Whether to cycle backwards
            
        Returns:
            Updated settings dictionary
        '''
        # Implementation would be moved from main.py
        # This is a placeholder for the refactoring
        return settings_dict
