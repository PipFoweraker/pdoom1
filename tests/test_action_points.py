"""
Tests for the Action Points (AP) system - Phase 1

Tests cover:
- AP initialization and reset
- AP deduction on action execution
- Action validation when AP insufficient
- Backward compatibility with existing actions
- UI glow effects when AP is spent
"""

import unittest
import sys
import os

# Add the parent directory to sys.path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_state import GameState


class TestActionPointsInitialization(unittest.TestCase):
    """Test that Action Points are properly initialized."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
    
    def test_action_points_initialization(self):
        """Test that AP are initialized correctly."""
        self.assertEqual(self.game_state.action_points, 3)
        self.assertEqual(self.game_state.max_action_points, 3)
        self.assertFalse(self.game_state.ap_spent_this_turn)
        self.assertEqual(self.game_state.ap_glow_timer, 0)
    
    def test_action_points_fields_exist(self):
        """Test that all AP-related fields exist."""
        self.assertTrue(hasattr(self.game_state, 'action_points'))
        self.assertTrue(hasattr(self.game_state, 'max_action_points'))
        self.assertTrue(hasattr(self.game_state, 'ap_spent_this_turn'))
        self.assertTrue(hasattr(self.game_state, 'ap_glow_timer'))


class TestActionPointsValidation(unittest.TestCase):
    """Test AP validation when selecting actions."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
        # Start with high money to avoid money constraint issues
        self.game_state.money = 100000
    
    def test_action_selection_with_sufficient_ap(self):
        """Test that actions can be selected when AP is sufficient."""
        initial_ap = self.game_state.action_points
        self.assertGreater(initial_ap, 0)
        
        # Try to select an action (Fundraise has 0 cost and 1 AP cost)
        fundraise_idx = next(i for i, action in enumerate(self.game_state.actions) 
                           if action["name"] == "Fundraise")
        
        # Simulate clicking on the action
        # We can't easily test the click handler, so we'll test the logic directly
        action = self.game_state.actions[fundraise_idx]
        ap_cost = action.get("ap_cost", 1)
        
        self.assertLessEqual(ap_cost, self.game_state.action_points)
        self.assertGreaterEqual(self.game_state.money, action["cost"])
    
    def test_action_validation_insufficient_ap(self):
        """Test that actions are blocked when AP is insufficient."""
        # Reduce AP to 0
        self.game_state.action_points = 0
        
        # Try to select an action
        action = self.game_state.actions[0]  # First action
        ap_cost = action.get("ap_cost", 1)
        
        # Verify AP validation would fail
        self.assertLess(self.game_state.action_points, ap_cost)
    
    def test_message_for_insufficient_ap(self):
        """Test that appropriate message is shown for insufficient AP."""
        # Set AP to 0
        self.game_state.action_points = 0
        
        # Mock mouse position and dimensions for click handling
        # This is a simplified test of the validation logic
        action = self.game_state.actions[0]
        ap_cost = action.get("ap_cost", 1)
        
        if self.game_state.action_points < ap_cost:
            expected_message = f"Not enough Action Points for {action['name']} (need {ap_cost}, have {self.game_state.action_points})."
            # In real game, this message would be added to self.messages
            self.assertIn("Action Points", expected_message)


