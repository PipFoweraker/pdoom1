"""
shared/core/game_logic.py

Pure game logic with NO pygame/Godot dependencies.
All UI interactions go through IGameEngine interface.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from shared.core.engine_interface import IGameEngine, MessageCategory, DialogOption, DialogResult
from shared.core.actions_engine import ActionsEngine
from shared.core.events_engine import EventsEngine

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
        
        # Initialize actions engine
        self.actions_engine = ActionsEngine()
        
        # Initialize events engine with deterministic seed
        seed_hash = hash(seed) % (2**31)
        self.events_engine = EventsEngine(seed=seed_hash)
        
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
        Execute a player action using ActionsEngine.
        
        Args:
            action_id: Action identifier
            
        Returns:
            TurnResult with action results
        """
        result = TurnResult(success=False)
        
        # Use actions engine
        action_result = self.actions_engine.execute_action(
            action_id, 
            self.state, 
            self.engine
        )
        
        result.success = action_result.success
        result.messages.append(action_result.message)
        result.state_changes = action_result.state_changes
        
        return result
    
    def can_afford_action(self, action_id: str) -> bool:
        """Check if player can afford an action."""
        can_execute, _ = self.actions_engine.check_requirements(action_id, self.state)
        return can_execute
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions for current state."""
        return self.actions_engine.get_available_actions(self.state)
# ========== Event Handling ==========
    
    def check_events(self) -> List[Dict[str, Any]]:
        """Check for triggered events using EventsEngine."""
        triggered_ids = self.events_engine.check_all_events(self.state)
        
        events = []
        for event_id in triggered_ids:
            event_def = self.events_engine.get_event(event_id)
            if not event_def:
                continue
            
            if self.events_engine.is_popup_event(event_id):
                events.append({
                    'id': event_id,
                    'name': event_def['name'],
                    'description': event_def['description'],
                    'options': self.events_engine.get_event_options(event_id)
                })
            else:
                self.events_engine.execute_normal_event(
                    event_id,
                    self.state,
                    self.engine
                )
        
        return events
    
    def handle_event_choice(self, event_id: str, choice_id: str) -> TurnResult:
        """Handle player's event choice using EventsEngine."""
        result = TurnResult(success=True)
        
        event_result = self.events_engine.execute_event_choice(
            event_id,
            choice_id,
            self.state,
            self.engine
        )
        
        result.success = event_result.triggered
        if event_result.message:
            result.messages.append(event_result.message)
        result.state_changes = event_result.state_changes
        
        return result