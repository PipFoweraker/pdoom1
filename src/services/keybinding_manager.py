"""
Keybinding management system for P(Doom).

Provides customizable keybindings with persistent storage and default configurations.
Supports remapping of game actions and menu navigation while maintaining compatibility.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Try to import pygame, fallback to dummy values for CI/testing environments
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    # Define dummy pygame constants for testing environments
    class DummyPygame:
        K_1 = 49
        K_2 = 50
        K_3 = 51
        K_4 = 52
        K_5 = 53
        K_6 = 54
        K_7 = 55
        K_8 = 56
        K_9 = 57
        K_0 = 48
        K_SPACE = 32
        K_ESCAPE = 27
        K_RETURN = 13
        K_UP = 273
        K_DOWN = 274
        K_LEFT = 276
        K_RIGHT = 275
        K_h = 104
        K_F5 = 292
        K_F9 = 296
        K_F10 = 297
        K_F11 = 298
        K_F12 = 299
        K_a = 97
        K_z = 122
        K_TAB = 9
        K_LALT = 308
        K_RALT = 307
        K_LCTRL = 306
        K_RCTRL = 305
    
    pygame = DummyPygame()

class KeybindingManager:
    """
    Manages customizable keybindings with persistent storage.
    
    Features:
    - Default keybinding configurations
    - Persistent storage in local config file (git-ignored)
    - Runtime keybinding modification
    - Conflict detection and resolution
    - Compatible with existing keyboard shortcut system
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize keybinding manager with config file."""
        self.config_path = config_path or "keybindings.json"
        self.keybindings = self._load_default_keybindings()
        self._load_user_keybindings()
    
    def _load_default_keybindings(self) -> Dict[str, int]:
        """Load default keybinding configuration."""
        return {
            # Action buttons (1-9 keys)
            "action_1": pygame.K_1,
            "action_2": pygame.K_2, 
            "action_3": pygame.K_3,
            "action_4": pygame.K_4,
            "action_5": pygame.K_5,
            "action_6": pygame.K_6,
            "action_7": pygame.K_7,
            "action_8": pygame.K_8,
            "action_9": pygame.K_9,
            
            # Game controls
            "end_turn": pygame.K_SPACE,
            "help_guide": pygame.K_h,
            "quit_to_menu": pygame.K_ESCAPE,
            
            # UI navigation
            "scroll_up": pygame.K_UP,
            "scroll_down": pygame.K_DOWN,
            "scroll_left": pygame.K_LEFT,
            "scroll_right": pygame.K_RIGHT,
            
            # Menu navigation
            "menu_up": pygame.K_UP,
            "menu_down": pygame.K_DOWN,
            "menu_select": pygame.K_RETURN,
            "menu_back": pygame.K_ESCAPE,
            
            # Quick access (F keys for common actions)
            "quick_save": pygame.K_F5,
            "quick_load": pygame.K_F9,
            "toggle_sound": pygame.K_F10,
            "fullscreen": pygame.K_F11,
            "screenshot": pygame.K_F12,
        }
    
    def _load_user_keybindings(self) -> None:
        """Load user customizations from config file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_bindings = json.load(f)
                    # Merge user customizations with defaults
                    self.keybindings.update(user_bindings)
        except Exception:
            # If loading fails, stick with defaults
            pass
    
    def save_keybindings(self) -> bool:
        """Save current keybindings to config file."""
        try:
            # Only save non-default bindings to keep file clean
            defaults = self._load_default_keybindings()
            user_customizations = {}
            
            for action, key in self.keybindings.items():
                if action not in defaults or defaults[action] != key:
                    user_customizations[action] = key
            
            with open(self.config_path, 'w') as f:
                json.dump(user_customizations, f, indent=2)
            return True
        except Exception:
            return False
    
    def get_key_for_action(self, action: str) -> Optional[int]:
        """Get pygame key constant for an action."""
        return self.keybindings.get(action)
    
    def get_action_for_key(self, key: int) -> Optional[str]:
        """Get action name for a pygame key constant."""
        for action, bound_key in self.keybindings.items():
            if bound_key == key:
                return action
        return None
    
    def set_keybinding(self, action: str, key: int) -> bool:
        """
        Set keybinding for an action.
        
        Args:
            action: Action name (e.g., "action_1", "end_turn")
            key: pygame key constant
            
        Returns:
            bool: True if binding was successful
        """
        if action in self.keybindings:
            # Check for conflicts with protected keys
            if self._is_protected_key(key):
                return False
            
            # Remove existing binding for this key if any
            self._clear_key_binding(key)
            
            self.keybindings[action] = key
            return True
        return False
    
    def _is_protected_key(self, key: int) -> bool:
        """Check if a key is protected from remapping."""
        protected_keys = [
            pygame.K_TAB,  # UI navigation
            pygame.K_LALT, pygame.K_RALT,  # System shortcuts
            pygame.K_LCTRL, pygame.K_RCTRL,  # System shortcuts
        ]
        return key in protected_keys
    
    def _clear_key_binding(self, key: int) -> None:
        """Remove any existing binding for a key."""
        to_clear = []
        for action, bound_key in self.keybindings.items():
            if bound_key == key:
                to_clear.append(action)
        
        for action in to_clear:
            if action in self._load_default_keybindings():
                # Reset to default if it exists
                self.keybindings[action] = self._load_default_keybindings()[action]
    
    def get_action_display_key(self, action: str) -> str:
        """
        Get human-readable key name for display.
        
        Args:
            action: Action name
            
        Returns:
            str: Human-readable key name (e.g., "Space", "Esc", "1")
        """
        key = self.get_key_for_action(action)
        if key is None:
            return "?"
        
        # Map pygame keys to display names
        key_names = {
            pygame.K_SPACE: "Space",
            pygame.K_ESCAPE: "Esc",
            pygame.K_RETURN: "Enter",
            pygame.K_UP: "↑",
            pygame.K_DOWN: "↓",
            pygame.K_LEFT: "←", 
            pygame.K_RIGHT: "→",
            pygame.K_h: "H",
            pygame.K_F5: "F5",
            pygame.K_F9: "F9",
            pygame.K_F10: "F10",
            pygame.K_F11: "F11",
            pygame.K_F12: "F12",
        }
        
        if key in key_names:
            return key_names[key]
        
        # For number keys
        if pygame.K_0 <= key <= pygame.K_9:
            return str(key - pygame.K_0)
        
        # For letter keys
        if pygame.K_a <= key <= pygame.K_z:
            return chr(key).upper()
        
        return f"Key{key}"
    
    def get_conflicts(self, action: str, new_key: int) -> List[str]:
        """
        Get list of actions that would conflict with a new keybinding.
        
        Args:
            action: Action to check
            new_key: Proposed new key
            
        Returns:
            List of conflicting action names
        """
        conflicts = []
        for other_action, bound_key in self.keybindings.items():
            if other_action != action and bound_key == new_key:
                conflicts.append(other_action)
        return conflicts
    
    def reset_to_defaults(self) -> None:
        """Reset all keybindings to defaults."""
        self.keybindings = self._load_default_keybindings()
    
    def get_action_number_key(self, action_index: int) -> Optional[int]:
        """
        Get keybinding for action by index (0-8 for actions 1-9).
        
        Args:
            action_index: 0-based action index
            
        Returns:
            pygame key constant or None
        """
        if 0 <= action_index <= 8:
            action_name = f"action_{action_index + 1}"
            return self.get_key_for_action(action_name)
        return None
    
    def is_action_key(self, key: int, action_index: int) -> bool:
        """
        Check if a key matches an action's keybinding.
        
        Args:
            key: pygame key constant
            action_index: 0-based action index
            
        Returns:
            bool: True if key matches the action's binding
        """
        action_key = self.get_action_number_key(action_index)
        return action_key is not None and action_key == key


# Global keybinding manager instance
keybinding_manager = KeybindingManager()

# Convenience functions for backwards compatibility
def get_action_key_display(action_index: int) -> str:
    """Get display string for action key (e.g., "1", "Q", "Space")."""
    if 0 <= action_index <= 8:
        action_name = f"action_{action_index + 1}"
        return keybinding_manager.get_action_display_key(action_name)
    return "?"

def is_action_key_pressed(key: int, action_index: int) -> bool:
    """Check if pressed key matches action's keybinding."""
    return keybinding_manager.is_action_key(key, action_index)

def get_end_turn_key() -> int:
    """Get keybinding for end turn action."""
    return keybinding_manager.get_key_for_action("end_turn") or pygame.K_SPACE

def get_end_turn_key_display() -> str:
    """Get display string for end turn key."""
    return keybinding_manager.get_action_display_key("end_turn")