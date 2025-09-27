"""
Dialog State Management System - Extracted from main.py monolith

This module standardizes dialog state handling across the game, eliminating
None vs False confusion and providing centralized modal blocking logic.

Key functionality:
- Modal dialog state tracking
- Blocking condition evaluation  
- Consistent dialog lifecycle management
- State validation and cleanup
- Integration with InputEventManager

Following patterns established in:
- DialogManager for basic dialog operations
- TurnManager for state management patterns
- MediaPRSystemManager for extraction architecture
"""

from typing import List, Optional, Set, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from src.core.game_state import GameState


class DialogType(Enum):
    """Enumeration of all dialog types in the game."""
    HIRING = "hiring"
    INTELLIGENCE = "intelligence"  
    FUNDRAISING = "fundraising"
    RESEARCH = "research"
    MEDIA = "media"
    TECHNICAL_DEBT = "technical_debt"
    HELP = "help"
    TUTORIAL = "tutorial"


class ModalState(Enum):
    """Modal dialog states."""
    CLOSED = "closed"
    OPEN = "open"
    TRANSITIONING = "transitioning"


class DialogStateManager:
    """
    Centralized dialog state management for P(Doom).
    
    Provides consistent tracking and validation of all modal dialogs,
    eliminating the None vs False confusion that caused blocking issues.
    """
    
    def __init__(self, game_state: 'GameState') -> None:
        """Initialize the dialog state manager.
        
        Args:
            game_state: Reference to the main game state
        """
        self.game_state = game_state
        
        # Track active dialogs
        self._active_dialogs: Set[DialogType] = set()
        
        # Modal state tracking
        self._modal_state = ModalState.CLOSED
        self._blocking_dialog: Optional[DialogType] = None
        
        # State validation cache (for performance)
        self._last_validation_time = 0
        self._cached_blocking_state = False
        self._validation_timeout = 100  # milliseconds
    
    def is_dialog_active(self, dialog_type: DialogType) -> bool:
        """
        Check if a specific dialog type is currently active.
        
        Args:
            dialog_type: Type of dialog to check
            
        Returns:
            True if dialog is active, False otherwise
        """
        if dialog_type == DialogType.HELP:
            # Help dialogs are managed differently (first_time_help_content)
            return self._check_help_dialog_active()
        elif dialog_type == DialogType.TUTORIAL:
            # Tutorial state is managed by onboarding system
            return self._check_tutorial_active()
        else:
            # Standard game dialogs
            return self._check_game_dialog_active(dialog_type)
    
    def get_active_dialogs(self) -> Set[DialogType]:
        """Get set of all currently active dialogs."""
        self._refresh_active_dialogs()
        return self._active_dialogs.copy()
    
    def has_blocking_dialog(self) -> bool:
        """Check if any blocking (modal) dialog is currently active."""
        # Always refresh for now (we can optimize caching later)
        self._refresh_active_dialogs()
        return len(self._active_dialogs) > 0
    
    def get_blocking_dialog(self) -> Optional[DialogType]:
        """Get the currently blocking dialog (if any)."""
        self._refresh_active_dialogs()
        return self._blocking_dialog
    
    def get_blocking_feedback_message(self) -> str:
        """Get appropriate feedback message for the blocking dialog."""
        blocking_dialog = self.get_blocking_dialog()
        
        if blocking_dialog == DialogType.HELP:
            return "Close the help popup first (ESC or click X)"
        elif blocking_dialog == DialogType.TUTORIAL:
            return "Complete or skip the tutorial step first"
        elif blocking_dialog == DialogType.HIRING:
            return "Close the hiring dialog first (ESC or click outside)"
        elif blocking_dialog == DialogType.FUNDRAISING:
            return "Close the funding dialog first (ESC or click outside)"
        elif blocking_dialog == DialogType.RESEARCH:
            return "Close the research dialog first (ESC or click outside)"
        elif blocking_dialog == DialogType.INTELLIGENCE:
            return "Close the intelligence dialog first (ESC or click outside)"
        elif blocking_dialog == DialogType.MEDIA:
            return "Close the media dialog first (ESC or click outside)"
        elif blocking_dialog == DialogType.TECHNICAL_DEBT:
            return "Close the technical debt dialog first (ESC or click outside)"
        else:
            return "Close the open dialog first"
    
    def dismiss_dialog(self, dialog_type: DialogType) -> bool:
        """
        Dismiss a specific dialog type.
        
        Args:
            dialog_type: Type of dialog to dismiss
            
        Returns:
            True if dialog was successfully dismissed, False otherwise
        """
        if dialog_type == DialogType.HELP:
            return self._dismiss_help_dialog()
        elif dialog_type == DialogType.TUTORIAL:
            return self._dismiss_tutorial()
        else:
            return self._dismiss_game_dialog(dialog_type)
    
    def dismiss_all_dialogs(self) -> int:
        """
        Dismiss all active dialogs.
        
        Returns:
            Number of dialogs that were dismissed
        """
        active_dialogs = self.get_active_dialogs()
        dismissed_count = 0
        
        for dialog_type in active_dialogs:
            if self.dismiss_dialog(dialog_type):
                dismissed_count += 1
        
        # Clear cache
        self._refresh_active_dialogs()
        
        return dismissed_count
    
    def validate_dialog_states(self) -> List[str]:
        """
        Validate all dialog states for debugging.
        
        Returns:
            List of validation issues found
        """
        issues: List[str] = []
        
        # Check for inconsistent dialog states
        for dialog_type in DialogType:
            is_active = self.is_dialog_active(dialog_type)
            
            if dialog_type in self._active_dialogs and not is_active:
                issues.append(f"Dialog {dialog_type.value} marked as active but not actually active")
            elif dialog_type not in self._active_dialogs and is_active:
                issues.append(f"Dialog {dialog_type.value} is active but not marked as active")
        
        # Check for None vs False issues
        game_dialog_attrs = [
            'pending_hiring_dialog',
            'pending_fundraising_dialog', 
            'pending_research_dialog',
            'pending_intelligence_dialog',
            'pending_media_dialog',
            'pending_technical_debt_dialog'
        ]
        
        for attr in game_dialog_attrs:
            if hasattr(self.game_state, attr):
                value = getattr(self.game_state, attr)
                if value is False:  # Should be None instead of False
                    issues.append(f"Dialog attribute {attr} is False, should be None")
        
        return issues
    
    def emergency_cleanup(self) -> int:
        """
        Emergency cleanup of stuck dialog states.
        
        Returns:
            Number of states that were cleaned up
        """
        cleanup_count = 0
        
        # Reset all game dialog attributes to None (not False)
        game_dialog_attrs = [
            'pending_hiring_dialog',
            'pending_fundraising_dialog',
            'pending_research_dialog', 
            'pending_intelligence_dialog',
            'pending_media_dialog',
            'pending_technical_debt_dialog'
        ]
        
        for attr in game_dialog_attrs:
            if hasattr(self.game_state, attr):
                current_value = getattr(self.game_state, attr)
                # Only count non-None and non-False values as needing cleanup
                if current_value is not None and current_value is not False:
                    setattr(self.game_state, attr, None)
                    cleanup_count += 1
                elif current_value is False:
                    # Fix False values to None but don't count as cleanup
                    setattr(self.game_state, attr, None)
        
        # Clear active dialogs cache
        self._active_dialogs.clear()
        self._modal_state = ModalState.CLOSED
        self._blocking_dialog = None
        
        return cleanup_count
    
    def _refresh_active_dialogs(self) -> None:
        """Refresh the set of active dialogs by checking current state."""
        self._active_dialogs.clear()
        
        # Check each dialog type
        for dialog_type in DialogType:
            if self.is_dialog_active(dialog_type):
                self._active_dialogs.add(dialog_type)
        
        # Update modal state
        if self._active_dialogs:
            self._modal_state = ModalState.OPEN
            # Calculate blocking dialog directly without recursion
            self._blocking_dialog = self._calculate_blocking_dialog()
        else:
            self._modal_state = ModalState.CLOSED
            self._blocking_dialog = None
    
    def _calculate_blocking_dialog(self) -> Optional[DialogType]:
        """Calculate which dialog is blocking (highest priority) without recursion."""
        # Priority order for blocking dialogs
        blocking_priority = [
            DialogType.TUTORIAL,      # Tutorial blocks everything
            DialogType.HELP,          # Help popups block game actions
            DialogType.HIRING,        # Game dialogs block end turn
            DialogType.FUNDRAISING,
            DialogType.RESEARCH,
            DialogType.INTELLIGENCE,
            DialogType.MEDIA,
            DialogType.TECHNICAL_DEBT
        ]
        
        for dialog_type in blocking_priority:
            if dialog_type in self._active_dialogs:
                return dialog_type
        
        return None
    
    def _check_help_dialog_active(self) -> bool:
        """Check if help dialog is active (external state)."""
        # This needs to be passed in from main.py since help state 
        # is managed there as first_time_help_content
        return False  # Placeholder - will be updated during integration
    
    def _check_tutorial_active(self) -> bool:
        """Check if tutorial is active via onboarding system."""
        try:
            from src.features.onboarding import onboarding
            return getattr(onboarding, 'show_tutorial_overlay', False)
        except ImportError:
            return False
    
    def _check_game_dialog_active(self, dialog_type: DialogType) -> bool:
        """Check if a game dialog is active."""
        dialog_mapping = {
            DialogType.HIRING: 'pending_hiring_dialog',
            DialogType.FUNDRAISING: 'pending_fundraising_dialog',
            DialogType.RESEARCH: 'pending_research_dialog',
            DialogType.INTELLIGENCE: 'pending_intelligence_dialog',
            DialogType.MEDIA: 'pending_media_dialog',
            DialogType.TECHNICAL_DEBT: 'pending_technical_debt_dialog'
        }
        
        attr_name = dialog_mapping.get(dialog_type)
        if attr_name and hasattr(self.game_state, attr_name):
            value = getattr(self.game_state, attr_name)
            # Consider both None and False as inactive (fixes None vs False confusion)
            return value is not None and value is not False
        
        return False
    
    def _dismiss_help_dialog(self) -> bool:
        """Dismiss help dialog (needs integration with main.py)."""
        # This will be handled during integration since help state
        # is managed in main.py
        return False  # Placeholder
    
    def _dismiss_tutorial(self) -> bool:
        """Dismiss tutorial via onboarding system."""
        try:
            from src.features.onboarding import onboarding
            if getattr(onboarding, 'show_tutorial_overlay', False):
                onboarding.dismiss_tutorial()
                return True
        except (ImportError, AttributeError):
            pass
        return False
    
    def _dismiss_game_dialog(self, dialog_type: DialogType) -> bool:
        """Dismiss a game dialog using the appropriate method."""
        dialog_methods = {
            DialogType.HIRING: 'dismiss_hiring_dialog',
            DialogType.FUNDRAISING: 'dismiss_fundraising_dialog',
            DialogType.RESEARCH: 'dismiss_research_dialog',
            DialogType.INTELLIGENCE: 'dismiss_intelligence_dialog'
        }
        
        # First check if dialog is actually active
        if not self.is_dialog_active(dialog_type):
            return False
        
        method_name = dialog_methods.get(dialog_type)
        if method_name and hasattr(self.game_state, method_name):
            method = getattr(self.game_state, method_name)
            try:
                method()
                return True
            except Exception:
                return False
        
        return False
    
    # Context manager support for dialog state tracking
    def __enter__(self):
        """Enter context for dialog state tracking."""
        self._refresh_active_dialogs()
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[object]) -> None:
        """Exit context and validate state consistency."""
        if exc_type is None:
            # No exception - validate states are consistent
            issues = self.validate_dialog_states()
            if issues:
                # Log validation issues (could be added to game messages)
                pass