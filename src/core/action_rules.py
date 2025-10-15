'''
Action Rules System for P(Doom) Game

This module provides a structured way to define and manage action availability rules.
The action rules system determines when specific actions become available to the player
based on game state conditions like turn number, resources, milestones, and upgrades.

Architecture:
1. Rule types: Turn-based, Resource-based, Milestone-based, Upgrade-based
2. Rule evaluation: Simple boolean functions with clear naming and documentation
3. Rule composition: Ability to combine multiple rules with AND/OR logic
4. Future extensibility: Easy to add new rule types and conditions

Usage:
- Actions in actions.py reference rule functions defined here
- Rules are evaluated in game_state.py when checking action availability
- Each rule function takes a GameState object and returns a boolean

Example:
    # In actions.py
    {
        'name': 'Advanced Action',
        'rules': lambda gs: ActionRules.requires_staff_and_turn(gs, min_staff=10, min_turn=8)
    }
'''

from typing import Any, Callable

# Import will be resolved at runtime to avoid circular imports
# GameState type annotation will use TYPE_CHECKING pattern if needed


class ActionRules:
    '''
    Centralized action rules system for managing action availability.
    
    This class provides static methods that define when actions become available.
    All rule methods take a GameState object as their first parameter and return
    a boolean indicating whether the action should be available.
    '''
    
    # === Turn-based Rules ===
    
    @staticmethod
    def requires_turn(gs: Any, min_turn: int) -> bool:
        '''
        Rule: Action requires a minimum turn number.
        
        Args:
            gs: GameState object
            min_turn: Minimum turn number required
            
        Returns:
            bool: True if current turn >= min_turn
            
        Example:
            Scout Opponent unlocks after turn 5
        '''
        return gs.turn >= min_turn
    
    # === Resource-based Rules ===
    
    @staticmethod
    def requires_staff(gs: Any, min_staff: int) -> bool:
        '''
        Rule: Action requires a minimum number of staff.
        
        Args:
            gs: GameState object
            min_staff: Minimum staff count required
            
        Returns:
            bool: True if current staff >= min_staff
            
        Example:
            Manager hiring unlocks at 9 staff
        '''
        return gs.staff >= min_staff
    
    @staticmethod
    def requires_money(gs: Any, min_money: int) -> bool:
        '''
        Rule: Action requires a minimum amount of money.
        
        Args:
            gs: GameState object
            min_money: Minimum money amount required
            
        Returns:
            bool: True if current money >= min_money
        '''
        return gs.money >= min_money
    
    @staticmethod
    def requires_reputation(gs: Any, min_reputation: int) -> bool:
        '''
        Rule: Action requires a minimum reputation level.
        
        Args:
            gs: GameState object
            min_reputation: Minimum reputation required
            
        Returns:
            bool: True if current reputation >= min_reputation
        '''
        return gs.reputation >= min_reputation
    
    # === Milestone-based Rules ===
    
    @staticmethod
    def requires_milestone_triggered(gs: Any, milestone_attr: str) -> bool:
        '''
        Rule: Action requires a specific milestone to be triggered.
        
        Args:
            gs: GameState object
            milestone_attr: String name of milestone attribute (e.g., 'manager_milestone_triggered')
            
        Returns:
            bool: True if milestone has been triggered
            
        Example:
            Some actions might only be available after manager milestone
        '''
        return getattr(gs, milestone_attr, False)
    
    @staticmethod
    def requires_board_members(gs: Any, min_board_members: int = 1) -> bool:
        '''
        Rule: Action requires board members to be installed.
        
        Args:
            gs: GameState object
            min_board_members: Minimum number of board members required
            
        Returns:
            bool: True if board_members >= min_board_members
            
        Example:
            Search action requires board oversight
        '''
        return gs.board_members >= min_board_members
    
    # === Upgrade-based Rules ===
    
    @staticmethod
    def requires_upgrade(gs: Any, upgrade_key: str) -> bool:
        '''
        Rule: Action requires a specific upgrade to be purchased.
        
        Args:
            gs: GameState object
            upgrade_key: String key of required upgrade effect
            
        Returns:
            bool: True if upgrade has been purchased
            
        Example:
            Advanced actions might require specific technology upgrades
        '''
        return upgrade_key in gs.upgrade_effects
    
    @staticmethod
    def requires_scrollable_log(gs: Any) -> bool:
        '''
        Rule: Action requires scrollable event log to be enabled.
        
        Args:
            gs: GameState object
            
        Returns:
            bool: True if scrollable event log is enabled
            
        Example:
            Log management actions require the scrollable log upgrade
        '''
        return gs.scrollable_event_log_enabled
    
    # === Composite Rules ===
    
    @staticmethod
    def requires_staff_and_turn(gs: Any, min_staff: int, min_turn: int) -> bool:
        '''
        Rule: Action requires both minimum staff and turn requirements.
        
        Args:
            gs: GameState object
            min_staff: Minimum staff count required
            min_turn: Minimum turn number required
            
        Returns:
            bool: True if both conditions are met
            
        Example:
            Advanced management actions require experience (turns) and scale (staff)
        '''
        return gs.staff >= min_staff and gs.turn >= min_turn
    
    @staticmethod
    def requires_any_specialized_staff(gs: Any, min_count: int = 1) -> bool:
        '''
        Rule: Action requires any type of specialized staff.
        
        Args:
            gs: GameState object
            min_count: Minimum number of specialized staff required
            
        Returns:
            bool: True if total specialized staff >= min_count
            
        Example:
            Delegation features require specialized staff
        '''
        total_specialized = gs.admin_staff + gs.research_staff + gs.ops_staff
        return total_specialized >= min_count
    
    # === Negation and Complex Logic ===
    
    @staticmethod
    def not_yet_triggered(gs: Any, milestone_attr: str) -> bool:
        '''
        Rule: Action is only available if milestone has NOT been triggered yet.
        
        Args:
            gs: GameState object
            milestone_attr: String name of milestone attribute
            
        Returns:
            bool: True if milestone has NOT been triggered
            
        Example:
            First-time actions that should only happen once
        '''
        return not getattr(gs, milestone_attr, False)
    
    @staticmethod
    def combine_and(gs: Any, *rule_functions: Callable[[Any], bool]) -> bool:
        '''
        Rule: Combine multiple rules with AND logic.
        
        Args:
            gs: GameState object
            *rule_functions: Variable number of rule functions to combine
            
        Returns:
            bool: True if ALL rules return True
            
        Example:
            Action requires multiple conditions to be met simultaneously
        '''
        return all(rule_func(gs) for rule_func in rule_functions)
    
    @staticmethod
    def combine_or(gs: Any, *rule_functions: Callable[[Any], bool]) -> bool:
        '''
        Rule: Combine multiple rules with OR logic.
        
        Args:
            gs: GameState object
            *rule_functions: Variable number of rule functions to combine
            
        Returns:
            bool: True if ANY rule returns True
            
        Example:
            Action available through multiple different paths
        '''
        return any(rule_func(gs) for rule_func in rule_functions)


