'''
Game Configuration System for P(Doom)

Provides centralized configuration management supporting:
- Multiple named config files stored locally
- Default config generation with sensible game balance
- Config selection and switching at runtime
- Backward compatibility with existing settings

Architecture follows existing JSON-based patterns used throughout the codebase.
'''

import json
import os
from typing import Dict, List, Any, Optional


class ConfigManager:
    '''
    Manages game configuration files and settings.
    
    Features:
    - Multiple named configurations stored locally
    - Default config generation
    - Config selection and switching
    - Backward compatibility with existing settings
    '''
    
    CONFIG_DIR = 'configs'
    DEFAULT_CONFIG_NAME = 'default'
    CURRENT_CONFIG_FILE = 'current_config.json'
    
    def __init__(self):
        '''Initialize the config manager and ensure config directory exists.'''
        self.current_config_name = self.DEFAULT_CONFIG_NAME
        self.current_config = {}
        self._ensure_config_directory()
        self._load_current_config_selection()
    
    def _ensure_config_directory(self):
        '''Create the configs directory if it doesn't exist.'''
        try:
            if not os.path.exists(self.CONFIG_DIR):
                os.makedirs(self.CONFIG_DIR)
        except OSError as e:
            print(f'Warning: Could not create config directory '{self.CONFIG_DIR}': {e}')
            # Create a fallback temporary directory if possible
            import tempfile
            try:
                self.CONFIG_DIR = tempfile.mkdtemp(prefix='pdoom_configs_')
                print(f'Using temporary config directory: {self.CONFIG_DIR}')
            except Exception as temp_e:
                print(f'Error: Could not create temporary config directory: {temp_e}')
                # Use current directory as last resort
                self.CONFIG_DIR = '.'
    
    def _get_config_path(self, config_name: str) -> str:
        '''Get the full path for a config file.'''
        return os.path.join(self.CONFIG_DIR, f'{config_name}.json')
    
    def _load_current_config_selection(self):
        '''Load the currently selected config name.'''
        try:
            with open(self.CURRENT_CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.current_config_name = data.get('current_config', self.DEFAULT_CONFIG_NAME)
        except (FileNotFoundError, json.JSONDecodeError, OSError, IOError):
            # Use default if file doesn't exist, is corrupted, or cannot be read
            self.current_config_name = self.DEFAULT_CONFIG_NAME
    
    def _save_current_config_selection(self):
        '''Save the currently selected config name.'''
        try:
            data = {'current_config': self.current_config_name}
            with open(self.CURRENT_CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f'Warning: Could not save current config selection: {e}')
    
    def get_default_config(self) -> Dict[str, Any]:
        '''
        Generate the default configuration with sensible game balance.
        
        This defines all configurable aspects of the game with their default values.
        These values match the current game balance as of implementation.
        '''
        return {
            # Metadata
            'config_name': 'Default Configuration',
            'description': 'Balanced settings for standard gameplay',
            'version': '1.0.0',
            
            # Game Balance - Starting Resources
            'starting_resources': {
                'money': 100000,  # Bootstrap v0.4.1: $100k starting funds for party demo
                'staff': 2,
                'reputation': 50,
                'action_points': 3,
                'doom': 25,  # Starting p(Doom) percentage
                'compute': 0
            },
            
            # Game Balance - Action Point System
            'action_points': {
                'base_ap_per_turn': 3,
                'staff_ap_bonus': 0.5,  # AP bonus per regular staff member
                'admin_ap_bonus': 1.0,  # AP bonus per admin assistant
                'max_ap_per_turn': 10   # Cap to prevent excessive AP accumulation
            },
            
            # Game Balance - Resource Limits
            'resource_limits': {
                'max_doom': 100,
                'max_reputation': 200,
                'max_money': 1000000,  # Practical limit to prevent overflow
                'max_staff': 100       # Practical limit for UI performance
            },
            
            # Game Balance - Milestone Thresholds
            'milestones': {
                'manager_threshold': 9,        # Staff count to trigger manager milestone
                'board_spending_threshold': 200000,  # Spending to trigger board member search (2x starting money)
                'enhanced_events_turn': 8,     # Turn when enhanced events unlock
                'scrollable_log_turn': 5       # Turn when scrollable event log unlocks
            },
            
            # UI Settings
            'ui': {
                'window_scale': 0.8,           # Percentage of screen size
                'fullscreen': True,            # Default to fullscreen for better onboarding
                'font_scale': 1.0,             # Font size multiplier
                'animation_speed': 1.0,        # Animation speed multiplier
                'tooltip_delay': 500,          # Milliseconds before tooltip appears
                'show_balance_changes': True,  # Show resource change indicators
                'show_keyboard_shortcuts': True,  # Show keyboard shortcuts on buttons
                'context_window': {
                    'enabled': True,           # Enable persistent context window
                    'always_visible': True,    # Show context window even when nothing is hovered
                    'minimized': False,        # Start minimized
                    'height_percent': 0.13,    # Height as percentage of screen height (when expanded)
                    'minimized_height_percent': 0.06,  # Height when minimized
                    'position': 'bottom'       # Position on screen (bottom only for now)
                }
            },
            
            # Audio Settings
            'audio': {
                'sound_enabled': True,
                'master_volume': 1.0,
                'ui_sounds': True,
                'feedback_sounds': True
            },
            
            # Tutorial and Help
            'tutorial': {
                'tutorial_enabled': True,
                'first_time_help': False,  # Disabled by default for experienced players
                'show_tips': True,
                'auto_help_on_errors': True
            },
            
            # Gameplay Settings
            'gameplay': {
                'auto_delegation': True,       # Use delegation when beneficial
                'show_opponent_intel': True,   # Show discovered opponent information
                'event_frequency': 1.0,        # Event probability multiplier
                'difficulty_modifier': 1.0,   # General difficulty adjustment
                'enhanced_events_enabled': True  # Enable popup/deferred event system
            },
            
            # Advanced Settings (for modding)
            'advanced': {
                'debug_mode': True,           # Enable debug hotkeys during beta
                'verbose_logging': True,       # Enable detailed activity logging by default
                'log_level': 'INFO',
                'enable_experimental_features': False,
                'enable_demo_window': False,  # W key demo window
                'custom_event_weights': {},    # Custom event probability overrides
                'custom_action_costs': {},     # Custom action cost overrides
                'custom_upgrade_costs': {}     # Custom upgrade cost overrides
            }
        }
    
    def create_default_config_if_needed(self) -> bool:
        '''
        Create the default config file if it doesn't exist.
        
        Returns:
            bool: True if a new config was created, False if one already existed
        '''
        default_path = self._get_config_path(self.DEFAULT_CONFIG_NAME)
        if not os.path.exists(default_path):
            self.save_config(self.DEFAULT_CONFIG_NAME, self.get_default_config())
            return True
        return False
    
    def list_available_configs(self) -> List[str]:
        '''
        Get a list of available configuration names.
        
        Returns:
            List[str]: List of config names (without .json extension)
        '''
        configs = []
        if os.path.exists(self.CONFIG_DIR):
            for filename in os.listdir(self.CONFIG_DIR):
                if filename.endswith('.json'):
                    config_name = filename[:-5]  # Remove .json extension
                    configs.append(config_name)
        
        # Ensure default config is always available
        if self.DEFAULT_CONFIG_NAME not in configs:
            self.create_default_config_if_needed()
            configs.append(self.DEFAULT_CONFIG_NAME)
        
        return sorted(configs)
    
    def load_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        '''
        Load a configuration by name.
        
        Args:
            config_name: Name of the config to load
            
        Returns:
            Dict containing config data, or None if config doesn't exist
        '''
        config_path = self._get_config_path(config_name)
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f'Warning: Could not load config '{config_name}': {e}')
            return None
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        '''
        Save a configuration with the given name.
        
        Args:
            config_name: Name to save the config under
            config_data: Configuration data to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        '''
        config_path = self._get_config_path(config_name)
        try:
            # Ensure parent directory exists
            parent_dir = os.path.dirname(config_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except (OSError, IOError, PermissionError) as e:
            print(f'Error: Could not save config '{config_name}': {e}')
            return False
        except Exception as e:
            print(f'Error: Unexpected error saving config '{config_name}': {e}')
            return False
    
    def get_current_config(self) -> Dict[str, Any]:
        '''
        Get the currently selected configuration.
        
        Returns:
            Dict containing current config data
        '''
        if not self.current_config:
            self.current_config = self.load_config(self.current_config_name)
            if not self.current_config:
                # Fallback to default if current config is missing
                print(f'Warning: Current config '{self.current_config_name}' not found, falling back to default')
                self.create_default_config_if_needed()
                self.current_config = self.load_config(self.DEFAULT_CONFIG_NAME)
                if not self.current_config:
                    # Ultimate fallback - use in-memory default
                    print(f'Warning: Could not load default config file, using in-memory defaults')
                    self.current_config = self.get_default_config()
                self.current_config_name = self.DEFAULT_CONFIG_NAME
        
        return self.current_config
    
    def switch_config(self, config_name: str) -> bool:
        '''
        Switch to a different configuration.
        
        Args:
            config_name: Name of the config to switch to
            
        Returns:
            bool: True if switched successfully, False if config doesn't exist
        '''
        config_data = self.load_config(config_name)
        if config_data:
            self.current_config_name = config_name
            self.current_config = config_data
            self._save_current_config_selection()
            return True
        return False
    
    def get_current_config_name(self) -> str:
        '''Get the name of the currently selected config.'''
        return self.current_config_name
    
    def create_config_copy(self, source_name: str, new_name: str) -> bool:
        '''
        Create a copy of an existing config with a new name.
        
        Args:
            source_name: Name of config to copy from
            new_name: Name for the new config
            
        Returns:
            bool: True if copied successfully, False otherwise
        '''
        source_config = self.load_config(source_name)
        if source_config:
            # Update metadata for the copy
            source_config['config_name'] = f'Copy of {source_config.get('config_name', source_name)}'
            source_config['description'] = f'Based on {source_name} configuration'
            return self.save_config(new_name, source_config)
        return False
    
    def delete_config(self, config_name: str) -> bool:
        '''
        Delete a configuration file.
        
        Args:
            config_name: Name of config to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        '''
        # Prevent deletion of default config
        if config_name == self.DEFAULT_CONFIG_NAME:
            print(f'Warning: Cannot delete the default configuration')
            return False
        
        # Switch to default if deleting current config
        if config_name == self.current_config_name:
            self.switch_config(self.DEFAULT_CONFIG_NAME)
        
        config_path = self._get_config_path(config_name)
        try:
            if os.path.exists(config_path):
                os.remove(config_path)
                return True
            return False
        except Exception as e:
            print(f'Error: Could not delete config '{config_name}': {e}')
            return False
    
    def get_config_info(self, config_name: str) -> Optional[Dict[str, str]]:
        '''
        Get metadata about a configuration.
        
        Args:
            config_name: Name of the config
            
        Returns:
            Dict with config metadata, or None if config doesn't exist
        '''
        config_data = self.load_config(config_name)
        if config_data:
            return {
                'name': config_data.get('config_name', config_name),
                'description': config_data.get('description', 'No description available'),
                'version': config_data.get('version', '1.0.0')
            }
        return None


# Global config manager instance
config_manager = ConfigManager()


def get_current_config() -> Dict[str, Any]:
    '''Convenience function to get the current configuration.'''
    return config_manager.get_current_config()


def initialize_config_system():
    '''Initialize the config system on first run.'''
    created_default = config_manager.create_default_config_if_needed()
    if created_default:
        print('Created default configuration file')
    return created_default