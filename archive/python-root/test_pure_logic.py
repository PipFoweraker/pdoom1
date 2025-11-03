"""
tests/test_shared_logic/test_game_logic.py

Tests for pure game logic - NO pygame/Godot dependencies.
Uses MockEngine to verify logic independently.
"""

import unittest
from shared.core.game_logic import GameLogic, GameState, TurnResult
from shared.core.engine_interface import MockEngine, MessageCategory, DialogOption, DialogResult


class TestGameState(unittest.TestCase):
    """Test GameState data structure."""
    
    def test_initialization(self):
        """Test GameState initializes with correct defaults."""
        state = GameState()
        
        self.assertEqual(state.turn, 0)
        self.assertEqual(state.money, 100000.0)
        self.assertEqual(state.compute, 100.0)
        self.assertEqual(state.safety, 0.0)
        self.assertEqual(state.capabilities, 0.0)
        self.assertFalse(state.game_over)
        self.assertFalse(state.victory)
    
    def test_serialization(self):
        """Test state can be saved and loaded."""
        state = GameState(turn=5, money=50000, safety=25)
        
        # Serialize
        data = state.to_dict()
        self.assertEqual(data['turn'], 5)
        self.assertEqual(data['money'], 50000)
        
        # Deserialize
        loaded = GameState.from_dict(data)
        self.assertEqual(loaded.turn, 5)
        self.assertEqual(loaded.money, 50000)
        self.assertEqual(loaded.safety, 25)
    
    def test_employee_count(self):
        """Test total employee calculation."""
        state = GameState()
        state.employees = {
            'safety_researchers': 3,
            'capabilities_researchers': 2,
        }
        
        self.assertEqual(state.get_total_employees(), 5)


class TestGameLogicTurnProcessing(unittest.TestCase):
    """Test turn processing logic."""
    
    def setUp(self):
        """Create fresh game logic for each test."""
        self.engine = MockEngine()
        self.logic = GameLogic(self.engine, seed="test")
    
    def test_turn_increment(self):
        """Test turn counter increments."""
        self.assertEqual(self.logic.state.turn, 0)
        
        result = self.logic.process_turn_end()
        
        self.assertTrue(result.success)
        self.assertEqual(self.logic.state.turn, 1)
        self.assertIn('turn', result.state_changes)
    
    def test_compute_consumption(self):
        """Test compute decreases each turn."""
        initial_compute = self.logic.state.compute
        
        result = self.logic.process_turn_end()
        
        self.assertEqual(
            self.logic.state.compute,
            initial_compute - self.logic.state.compute_rate
        )
        self.assertIn('compute', result.state_changes)
    
    def test_staff_maintenance(self):
        """Test staff maintenance costs money."""
        self.logic.state.employees['safety_researchers'] = 2
        initial_money = self.logic.state.money
        
        result = self.logic.process_turn_end()
        
        expected_cost = 2 * self.logic.state.staff_maintenance_cost
        self.assertEqual(
            self.logic.state.money,
            initial_money - expected_cost
        )
        self.assertIn('Staff maintenance', result.messages[0])
    
    def test_game_over_no_money(self):
        """Test game over when money runs out."""
        self.logic.state.money = 0
        
        result = self.logic.process_turn_end()
        
        self.assertTrue(result.game_over)
        self.assertTrue(self.logic.state.game_over)
        self.assertIn("GAME OVER", result.messages[0])
    
    def test_game_over_no_compute(self):
        """Test game over when compute runs out."""
        self.logic.state.compute = 0
        
        result = self.logic.process_turn_end()
        
        self.assertTrue(result.game_over)
        self.assertTrue(self.logic.state.game_over)
    
    def test_victory_condition(self):
        """Test victory when safety reaches 100."""
        self.logic.state.safety = 100
        
        result = self.logic.process_turn_end()
        
        self.assertTrue(result.victory)
        self.assertTrue(self.logic.state.victory)
        self.assertIn("VICTORY", result.messages[0])
    
    def test_engine_notifications(self):
        """Test engine receives state update notifications."""
        self.logic.process_turn_end()
        
        # Verify engine was notified
        self.assertEqual(self.engine.turn, 1)
        self.assertIn('money', self.engine.resources)
        self.assertIn('compute', self.engine.resources)


