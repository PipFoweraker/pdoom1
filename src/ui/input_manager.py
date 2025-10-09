'''
Input Manager - Consolidated keyboard and mouse input handling

This module consolidates the fragmented input handling that was scattered throughout main.py,
providing a clean event pipeline that prevents duplicate processing and infinite loops.
'''

import pygame
from typing import Optional, Dict, Any, Callable


class InputManager:
    '''
    Manages all input events with proper event consumption to prevent duplicate processing.
    
    This replaces the fragmented keyboard handling that was causing freezes when rapidly
    pressing keys like Enter.
    '''
    
    def __init__(self):
        '''Initialize the input manager with empty handler registry.'''
        self.handlers: Dict[str, Dict[int, Callable]] = {
            'global': {},      # Global handlers (F10 dev mode, etc.)
            'state': {},       # State-specific handlers 
            'game': {}         # Game-specific handlers
        }
        
        # Track whether an event was consumed to prevent double processing
        self.event_consumed = False
        
    def register_global_handler(self, key: int, handler: Callable) -> None:
        '''Register a global key handler that works in all states.'''
        self.handlers['global'][key] = handler
        
    def register_state_handler(self, key: int, handler: Callable) -> None:
        '''Register a state-specific key handler.'''
        self.handlers['state'][key] = handler
        
    def register_game_handler(self, key: int, handler: Callable) -> None:
        '''Register a game-specific key handler.'''
        self.handlers['game'][key] = handler
        
    def handle_keyboard_event(self, event: pygame.event.Event, current_state: str, game_state=None) -> bool:
        '''
        Handle keyboard events with proper consumption tracking.
        
        Args:
            event: The pygame keyboard event
            current_state: Current game state (main_menu, game, etc.)
            game_state: Current game state object (if in game)
            
        Returns:
            True if the event was consumed, False otherwise
        '''
        if event.type != pygame.KEYDOWN:
            return False
            
        self.event_consumed = False
        key = event.key
        
        # 1. Global handlers first (F10 dev mode, help, etc.)
        if key in self.handlers['global']:
            self.event_consumed = self.handlers['global'][key](event, current_state, game_state)
            if self.event_consumed:
                return True
                
        # 2. State-specific handlers
        if not self.event_consumed and key in self.handlers['state']:
            self.event_consumed = self.handlers['state'][key](event, current_state, game_state)
            if self.event_consumed:
                return True
                
        # 3. Game-specific handlers (only if in game state)
        if not self.event_consumed and current_state == 'game' and key in self.handlers['game']:
            self.event_consumed = self.handlers['game'][key](event, current_state, game_state)
            if self.event_consumed:
                return True
                
        return self.event_consumed
        
    def clear_handlers(self) -> None:
        '''Clear all registered handlers.'''
        for handler_type in self.handlers:
            self.handlers[handler_type].clear()


# Global input manager instance
input_manager = InputManager()


def handle_dev_mode_toggle(event: pygame.event.Event, current_state: str, game_state=None) -> bool:
    '''
    Handle F10 dev mode toggle - works in all states.
    
    Returns:
        True if event was consumed
    '''
    try:
        from src.services.dev_mode import toggle_dev_mode, get_dev_mode_manager
        new_state = toggle_dev_mode()
        status_msg = 'DEV MODE ON' if new_state else 'DEV MODE OFF'
        
        # Initialize verbose logging if DEV MODE was enabled
        if new_state and game_state:
            dev_manager = get_dev_mode_manager()
            dev_manager.initialize_verbose_logging(game_state.seed)
            if dev_manager.is_verbose_logging_enabled():
                status_msg += ' | VERBOSE LOGGING ON'
        
        # Show message in appropriate context
        if current_state == 'game' and game_state:
            game_state.add_message(f'System: {status_msg} (F10)')
            if hasattr(game_state, 'sound_manager'):
                game_state.sound_manager.play_sound('ui_accept')
                
        return True  # Event consumed
        
    except ImportError:
        return False  # Event not consumed if dev_mode unavailable


def handle_help_key(event: pygame.event.Event, current_state: str, game_state=None) -> bool:
    '''
    Handle H key for help - works in game state.
    
    Returns:
        True if event was consumed
    '''
    if current_state == 'game':
        # This would need to be implemented with proper overlay handling
        # For now, just return True to indicate we consumed it
        return True
    return False


# Register default global handlers
input_manager.register_global_handler(pygame.K_F10, handle_dev_mode_toggle)
input_manager.register_game_handler(pygame.K_h, handle_help_key)
