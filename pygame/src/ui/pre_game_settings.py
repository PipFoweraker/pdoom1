'''
Pre-Game Settings Handler

This module handles the enhanced pre-game settings functionality including:
- Improved name input UX (auto-select, clear-on-type)
- Random lab name generation
- Settings validation and management

This reduces complexity in main.py by extracting specialized functionality.
'''

import time
from typing import Dict, Any, Tuple
from src.services.lab_name_manager import get_lab_name_manager


class PreGameSettingsManager:
    '''Manages pre-game settings state and interactions.'''
    
    def __init__(self):
        self.text_input_active = False
        self.text_input_field = ''  # 'player_name' or 'lab_name'
        self.text_input_selected = False  # True if current text should be replaced on next input
    
    def activate_text_input(self, field_name: str, settings: Dict[str, Any]) -> None:
        '''
        Activate text input mode for a specific field.
        
        Args:
            field_name: Either 'player_name' or 'lab_name'
            settings: The pre_game_settings dictionary
        '''
        self.text_input_active = True
        self.text_input_field = field_name
        self.text_input_selected = True  # Select all existing text
    
    def deactivate_text_input(self) -> None:
        '''Exit text input mode.'''
        self.text_input_active = False
        self.text_input_field = ''
        self.text_input_selected = False
    
    def handle_backspace(self, settings: Dict[str, Any]) -> None:
        '''
        Handle backspace key in text input mode.
        
        Args:
            settings: The pre_game_settings dictionary
        '''
        if not self.text_input_active or not self.text_input_field:
            return
            
        if self.text_input_selected:
            # Clear all selected text
            settings[self.text_input_field] = ''
            self.text_input_selected = False
        elif settings[self.text_input_field]:
            # Remove last character
            settings[self.text_input_field] = settings[self.text_input_field][:-1]
    
    def handle_text_input(self, text: str, settings: Dict[str, Any]) -> None:
        '''
        Handle text input for name fields.
        
        Args:
            text: The input text
            settings: The pre_game_settings dictionary
        '''
        if not self.text_input_active or not self.text_input_field:
            return
            
        # Clear selected text on first input
        if self.text_input_selected:
            settings[self.text_input_field] = ''
            self.text_input_selected = False
        
        # Add character with length limit
        if len(settings[self.text_input_field]) < 30:  # Max 30 characters
            settings[self.text_input_field] += text
    
    def generate_random_lab_name(self, settings: Dict[str, Any]) -> str:
        '''
        Generate a random lab name and update settings.
        
        Args:
            settings: The pre_game_settings dictionary
            
        Returns:
            The generated lab name
        '''
        lab_manager = get_lab_name_manager()
        # Use current timestamp as seed for randomness
        seed = str(int(time.time() * 1000))
        new_name = lab_manager.get_random_lab_name(seed)
        settings['lab_name'] = new_name
        return new_name
    
    def cycle_setting_value(self, setting_index: int, settings: Dict[str, Any], reverse: bool = False) -> None:
        '''
        Cycle through available values for a setting.
        
        Args:
            setting_index: The index of the setting to cycle
            settings: The pre_game_settings dictionary
            reverse: Whether to cycle in reverse direction
        '''
        if setting_index == 1:  # Player Name - activate text input mode
            self.activate_text_input('player_name', settings)
            
        elif setting_index == 2:  # Lab Name - activate text input mode
            self.activate_text_input('lab_name', settings)
            
        elif setting_index == 3:  # Research Intensity (Difficulty)
            options = ['EASY', 'STANDARD', 'HARD']
            current = settings['difficulty']
            current_idx = options.index(current) if current in options else 1
            new_idx = (current_idx + (-1 if reverse else 1)) % len(options)
            settings['difficulty'] = options[new_idx]
            
        elif setting_index == 4:  # Audio Alerts Volume (Sound Volume)
            options = [30, 50, 70, 80, 90, 100]
            current = settings['sound_volume']
            try:
                current_idx = options.index(current)
            except ValueError:
                current_idx = 3  # Default to 80
            new_idx = (current_idx + (-1 if reverse else 1)) % len(options)
            settings['sound_volume'] = options[new_idx]
            
        elif setting_index == 5:  # Visual Enhancement (Graphics Quality)
            options = ['LOW', 'STANDARD', 'HIGH']
            current = settings['graphics_quality']
            current_idx = options.index(current) if current in options else 1
            new_idx = (current_idx + (-1 if reverse else 1)) % len(options)
            settings['graphics_quality'] = options[new_idx]
            
        elif setting_index == 6:  # Safety Protocol Level
            options = ['MINIMAL', 'STANDARD', 'ENHANCED', 'MAXIMUM']
            current = settings['safety_level']
            current_idx = options.index(current) if current in options else 1
            new_idx = (current_idx + (-1 if reverse else 1)) % len(options)
            settings['safety_level'] = options[new_idx]
    
    def handle_random_lab_name_click(self, mouse_pos: Tuple[int, int], w: int, h: int, settings: Dict[str, Any]) -> bool:
        '''
        Check if the random lab name button was clicked.
        
        Args:
            mouse_pos: Mouse position (x, y)
            w: Screen width
            h: Screen height
            settings: The pre_game_settings dictionary
            
        Returns:
            True if the button was clicked and handled
        '''
        # Calculate button position (next to lab name field)
        # This should match the UI layout in draw_pre_game_settings
        button_width = int(w * 0.55)
        button_height = int(h * 0.07)
        start_y = int(h * 0.32)
        spacing = int(h * 0.085)
        center_x = w // 2
        
        # Lab name is at index 2, so button_y = start_y + 2 * spacing
        lab_name_button_y = start_y + 2 * spacing
        
        # Random button is small and to the right of the main button
        random_button_size = int(button_height * 0.8)
        random_button_x = center_x + button_width // 2 + 10
        random_button_y = lab_name_button_y + (button_height - random_button_size) // 2
        
        mx, my = mouse_pos
        (random_button_x, random_button_y, random_button_size, random_button_size)
        
        if (random_button_x <= mx <= random_button_x + random_button_size and 
            random_button_y <= my <= random_button_y + random_button_size):
            # Generate new random lab name
            self.generate_random_lab_name(settings)
            return True
        
        return False
    
    def is_text_input_active(self) -> bool:
        '''Check if text input is currently active.'''
        return self.text_input_active
    
    def get_text_input_field(self) -> str:
        '''Get the current text input field name.'''
        return self.text_input_field
    
    def is_text_selected(self) -> bool:
        '''Check if text is currently selected for replacement.'''
        return self.text_input_selected


# Global instance for use in main.py
pre_game_settings_manager = PreGameSettingsManager()