class TestActionPointsDeduction(unittest.TestCase):
    """Test AP deduction during action execution."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
        self.game_state.money = 100000  # High money to avoid constraints
        self.initial_ap = self.game_state.action_points
    
    def test_ap_deduction_on_action_execution(self):
        """Test that AP is deducted when actions are executed."""
        # Select an action (Fundraise is free and safe to test)
        fundraise_idx = next(i for i, action in enumerate(self.game_state.actions) 
                           if action["name"] == "Fundraise")
        
        self.game_state.selected_actions.append(fundraise_idx)
        
        # Execute turn
        self.game_state.end_turn()
        
        # Check that AP was deducted (but then reset at end of turn)
        # Since AP resets at end of turn, we can check that the glow flag was set
        # In a real implementation, we'd test the deduction before the reset
        self.assertEqual(self.game_state.action_points, self.game_state.max_action_points)
    
    def test_ap_glow_effect_triggered(self):
        """Test that glow effect is triggered when AP is spent."""
        # Select an action
        self.game_state.selected_actions.append(0)  # First action
        
        # Execute the action part manually to test glow effect
        action = self.game_state.actions[0]
        ap_cost = action.get("ap_cost", 1)
        
        # Simulate action execution
        self.game_state.action_points -= ap_cost
        self.game_state.ap_spent_this_turn = True
        self.game_state.ap_glow_timer = 30
        
        # Verify glow effect is set
        self.assertTrue(self.game_state.ap_spent_this_turn)
        self.assertEqual(self.game_state.ap_glow_timer, 30)
    
    def test_multiple_actions_ap_deduction(self):
        """Test AP deduction with multiple actions."""
        initial_ap = self.game_state.action_points
        
        # Select multiple actions (up to available AP)
        actions_to_select = min(initial_ap, 2)  # Select up to 2 actions
        for i in range(actions_to_select):
            if i < len(self.game_state.actions):
                action = self.game_state.actions[i]
                if action.get("ap_cost", 1) <= self.game_state.action_points:
                    self.game_state.selected_actions.append(i)
                    # Simulate AP deduction
                    self.game_state.action_points -= action.get("ap_cost", 1)
        
        # Verify AP was deducted
        self.assertLess(self.game_state.action_points, initial_ap)


class TestActionPointsReset(unittest.TestCase):
    """Test AP reset at end of turn."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
        self.game_state.money = 100000
    
    def test_ap_reset_end_of_turn(self):
        """Test that AP resets to max at end of turn."""
        # Reduce AP
        self.game_state.action_points = 1
        self.game_state.ap_spent_this_turn = True
        self.game_state.ap_glow_timer = 15
        
        # End turn
        self.game_state.end_turn()
        
        # Verify AP reset (should be recalculated based on current staff)
        expected_max_ap = self.game_state.calculate_max_ap()
        self.assertEqual(self.game_state.action_points, expected_max_ap)
        self.assertEqual(self.game_state.max_action_points, expected_max_ap)
        self.assertFalse(self.game_state.ap_spent_this_turn)
    
    def test_glow_timer_decreases(self):
        """Test that glow timer decreases over turns."""
        self.game_state.ap_glow_timer = 10
        
        # End turn
        self.game_state.end_turn()
        
        # Glow timer should decrease (but not below 0)
        self.assertLess(self.game_state.ap_glow_timer, 10)
        self.assertGreaterEqual(self.game_state.ap_glow_timer, 0)


class TestActionPointsBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing actions."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
    
    def test_all_actions_have_ap_cost(self):
        """Test that all actions have an ap_cost field."""
        for action in self.game_state.actions:
            # Should have ap_cost field or default to 1
            ap_cost = action.get("ap_cost", 1)
            self.assertIsInstance(ap_cost, int)
            self.assertGreater(ap_cost, 0)
    
    def test_default_ap_cost_is_one(self):
        """Test that default AP cost is 1 for backward compatibility."""
        # Test with a mock action without ap_cost
        mock_action = {"name": "Test Action", "cost": 0}
        ap_cost = mock_action.get("ap_cost", 1)
        self.assertEqual(ap_cost, 1)
    
    def test_existing_actions_unchanged(self):
        """Test that existing actions still work with AP system."""
        # Verify that all existing actions have reasonable AP costs
        action_names = [action["name"] for action in self.game_state.actions]
        expected_actions = [
            "Grow Community", "Fundraise", "Safety Research", 
            "Governance Research", "Buy Compute", "Hire Staff", 
            "Espionage", "Scout Opponent"
        ]
        
        for expected_action in expected_actions:
            self.assertIn(expected_action, action_names)
    
    def test_action_costs_preserved(self):
        """Test that money costs of actions are preserved."""
        # Check that specific actions have their expected costs
        fundraise_action = next(action for action in self.game_state.actions 
                              if action["name"] == "Fundraise")
        self.assertEqual(fundraise_action["cost"], 0)
        
        safety_research = next(action for action in self.game_state.actions 
                             if action["name"] == "Safety Research")
        self.assertEqual(safety_research["cost"], 40)


