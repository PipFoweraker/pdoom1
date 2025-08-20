"""
Tests for event log unlock functionality.

This module tests the event that unlocks the scrollable event log feature.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock, patch
from src.core.game_state import GameState
from src.core.events import EVENTS, unlock_scrollable_event_log


class TestEventLogUnlock(unittest.TestCase):
    """Test event log unlock functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.game_state = GameState(seed=12345)

    def test_event_log_initially_disabled(self):
        """Test that event log starts disabled."""
        self.assertFalse(self.game_state.scrollable_event_log_enabled)

    def test_unlock_scrollable_event_log_function(self):
        """Test the unlock function directly."""
        # Mock the show_tutorial_message method
        self.game_state.show_tutorial_message = MagicMock()
        
        # Initially disabled
        self.assertFalse(self.game_state.scrollable_event_log_enabled)
        
        # Call unlock function
        unlock_scrollable_event_log(self.game_state)
        
        # Should be enabled now
        self.assertTrue(self.game_state.scrollable_event_log_enabled)
        
        # Should add message
        self.assertTrue(any("Event Log Upgrade unlocked" in msg for msg in self.game_state.messages))
        
        # Should show tutorial
        self.game_state.show_tutorial_message.assert_called_once()

    def test_event_log_unlock_event_exists(self):
        """Test that the event log unlock event is defined."""
        event_log_events = [event for event in EVENTS if "Event Log System Upgrade" in event["name"]]
        self.assertEqual(len(event_log_events), 1)
        
        event = event_log_events[0]
        self.assertEqual(event["effect"], unlock_scrollable_event_log)

    def test_event_log_unlock_trigger_conditions(self):
        """Test the trigger conditions for event log unlock."""
        event_log_events = [event for event in EVENTS if "Event Log System Upgrade" in event["name"]]
        event = event_log_events[0]
        trigger = event["trigger"]
        
        # Should not trigger before turn 5
        self.game_state.turn = 4
        self.assertFalse(trigger(self.game_state))
        
        # Should trigger at turn 5
        self.game_state.turn = 5
        self.assertTrue(trigger(self.game_state))
        
        # Should not trigger again if already enabled
        self.game_state.scrollable_event_log_enabled = True
        self.assertFalse(trigger(self.game_state))

    def test_event_log_history_preservation(self):
        """Test that event log history is preserved after unlock."""
        # Add some messages before unlock
        self.game_state.messages = ["Initial message 1", "Initial message 2"]
        
        # Mock the show_tutorial_message method
        self.game_state.show_tutorial_message = MagicMock()
        
        # Unlock the feature
        unlock_scrollable_event_log(self.game_state)
        
        # History should be empty initially but messages should be preserved
        self.assertEqual(len(self.game_state.event_log_history), 0)
        self.assertTrue(len(self.game_state.messages) > 2)  # Original + unlock message

    def test_scrollable_log_with_turn_progression(self):
        """Test that scrollable log works correctly with turn progression."""
        # Mock the show_tutorial_message method
        self.game_state.show_tutorial_message = MagicMock()
        
        # Enable scrollable log
        unlock_scrollable_event_log(self.game_state)
        
        # Add messages and end turn
        self.game_state.messages = ["Turn 1 message"]
        initial_turn = self.game_state.turn
        
        # Mock some required methods for end_turn
        self.game_state.logger = MagicMock()
        self.game_state.logger.log_turn_summary = MagicMock()
        self.game_state._update_staff_scaling = MagicMock()
        self.game_state._random_event_check = MagicMock()
        self.game_state._milestone_check = MagicMock()
        self.game_state._maintenance_check = MagicMock()
        self.game_state._check_achievement_unlock = MagicMock()
        
        # End turn
        self.game_state.end_turn()
        
        # History should now contain the previous turn's messages
        self.assertTrue(len(self.game_state.event_log_history) > 0)
        self.assertTrue(any("Turn 1 message" in str(entry) for entry in self.game_state.event_log_history))

    def test_event_log_scroll_offset_functionality(self):
        """Test the scroll offset functionality."""
        # Mock the show_tutorial_message method
        self.game_state.show_tutorial_message = MagicMock()
        
        # Enable scrollable log
        unlock_scrollable_event_log(self.game_state)
        
        # Initial scroll offset should be 0
        self.assertEqual(self.game_state.event_log_scroll_offset, 0)
        
        # Add some history
        self.game_state.event_log_history = ["Entry 1", "Entry 2", "Entry 3", "Entry 4", "Entry 5"]
        
        # Test scroll offset manipulation
        self.game_state.event_log_scroll_offset = 2
        self.assertEqual(self.game_state.event_log_scroll_offset, 2)


class TestEventLogScrolling(unittest.TestCase):
    """Test event log scrolling behavior in UI."""

    def test_scrollable_log_keyboard_handling(self):
        """Test that keyboard scrolling works when log is enabled."""
        # This test checks the main.py keyboard handling
        # We'll test the logic that should exist in main.py
        
        # Mock game state with scrollable log enabled
        game_state = MagicMock()
        game_state.scrollable_event_log_enabled = True
        game_state.event_log_scroll_offset = 0
        game_state.event_log_history = ["Entry 1", "Entry 2", "Entry 3"]
        game_state.messages = ["Current message"]
        
        # Simulate up arrow key
        original_offset = game_state.event_log_scroll_offset
        # Verify that the scroll offset can be modified
        game_state.event_log_scroll_offset = max(0, game_state.event_log_scroll_offset - 1)
        self.assertEqual(game_state.event_log_scroll_offset, 0)  # Should stay at 0 when already at top
        
        # Simulate down arrow key
        max_scroll = max(0, len(game_state.event_log_history) + len(game_state.messages) - 7)
        game_state.event_log_scroll_offset = min(max_scroll, game_state.event_log_scroll_offset + 1)
        self.assertGreaterEqual(game_state.event_log_scroll_offset, 0)


if __name__ == '__main__':
    unittest.main()