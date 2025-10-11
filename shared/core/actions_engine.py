"""
shared/core/actions_engine.py

Data-driven actions system - loads from JSON.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from shared.core.engine_interface import MessageCategory

@dataclass
class ActionResult:
    """Result of executing an action."""
    success: bool
    action_id: str
    message: str
    state_changes: Dict[str, Any]
    cost_paid: Dict[str, float]

class ActionsEngine:
    """
    Data-driven actions engine.
    Loads action definitions from JSON and executes them.
    """
    
    def __init__(self, actions_file: Optional[str] = None):
        """
        Initialize actions engine.
        
        Args:
            actions_file: Path to actions.json (defaults to shared/data/actions.json)
        """
        if actions_file is None:
            # Default to shared/data/actions.json
            base_dir = Path(__file__).parent.parent
            actions_file = base_dir / "data" / "actions.json"
        
        self.actions_file = Path(actions_file)
        self.actions: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, Dict[str, str]] = {}
        
        self.load_actions()
    
    def load_actions(self) -> None:
        """Load actions from JSON file."""
        if not self.actions_file.exists():
            raise FileNotFoundError(f"Actions file not found: {self.actions_file}")
        
        with open(self.actions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.actions = data.get('actions', {})
        self.categories = data.get('categories', {})
    
    def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get action definition by ID."""
        return self.actions.get(action_id)
    
    def get_all_actions(self) -> List[str]:
        """Get list of all action IDs."""
        return list(self.actions.keys())
    
    def get_actions_by_category(self, category: str) -> List[str]:
        """Get all action IDs in a category."""
        return [
            action_id
            for action_id, action in self.actions.items()
            if action.get('category') == category
        ]
    
    def check_requirements(
        self,
        action_id: str,
        state: Any
    ) -> tuple[bool, Optional[str]]:
        """
        Check if action requirements are met.
        
        Args:
            action_id: Action to check
            state: Current game state
            
        Returns:
            (can_execute, reason_if_not)
        """
        action = self.get_action(action_id)
        if not action:
            return False, f"Unknown action: {action_id}"
        
        requirements = action.get('requirements', {})
        
        # Check turn requirements
        if 'min_turn' in requirements:
            if state.turn < requirements['min_turn']:
                return False, f"Available from turn {requirements['min_turn']}"
        
        # Check employee requirements (e.g., min_employees.safety_researchers)
        for key, value in requirements.items():
            if key.startswith('min_employees.'):
                employee_type = key.split('.', 1)[1]
                current = state.employees.get(employee_type, 0)
                if current < value:
                    return False, f"Need {value} {employee_type.replace('_', ' ')}"
        
        # Check resource costs
        costs = action.get('costs', {})
        for resource, cost in costs.items():
            if hasattr(state, resource):
                if getattr(state, resource) < cost:
                    msg_key = f"insufficient_{resource}"
                    return False, action.get('messages', {}).get(msg_key, f"Not enough {resource}")
        
        return True, None
    
    def execute_action(
        self,
        action_id: str,
        state: Any,
        engine: Any
    ) -> ActionResult:
        """
        Execute an action.
        
        Args:
            action_id: Action to execute
            state: Game state to modify
            engine: Engine for UI notifications
            
        Returns:
            ActionResult with outcome
        """
        action = self.get_action(action_id)
        if not action:
            engine.display_message(
                f"Unknown action: {action_id}",
                MessageCategory.ERROR
            )
            return ActionResult(
                success=False,
                action_id=action_id,
                message=f"Unknown action: {action_id}",
                state_changes={},
                cost_paid={}
            )
        
        # Check requirements
        can_execute, reason = self.check_requirements(action_id, state)
        if not can_execute:
            engine.display_message(
                reason or "Requirements not met",
                MessageCategory.WARNING
            )
            return ActionResult(
                success=False,
                action_id=action_id,
                message=reason or "Requirements not met",
                state_changes={},
                cost_paid={}
            )
        
        # Apply costs
        costs = action.get('costs', {})
        cost_paid = {}
        for resource, cost in costs.items():
            if hasattr(state, resource):
                old_value = getattr(state, resource)
                setattr(state, resource, old_value - cost)
                cost_paid[resource] = cost
        
        # Apply effects
        effects = action.get('effects', {})
        state_changes = {}
        
        for key, value in effects.items():
            if '.' in key:
                # Nested attribute (e.g., employees.safety_researchers)
                parts = key.split('.')
                obj = state
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                
                if isinstance(obj, dict):
                    final_key = parts[-1]
                    old_val = obj.get(final_key, 0)
                    obj[final_key] = old_val + value
                    state_changes[key] = value
            else:
                # Direct attribute
                if hasattr(state, key):
                    old_value = getattr(state, key)
                    setattr(state, key, old_value + value)
                    state_changes[key] = value
        
        # Notify engine
        success_msg = action.get('messages', {}).get('success', f"Executed {action_id}")
        engine.display_message(success_msg, MessageCategory.SUCCESS)
        
        if 'sound' in action:
            engine.play_sound(action['sound'])
        
        # Update resource displays
        engine.update_resource_display({
            'money': state.money,
            'compute': state.compute,
            'safety': state.safety,
            'capabilities': state.capabilities,
        })
        
        if state_changes.get('employees.safety_researchers') or \
           state_changes.get('employees.capabilities_researchers') or \
           state_changes.get('employees.compute_researchers'):
            engine.update_employee_display(state.employees)
        
        return ActionResult(
            success=True,
            action_id=action_id,
            message=success_msg,
            state_changes=state_changes,
            cost_paid=cost_paid
        )
    
    def get_available_actions(self, state: Any) -> List[str]:
        """
        Get list of actions player can currently execute.
        
        Args:
            state: Current game state
            
        Returns:
            List of action IDs that meet requirements
        """
        available = []
        
        for action_id in self.get_all_actions():
            can_execute, _ = self.check_requirements(action_id, state)
            if can_execute:
                available.append(action_id)
        
        return available
    
    def get_action_cost(self, action_id: str, resource: str) -> float:
        """Get cost of action for specific resource."""
        action = self.get_action(action_id)
        if not action:
            return 0.0
        
        return action.get('costs', {}).get(resource, 0.0)
    
    def get_action_display_info(self, action_id: str) -> Dict[str, Any]:
        """Get action info for UI display."""
        action = self.get_action(action_id)
        if not action:
            return {}
        
        return {
            'id': action_id,
            'name': action.get('name', action_id),
            'category': action.get('category', 'uncategorized'),
            'costs': action.get('costs', {}),
            'effects': action.get('effects', {}),
        }