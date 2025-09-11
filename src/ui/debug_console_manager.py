"""
Debug Console Manager for P(Doom)
Handles all debug console integration without polluting main game loop.
"""

import pygame
from typing import Optional


class DebugConsoleManager:
    """
    Manages debug console integration with the main game loop.
    Encapsulates all debug console logic to keep main.py clean.
    """
    
    def __init__(self):
        self._debug_console = None
        self._keybinding_manager = None
        self._initialized = False
    
    def _lazy_init(self):
        """Initialize debug console and keybinding manager on first use."""
        if self._initialized:
            return
            
        try:
            from src.ui.debug_console import debug_console
            self._debug_console = debug_console
        except ImportError:
            self._debug_console = None
            
        try:
            from src.services.keybinding_manager import keybinding_manager
            self._keybinding_manager = keybinding_manager
        except ImportError:
            self._keybinding_manager = None
            
        self._initialized = True
    
    def handle_keypress(self, key: int, game_state=None) -> bool:
        """
        Handle keypress for debug console.
        
        Args:
            key: Pygame key code
            game_state: Current game state (for sound effects)
            
        Returns:
            True if keypress was handled by debug console
        """
        self._lazy_init()
        
        if not self._debug_console:
            return False
            
        # Check if this key should toggle debug console
        should_handle = False
        
        if self._keybinding_manager:
            # Use keybinding system if available
            try:
                debug_key = self._keybinding_manager.get_key_for_action("debug_console")
                should_handle = (key == debug_key)
            except:
                # Fallback if keybinding lookup fails
                should_handle = (key == pygame.K_BACKQUOTE)
        else:
            # Fallback to hardcoded key if keybinding system unavailable
            should_handle = (key == pygame.K_BACKQUOTE)
        
        if should_handle:
            handled = self._debug_console.handle_keypress(key)
            if handled and game_state and hasattr(game_state, 'sound_manager'):
                game_state.sound_manager.play_sound('ui_select')
            return handled
            
        return False
    
    def handle_click(self, pos: tuple, screen_w: int, screen_h: int) -> bool:
        """
        Handle mouse click for debug console.
        
        Args:
            pos: Mouse position (x, y)
            screen_w: Screen width
            screen_h: Screen height
            
        Returns:
            True if click was handled by debug console
        """
        self._lazy_init()
        
        if not self._debug_console:
            return False
            
        return self._debug_console.handle_click(pos, screen_w, screen_h)
    
    def draw(self, screen: pygame.Surface, game_state, screen_w: int, screen_h: int):
        """
        Draw debug console overlay.
        
        Args:
            screen: Pygame surface to draw on
            game_state: Current game state
            screen_w: Screen width  
            screen_h: Screen height
        """
        self._lazy_init()
        
        if self._debug_console:
            self._debug_console.draw(screen, game_state, screen_w, screen_h)
    
    def is_available(self) -> bool:
        """Check if debug console is available."""
        self._lazy_init()
        return self._debug_console is not None
    
    def get_current_keybinding(self) -> str:
        """Get the current debug console keybinding for display."""
        self._lazy_init()
        
        if self._keybinding_manager:
            try:
                key_code = self._keybinding_manager.get_key_for_action("debug_console")
                # Convert key codes to readable names
                key_names = {
                    96: "`", 49: "1", 50: "2", 51: "3", 52: "4", 53: "5",
                    54: "6", 55: "7", 56: "8", 57: "9", 48: "0",
                    97: "A", 100: "D", 122: "Z", 120: "X", 99: "C"
                }
                return key_names.get(key_code, f"Key{key_code}")
            except:
                return "`"
        return "`"


# Global instance - created once, used throughout the application
debug_console_manager = DebugConsoleManager()
