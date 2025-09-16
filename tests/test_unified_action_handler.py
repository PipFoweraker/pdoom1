"""
Tests for the unified action handler system and global per-turn action point limits.

Tests cover:
- Unified action selection for mouse and keyboard
- Immediate AP deduction on action selection
- Undo/unclick functionality with AP refund
- Sound feedback behavior (click on selection, no sound on undo)
- UI state updates and button enabling/disabling
- Action usage indicators
- Edge cases and error handling
"""

import unittest
import sys
import os

# Add the parent directory to sys.path so we can import the game modules  
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game_state import GameState


class TestUnifiedActionHandler(unittest.TestCase):
    """Test the unified action handler functionality."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
        self.game_state.money = 100000  # High money to avoid constraints
    
    def test_action_selection_success(self):
        """Test successful action selection through unified handler."""
        initial_ap = self.game_state.action_points
        
        result = self.game_state.attempt_action_selection(0, is_undo=False)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['play_sound'])
        self.assertIn("Selected:", result['message'])
        self.assertEqual(self.game_state.action_points, initial_ap - 1)
        self.assertIn(0, self.game_state.selected_gameplay_actions)
        self.assertEqual(len(self.game_state.selected_gameplay_action_instances), 1)
    
    def test_action_selection_insufficient_ap(self):
        """Test action selection when AP is insufficient."""
        self.game_state.action_points = 0
        
        result = self.game_state.attempt_action_selection(0, is_undo=False)
        
        self.assertFalse(result['success'])
        self.assertFalse(result['play_sound'])
        self.assertIn("Not enough Action Points", result['message'])
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 0)
        self.assertEqual(len(self.game_state.selected_gameplay_action_instances), 0)
    
    def test_action_selection_insufficient_money(self):
        """Test action selection when money is insufficient."""
        self.game_state.money = 1
        safety_idx = next(i for i, action in enumerate(self.game_state.actions) 
                         if action["name"] == "Safety Research")
        
        result = self.game_state.attempt_action_selection(safety_idx, is_undo=False)
        
        self.assertFalse(result['success'])
        self.assertFalse(result['play_sound'])
        self.assertIn("Not enough money", result['message'])
    
    def test_action_undo_success(self):
        """Test successful action undo through unified handler."""
        # First select an action
        self.game_state.attempt_action_selection(0, is_undo=False)
        initial_ap = self.game_state.action_points
        
        # Then undo it
        result = self.game_state.attempt_action_selection(0, is_undo=True)
        
        self.assertTrue(result['success'])
        self.assertFalse(result['play_sound'])  # No sound on undo
        self.assertIn("Undid:", result['message'])
        self.assertIn("refunded", result['message'])
        self.assertEqual(self.game_state.action_points, initial_ap + 1)
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 0)
        self.assertEqual(len(self.game_state.selected_gameplay_action_instances), 0)
    
    def test_action_undo_no_instance(self):
        """Test undo when no instance of action exists."""
        result = self.game_state.attempt_action_selection(0, is_undo=True)
        
        self.assertFalse(result['success'])
        self.assertFalse(result['play_sound'])
        self.assertIn("No selected instance", result['message'])
    
    def test_multiple_action_instances(self):
        """Test selecting the same action multiple times."""
        # Select same action three times
        for _ in range(3):
            result = self.game_state.attempt_action_selection(0, is_undo=False)
            self.assertTrue(result['success'])
        
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 3)
        self.assertEqual(len(self.game_state.selected_gameplay_action_instances), 3)
        self.assertEqual(self.game_state.action_points, 0)  # Started with 3 AP
        
        # Undo one instance
        result = self.game_state.attempt_action_selection(0, is_undo=True)
        self.assertTrue(result['success'])
        
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 2)
        self.assertEqual(len(self.game_state.selected_gameplay_action_instances), 2)
        self.assertEqual(self.game_state.action_points, 1)
    
    def test_keyboard_shortcut_integration(self):
        """Test keyboard shortcuts use unified handler."""
        initial_ap = self.game_state.action_points
        
        success = self.game_state.execute_gameplay_action_by_keyboard(0)
        
        self.assertTrue(success)
        self.assertEqual(self.game_state.action_points, initial_ap - 1)
        self.assertIn(0, self.game_state.selected_gameplay_actions)
    
    def test_keyboard_shortcut_undo(self):
        """Test keyboard shortcut undo functionality."""
        # Select action first
        self.game_state.execute_gameplay_action_by_keyboard(0)
        initial_ap = self.game_state.action_points
        
        # Undo via keyboard (same key when action is selected)
        success = self.game_state.execute_gameplay_action_by_keyboard(0)
        
        self.assertTrue(success)
        self.assertEqual(self.game_state.action_points, initial_ap + 1)
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 0)
    
    def test_invalid_action_index(self):
        """Test handling of invalid action indices."""
        invalid_idx = len(self.game_state.actions) + 5
        
        result = self.game_state.attempt_action_selection(invalid_idx, is_undo=False)
        
        self.assertFalse(result['success'])
        self.assertFalse(result['play_sound'])
        self.assertIsNone(result['message'])
    
    def test_action_instances_cleared_on_turn_end(self):
        """Test that action instances are cleared at end of turn."""
        # Select some actions
        self.game_state.attempt_action_selection(0, is_undo=False)
        self.game_state.attempt_action_selection(1, is_undo=False)
        
        self.assertGreater(len(self.game_state.selected_gameplay_action_instances), 0)
        
        # End turn
        self.game_state.end_turn()
        
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 0)
        self.assertEqual(len(self.game_state.selected_gameplay_action_instances), 0)
        self.assertEqual(self.game_state.action_points, self.game_state.max_action_points)
    
    def test_delegation_in_unified_handler(self):
        """Test that delegation works through unified handler."""
        # Add ops staff to enable delegation for Buy Compute
        self.game_state.ops_staff = 1
        
        buy_compute_idx = next(i for i, action in enumerate(self.game_state.actions) 
                              if action["name"] == "Buy Compute")
        
        result = self.game_state.attempt_action_selection(buy_compute_idx, is_undo=False)
        
        self.assertTrue(result['success'])
        self.assertIn("delegated", result['message'])
        # Buy Compute delegated costs 0 AP, so AP should not decrease
        self.assertEqual(self.game_state.action_points, 3)


class TestUIButtonStates(unittest.TestCase):
    """Test UI button state updates based on AP availability."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
        self.game_state.money = 100000
    
    def test_selected_gameplay_action_instances_attribute(self):
        """Test that selected_gameplay_action_instances attribute exists and is initialized."""
        self.assertTrue(hasattr(self.game_state, 'selected_gameplay_action_instances'))
        self.assertEqual(len(self.game_state.selected_gameplay_action_instances), 0)
    
    def test_action_instance_tracking(self):
        """Test that action instances are tracked correctly for UI."""
        # Select same action twice (uses 2 AP)
        for i in range(2):
            self.game_state.attempt_action_selection(0, is_undo=False)
        
        # Count instances of action 0
        action_0_count = sum(1 for inst in self.game_state.selected_gameplay_action_instances 
                            if inst['action_idx'] == 0)
        self.assertEqual(action_0_count, 2)
        
        # Select different action (uses 1 more AP, total 3 AP used)
        result = self.game_state.attempt_action_selection(1, is_undo=False)
        self.assertTrue(result['success'])  # Should succeed with 1 AP remaining
        
        action_1_count = sum(1 for inst in self.game_state.selected_gameplay_action_instances 
                            if inst['action_idx'] == 1)
        self.assertEqual(action_1_count, 1)


