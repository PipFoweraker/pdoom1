'''
Game Configuration Manager for P(Doom)

This module handles the creation, management, and sharing of custom game configurations.
It integrates with the existing config system but focuses on gameplay parameters that
players would want to customize and share with others.

Key features:
- Create custom game configurations with meaningful names
- Share configs + seeds for community challenges  
- Template system for easy config creation
- Validation of configuration parameters
'''

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from src.services.config_manager import config_manager
from src.services.version import get_display_version


class GameConfigManager:
    '''Manages game configurations specifically for player customization and sharing.'''
    
    def __init__(self):
        self.configs_dir = 'configs'
        self.user_configs_dir = os.path.join(self.configs_dir, 'user')
        self.ensure_directories_exist()
    
    def ensure_directories_exist(self):
        '''Ensure required directories exist.'''
        os.makedirs(self.configs_dir, exist_ok=True)
        os.makedirs(self.user_configs_dir, exist_ok=True)
    
    def get_available_configs(self) -> List[Dict[str, Any]]:
        '''
        Get list of available game configurations.
        
        Returns:
            List of config info dictionaries with name, description, type, etc.
        '''
        configs = []
        
        # Add built-in configs
        builtin_configs = config_manager.list_available_configs()
        for config_name in builtin_configs:
            config_data = config_manager.load_config(config_name)
            if config_data:
                configs.append({
                    'name': config_name,
                    'display_name': config_data.get('config_name', config_name),
                    'description': config_data.get('description', 'No description'),
                    'type': 'builtin',
                    'file_path': os.path.join(self.configs_dir, f'{config_name}.json')
                })
        
        # Add user configs
        if os.path.exists(self.user_configs_dir):
            for filename in os.listdir(self.user_configs_dir):
                if filename.endswith('.json'):
                    config_name = filename[:-5]  # Remove .json
                    try:
                        with open(os.path.join(self.user_configs_dir, filename), 'r') as f:
                            config_data = json.load(f)
                        configs.append({
                            'name': config_name,
                            'display_name': config_data.get('config_name', config_name),
                            'description': config_data.get('description', 'User-created configuration'),
                            'type': 'user',
                            'file_path': os.path.join(self.user_configs_dir, filename)
                        })
                    except (json.JSONDecodeError, IOError):
                        # Skip invalid config files
                        continue
        
        return configs
    
    def create_config_from_template(self, template_name: str = 'default') -> Dict[str, Any]:
        '''
        Create a new configuration based on a template.
        
        Args:
            template_name: Name of template to base config on
            
        Returns:
            Dictionary with new config data
        '''
        # Get base template
        if template_name in config_manager.list_available_configs():
            base_config = config_manager.get_config(template_name).copy()
        else:
            base_config = config_manager.get_default_config().copy()
        
        # Modify for user customization
        base_config.update({
            'config_name': 'Custom Configuration',
            'description': 'Player-created custom configuration',
            'version': get_display_version(),
            'created_date': datetime.now().isoformat(),
            'created_by': 'player',
            'is_custom': True
        })
        
        return base_config
    
    def save_user_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        '''
        Save a user configuration to the user configs directory.
        
        Args:
            config_name: Name for the configuration file
            config_data: Configuration data dictionary
            
        Returns:
            True if saved successfully, False otherwise
        '''
        try:
            # Sanitize config name for filename
            safe_name = self._sanitize_filename(config_name)
            file_path = os.path.join(self.user_configs_dir, f'{safe_name}.json')
            
            # Add metadata
            config_data['config_name'] = config_name
            config_data['last_modified'] = datetime.now().isoformat()
            config_data['is_custom'] = True
            
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
        except (IOError, json.JSONEncodeError):
            return False
    
    def load_user_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        '''
        Load a user configuration.
        
        Args:
            config_name: Name of configuration to load
            
        Returns:
            Configuration data if found, None otherwise
        '''
        safe_name = self._sanitize_filename(config_name)
        file_path = os.path.join(self.user_configs_dir, f'{safe_name}.json')
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None
    
    def delete_user_config(self, config_name: str) -> bool:
        '''
        Delete a user configuration.
        
        Args:
            config_name: Name of configuration to delete
            
        Returns:
            True if deleted successfully, False otherwise
        '''
        safe_name = self._sanitize_filename(config_name)
        file_path = os.path.join(self.user_configs_dir, f'{safe_name}.json')
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except IOError:
            pass
        
        return False
    
    def export_config_for_sharing(self, config_name: str, seed: str = None) -> Optional[Dict[str, Any]]:
        '''
        Export a configuration in a format suitable for sharing.
        
        Args:
            config_name: Name of configuration to export
            seed: Optional seed to include with config
            
        Returns:
            Shareable config package or None if config not found
        '''
        # Try user configs first, then built-in
        config_data = self.load_user_config(config_name)
        if not config_data:
            if config_name in config_manager.list_available_configs():
                config_data = config_manager.load_config(config_name)
            else:
                return None
        
        # Create shareable package
        package = {
            'pdoom_config_package': True,
            'version': get_display_version(),
            'created_date': datetime.now().isoformat(),
            'config_name': config_data.get('config_name', config_name),
            'description': config_data.get('description', 'Shared configuration'),
            'config': config_data,
            'seed': seed,
            'sharing_info': {
                'instructions': 'Import this file in P(Doom) Game Config menu',
                'challenge': f'Can you beat this configuration with seed '{seed}'?' if seed else None
            }
        }
        
        return package
    
    def import_shared_config(self, package_data: Dict[str, Any]) -> Tuple[bool, str]:
        '''
        Import a shared configuration package.
        
        Args:
            package_data: Shared config package data
            
        Returns:
            Tuple of (success, message)
        '''
        try:
            # Validate package
            if not package_data.get('pdoom_config_package'):
                return False, 'Invalid configuration package format'
            
            config_data = package_data.get('config')
            if not config_data:
                return False, 'No configuration data found in package'
            
            # Generate unique name if needed
            base_name = package_data.get('config_name', 'Imported Config')
            config_name = self._generate_unique_config_name(base_name)
            
            # Modify config for import
            config_data['description'] = f'Imported: {config_data.get('description', '')}'
            config_data['imported_date'] = datetime.now().isoformat()
            
            # Save the config
            if self.save_user_config(config_name, config_data):
                seed_info = ''
                if package_data.get('seed'):
                    seed_info = f' with seed '{package_data['seed']}''
                return True, f'Configuration '{config_name}' imported successfully{seed_info}'
            else:
                return False, 'Failed to save imported configuration'
                
        except Exception as e:
            return False, f'Import error: {str(e)}'
    
    def get_config_templates(self) -> Dict[str, Dict[str, Any]]:
        '''
        Get available configuration templates for creating new configs.
        
        Returns:
            Dictionary of template configurations
        '''
        templates = {
            'standard': {
                'name': 'Standard Play',
                'description': 'Balanced gameplay for normal difficulty',
                'modifications': {
                    'starting_resources.money': 1000,
                    'starting_resources.staff': 2,
                    'starting_resources.doom': 25
                }
            },
            'hardcore': {
                'name': 'Hardcore Mode',
                'description': 'Challenging gameplay with limited resources',
                'modifications': {
                    'starting_resources.money': 500,
                    'starting_resources.staff': 1,
                    'starting_resources.doom': 35,
                    'gameplay.difficulty_modifier': 1.5
                }
            },
            'sandbox': {
                'name': 'Sandbox Mode', 
                'description': 'Relaxed gameplay for experimentation',
                'modifications': {
                    'starting_resources.money': 5000,
                    'starting_resources.staff': 5,
                    'starting_resources.doom': 10,
                    'gameplay.difficulty_modifier': 0.7
                }
            },
            'speedrun': {
                'name': 'Speedrun Setup',
                'description': 'Optimized for fast completion attempts',
                'modifications': {
                    'starting_resources.action_points': 5,
                    'action_points.base_ap_per_turn': 5,
                    'gameplay.event_frequency': 0.5
                }
            }
        }
        
        return templates
    
    def _sanitize_filename(self, filename: str) -> str:
        '''Sanitize a string for use as a filename.'''
        # Remove invalid characters and replace with underscores
        invalid_chars = '<>:'/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length and strip whitespace
        filename = filename.strip()[:50]
        
        # Ensure it's not empty
        if not filename:
            filename = 'config'
            
        return filename
    
    def _generate_unique_config_name(self, base_name: str) -> str:
        '''Generate a unique configuration name by appending numbers if needed.'''
        configs = self.get_available_configs()
        existing_names = {config['name'] for config in configs}
        
        if base_name not in existing_names:
            return base_name
        
        counter = 1
        while f'{base_name}_{counter}' in existing_names:
            counter += 1
        
        return f'{base_name}_{counter}'
    
    def validate_config(self, config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        '''
        Validate a configuration for correctness.
        
        Args:
            config_data: Configuration data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        '''
        errors = []
        
        # Check required sections
        required_sections = ['starting_resources', 'action_points', 'resource_limits']
        for section in required_sections:
            if section not in config_data:
                errors.append(f'Missing required section: {section}')
        
        # Validate starting resources
        if 'starting_resources' in config_data:
            resources = config_data['starting_resources']
            if resources.get('money', 0) < 0:
                errors.append('Starting money cannot be negative')
            if resources.get('staff', 0) < 1:
                errors.append('Starting staff must be at least 1')
            if not 0 <= resources.get('doom', 0) <= 100:
                errors.append('Starting doom must be between 0 and 100')
        
        # Validate action points
        if 'action_points' in config_data:
            ap = config_data['action_points']
            if ap.get('base_ap_per_turn', 0) < 1:
                errors.append('Base AP per turn must be at least 1')
            if ap.get('max_ap_per_turn', 0) < ap.get('base_ap_per_turn', 3):
                errors.append('Max AP per turn cannot be less than base AP')
        
        # Validate resource limits
        if 'resource_limits' in config_data:
            limits = config_data['resource_limits']
            if limits.get('max_doom', 100) < 50:
                errors.append('Max doom should be at least 50 for playability')
        
        return len(errors) == 0, errors


# Global instance
game_config_manager = GameConfigManager()
