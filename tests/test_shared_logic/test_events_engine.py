"""
tests/test_shared_logic/test_events_engine.py

Tests for data-driven events engine.
"""

import unittest
import json
import tempfile
from pathlib import Path
from shared.core.events_engine import EventsEngine, EventResult
from shared.core.game_logic import GameState
from shared.core.engine_interface import MockEngine


class TestEventsEngine(unittest.TestCase):
    """Test EventsEngine loading and execution."""
    
    def setUp(self):
        """Create test events file."""
        self.engine = MockEngine()
        
        self.temp_dir = tempfile.mkdtemp()
        self.events_file = Path(self.temp_dir) / "test_events.json"
        
        test_data = {
            "events": {
                "test_crisis": {
                    "id": "test_crisis",
                    "name": "Test Crisis",
                    "description": "A test crisis",
                    "type": "popup",
                    "trigger": {
                        "type": "turn_and_resource",
                        "turn": 5,
                        "condition": "money < 1000"
                    },
                    "options": [
                        {
                            "id": "fix",
                            "text": "Fix It",
                            "effects": {"money": 500},
                            "message": "Fixed the crisis"
                        },
                        {
                            "id": "ignore",
                            "text": "Ignore",
                            "effects": {},
                            "message": "Ignored the crisis"
                        }
                    ]
                },
                "test_threshold": {
                    "id": "test_threshold",
                    "name": "Threshold Event",
                    "description": "Triggered by threshold",
                    "type": "normal",
                    "trigger": {
                        "type": "threshold",
                        "condition": "safety >= 50"
                    },
                    "effect": {
                        "message": "Threshold reached!"
                    }
                }
            }
        }
        
        with open(self.events_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        self.events_engine = EventsEngine(str(self.events_file), seed=42)
    
    def test_load_events(self):
        """Test events load from JSON."""
        self.assertEqual(len(self.events_engine.events), 2)
        self.assertIn('test_crisis', self.events_engine.events)
    
    def test_check_trigger_turn_and_resource(self):
        """Test turn+resource trigger."""
        state = GameState()
        state.turn = 5
        state.money = 500
        
        triggered = self.events_engine.check_trigger('test_crisis', state)
        self.assertTrue(triggered)
    
    def test_check_trigger_not_met(self):
        """Test trigger not met."""
        state = GameState()
        state.turn = 5
        state.money = 5000  # Too much money
        
        triggered = self.events_engine.check_trigger('test_crisis', state)
        self.assertFalse(triggered)
    
    def test_check_trigger_wrong_turn(self):
        """Test wrong turn."""
        state = GameState()
        state.turn = 3
        state.money = 500
        
        triggered = self.events_engine.check_trigger('test_crisis', state)
        self.assertFalse(triggered)
    
    def test_check_trigger_threshold(self):
        """Test threshold trigger."""
        state = GameState()
        state.safety = 60
        
        triggered = self.events_engine.check_trigger('test_threshold', state)
        self.assertTrue(triggered)
    
    def test_check_all_events(self):
        """Test checking all events."""
        state = GameState()
        state.turn = 5
        state.money = 500
        
        triggered = self.events_engine.check_all_events(state)
        self.assertIn('test_crisis', triggered)
    
    def test_no_repeat_trigger(self):
        """Test events don't trigger twice."""
        state = GameState()
        state.turn = 5
        state.money = 500
        
        triggered1 = self.events_engine.check_all_events(state)
        self.assertEqual(len(triggered1), 1)
        
        triggered2 = self.events_engine.check_all_events(state)
        self.assertEqual(len(triggered2), 0)  # Already triggered
    
    def test_execute_event_choice(self):
        """Test executing event choice."""
        state = GameState()
        state.money = 1000
        
        result = self.events_engine.execute_event_choice(
            'test_crisis',
            'fix',
            state,
            self.engine
        )
        
        self.assertTrue(result.triggered)
        self.assertEqual(state.money, 1500)  # +500
    
    def test_execute_normal_event(self):
        """Test normal event execution."""
        state = GameState()
        
        result = self.events_engine.execute_normal_event(
            'test_threshold',
            state,
            self.engine
        )
        
        self.assertTrue(result.triggered)
        self.assertIn('Threshold', result.message)
    
    def test_is_popup_event(self):
        """Test popup event detection."""
        self.assertTrue(self.events_engine.is_popup_event('test_crisis'))
        self.assertFalse(self.events_engine.is_popup_event('test_threshold'))


class TestEventsEngineIntegration(unittest.TestCase):
    """Test with real events.json."""
    
    def test_load_real_events(self):
        """Test loading real events."""
        try:
            engine = EventsEngine(seed=42)
            events = list(engine.events.keys())
            
            self.assertIn('funding_crisis', events)
            self.assertGreater(len(events), 0)
        except FileNotFoundError:
            self.skipTest("events.json not found")
    
    def test_funding_crisis_trigger(self):
        """Test real funding crisis event."""
        try:
            events_engine = EventsEngine(seed=42)
            mock_engine = MockEngine()
            
            state = GameState()
            state.turn = 10
            state.money = 30000
            
            triggered = events_engine.check_all_events(state)
            self.assertIn('funding_crisis', triggered)
        except FileNotFoundError:
            self.skipTest("events.json not found")


if __name__ == '__main__':
    unittest.main()

    