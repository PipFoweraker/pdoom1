#!/usr/bin/env python3
"""
Phase 2: Events System Setup

Installs events.json, events_engine.py, and updates game_logic.py
Run from project root: python tools/phase2_setup.py
"""

import os
import shutil
from pathlib import Path

# Events JSON content
EVENTS_JSON = """{
  "events": {
    "funding_crisis": {
      "id": "funding_crisis",
      "name": "Funding Crisis",
      "description": "Your lab is running dangerously low on funds!",
      "type": "popup",
      "trigger": {
        "type": "turn_and_resource",
        "turn": 10,
        "condition": "money < 50000"
      },
      "options": [
        {
          "id": "emergency_fundraise",
          "text": "Emergency Fundraising",
          "effects": {
            "money": 75000
          },
          "message": "Secured emergency funding: +$75,000"
        },
        {
          "id": "accept",
          "text": "Continue Anyway",
          "effects": {},
          "message": "Continuing with limited funds..."
        }
      ],
      "sound": "event"
    },
    "breakthrough": {
      "id": "breakthrough",
      "name": "Safety Breakthrough!",
      "description": "Your researchers have made a significant safety advancement!",
      "type": "popup",
      "trigger": {
        "type": "threshold",
        "condition": "safety >= 50 and capabilities < safety"
      },
      "options": [
        {
          "id": "publish",
          "text": "Publish Results",
          "effects": {
            "safety": 10,
            "money": -20000
          },
          "message": "Published breakthrough (+10 safety, -$20k for publication)"
        },
        {
          "id": "keep_secret",
          "text": "Keep Secret",
          "effects": {
            "safety": 5
          },
          "message": "Kept research confidential (+5 safety)"
        }
      ],
      "sound": "upgrade"
    },
    "compute_shortage": {
      "id": "compute_shortage",
      "name": "Compute Shortage",
      "description": "Your compute resources are critically low!",
      "type": "normal",
      "trigger": {
        "type": "threshold",
        "condition": "compute < 20"
      },
      "effect": {
        "message": "WARNING: Compute critically low!"
      },
      "sound": "event"
    },
    "talent_recruitment": {
      "id": "talent_recruitment",
      "name": "Talent Opportunity",
      "description": "A brilliant researcher wants to join your lab at reduced cost!",
      "type": "popup",
      "trigger": {
        "type": "random",
        "probability": 0.1,
        "min_turn": 5
      },
      "options": [
        {
          "id": "hire_discounted",
          "text": "Hire at Discount",
          "costs": {
            "money": 25000
          },
          "effects": {
            "safety": 3,
            "employees.safety_researchers": 1
          },
          "message": "Hired talented researcher at discount!"
        },
        {
          "id": "decline",
          "text": "Decline Offer",
          "effects": {},
          "message": "Declined the recruitment opportunity"
        }
      ],
      "sound": "hire"
    },
    "capabilities_race": {
      "id": "capabilities_race",
      "name": "Capabilities Race Intensifies",
      "description": "Competitors are rapidly advancing AI capabilities!",
      "type": "normal",
      "trigger": {
        "type": "turn_threshold",
        "turn": 15,
        "condition": "capabilities < 30"
      },
      "effect": {
        "message": "The capabilities race is heating up!"
      },
      "sound": "event"
    }
  },
  "event_types": {
    "normal": {
      "name": "Normal Event",
      "description": "Immediate effect, no player choice"
    },
    "popup": {
      "name": "Popup Event",
      "description": "Requires player decision"
    },
    "deferred": {
      "name": "Deferred Event",
      "description": "Can be postponed, expires after turns"
    }
  }
}
"""

# Events Engine content
EVENTS_ENGINE = '''"""
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
'''

# Game logic update - add events_engine to __init__
GAME_LOGIC_INIT_ADDITION = '''
        # Initialize events engine with deterministic seed
        seed_hash = hash(seed) % (2**31)
        self.events_engine = EventsEngine(seed=seed_hash)
'''

GAME_LOGIC_IMPORT_ADDITION = "from shared.core.events_engine import EventsEngine"

GAME_LOGIC_EVENT_METHODS = '''
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
'''

def main():
    project_root = Path.cwd()
    
    print("[ROCKET] Phase 2: Events System Setup")
    print("=" * 40)
    
    # 1. Create events.json
    events_file = project_root / "shared" / "data" / "events.json"
    print(f"\n[FILE] Creating {events_file}")
    events_file.write_text(EVENTS_JSON, encoding='utf-8')
    print("  [OK] events.json created")
    
    # 2. Create events_engine.py
    engine_file = project_root / "shared" / "core" / "events_engine.py"
    print(f"\n[FILE] Creating {engine_file}")
    engine_file.write_text(EVENTS_ENGINE, encoding='utf-8')
    print("  [OK] events_engine.py created")
    
    # 3. Update game_logic.py
    game_logic_file = project_root / "shared" / "core" / "game_logic.py"
    print(f"\n[FILE] Updating {game_logic_file}")
    
    content = game_logic_file.read_text(encoding='utf-8')
    
    # Add import if not present
    if "from shared.core.events_engine import EventsEngine" not in content:
        # Add after actions_engine import
        content = content.replace(
            "from shared.core.actions_engine import ActionsEngine",
            "from shared.core.actions_engine import ActionsEngine\n" + GAME_LOGIC_IMPORT_ADDITION
        )
        print("  [OK] Added EventsEngine import")
    
    # Add events_engine initialization in __init__
    if "self.events_engine" not in content:
        # Find where to add it (after actions_engine init)
        insert_point = content.find("self.actions_engine = ActionsEngine()")
        if insert_point > 0:
            # Find end of that line
            end_of_line = content.find("\n", insert_point)
            content = content[:end_of_line+1] + GAME_LOGIC_INIT_ADDITION + content[end_of_line+1:]
            print("  [OK] Added events_engine initialization")
    
    # Add event methods if not present
    if "def check_events(self)" not in content:
        # Add at end of GameLogic class (before last line)
        content = content.rstrip() + "\n" + GAME_LOGIC_EVENT_METHODS + "\n"
        print("  [OK] Added event methods")
    
    game_logic_file.write_text(content, encoding='utf-8')
    print("  [OK] game_logic.py updated")
    
    # 4. Clear Python cache
    print("\n[CLEAN] Clearing Python cache")
    import subprocess
    try:
        subprocess.run(['find', '.', '-type', 'd', '-name', '__pycache__', '-exec', 'rm', '-rf', '{}', '+'], 
                      stderr=subprocess.DEVNULL, check=False)
        subprocess.run(['find', '.', '-name', '*.pyc', '-delete'], 
                      stderr=subprocess.DEVNULL, check=False)
        print("  [OK] Cache cleared")
    except Exception:
        print("  [SKIP] Cache clear failed (Windows - normal)")
    
    print("\n[SUCCESS] Phase 2 setup complete!")
    print("\nNext: Run tests")
    print("  python -m unittest discover tests/test_shared_logic -v")

if __name__ == "__main__":
    main()
