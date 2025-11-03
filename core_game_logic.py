"""
shared/core/game_logic.py

Pure game logic with NO pygame/Godot dependencies.
All UI interactions go through IGameEngine interface.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from shared.core.engine_interface import IGameEngine, MessageCategory, DialogOption, DialogResult

@dataclass
class GameState:
    """
    Pure game state data structure.
    No pygame or Godot dependencies.
    """
    # Core resources
    turn: int = 0
    money: float = 100000.0
    compute: float = 100.0
    safety: float = 0.0
    capabilities: float = 0.0
    
    # Staff
    employees: Dict[str, int] = field(default_factory=dict)
    
    # Upgrades & research
    upgrades: List[str] = field(default_factory=list)
    active_projects: List[Dict[str, Any]] = field(default_factory=list)
    
    # Game configuration
    seed: str = "default"
    compute_rate: float = 5.0
    staff_maintenance_cost: float = 10000.0
    
    # State flags
    game_over: bool = False
    victory: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for saving."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Deserialize from saved data."""
        return cls(**data)
    
    def get_total_employees(self) -> int:
        """Get total employee count."""
        return sum(self.employees.values())


@dataclass
class TurnResult:
    """Result of processing a turn."""
    success: bool
    events: List[Dict[str, Any]] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)
    state_changes: Dict[str, Any] = field(default_factory=dict)
    game_over: bool = False
    victory: bool = False


