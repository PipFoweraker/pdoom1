"""
shared/core/events_engine.py

Data-driven events system - loads from JSON.
"""

import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from shared.core.engine_interface import MessageCategory, DialogOption

@dataclass
class EventResult:
    """Result of processing an event."""
    event_id: str
    triggered: bool
    message: Optional[str] = None
    state_changes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.state_changes is None:
            self.state_changes = {}

class EventsEngine:
    """Data-driven events engine."""
    
    def __init__(self, events_file: Optional[str] = None, seed: Optional[int] = None):
        if events_file is None:
            base_dir = Path(__file__).parent.parent
            events_file = base_dir / "data" / "events.json"
        
        self.events_file = Path(events_file)
        self.events: Dict[str, Dict[str, Any]] = {}
        self.event_types: Dict[str, Dict[str, str]] = {}
        self.triggered_events: set = set()
        
        # RNG for random events (deterministic if seed provided)
        self.rng = random.Random(seed)
        
        self.load_events()
    
    def load_events(self) -> None:
        """Load events from JSON."""
        if not self.events_file.exists():
            raise FileNotFoundError(f"Events file not found: {self.events_file}")
        
        with open(self.events_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.events = data.get('events', {})
        self.event_types = data.get('event_types', {})
    
    def check_trigger(self, event_id: str, state: Any) -> bool:
        """Check if event trigger condition is met."""
        event = self.events.get(event_id)
        if not event:
            return False
        
        # Don't trigger same event twice (unless repeatable)
        if event_id in self.triggered_events and not event.get('repeatable', False):
            return False
        
        trigger = event.get('trigger', {})
        trigger_type = trigger.get('type')
        
        if trigger_type == 'turn_and_resource':
            # Specific turn + resource condition
            if state.turn != trigger.get('turn'):
                return False
            return self._evaluate_condition(trigger.get('condition', 'True'), state)
        
        elif trigger_type == 'threshold':
            # Resource threshold
            return self._evaluate_condition(trigger.get('condition', 'False'), state)
        
        elif trigger_type == 'turn_threshold':
            # Turn + condition
            if state.turn < trigger.get('turn', 0):
                return False
            return self._evaluate_condition(trigger.get('condition', 'True'), state)
        
        elif trigger_type == 'random':
            # Random chance
            if state.turn < trigger.get('min_turn', 0):
                return False
            return self.rng.random() < trigger.get('probability', 0.1)
        
        return False
    
    def _evaluate_condition(self, condition: str, state: Any) -> bool:
        """Safely evaluate condition string."""
        try:
            # Create safe namespace with only state attributes
            namespace = {
                'money': state.money,
                'compute': state.compute,
                'safety': state.safety,
                'capabilities': state.capabilities,
                'turn': state.turn,
            }
            return eval(condition, {"__builtins__": {}}, namespace)
        except Exception:
            return False
    
    def check_all_events(self, state: Any) -> List[str]:
        """Check all events and return triggered event IDs."""
        triggered = []
        
        for event_id in self.events.keys():
            if self.check_trigger(event_id, state):
                triggered.append(event_id)
                self.triggered_events.add(event_id)
        
        return triggered
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event definition."""
        return self.events.get(event_id)
    
    def get_event_options(self, event_id: str) -> List[DialogOption]:
        """Get event options as DialogOptions."""
        event = self.get_event(event_id)
        if not event:
            return []
        
        options = []
        for opt in event.get('options', []):
            # Check if option has cost requirements
            enabled = True
            if 'costs' in opt:
                # Will check affordability when executing
                pass
            
            options.append(DialogOption(
                id=opt['id'],
                text=opt['text'],
                enabled=enabled
            ))
        
        return options
    
    def execute_event_choice(
        self,
        event_id: str,
        choice_id: str,
        state: Any,
        engine: Any
    ) -> EventResult:
        """Execute player's event choice."""
        event = self.get_event(event_id)
        if not event:
            return EventResult(
                event_id=event_id,
                triggered=False,
                message="Unknown event"
            )
        
        # Find chosen option
        chosen_option = None
        for opt in event.get('options', []):
            if opt['id'] == choice_id:
                chosen_option = opt
                break
        
        if not chosen_option:
            return EventResult(
                event_id=event_id,
                triggered=False,
                message="Unknown option"
            )
        
        # Check costs
        costs = chosen_option.get('costs', {})
        for resource, cost in costs.items():
            if hasattr(state, resource):
                if getattr(state, resource) < cost:
                    engine.display_message(
                        f"Not enough {resource}",
                        MessageCategory.WARNING
                    )
                    return EventResult(
                        event_id=event_id,
                        triggered=False,
                        message=f"Not enough {resource}"
                    )
        
        # Apply costs
        for resource, cost in costs.items():
            if hasattr(state, resource):
                old_value = getattr(state, resource)
                setattr(state, resource, old_value - cost)
        
        # Apply effects
        effects = chosen_option.get('effects', {})
        state_changes = {}
        
        for key, value in effects.items():
            if '.' in key:
                # Nested (e.g., employees.safety_researchers)
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
                if hasattr(state, key):
                    old_value = getattr(state, key)
                    setattr(state, key, old_value + value)
                    state_changes[key] = value
        
        # Display message
        message = chosen_option.get('message', 'Event processed')
        engine.display_message(message, MessageCategory.EVENT)
        
        # Play sound
        if 'sound' in event:
            engine.play_sound(event['sound'])
        
        # Update displays
        engine.update_resource_display({
            'money': state.money,
            'compute': state.compute,
            'safety': state.safety,
            'capabilities': state.capabilities,
        })
        
        if 'employees.' in str(state_changes):
            engine.update_employee_display(state.employees)
        
        return EventResult(
            event_id=event_id,
            triggered=True,
            message=message,
            state_changes=state_changes
        )
    
    def execute_normal_event(
        self,
        event_id: str,
        state: Any,
        engine: Any
    ) -> EventResult:
        """Execute normal (non-popup) event."""
        event = self.get_event(event_id)
        if not event:
            return EventResult(event_id=event_id, triggered=False)
        
        effect = event.get('effect', {})
        message = effect.get('message', 'Event occurred')
        
        engine.display_message(message, MessageCategory.EVENT)
        
        if 'sound' in event:
            engine.play_sound(event['sound'])
        
        return EventResult(
            event_id=event_id,
            triggered=True,
            message=message
        )
    
    def is_popup_event(self, event_id: str) -> bool:
        """Check if event is popup type."""
        event = self.get_event(event_id)
        if not event:
            return False
        return event.get('type') == 'popup'
    
    def reset_triggered_events(self) -> None:
        """Clear triggered events history."""
        self.triggered_events.clear()
