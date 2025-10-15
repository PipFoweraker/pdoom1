"""
tests/test_shared_logic/test_actions_engine.py

Tests for data-driven actions engine.
"""

import unittest
import json
import tempfile
from pathlib import Path
from shared.core.actions_engine import ActionsEngine, ActionResult
from shared.core.game_logic import GameState
from shared.core.engine_interface import MockEngine


class TestActionsEngine(unittest.TestCase):
    """Test ActionsEngine loading and execution."""
    
    def setUp(self):
        """Create test actions file."""
        self.engine = MockEngine()
        
        # Create temporary actions file
        self.temp_dir = tempfile.mkdtemp()
        self.actions_file = Path(self.temp_dir) / "test_actions.json"
        
        test_data = {
            "actions": {
                "test_hire": {
                    "id": "test_hire",
                    "name": "Test Hire",
                    "category": "hiring",
                    "costs": {"money": 1000},
                    "effects": {"safety": 5},
                    "messages": {
                        "success": "Hired successfully",
                        "insufficient_money": "Not enough money"
                    },
                    "sound": "hire"
                },
                "test_research": {
                    "id": "test_research",
                    "name": "Test Research",
                    "category": "research",
                    "costs": {"compute": 10},
                    "effects": {"capabilities": 3},
                    "requirements": {
                        "min_turn": 5
                    },
                    "messages": {
                        "success": "Research complete"
                    }
                }
            },
            "categories": {
                "hiring": {"name": "Hiring"},
                "research": {"name": "Research"}
            }
        }
        
        with open(self.actions_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        self.actions_engine = ActionsEngine(str(self.actions_file))
    
    def test_load_actions(self):
        """Test actions load from JSON."""
        self.assertEqual(len(self.actions_engine.actions), 2)
        self.assertIn('test_hire', self.actions_engine.actions)
        self.assertIn('test_research', self.actions_engine.actions)
    
    def test_get_action(self):
        """Test retrieving action definition."""
        action = self.actions_engine.get_action('test_hire')
        self.assertIsNotNone(action)
        self.assertEqual(action['name'], 'Test Hire')
        self.assertEqual(action['costs']['money'], 1000)
    
    def test_get_all_actions(self):
        """Test getting all action IDs."""
        actions = self.actions_engine.get_all_actions()
        self.assertEqual(len(actions), 2)
    
    def test_get_actions_by_category(self):
        """Test filtering actions by category."""
        hiring = self.actions_engine.get_actions_by_category('hiring')
        self.assertEqual(len(hiring), 1)
        self.assertEqual(hiring[0], 'test_hire')
    
    def test_check_requirements_pass(self):
        """Test requirements check when all met."""
        state = GameState()
        state.turn = 10
        state.money = 5000
        
        can_execute, reason = self.actions_engine.check_requirements('test_hire', state)
        self.assertTrue(can_execute)
        self.assertIsNone(reason)
    
    def test_check_requirements_fail_money(self):
        """Test requirements check fails on insufficient money."""
        state = GameState()
        state.money = 500  # Not enough
        
        can_execute, reason = self.actions_engine.check_requirements('test_hire', state)
        self.assertFalse(can_execute)
        self.assertIn('money', reason.lower())
    
    def test_check_requirements_fail_turn(self):
        """Test requirements check fails on turn requirement."""
        state = GameState()
        state.turn = 3  # Too early
        state.compute = 100
        
        can_execute, reason = self.actions_engine.check_requirements('test_research', state)
        self.assertFalse(can_execute)
        self.assertIn('turn', reason.lower())
    
    def test_execute_action_success(self):
        """Test successful action execution."""
        state = GameState()
        state.money = 5000
        initial_safety = state.safety
        
        result = self.actions_engine.execute_action('test_hire', state, self.engine)
        
        self.assertTrue(result.success)
        self.assertEqual(state.money, 4000)  # 5000 - 1000
        self.assertEqual(state.safety, initial_safety + 5)
        self.assertEqual(result.cost_paid['money'], 1000)
    
    def test_execute_action_insufficient_funds(self):
        """Test action fails with insufficient funds."""
        state = GameState()
        state.money = 500  # Not enough
        
        result = self.actions_engine.execute_action('test_hire', state, self.engine)
        
        self.assertFalse(result.success)
        self.assertEqual(state.money, 500)  # Unchanged
    
    def test_get_available_actions(self):
        """Test getting list of available actions."""
        state = GameState()
        state.turn = 10
        state.money = 5000
        state.compute = 100
        
        available = self.actions_engine.get_available_actions(state)
        
        self.assertIn('test_hire', available)
        self.assertIn('test_research', available)
    
    def test_get_available_actions_filtered(self):
        """Test available actions filtered by requirements."""
        state = GameState()
        state.turn = 2  # Before research requirement
        state.money = 5000
        
        available = self.actions_engine.get_available_actions(state)
        
        self.assertIn('test_hire', available)
        self.assertNotIn('test_research', available)


class TestActionsEngineIntegration(unittest.TestCase):
    """Test ActionsEngine with real actions.json."""
    
    def test_load_real_actions(self):
        """Test loading actual game actions."""
        # This will use shared/data/actions.json
        try:
            engine = ActionsEngine()
            actions = engine.get_all_actions()
            
            # Should have the actions we defined
            self.assertIn('hire_safety_researcher', actions)
            self.assertIn('fundraise', actions)
            self.assertGreater(len(actions), 0)
        except FileNotFoundError:
            self.skipTest("actions.json not found")
    
    def test_hire_safety_researcher_real(self):
        """Test real hire_safety_researcher action."""
        try:
            actions_engine = ActionsEngine()
            mock_engine = MockEngine()
            state = GameState()
            state.money = 100000
            
            result = actions_engine.execute_action(
                'hire_safety_researcher',
                state,
                mock_engine
            )
            
            self.assertTrue(result.success)
            self.assertEqual(state.money, 50000)
            self.assertEqual(state.safety, 2)
        except FileNotFoundError:
            self.skipTest("actions.json not found")


if __name__ == '__main__':
    unittest.main()