class TestSoundBehavior(unittest.TestCase):
    """Test sound feedback behavior."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
        self.game_state.money = 100000
    
    def test_sound_on_selection(self):
        """Test that play_sound is True for successful selections."""
        result = self.game_state.attempt_action_selection(0, is_undo=False)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['play_sound'])
    
    def test_no_sound_on_undo(self):
        """Test that play_sound is False for undo operations."""
        # Select first
        self.game_state.attempt_action_selection(0, is_undo=False)
        
        # Then undo
        result = self.game_state.attempt_action_selection(0, is_undo=True)
        
        self.assertTrue(result['success'])
        self.assertFalse(result['play_sound'])
    
    def test_no_sound_on_failure(self):
        """Test that play_sound is False for failed selections."""
        self.game_state.action_points = 0
        
        result = self.game_state.attempt_action_selection(0, is_undo=False)
        
        self.assertFalse(result['success'])
        self.assertFalse(result['play_sound'])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
        self.game_state.money = 100000
    
    def test_undo_most_recent_instance(self):
        """Test that undo removes the most recent instance of an action."""
        # Select action 0 twice, then action 1 (uses all 3 AP)
        self.game_state.attempt_action_selection(0, is_undo=False)  # instance_id: 0
        self.game_state.attempt_action_selection(0, is_undo=False)  # instance_id: 1
        self.game_state.attempt_action_selection(1, is_undo=False)  # instance_id: 2
        
        # Undo action 0 - should remove most recent instance (instance_id: 1)
        result = self.game_state.attempt_action_selection(0, is_undo=True)
        
        self.assertTrue(result['success'])
        # Should still have 1 instance of action 0 (instance_id: 0)
        action_0_count = sum(1 for inst in self.game_state.selected_gameplay_action_instances 
                            if inst['action_idx'] == 0)
        self.assertEqual(action_0_count, 1)
        
        # Total instances should be 2 (1 action 0 + 1 action 1)
        self.assertEqual(len(self.game_state.selected_gameplay_action_instances), 2)
    
    def test_game_over_state(self):
        """Test that actions cannot be executed when game is over."""
        self.game_state.game_over = True
        
        success = self.game_state.execute_gameplay_action_by_keyboard(0)
        self.assertFalse(success)
    
    def test_rapid_toggling(self):
        """Test rapid selection and undo of the same action."""
        initial_ap = self.game_state.action_points
        
        # Select and undo same action multiple times
        for _ in range(5):
            # Select
            result1 = self.game_state.attempt_action_selection(0, is_undo=False)
            self.assertTrue(result1['success'])
            
            # Undo
            result2 = self.game_state.attempt_action_selection(0, is_undo=True)
            self.assertTrue(result2['success'])
        
        # Should be back to initial state
        self.assertEqual(self.game_state.action_points, initial_ap)
        self.assertEqual(len(self.game_state.selected_gameplay_actions), 0)
        self.assertEqual(len(self.game_state.selected_gameplay_action_instances), 0)
    
    def test_undoing_last_ap(self):
        """Test undoing when it's the last available action point."""
        # Use up all but 1 AP
        for _ in range(2):
            self.game_state.attempt_action_selection(0, is_undo=False)
        
        self.assertEqual(self.game_state.action_points, 1)
        
        # Select last AP
        result = self.game_state.attempt_action_selection(1, is_undo=False)
        self.assertTrue(result['success'])
        self.assertEqual(self.game_state.action_points, 0)
        
        # Undo should refund AP
        result = self.game_state.attempt_action_selection(1, is_undo=True)
        self.assertTrue(result['success'])
        self.assertEqual(self.game_state.action_points, 1)


if __name__ == '__main__':
    unittest.main()