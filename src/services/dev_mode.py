'''
Developer Mode System for P(Doom)

Provides centralized control for development features including verbose logging,
debug tools, and development UI indicators.
'''

import os
import json
from typing import Optional, Dict, Any
from src.services.verbose_logging import init_verbose_logging, LogLevel, is_logging_enabled


class DevModeManager:
    '''Manages developer mode state and features across the application.'''
    
    def __init__(self):
        self.dev_mode_enabled = False
        self.verbose_logging_enabled = False
        self.debug_console_enabled = True  # Debug console is separate from dev mode
        self.dev_config_file = 'dev_mode.json'
        self._load_dev_config()
    
    def _load_dev_config(self):
        '''Load dev mode configuration from file if it exists.'''
        if os.path.exists(self.dev_config_file):
            try:
                with open(self.dev_config_file, 'r') as f:
                    config = json.load(f)
                    self.dev_mode_enabled = config.get('dev_mode_enabled', False)
                    self.verbose_logging_enabled = config.get('verbose_logging_enabled', False)
                    self.debug_console_enabled = config.get('debug_console_enabled', True)
            except Exception:
                # Use defaults if config file is corrupted
                pass
    
    def _save_dev_config(self):
        '''Save current dev mode configuration to file.'''
        config = {
            'dev_mode_enabled': self.dev_mode_enabled,
            'verbose_logging_enabled': self.verbose_logging_enabled,
            'debug_console_enabled': self.debug_console_enabled
        }
        try:
            with open(self.dev_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass  # Fail silently if we can't save
    
    def toggle_dev_mode(self) -> bool:
        '''Toggle developer mode on/off. Returns new state.'''
        self.dev_mode_enabled = not self.dev_mode_enabled
        
        # When enabling dev mode, also enable verbose logging by default
        if self.dev_mode_enabled:
            self.verbose_logging_enabled = True
        
        self._save_dev_config()
        return self.dev_mode_enabled
    
    def toggle_verbose_logging(self) -> bool:
        '''Toggle verbose logging on/off. Returns new state.'''
        self.verbose_logging_enabled = not self.verbose_logging_enabled
        self._save_dev_config()
        return self.verbose_logging_enabled
    
    def is_dev_mode_enabled(self) -> bool:
        '''Check if developer mode is currently enabled.'''
        return self.dev_mode_enabled
    
    def is_verbose_logging_enabled(self) -> bool:
        '''Check if verbose logging is currently enabled.'''
        return self.verbose_logging_enabled
    
    def initialize_verbose_logging(self, game_seed: str):
        '''Initialize verbose logging system if enabled.'''
        if self.verbose_logging_enabled:
            if not is_logging_enabled():
                log_level = LogLevel.DEBUG if self.dev_mode_enabled else LogLevel.VERBOSE
                init_verbose_logging(
                    game_seed=game_seed,
                    log_level=log_level,
                    enable_human_readable=True,
                    enable_json_export=True
                )
    
    def get_dev_status_text(self) -> str:
        '''Get text to display in dev mode indicator.'''
        if not self.dev_mode_enabled:
            return ''
        
        status_parts = ['DEV']
        if self.verbose_logging_enabled:
            status_parts.append('VERBOSE')
        if is_logging_enabled():
            status_parts.append('LOGGING')
        
        return ' | '.join(status_parts)
    
    def get_dev_tools_available(self) -> Dict[str, Any]:
        '''Get list of available dev tools and their status.'''
        return {
            'screenshot': {
                'name': 'Take Screenshot',
                'hotkey': 'F9',
                'description': 'Save current screen to screenshots/ directory',
                'available': True
            },
            'debug_console': {
                'name': 'Debug Console',
                'hotkey': 'Backtick (`)',
                'description': 'Toggle real-time debug information overlay',
                'available': self.debug_console_enabled
            },
            'bug_report': {
                'name': 'Bug Report',
                'hotkey': 'F11',
                'description': 'Open bug report form with system info',
                'available': True
            },
            'export_logs': {
                'name': 'Export Logs',
                'hotkey': 'Ctrl+L',
                'description': 'Export verbose logs to JSON file',
                'available': self.verbose_logging_enabled and is_logging_enabled()
            },
            'verbose_logging': {
                'name': 'Toggle Verbose Logging',
                'hotkey': 'Ctrl+V',
                'description': 'Enable/disable detailed game logging',
                'available': True,
                'status': 'ON' if self.verbose_logging_enabled else 'OFF'
            }
        }


# Global dev mode manager instance
_dev_mode_manager: Optional[DevModeManager] = None


def get_dev_mode_manager() -> DevModeManager:
    '''Get the global dev mode manager instance.'''
    global _dev_mode_manager
    if _dev_mode_manager is None:
        _dev_mode_manager = DevModeManager()
    return _dev_mode_manager


def is_dev_mode_enabled() -> bool:
    '''Quick check if dev mode is enabled.'''
    return get_dev_mode_manager().is_dev_mode_enabled()


def toggle_dev_mode() -> bool:
    '''Quick toggle for dev mode.'''
    return get_dev_mode_manager().toggle_dev_mode()


def get_dev_status_text() -> str:
    '''Quick access to dev status text.'''
    return get_dev_mode_manager().get_dev_status_text()
