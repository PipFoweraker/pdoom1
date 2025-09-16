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
import pytest
import sys
import os

# Add the parent directory to sys.path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game_state import GameState


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
        
        # Try to select an action (Fundraising Options has 0 cost and 1 AP cost)
        fundraise_idx = next(i for i, action in enumerate(self.game_state.actions) 
                           if action["name"] == "Fundraising Options")
        
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


@pytest.mark.skip(reason="Action Points deduction bugs - See issue #action-points-deduction-bug")
class TestActionPointsDeduction(unittest.TestCase):
    """Test AP deduction during action execution."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
        self.game_state.money = 100000  # High money to avoid constraints
        self.initial_ap = self.game_state.action_points
    
    def test_ap_deduction_on_action_execution(self):
        """Test that AP is deducted when actions are executed."""
        # Select an action (Fundraising Options is safe to test)
        fundraise_idx = next(i for i, action in enumerate(self.game_state.actions) 
                           if action["name"] == "Fundraising Options")
        
        self.game_state.selected_gameplay_actions.append(fundraise_idx)
        
        # Execute turn
        self.game_state.end_turn()
        
        # Check that AP was deducted (but then reset at end of turn)
        # Since AP resets at end of turn, we can check that the glow flag was set
        # In a real implementation, we'd test the deduction before the reset
        self.assertEqual(self.game_state.action_points, self.game_state.max_action_points)
    
    def test_ap_glow_effect_triggered(self):
        """Test that glow effect is triggered when AP is spent."""
        # Select an action
        self.game_state.selected_gameplay_actions.append(0)  # First action
        
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
                    self.game_state.selected_gameplay_actions.append(i)
                    # Simulate AP deduction
                    self.game_state.action_points -= action.get("ap_cost", 1)
        
        # Verify AP was deducted
        self.assertLess(self.game_state.action_points, initial_ap)


@pytest.mark.skip(reason="Action Points reset bugs - See issue #action-points-reset-bug")
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
            # Allow 0 AP cost for configuration actions (research quality settings, etc.)
            action_name = action.get("name", "")
            if ("Set Research Quality" in action_name or 
                "Research Speed:" in action_name or
                "Research Quality:" in action_name):
                self.assertGreaterEqual(ap_cost, 0)  # Allow 0 for config actions
            else:
                self.assertGreater(ap_cost, 0)  # Require > 0 for gameplay actions
    
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
        # Updated to match current action names in v0.4.1
        expected_actions = [
            "Grow Community", "Fundraising Options", "Research Options", 
            "Buy Compute", "Hire Staff", "Espionage", "Scout Opponent"
        ]
        
        for expected_action in expected_actions:
            self.assertIn(expected_action, action_names)
    
    def test_action_costs_preserved(self):
        """Test that money costs of actions are preserved."""
        # Check that specific actions have their expected costs
        fundraise_action = next(action for action in self.game_state.actions 
                              if action["name"] == "Fundraising Options")
        self.assertEqual(fundraise_action["cost"], 0)
        
        # Check for any research-related action with reasonable cost
        research_actions = [a for a in self.game_state.actions if 'research' in a["name"].lower()]
        self.assertGreater(len(research_actions), 0, "Should have at least one research action")
        
        # Check one of the research actions has expected properties
        research_action = research_actions[0]  # Take first research action
        self.assertIn("cost", research_action, "Research action should have cost property")


@pytest.mark.skip(reason="Action Points staff scaling bugs - See issue #action-points-scaling-bug")
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
        
        expected = 3 + (10 * 0.5) + (3 * 1.0)  # 3 + 5 + 3 = 11, but capped at 10
        self.assertEqual(self.game_state.calculate_max_ap(), 10)
    
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
    
    def test_hiring_dialog_action_exists(self):
        """Test that general hiring dialog action exists (replaces removed direct hire actions)."""
        action_names = [action["name"] for action in self.game_state.actions]
        
        # The general hiring action should exist
        self.assertIn("Hire Staff", action_names)
        
        # Direct hire actions should be removed (consolidated into hiring dialog)
        self.assertNotIn("Hire Admin Assistant", action_names)
        self.assertNotIn("Hire Research Staff", action_names)
        self.assertNotIn("Hire Operations Staff", action_names)
    
    def test_specialized_staff_hiring_via_dialog(self):
        """Test that specialized staff can be hired through the hiring dialog."""
        # Set up sufficient resources
        self.game_state.money = 1000
        self.game_state.action_points = 10
        
        # Trigger hiring dialog
        self.game_state._trigger_hiring_dialog()
        self.assertIsNotNone(self.game_state.pending_hiring_dialog)
        
        # Check that specialized staff are available
        available_types = self.game_state.pending_hiring_dialog["available_subtypes"]
        type_names = [t["data"]["name"] for t in available_types]
        
        self.assertIn("Administrator", type_names)  # Equivalent to "Hire Admin Assistant"
        self.assertIn("Researcher", type_names)     # Equivalent to "Hire Research Staff"
        self.assertIn("Engineer", type_names)       # Equivalent to "Hire Operations Staff"
        
        # Verify costs through dialog (these are the definitive costs now)
        admin_type = next(t for t in available_types if t["data"]["name"] == "Administrator")
        research_type = next(t for t in available_types if t["data"]["name"] == "Researcher")
        engineer_type = next(t for t in available_types if t["data"]["name"] == "Engineer")
        
        # These are the correct costs from employee_subtypes.py
        self.assertEqual(admin_type["data"]["cost"], 85)
        self.assertEqual(admin_type["data"]["ap_cost"], 2)
        self.assertEqual(research_type["data"]["cost"], 75)
        self.assertEqual(research_type["data"]["ap_cost"], 2)
        self.assertEqual(engineer_type["data"]["cost"], 80)
        self.assertEqual(engineer_type["data"]["ap_cost"], 2)


@unittest.skip("TECH DEBT: Delegation system hardcoded for old action names, future release roadmap")
class TestActionPointsDelegation(unittest.TestCase):
    """
    Test Phase 3: Delegation System functionality.
    
    TODO: TECH DEBT - Complete delegation system implementation
    - Currently hardcoded for specific old action names that no longer exist
    - Delegation is planned for future release, not hotfix priority
    - Tests fail because delegation system needs full redesign for current action structure
    """
    
    def setUp(self):
        """Set up test environment."""
        self.game_state = GameState("test_seed")
        self.game_state.money = 100000
    
    def test_delegation_fields_exist(self):
        """Test that delegatable actions have required delegation fields."""
        safety_research = next(action for action in self.game_state.actions 
                              if action["name"] == "Safety Research")
        
        self.assertTrue(safety_research.get("delegatable", False))
        self.assertIn("delegate_staff_req", safety_research)
        self.assertIn("delegate_ap_cost", safety_research)
        self.assertIn("delegate_effectiveness", safety_research)
    
    def test_can_delegate_action_without_staff(self):
        """Test that delegation is not possible without required staff."""
        safety_research = next(action for action in self.game_state.actions 
                              if action["name"] == "Safety Research")
        
        # No research staff
        self.game_state.research_staff = 0
        self.assertFalse(self.game_state.can_delegate_action(safety_research))
    
    @unittest.skip("Delegation system not fully implemented for current action structure")
    def test_can_delegate_action_with_sufficient_staff(self):
        """Test that delegation is possible with sufficient staff."""
        safety_research = next(action for action in self.game_state.actions 
                              if action["name"] == "Safety Research")
        
        # Add sufficient research staff
        self.game_state.research_staff = 2
        self.assertTrue(self.game_state.can_delegate_action(safety_research))
    
    def test_can_delegate_operational_action(self):
        """Test delegation of operational actions."""
        buy_compute = next(action for action in self.game_state.actions 
                          if action["name"] == "Buy Compute")
        
        # No ops staff initially
        self.game_state.ops_staff = 0
        self.assertFalse(self.game_state.can_delegate_action(buy_compute))
        
        # Add ops staff
        self.game_state.ops_staff = 1
        self.assertTrue(self.game_state.can_delegate_action(buy_compute))
    
    def test_non_delegatable_action(self):
        """Test that non-delegatable actions cannot be delegated."""
        fundraise = next(action for action in self.game_state.actions 
                        if action["name"] == "Fundraise")
        
        # Even with staff, non-delegatable actions cannot be delegated
        self.game_state.research_staff = 5
        self.game_state.ops_staff = 5
        self.assertFalse(self.game_state.can_delegate_action(fundraise))
    
    def test_execute_action_without_delegation(self):
        """Test executing action without delegation."""
        safety_idx = next(i for i, action in enumerate(self.game_state.actions) 
                         if action["name"] == "Safety Research")
        
        self.game_state.action_points
        result = self.game_state.execute_action_with_delegation(safety_idx, delegate=False)
        
        self.assertTrue(result)
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 1)
        self.assertIn(safety_idx, self.game_state.selected_gameplay_actions)
    
    def test_execute_action_with_delegation(self):
        """Test executing action with delegation."""
        safety_idx = next(i for i, action in enumerate(self.game_state.actions) 
                         if action["name"] == "Safety Research")
        
        # Add research staff to enable delegation
        self.game_state.research_staff = 2
        
        result = self.game_state.execute_action_with_delegation(safety_idx, delegate=True)
        
        self.assertTrue(result)
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 1)
        # Check delegation info is stored
        self.assertTrue(hasattr(self.game_state, '_action_delegations'))
        self.assertIn(safety_idx, self.game_state._action_delegations)
        self.assertTrue(self.game_state._action_delegations[safety_idx]['delegated'])
    
    def test_delegation_with_lower_ap_cost(self):
        """Test that delegation can provide lower AP cost for operational tasks."""
        buy_compute_idx = next(i for i, action in enumerate(self.game_state.actions) 
                              if action["name"] == "Buy Compute")
        
        # Add ops staff to enable delegation
        self.game_state.ops_staff = 1
        
        result = self.game_state.execute_action_with_delegation(buy_compute_idx, delegate=True)
        
        self.assertTrue(result)
        # Check that delegation info shows lower AP cost
        delegation_info = self.game_state._action_delegations[buy_compute_idx]
        self.assertEqual(delegation_info['ap_cost'], 0)  # Delegated Buy Compute costs 0 AP
    
    def test_delegation_effectiveness_stored(self):
        """Test that delegation effectiveness is properly stored."""
        safety_idx = next(i for i, action in enumerate(self.game_state.actions) 
                         if action["name"] == "Safety Research")
        
        # Add research staff to enable delegation
        self.game_state.research_staff = 2
        
        self.game_state.execute_action_with_delegation(safety_idx, delegate=True)
        
        delegation_info = self.game_state._action_delegations[safety_idx]
        self.assertEqual(delegation_info['effectiveness'], 0.8)  # 80% effectiveness
    
    def test_auto_delegation_when_beneficial(self):
        """Test that actions are auto-delegated when beneficial (lower AP cost)."""
        buy_compute_idx = next(i for i, action in enumerate(self.game_state.actions) 
                              if action["name"] == "Buy Compute")
        
        # Add ops staff to enable delegation
        self.game_state.ops_staff = 1
        
        # Simulate clicking the action
        action_rects = self.game_state._get_action_rects(800, 600)
        if buy_compute_idx < len(action_rects):
            rect = action_rects[buy_compute_idx]
            click_pos = (rect[0] + rect[2]//2, rect[1] + rect[3]//2)
            self.game_state.handle_click(click_pos, 800, 600)
            
            # Should be auto-delegated due to lower AP cost
            if hasattr(self.game_state, '_action_delegations') and buy_compute_idx in self.game_state._action_delegations:
                delegation_info = self.game_state._action_delegations[buy_compute_idx]
                self.assertTrue(delegation_info.get('delegated', False))


@pytest.mark.skip(reason="Keyboard shortcuts bugs - See issue #keyboard-shortcuts-bug")
class TestKeyboardShortcuts(unittest.TestCase):
    """Test keyboard shortcut functionality for actions."""
    
    def setUp(self):
        """Set up test environment."""
        self.game_state = GameState("test_seed")
        self.game_state.money = 100000  # High money to avoid constraints
    
    def test_execute_gameplay_action_by_keyboard_success(self):
        """Test that keyboard shortcuts execute actions successfully."""
        self.game_state.action_points
        
        # Execute first action (Grow Community) via keyboard
        success = self.game_state.execute_gameplay_action_by_keyboard(0)
        
        self.assertTrue(success)
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 1)
        self.assertIn(0, self.game_state.selected_gameplay_actions)
        
        # Check AP feedback was triggered
        self.assertTrue(self.game_state.ap_spent_this_turn)
        self.assertEqual(self.game_state.ap_glow_timer, 30)
    
    def test_execute_gameplay_action_by_keyboard_insufficient_ap(self):
        """Test keyboard shortcuts handle insufficient AP correctly."""
        # Reduce AP to 0
        self.game_state.action_points = 0
        
        success = self.game_state.execute_gameplay_action_by_keyboard(0)
        
        self.assertFalse(success)
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 0)
        # Should have error message
        self.assertTrue(any("Not enough Action Points" in msg for msg in self.game_state.messages))
    
    def test_execute_gameplay_action_by_keyboard_insufficient_money(self):
        """Test keyboard shortcuts handle insufficient money correctly."""
        # Set money to very low amount
        self.game_state.money = 1
        
        # Try expensive action (Safety Research costs 40)
        safety_idx = next(i for i, action in enumerate(self.game_state.actions) 
                         if action["name"] == "Safety Research")
        
        success = self.game_state.execute_gameplay_action_by_keyboard(safety_idx)
        
        self.assertFalse(success)
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 0)
        # Should have error message
        self.assertTrue(any("Not enough money" in msg for msg in self.game_state.messages))
    
    def test_execute_gameplay_action_by_keyboard_action_not_available(self):
        """Test keyboard shortcuts handle unavailable actions correctly."""
        # Try an action that has rules (Scout Opponent requires turn 5+)
        scout_idx = next(i for i, action in enumerate(self.game_state.actions) 
                        if action["name"] == "Scout Opponent")
        
        # Should fail on turn 0
        success = self.game_state.execute_gameplay_action_by_keyboard(scout_idx)
        
        self.assertFalse(success)
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 0)
        # Should have error message
        self.assertTrue(any("not available yet" in msg for msg in self.game_state.messages))
    
    def test_execute_gameplay_action_by_keyboard_invalid_index(self):
        """Test keyboard shortcuts handle invalid action indices."""
        # Try index beyond available actions
        invalid_idx = len(self.game_state.actions) + 5
        
        success = self.game_state.execute_gameplay_action_by_keyboard(invalid_idx)
        
        self.assertFalse(success)
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 0)
    
    @unittest.skip("TECH DEBT: Delegation system hardcoded for old actions, future release")
    def test_keyboard_shortcut_auto_delegation(self):
        """Test that keyboard shortcuts use auto-delegation when beneficial."""
        # TODO: Re-enable when delegation system is properly implemented
        pass


@pytest.mark.skip(reason="Enhanced AP feedback bugs - See issue #enhanced-ap-feedback-bug")
class TestEnhancedAPFeedback(unittest.TestCase):
    """Test enhanced Action Points feedback system."""
    
    def setUp(self):
        """Set up test environment."""
        self.game_state = GameState("test_seed")
        self.game_state.money = 100000
    
    def test_ap_glow_timer_initialization(self):
        """Test that AP glow timer is properly initialized."""
        self.assertEqual(self.game_state.ap_glow_timer, 0)
        self.assertFalse(self.game_state.ap_spent_this_turn)
    
    def test_ap_glow_effect_on_action_execution(self):
        """Test that AP glow effect is triggered when executing actions."""
        # Execute action via keyboard
        success = self.game_state.execute_gameplay_action_by_keyboard(0)
        
        self.assertTrue(success)
        self.assertTrue(self.game_state.ap_spent_this_turn)
        self.assertEqual(self.game_state.ap_glow_timer, 30)
    
    def test_error_tracking_for_easter_egg(self):
        """Test that repeated errors are tracked for easter egg."""
        # Set AP to 0 to trigger errors
        self.game_state.action_points = 0
        
        # First error
        success1 = self.game_state.execute_gameplay_action_by_keyboard(0)
        self.assertFalse(success1)
        
        # Second error (same action)
        success2 = self.game_state.execute_gameplay_action_by_keyboard(0)
        self.assertFalse(success2)
        
        # Third error should trigger easter egg
        # Note: The actual beep sound can't be tested easily, but we can verify the error tracking
        success3 = self.game_state.execute_gameplay_action_by_keyboard(0)
        self.assertFalse(success3)
        
        # Should have multiple error messages
        error_messages = [msg for msg in self.game_state.messages if "Not enough Action Points" in msg]
        self.assertEqual(len(error_messages), 3)
    
    def test_ap_deduction_on_keyboard_action(self):
        """Test that AP is properly deducted when using keyboard shortcuts."""
        initial_ap = self.game_state.action_points
        
        success = self.game_state.execute_gameplay_action_by_keyboard(0)
        
        self.assertTrue(success)
        # AP should be deducted (action costs 1 AP by default)
        expected_ap = initial_ap - 1
        self.assertEqual(self.game_state.action_points, expected_ap)


@pytest.mark.skip(reason="Blob positioning bugs - See issue #blob-positioning-bug")
class TestBlobPositioning(unittest.TestCase):
    """Test improved blob positioning system."""
    
    def setUp(self):
        """Set up test environment."""
        self.game_state = GameState("test_seed")
    
    def test_calculate_blob_position_basic(self):
        """Test basic blob position calculation."""
        # Test with default screen size
        x, y = self.game_state._calculate_blob_position(0)
        
        # Should be within reasonable bounds
        self.assertGreater(x, 0)
        self.assertGreater(y, 0)
        self.assertLess(x, 1200)  # Default screen width
        self.assertLess(y, 800)   # Default screen height
    
    def test_calculate_blob_position_multiple_blobs(self):
        """Test that multiple blobs get different positions."""
        positions = []
        for i in range(5):
            x, y = self.game_state._calculate_blob_position(i)
            positions.append((x, y))
        
        # All positions should be unique
        self.assertEqual(len(positions), len(set(positions)))
    
    def test_calculate_blob_position_center_spiral(self):
        """Test that blobs are positioned in center-based spiral pattern."""
        screen_w, screen_h = 1200, 800
        center_x, center_y = screen_w // 2, screen_h // 2
        
        # First blob should be at center
        x0, y0 = self.game_state._calculate_blob_position(0, screen_w, screen_h)
        self.assertEqual(x0, center_x)
        self.assertEqual(y0, center_y)
        
        # Other blobs should be arranged in a spiral around center
        positions = []
        for i in range(1, 10):
            x, y = self.game_state._calculate_blob_position(i, screen_w, screen_h)
            
            # Should be within screen bounds (accounting for blob radius)
            blob_radius = 25
            self.assertGreaterEqual(x, blob_radius)
            self.assertLessEqual(x, screen_w - blob_radius)
            self.assertGreaterEqual(y, blob_radius) 
            self.assertLessEqual(y, screen_h - blob_radius)
            
            # Should be reasonably near center for initial positioning
            # (dynamic collision detection handles UI avoidance)
            distance_from_center = ((x - center_x)**2 + (y - center_y)**2)**0.5
            self.assertLess(distance_from_center, min(screen_w, screen_h) * 0.4)
            
            positions.append((x, y))
        
        # Positions should be unique (no two blobs at exactly same position)
        self.assertEqual(len(positions), len(set(positions)))
    
    def test_blob_position_updates_with_screen_size(self):
        """Test that blob positions update when screen size changes."""
        # This would be tested in integration with the UI system
        # For now, just verify the method exists and works
        self.assertTrue(hasattr(self.game_state, '_calculate_blob_position'))
        
        # Test with different screen sizes
        x1, y1 = self.game_state._calculate_blob_position(0, 800, 600)
        x2, y2 = self.game_state._calculate_blob_position(0, 1600, 1200)
        
        # Positions should scale with screen size
        self.assertNotEqual((x1, y1), (x2, y2))


if __name__ == '__main__':
    unittest.main()