# === Convenience Functions for Common Patterns ===

def manager_unlock_rule(gs: Any) -> bool:
    '''
    Convenience function: Manager hiring becomes available at 9+ staff.
    
    This is the canonical rule for manager availability, used as an example
    of how to create clear, named rule functions for specific game mechanics.
    '''
    return ActionRules.requires_staff(gs, min_staff=9)


def scout_unlock_rule(gs: Any) -> bool:
    '''
    Convenience function: Scout Opponent becomes available after turn 5.
    
    Represents the game progression where intelligence operations become
    available after the player develops the necessary infrastructure and reputation.
    '''
    return ActionRules.requires_turn(gs, min_turn=5)


def search_unlock_rule(gs: Any) -> bool:
    '''
    Convenience function: Search action requires board oversight.
    
    This action only becomes available when board members have been installed
    due to high spending without accounting software.
    '''
    return ActionRules.requires_board_members(gs, min_board_members=1)


# === Future Extension Guidelines ===

'''
Guidelines for extending the action rules system:

1. **Naming Convention**: Use descriptive names that clearly indicate the condition
   - requires_* for positive conditions
   - not_* for negative conditions  
   - *_unlock_rule for specific action unlock conditions

2. **Documentation**: Each rule function should have:
   - Clear docstring explaining what it checks
   - Parameter documentation
   - Example of when it would be used
   - Return value documentation

3. **Composability**: Prefer simple, single-responsibility rules that can be combined
   rather than complex rules that check multiple conditions

4. **Testing**: New rules should have corresponding unit tests that verify:
   - Rule returns True when condition is met
   - Rule returns False when condition is not met
   - Edge cases and boundary conditions

5. **Game Balance**: Consider the player experience when adding new rules:
   - Actions should unlock at appropriate points in game progression
   - Players should understand why actions are/aren't available
   - Provide clear feedback when actions are locked

6. **Performance**: Rules are evaluated frequently, so keep them simple and fast:
   - Avoid complex calculations in rule functions
   - Use simple attribute checks when possible
   - Cache expensive calculations in game state if needed

Example of adding a new rule:

'''
