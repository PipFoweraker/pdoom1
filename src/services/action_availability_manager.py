"""
Action Availability Manager - Centralized Action State Management

Handles all logic for determining action availability, including AP costs, rules,
and UI state synchronization. Prevents inconsistencies between action filtering
and display states.

Using our "slightly more verbose but clearer" naming approach for maintainability.
"""

from typing import List, Dict, Any, Tuple, Optional
from enum import Enum


class ActionAvailabilityState(Enum):
    """Clear action state classification for consistent UI behavior."""
    AVAILABLE = "available"          # Action can be selected and executed
    DISABLED_NO_AP = "disabled_no_ap"  # Action visible but insufficient AP
    DISABLED_RULE = "disabled_rule"    # Action visible but rule check failed
    HIDDEN = "hidden"                  # Action completely hidden from UI


class ActionAvailabilityInfo:
    """
    Complete availability information for a single action with clear reasoning.
    """
    
    def __init__(self, action_index: int, action_data: Dict[str, Any], 
                 state: ActionAvailabilityState, reason: str = ""):
        self.action_index = action_index
        self.action_data = action_data
        self.state = state
        self.reason = reason
        self.ap_cost = action_data.get("ap_cost", 1)
        self.name = action_data.get("name", "Unknown Action")
    
    @property
    def is_visible(self) -> bool:
        """Whether action should appear in UI."""
        return self.state != ActionAvailabilityState.HIDDEN
    
    @property
    def is_selectable(self) -> bool:
        """Whether action can be clicked/selected."""
        return self.state == ActionAvailabilityState.AVAILABLE
    
    @property
    def is_disabled(self) -> bool:
        """Whether action should be shown as disabled/grayed out."""
        return self.state in [ActionAvailabilityState.DISABLED_NO_AP, 
                             ActionAvailabilityState.DISABLED_RULE]


class ActionAvailabilityManager:
    """
    Centralized manager for all action availability logic with consistent
    state tracking and UI synchronization.
    """
    
    def __init__(self):
        self._cached_availability: Optional[List[ActionAvailabilityInfo]] = None
        self._last_game_state_hash: Optional[int] = None
    
    def get_action_availability_states(self, game_state) -> List[ActionAvailabilityInfo]:
        """
        Get complete availability information for all actions with caching
        to prevent unnecessary recalculation.
        
        Args:
            game_state: Current game state to evaluate
            
        Returns:
            List of ActionAvailabilityInfo for all actions
        """
        # Create a simple hash of relevant game state for cache invalidation
        current_hash = self._calculate_game_state_hash_for_action_availability(game_state)
        
        # Return cached result if game state hasn't changed
        if (self._cached_availability is not None and 
            self._last_game_state_hash == current_hash):
            return self._cached_availability
        
        # Recalculate availability states
        availability_states = []
        
        for idx, action in enumerate(game_state.gameplay_actions):
            state = self._determine_action_availability_state(game_state, action)
            reason = self._get_unavailability_reason(game_state, action, state)
            
            availability_info = ActionAvailabilityInfo(
                action_index=idx,
                action_data=action,
                state=state,
                reason=reason
            )
            availability_states.append(availability_info)
        
        # Cache the results
        self._cached_availability = availability_states
        self._last_game_state_hash = current_hash
        
        return availability_states
    
    def get_visible_actions_with_display_mapping(self, game_state) -> Tuple[List[ActionAvailabilityInfo], List[int]]:
        """
        Get actions that should be visible in UI with proper index mapping.
        
        Returns:
            Tuple of (visible_actions, original_indices) for UI rendering
        """
        all_actions = self.get_action_availability_states(game_state)
        
        visible_actions = [action for action in all_actions if action.is_visible]
        original_indices = [action.action_index for action in visible_actions]
        
        return visible_actions, original_indices
    
    def is_action_selectable_by_index(self, game_state, action_index: int) -> bool:
        """
        Quick check if specific action is selectable (for click handling).
        
        Args:
            game_state: Current game state
            action_index: Original action index to check
            
        Returns:
            True if action can be selected/executed
        """
        availability_states = self.get_action_availability_states(game_state)
        
        if action_index >= len(availability_states):
            return False
            
        return availability_states[action_index].is_selectable
    
    def invalidate_cache(self) -> None:
        """Force recalculation on next availability check."""
        self._cached_availability = None
        self._last_game_state_hash = None
    
    def _determine_action_availability_state(self, game_state, action: Dict[str, Any]) -> ActionAvailabilityState:
        """
        Core logic for determining action availability state with clear priority.
        
        Priority order:
        1. Rule checks (hidden if rules fail)
        2. AP cost checks (disabled if insufficient AP)
        3. Available if all checks pass
        """
        # Check rules first - if rules fail, action is typically hidden
        if action.get("rules") and not action["rules"](game_state):
            return ActionAvailabilityState.HIDDEN
        
        # Check AP cost - if insufficient AP, action is visible but disabled
        ap_cost = action.get("ap_cost", 1)
        if game_state.action_points < ap_cost:
            return ActionAvailabilityState.DISABLED_NO_AP
        
        # All checks passed - action is available
        return ActionAvailabilityState.AVAILABLE
    
    def _get_unavailability_reason(self, game_state, action: Dict[str, Any], 
                                  state: ActionAvailabilityState) -> str:
        """Generate clear reason text for why action is unavailable."""
        if state == ActionAvailabilityState.DISABLED_NO_AP:
            ap_cost = action.get("ap_cost", 1)
            return f"Insufficient AP (need {ap_cost}, have {game_state.action_points})"
        elif state == ActionAvailabilityState.DISABLED_RULE:
            return "Requirements not met"
        elif state == ActionAvailabilityState.HIDDEN:
            return "Not available"
        else:
            return ""
    
    def _calculate_game_state_hash_for_action_availability(self, game_state) -> int:
        """
        Calculate simple hash of game state properties that affect action availability.
        Only includes properties that actually impact action availability to minimize
        unnecessary cache invalidation.
        """
        # Only hash properties that affect action availability
        relevant_properties = (
            game_state.action_points,
            game_state.money,
            game_state.staff,
            game_state.reputation,
            game_state.research_progress,
            game_state.turn,
            len(getattr(game_state, 'selected_gameplay_actions', [])),
            # Add other properties that rules commonly check
            getattr(game_state, 'doom', 0),
            getattr(game_state, 'compute', 0),
            getattr(game_state, 'papers_published', 0)
        )
        
        return hash(relevant_properties)


# Global action availability manager instance
action_availability_manager = ActionAvailabilityManager()


def get_action_availability_manager() -> ActionAvailabilityManager:
    """Get the global action availability manager instance."""
    return action_availability_manager