class TestGameLogicActions(unittest.TestCase):
    """Test action execution logic."""
    
    def setUp(self):
        """Create fresh game logic for each test."""
        self.engine = MockEngine()
        self.logic = GameLogic(self.engine, seed="test")
    
    def test_hire_safety_researcher_success(self):
        """Test hiring safety researcher."""
        initial_money = self.logic.state.money
        initial_safety = self.logic.state.safety
        
        result = self.logic.execute_action('hire_safety_researcher')
        
        self.assertTrue(result.success)
        self.assertEqual(self.logic.state.money, initial_money - 50000)
        self.assertEqual(self.logic.state.safety, initial_safety + 2)
        self.assertEqual(
            self.logic.state.employees['safety_researchers'],
            1
        )
        
        # Verify engine notifications
        self.assertIn('hire', self.engine.sounds_played)
        self.assertEqual(
            len([m for m in self.engine.messages if 'safety researcher' in m[0]]),
            1
        )
    
    def test_hire_safety_researcher_insufficient_funds(self):
        """Test hiring fails with insufficient funds."""
        self.logic.state.money = 1000  # Not enough
        
        result = self.logic.execute_action('hire_safety_researcher')
        
        self.assertFalse(result.success)
        self.assertEqual(
            self.logic.state.employees['safety_researchers'],
            0
        )
        
        # Verify warning message
        warnings = [m for m in self.engine.messages 
                   if m[1] == MessageCategory.WARNING]
        self.assertGreater(len(warnings), 0)
    
    def test_hire_capabilities_researcher(self):
        """Test hiring capabilities researcher."""
        result = self.logic.execute_action('hire_capabilities_researcher')
        
        self.assertTrue(result.success)
        self.assertEqual(self.logic.state.capabilities, 3)
        self.assertEqual(
            self.logic.state.employees['capabilities_researchers'],
            1
        )
    
    def test_purchase_compute(self):
        """Test purchasing compute."""
        initial_compute = self.logic.state.compute
        
        result = self.logic.execute_action('purchase_compute')
        
        self.assertTrue(result.success)
        self.assertEqual(self.logic.state.compute, initial_compute + 50)
        self.assertEqual(self.logic.state.money, 100000 - 10000)
    
    def test_fundraise(self):
        """Test fundraising action."""
        initial_money = self.logic.state.money
        
        result = self.logic.execute_action('fundraise')
        
        self.assertTrue(result.success)
        self.assertEqual(self.logic.state.money, initial_money + 100000)
        
        # Verify success message
        success_msgs = [m for m in self.engine.messages 
                       if m[1] == MessageCategory.SUCCESS]
        self.assertGreater(len(success_msgs), 0)
    
    def test_unknown_action(self):
        """Test handling of unknown action."""
        result = self.logic.execute_action('invalid_action')
        
        self.assertFalse(result.success)
        
        # Verify error message
        error_msgs = [m for m in self.engine.messages 
                     if m[1] == MessageCategory.ERROR]
        self.assertGreater(len(error_msgs), 0)
    
    def test_can_afford_action(self):
        """Test affordability checking."""
        self.assertTrue(
            self.logic.can_afford_action('hire_safety_researcher')
        )
        
        self.logic.state.money = 1000
        self.assertFalse(
            self.logic.can_afford_action('hire_safety_researcher')
        )
    
    def test_get_available_actions(self):
        """Test available actions based on state."""
        actions = self.logic.get_available_actions()
        
        self.assertIn('fundraise', actions)  # Always available
        self.assertIn('hire_safety_researcher', actions)
        
        # With low money
        self.logic.state.money = 5000
        actions = self.logic.get_available_actions()
        
        self.assertIn('fundraise', actions)
        self.assertNotIn('hire_safety_researcher', actions)


class TestGameLogicEvents(unittest.TestCase):
    """Test event system logic."""
    
    def setUp(self):
        """Create fresh game logic for each test."""
        self.engine = MockEngine()
        self.logic = GameLogic(self.engine, seed="test")
    
    def test_funding_crisis_trigger(self):
        """Test funding crisis event triggers at turn 10."""
        self.logic.state.turn = 10
        self.logic.state.money = 30000  # Low funds
        
        events = self.logic.check_events()
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['id'], 'funding_crisis')
        self.assertEqual(len(events[0]['options']), 2)
    
    def test_no_events_when_funded(self):
        """Test no crisis when well-funded."""
        self.logic.state.turn = 10
        self.logic.state.money = 100000  # Plenty of money
        
        events = self.logic.check_events()
        
        self.assertEqual(len(events), 0)
    
    def test_event_choice_emergency_fundraise(self):
        """Test emergency fundraising choice."""
        initial_money = self.logic.state.money
        
        result = self.logic.handle_event_choice(
            'funding_crisis',
            'emergency_fundraise'
        )
        
        self.assertTrue(result.success)
        self.assertEqual(self.logic.state.money, initial_money + 75000)
        self.assertIn('Emergency fundraising', result.messages[0])
    
    def test_event_choice_continue(self):
        """Test continuing without action."""
        initial_money = self.logic.state.money
        
        result = self.logic.handle_event_choice(
            'funding_crisis',
            'accept'
        )
        
        self.assertTrue(result.success)
        self.assertEqual(self.logic.state.money, initial_money)


class TestDeterministicBehavior(unittest.TestCase):
    """Test deterministic behavior with same seed."""
    
    def test_same_seed_same_results(self):
        """Test same seed produces identical results."""
        engine1 = MockEngine()
        logic1 = GameLogic(engine1, seed="test-123")
        
        engine2 = MockEngine()
        logic2 = GameLogic(engine2, seed="test-123")
        
        # Execute identical actions
        for _ in range(5):
            logic1.execute_action('hire_safety_researcher')
            logic1.process_turn_end()
            
            logic2.execute_action('hire_safety_researcher')
            logic2.process_turn_end()
        
        # Verify identical state
        self.assertEqual(logic1.state.turn, logic2.state.turn)
        self.assertEqual(logic1.state.money, logic2.state.money)
        self.assertEqual(logic1.state.safety, logic2.state.safety)


class TestIntegrationScenario(unittest.TestCase):
    """Test complete gameplay scenarios."""
    
    def test_basic_game_progression(self):
        """Test realistic game progression."""
        engine = MockEngine()
        logic = GameLogic(engine, seed="scenario-test")
        
        # Turn 1: Hire safety researcher
        result = logic.execute_action('hire_safety_researcher')
        self.assertTrue(result.success)
        
        # Turn 2: Buy compute
        result = logic.process_turn_end()
        self.assertTrue(result.success)
        
        result = logic.execute_action('purchase_compute')
        self.assertTrue(result.success)
        
        # Turn 3: Fundraise
        result = logic.process_turn_end()
        result = logic.execute_action('fundraise')
        self.assertTrue(result.success)
        
        # Verify progression
        self.assertEqual(logic.state.turn, 2)
        self.assertEqual(logic.state.employees['safety_researchers'], 1)
        self.assertGreater(logic.state.safety, 0)
        self.assertFalse(logic.state.game_over)


if __name__ == '__main__':
    unittest.main()