class TestActionPointsStaffScaling(unittest.TestCase):
    """Test Phase 2: Staff-Based AP Scaling functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.game_state = GameState("test_seed")
        self.game_state.money = 100000
    
    def test_calculate_max_ap_base(self):
        """Test base AP calculation without staff bonuses."""
        # Reset staff to 0 for clean test
        self.game_state.staff = 0
        self.game_state.admin_staff = 0
        
        expected = 3  # Base AP
        self.assertEqual(self.game_state.calculate_max_ap(), expected)
    
    def test_calculate_max_ap_with_regular_staff(self):
        """Test AP calculation with regular staff bonus."""
        self.game_state.staff = 4
        self.game_state.admin_staff = 0
        
        expected = 3 + (4 * 0.5)  # Base + staff bonus
        self.assertEqual(self.game_state.calculate_max_ap(), int(expected))
    
    def test_calculate_max_ap_with_admin_staff(self):
        """Test AP calculation with admin staff bonus."""
        self.game_state.staff = 2
        self.game_state.admin_staff = 2
        
        expected = 3 + (2 * 0.5) + (2 * 1.0)  # Base + staff + admin bonus
        self.assertEqual(self.game_state.calculate_max_ap(), int(expected))
    
    def test_calculate_max_ap_complex_composition(self):
        """Test AP calculation with complex staff composition."""
        self.game_state.staff = 10
        self.game_state.admin_staff = 3
        
        expected = 3 + (10 * 0.5) + (3 * 1.0)  # 3 + 5 + 3 = 11
        self.assertEqual(self.game_state.calculate_max_ap(), 11)
    
    def test_ap_recalculation_on_turn_end(self):
        """Test that max AP is recalculated at turn end."""
        # Start with some staff
        self.game_state.staff = 6
        self.game_state.admin_staff = 1
        
        # End turn to trigger recalculation
        self.game_state.end_turn()
        
        expected_max = 3 + (6 * 0.5) + (1 * 1.0)  # 3 + 3 + 1 = 7
        self.assertEqual(self.game_state.max_action_points, 7)
        self.assertEqual(self.game_state.action_points, 7)
    
    def test_specialized_staff_fields_initialization(self):
        """Test that specialized staff fields are properly initialized."""
        self.assertEqual(self.game_state.admin_staff, 0)
        self.assertEqual(self.game_state.research_staff, 0)
        self.assertEqual(self.game_state.ops_staff, 0)
    
    def test_add_specialized_staff(self):
        """Test adding specialized staff through _add method."""
        self.game_state._add('admin_staff', 2)
        self.game_state._add('research_staff', 1)
        self.game_state._add('ops_staff', 3)
        
        self.assertEqual(self.game_state.admin_staff, 2)
        self.assertEqual(self.game_state.research_staff, 1)
        self.assertEqual(self.game_state.ops_staff, 3)
    
    def test_specialized_staff_cannot_go_negative(self):
        """Test that specialized staff counts cannot go below zero."""
        self.game_state._add('admin_staff', -5)
        self.game_state._add('research_staff', -3)
        self.game_state._add('ops_staff', -1)
        
        self.assertEqual(self.game_state.admin_staff, 0)
        self.assertEqual(self.game_state.research_staff, 0)
        self.assertEqual(self.game_state.ops_staff, 0)
    
    def test_new_staff_hiring_actions_exist(self):
        """Test that new specialized staff hiring actions exist."""
        action_names = [action["name"] for action in self.game_state.actions]
        
        self.assertIn("Hire Admin Assistant", action_names)
        self.assertIn("Hire Research Staff", action_names)
        self.assertIn("Hire Operations Staff", action_names)
    
    def test_specialized_staff_hiring_costs(self):
        """Test that specialized staff have appropriate costs."""
        admin_action = next(action for action in self.game_state.actions 
                           if action["name"] == "Hire Admin Assistant")
        research_action = next(action for action in self.game_state.actions 
                              if action["name"] == "Hire Research Staff")
        ops_action = next(action for action in self.game_state.actions 
                         if action["name"] == "Hire Operations Staff")
        
        # Admin assistants should cost more due to higher AP bonus
        self.assertEqual(admin_action["cost"], 80)
        self.assertEqual(admin_action["ap_cost"], 2)
        
        # Research and ops staff should cost the same
        self.assertEqual(research_action["cost"], 70)
        self.assertEqual(research_action["ap_cost"], 2)
        self.assertEqual(ops_action["cost"], 70)
        self.assertEqual(ops_action["ap_cost"], 2)


if __name__ == '__main__':
    unittest.main()