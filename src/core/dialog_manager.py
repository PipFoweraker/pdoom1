"""
Dialog Management Module

Extracted from game_state.py monolith for better maintainability.
Handles all dialog dismissal and state management operations.

This module reduces the game_state.py monolith by centralizing dialog operations
that were previously scattered throughout the main class.
"""

from typing import Any, Optional


class DialogManager:
    """
    Centralized dialog management system for P(Doom) game dialogs.
    
    Handles dismissal, validation, and state management for all dialog types
    including hiring, intelligence, media, technical debt, fundraising, and research.
    """
    
    # Valid dialog types that can be managed
    VALID_DIALOG_TYPES = {
        'hiring', 'intelligence', 'media', 'technical_debt', 
        'fundraising', 'research'
    }
    
    @staticmethod
    def dismiss_dialog(game_state: Any, dialog_type: str) -> bool:
        """
        Universal dialog dismiss function for all dialog types.
        
        Args:
            game_state: The game state object containing dialog attributes
            dialog_type: Type of dialog to dismiss ('hiring', 'intelligence', 'media', 
                        'technical_debt', 'fundraising', 'research')
                        
        Returns:
            bool: True if dialog was successfully dismissed, False if invalid type or not found
        """
        if dialog_type not in DialogManager.VALID_DIALOG_TYPES:
            return False
            
        dialog_attr = f'pending_{dialog_type}_dialog'
        if hasattr(game_state, dialog_attr):
            current_value = getattr(game_state, dialog_attr)
            if current_value is not None:
                setattr(game_state, dialog_attr, None)
                return True
        return False
    
    @staticmethod
    def has_pending_dialog(game_state: Any, dialog_type: str) -> bool:
        """
        Check if a specific dialog type is currently pending.
        
        Args:
            game_state: The game state object containing dialog attributes
            dialog_type: Type of dialog to check
            
        Returns:
            bool: True if the dialog is pending, False otherwise
        """
        if dialog_type not in DialogManager.VALID_DIALOG_TYPES:
            return False
            
        dialog_attr = f'pending_{dialog_type}_dialog'
        return hasattr(game_state, dialog_attr) and getattr(game_state, dialog_attr) is not None
    
    @staticmethod
    def get_pending_dialog(game_state: Any, dialog_type: str) -> Optional[Any]:
        """
        Get the pending dialog data for a specific dialog type.
        
        Args:
            game_state: The game state object containing dialog attributes
            dialog_type: Type of dialog to retrieve
            
        Returns:
            The dialog data if pending, None otherwise
        """
        if dialog_type not in DialogManager.VALID_DIALOG_TYPES:
            return None
            
        dialog_attr = f'pending_{dialog_type}_dialog'
        if hasattr(game_state, dialog_attr):
            return getattr(game_state, dialog_attr)
        return None
    
    @staticmethod
    def dismiss_all_dialogs(game_state: Any) -> int:
        """
        Dismiss all pending dialogs.
        
        Args:
            game_state: The game state object containing dialog attributes
            
        Returns:
            int: Number of dialogs that were dismissed
        """
        dismissed_count = 0
        for dialog_type in DialogManager.VALID_DIALOG_TYPES:
            if DialogManager.dismiss_dialog(game_state, dialog_type):
                dismissed_count += 1
        return dismissed_count
    
    @staticmethod
    def get_active_dialog_types(game_state: Any) -> list[str]:
        """
        Get a list of all currently active dialog types.
        
        Args:
            game_state: The game state object containing dialog attributes
            
        Returns:
            list[str]: List of active dialog type names
        """
        active_dialogs = []
        for dialog_type in DialogManager.VALID_DIALOG_TYPES:
            if DialogManager.has_pending_dialog(game_state, dialog_type):
                active_dialogs.append(dialog_type)
        return active_dialogs
    
    @staticmethod
    def has_any_pending_dialog(game_state: Any) -> bool:
        """
        Check if any dialog is currently pending.
        
        Args:
            game_state: The game state object containing dialog attributes
            
        Returns:
            bool: True if any dialog is pending, False otherwise
        """
        return len(DialogManager.get_active_dialog_types(game_state)) > 0