class GameLogic:
    """
    Core game logic engine.
    Engine-agnostic - works with pygame, Godot, or testing.
    """
    
    def __init__(self, engine: IGameEngine, seed: str = "default"):
        """
        Initialize game logic.
        
        Args:
            engine: Engine interface for UI operations
            seed: Random seed for deterministic gameplay
        """
        self.engine = engine
        self.state = GameState(seed=seed)
        
        # Initialize default employees
        self.state.employees = {
            "safety_researchers": 0,
            "capabilities_researchers": 0,
            "compute_researchers": 0,
        }
    
    # ========== Turn Management ==========
    
    def process_turn_end(self) -> TurnResult:
        """
        Process end of turn - pure logic, no UI.
        
        Returns:
            TurnResult with events and state changes
        """
        result = TurnResult(success=True)
        
        # Increment turn
        old_turn = self.state.turn
        self.state.turn += 1
        result.state_changes['turn'] = (old_turn, self.state.turn)
        
        # Consume compute
        old_compute = self.state.compute
        self.state.compute = max(0, self.state.compute - self.state.compute_rate)
        result.state_changes['compute'] = (old_compute, self.state.compute)
        
        # Staff maintenance
        total_employees = self.state.get_total_employees()
        if total_employees > 0:
            maintenance = total_employees * self.state.staff_maintenance_cost
            old_money = self.state.money
            self.state.money -= maintenance
            result.state_changes['money'] = (old_money, self.state.money)
            result.messages.append(
                f"Staff maintenance: -${maintenance:,.0f}"
            )
        
        # Check game over conditions
        if self.state.money <= 0:
            self.state.game_over = True
            result.game_over = True
            result.messages.append("GAME OVER: Ran out of money")
        
        if self.state.compute <= 0:
            self.state.game_over = True
            result.game_over = True
            result.messages.append("GAME OVER: Ran out of compute")
        
        # Check victory conditions
        if self.state.safety >= 100:
            self.state.victory = True
            result.victory = True
            result.messages.append("VICTORY: Achieved AI safety!")
        
        # Notify engine of state changes
        self.engine.update_turn_display(self.state.turn)
        self.engine.update_resource_display({
            'money': self.state.money,
            'compute': self.state.compute,
            'safety': self.state.safety,
            'capabilities': self.state.capabilities,
        })
        
        return result
    
    # ========== Action Execution ==========
    
    def execute_action(self, action_id: str) -> TurnResult:
        """
        Execute a player action.
        
        Args:
            action_id: Action identifier
            
        Returns:
            TurnResult with action results
        """
        result = TurnResult(success=False)
        
        # Validate action exists (will load from JSON later)
        action_handlers = {
            'hire_safety_researcher': self._action_hire_safety,
            'hire_capabilities_researcher': self._action_hire_capabilities,
            'purchase_compute': self._action_purchase_compute,
            'fundraise': self._action_fundraise,
        }
        
        handler = action_handlers.get(action_id)
        if not handler:
            result.messages.append(f"Unknown action: {action_id}")
            self.engine.display_message(
                f"Unknown action: {action_id}",
                MessageCategory.ERROR
            )
            return result
        
        # Execute action
        return handler()
    
    def _action_hire_safety(self) -> TurnResult:
        """Hire a safety researcher."""
        result = TurnResult(success=True)
        
        cost = 50000
        if self.state.money < cost:
            result.success = False
            result.messages.append("Not enough money to hire safety researcher")
            self.engine.display_message(
                "Not enough money to hire safety researcher",
                MessageCategory.WARNING
            )
            return result
        
        # Apply costs and effects
        self.state.money -= cost
        self.state.employees['safety_researchers'] += 1
        self.state.safety += 2
        
        result.messages.append("Hired safety researcher")
        result.state_changes['money'] = cost
        result.state_changes['safety_researchers'] = 1
        result.state_changes['safety'] = 2
        
        # Notify engine
        self.engine.display_message(
            "Hired safety researcher (+2 safety)",
            MessageCategory.SUCCESS
        )
        self.engine.play_sound("hire")
        self.engine.update_resource_display({
            'money': self.state.money,
            'safety': self.state.safety,
        })
        self.engine.update_employee_display(self.state.employees)
        
        return result
    
    def _action_hire_capabilities(self) -> TurnResult:
        """Hire a capabilities researcher."""
        result = TurnResult(success=True)
        
        cost = 50000
        if self.state.money < cost:
            result.success = False
            result.messages.append("Not enough money")
            self.engine.display_message(
                "Not enough money to hire capabilities researcher",
                MessageCategory.WARNING
            )
            return result
        
        self.state.money -= cost
        self.state.employees['capabilities_researchers'] += 1
        self.state.capabilities += 3
        
        result.messages.append("Hired capabilities researcher")
        
        self.engine.display_message(
            "Hired capabilities researcher (+3 capabilities)",
            MessageCategory.SUCCESS
        )
        self.engine.play_sound("hire")
        self.engine.update_resource_display({
            'money': self.state.money,
            'capabilities': self.state.capabilities,
        })
        self.engine.update_employee_display(self.state.employees)
        
        return result
    
    def _action_purchase_compute(self) -> TurnResult:
        """Purchase compute resources."""
        result = TurnResult(success=True)
        
        cost = 10000
        if self.state.money < cost:
            result.success = False
            self.engine.display_message(
                "Not enough money to purchase compute",
                MessageCategory.WARNING
            )
            return result
        
        self.state.money -= cost
        self.state.compute += 50
        
        result.messages.append("Purchased compute")
        
        self.engine.display_message(
            "Purchased compute (+50)",
            MessageCategory.SUCCESS
        )
        self.engine.play_sound("upgrade")
        self.engine.update_resource_display({
            'money': self.state.money,
            'compute': self.state.compute,
        })
        
        return result
    
    def _action_fundraise(self) -> TurnResult:
        """Fundraise to get money."""
        result = TurnResult(success=True)
        
        amount = 100000
        self.state.money += amount
        
        result.messages.append(f"Raised ${amount:,.0f}")
        
        self.engine.display_message(
            f"Successfully raised ${amount:,.0f}",
            MessageCategory.SUCCESS
        )
        self.engine.play_sound("event")
        self.engine.update_resource_display({
            'money': self.state.money,
        })
        
        return result
    
    # ========== Event Handling ==========
    
    def check_events(self) -> List[Dict[str, Any]]:
        """
        Check for triggered events (pure logic).
        
        Returns:
            List of triggered events
        """
        events = []
        
        # Example: Funding crisis at turn 10
        if self.state.turn == 10 and self.state.money < 50000:
            events.append({
                'id': 'funding_crisis',
                'name': 'Funding Crisis',
                'description': 'Your lab is running low on funds!',
                'options': [
                    DialogOption('emergency_fundraise', 'Emergency fundraising'),
                    DialogOption('accept', 'Continue anyway'),
                ]
            })
        
        return events
    
    def handle_event_choice(
        self,
        event_id: str,
        choice_id: str
    ) -> TurnResult:
        """
        Handle player's choice for an event.
        
        Args:
            event_id: Event identifier
            choice_id: Chosen option identifier
            
        Returns:
            TurnResult with event outcome
        """
        result = TurnResult(success=True)
        
        if event_id == 'funding_crisis':
            if choice_id == 'emergency_fundraise':
                self.state.money += 75000
                result.messages.append("Emergency fundraising: +$75,000")
                self.engine.display_message(
                    "Secured emergency funding",
                    MessageCategory.SUCCESS
                )
            else:
                result.messages.append("Continuing with low funds...")
        
        return result
    
    # ========== State Query Methods ==========
    
    def can_afford_action(self, action_id: str) -> bool:
        """Check if player can afford an action."""
        costs = {
            'hire_safety_researcher': 50000,
            'hire_capabilities_researcher': 50000,
            'purchase_compute': 10000,
            'fundraise': 0,
        }
        
        cost = costs.get(action_id, 0)
        return self.state.money >= cost
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions for current state."""
        actions = ['fundraise']  # Always available
        
        if self.state.money >= 50000:
            actions.extend([
                'hire_safety_researcher',
                'hire_capabilities_researcher',
            ])
        
        if self.state.money >= 10000:
            actions.append('purchase_compute')
        
        return actions
