import unittest
import sys
import os

# Add the parent directory to the path so we can import game_state
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_state import GameState


class TestGameStateInitialization(unittest.TestCase):
    """Test that GameState initializes with expected default values."""
    
    def test_game_state_default_values(self):
        """Test that a new GameState starts with the correct default values."""
        # Create a new GameState with a test seed
        game_state = GameState("test_seed")
        
        # Verify core resource defaults
        self.assertEqual(game_state.money, 300, "Initial money should be 300")
        self.assertEqual(game_state.staff, 2, "Initial staff should be 2")
        self.assertEqual(game_state.reputation, 15, "Initial reputation should be 15")
        self.assertEqual(game_state.doom, 12, "Initial doom should be 12")
        
        # Verify game state defaults
        self.assertEqual(game_state.turn, 0, "Initial turn should be 0")
        self.assertEqual(game_state.max_doom, 100, "Max doom should be 100")
        self.assertFalse(game_state.game_over, "Game should not be over initially")
        
        # Verify seed is set correctly
        self.assertEqual(game_state.seed, "test_seed", "Seed should be set correctly")
        
        # Verify collections are initialized
        self.assertIsInstance(game_state.selected_actions, list, "Selected actions should be a list")
        self.assertEqual(len(game_state.selected_actions), 0, "Selected actions should be empty initially")
        self.assertIsInstance(game_state.messages, list, "Messages should be a list")
        self.assertGreater(len(game_state.messages), 0, "Should have initial game message")


class TestEventLog(unittest.TestCase):
    """Test event log behavior, specifically that it clears each turn."""
    
    def test_event_log_clears_on_end_turn(self):
        """Test that the event log is cleared at the start of each turn."""
        # Create a new GameState with sufficient resources
        game_state = GameState("test_seed")
        
        # Verify we start with an initial message
        initial_message_count = len(game_state.messages)
        self.assertGreater(initial_message_count, 0, "Should have initial game message")
        
        # Add some messages manually to simulate events
        game_state.messages.append("Test message 1")
        game_state.messages.append("Test message 2")
        
        # Verify messages were added
        self.assertEqual(len(game_state.messages), initial_message_count + 2, 
                        "Should have added 2 test messages")
        
        # Store the pre-turn messages to verify they're cleared
        pre_turn_messages = game_state.messages.copy()
        
        # End the turn
        game_state.end_turn()
        
        # Verify the old messages are gone by checking none of our test messages remain
        for old_message in pre_turn_messages:
            self.assertNotIn(old_message, game_state.messages, 
                           "Old messages should be cleared from the log")
    
    def test_event_log_shows_only_current_turn_events(self):
        """Test that the event log shows only events from the current turn."""
        # Create a game state that will have staff unable to be paid (triggers a message)
        game_state = GameState("test_seed")
        
        # Set up a scenario where staff maintenance will cause a message
        game_state.money = 10  # Not enough for staff maintenance (2 staff * 15 = 30)
        
        # Add some old messages
        game_state.messages.append("Old message 1")
        game_state.messages.append("Old message 2")
        old_messages = game_state.messages.copy()
        
        # End the turn - this should clear old messages and add new ones about staff leaving
        game_state.end_turn()
        
        # Verify old messages are gone
        for old_message in old_messages:
            self.assertNotIn(old_message, game_state.messages,
                           "Old messages should not be in the current turn log")
        
        # Verify we got a message about staff leaving (since we couldn't pay them)
        staff_message_found = any("staff" in msg.lower() for msg in game_state.messages)
        self.assertTrue(staff_message_found, 
                       "Should have a message about staff when unable to pay maintenance")
    
    def test_event_log_empty_at_turn_start_by_default(self):
        """Test that the event log is empty at the start of each turn by default."""
        game_state = GameState("test_seed")
        
        # Add messages to simulate previous turn activity
        game_state.messages.extend([
            "Previous turn message 1",
            "Previous turn message 2", 
            "Action completed",
            "Event triggered"
        ])
        
        # Verify messages are present before turn end
        self.assertGreater(len(game_state.messages), 0, "Should have messages before turn")
        
        # End turn - this should clear all messages first
        game_state.end_turn()
        
        # The messages list should be empty at the very start of turn processing,
        # then filled with current turn events. Since we have no selected actions
        # and sufficient money, we should only see system-generated messages
        
        # Verify no old messages remain
        for msg in ["Previous turn message 1", "Previous turn message 2", 
                   "Action completed", "Event triggered"]:
            self.assertNotIn(msg, game_state.messages,
                           f"Old message '{msg}' should not persist into new turn")
    
    def test_event_log_preserves_current_turn_messages_only(self):
        """Test that only messages generated during the current turn are preserved."""
        game_state = GameState("test_seed")
        
        # Start with some messages from "previous turns"
        game_state.messages = ["Old message 1", "Old message 2"]
        
        # Select an action that will generate a message when executed
        if game_state.money >= game_state.actions[0]["cost"]:
            game_state.selected_actions.append(0)  # Select first action
            game_state.messages.append(f"Selected: {game_state.actions[0]['name']}")
        
        pre_turn_messages = game_state.messages.copy()
        
        # End the turn - this clears messages, then processes actions/events
        game_state.end_turn()
        
        # Verify old messages are gone
        for old_msg in ["Old message 1", "Old message 2"]:
            self.assertNotIn(old_msg, game_state.messages,
                           "Old messages should be cleared")
        
        # Any messages present now should be from current turn processing only
        # (such as action execution, events, or maintenance messages)
        for msg in game_state.messages:
            self.assertNotIn(msg, pre_turn_messages,
                           "Current messages should be new, not carried over")
    
    def test_multiple_turn_event_log_isolation(self):
        """Test that event logs are properly isolated across multiple turns."""
        game_state = GameState("test_seed")
        
        # Set up for multiple turns with sufficient resources
        game_state.money = 1000  # Plenty of money
        
        turn_messages = {}
        
        # Run several turns and verify message isolation
        for turn_num in range(3):
            # Add a unique message before ending turn
            unique_msg = f"Turn {turn_num} specific message"
            game_state.messages.append(unique_msg)
            
            # Store current messages
            pre_turn = game_state.messages.copy()
            
            # End turn
            game_state.end_turn()
            
            # Store messages from this turn
            turn_messages[turn_num] = game_state.messages.copy()
            
            # Verify the unique message we added is gone
            self.assertNotIn(unique_msg, game_state.messages,
                           f"Turn {turn_num} message should not persist")
            
            # Verify no messages from previous turns persist
            for prev_turn in range(turn_num):
                for prev_msg in turn_messages[prev_turn]:
                    self.assertNotIn(prev_msg, game_state.messages,
                                   f"Message from turn {prev_turn} should not appear in turn {turn_num}")
        
        # Final verification: each turn should have had its own isolated message log
        self.assertEqual(len(turn_messages), 3, "Should have captured 3 turns of messages")


class TestScrollableEventLog(unittest.TestCase):
    """Test scrollable event log functionality."""
    
    def test_scrollable_event_log_initially_disabled(self):
        """Test that the scrollable event log starts disabled."""
        game_state = GameState("test_seed")
        
        # Verify scrollable event log is initially disabled
        self.assertFalse(game_state.scrollable_event_log_enabled, 
                        "Scrollable event log should be disabled initially")
        
        # Verify event log history starts empty
        self.assertEqual(len(game_state.event_log_history), 0,
                        "Event log history should be empty initially")
        
        # Verify scroll offset starts at 0
        self.assertEqual(game_state.event_log_scroll_offset, 0,
                        "Event log scroll offset should be 0 initially")
    
    def test_scrollable_event_log_flag_set_by_event(self):
        """Test that the scrollable event log flag is set when the event triggers."""
        game_state = GameState("test_seed")
        
        # Verify flag is initially False
        self.assertFalse(game_state.scrollable_event_log_enabled)
        
        # Manually trigger the event (simulating the condition being met)
        # Find the event log upgrade event
        event_log_event = None
        for event in game_state.events:
            if event["name"] == "Event Log System Upgrade":
                event_log_event = event
                break
        
        self.assertIsNotNone(event_log_event, "Event Log System Upgrade event should exist")
        
        # Execute the event effect
        event_log_event["effect"](game_state)
        
        # Verify the flag is now set
        self.assertTrue(game_state.scrollable_event_log_enabled,
                       "Scrollable event log should be enabled after event triggers")
        
        # Verify a message was added about the upgrade
        upgrade_message_found = any("Event Log Upgrade" in msg for msg in game_state.messages)
        self.assertTrue(upgrade_message_found,
                       "Should have a message about the event log upgrade")
    
    def test_event_history_storage_when_enabled(self):
        """Test that event history is stored when scrollable log is enabled."""
        game_state = GameState("test_seed")
        
        # Enable the scrollable event log
        game_state.scrollable_event_log_enabled = True
        
        # Add some messages
        game_state.messages.extend([
            "Test message 1",
            "Test message 2",
            "Action completed"
        ])
        
        # Verify event log history is empty before turn end
        self.assertEqual(len(game_state.event_log_history), 0,
                        "Event log history should be empty before turn end")
        
        # End the turn
        game_state.end_turn()
        
        # Verify messages were stored in history
        self.assertGreater(len(game_state.event_log_history), 0,
                          "Event log history should have entries after turn end")
        
        # Verify the turn header was added
        turn_header_found = any("=== Turn" in entry for entry in game_state.event_log_history)
        self.assertTrue(turn_header_found,
                       "Event log history should contain a turn header")
        
        # Verify our test messages were stored
        for test_msg in ["Test message 1", "Test message 2", "Action completed"]:
            self.assertIn(test_msg, game_state.event_log_history,
                         f"Message '{test_msg}' should be in event log history")
    
    def test_event_history_not_stored_when_disabled(self):
        """Test that event history is not stored when scrollable log is disabled."""
        game_state = GameState("test_seed")
        
        # Ensure scrollable event log is disabled
        game_state.scrollable_event_log_enabled = False
        
        # Add some messages
        game_state.messages.extend([
            "Test message 1",
            "Test message 2"
        ])
        
        # End the turn
        game_state.end_turn()
        
        # Verify event log history remains empty
        self.assertEqual(len(game_state.event_log_history), 0,
                        "Event log history should remain empty when feature is disabled")
    
    def test_multiple_turns_history_accumulation(self):
        """Test that history accumulates across multiple turns when enabled."""
        game_state = GameState("test_seed")
        game_state.scrollable_event_log_enabled = True
        game_state.money = 1000  # Ensure we have enough money for multiple turns
        
        # Account for the initial "Game started!" message
        initial_messages = game_state.messages.copy()
        
        # Track expected messages for verification
        expected_history = []
        
        # Run multiple turns
        for turn in range(3):
            # Add the turn header and initial messages if this is the first turn
            if turn == 0:
                expected_history.append(f"=== Turn 1 ===")
                expected_history.extend(initial_messages)
            else:
                expected_history.append(f"=== Turn {turn + 1} ===")
            
            # Add unique messages for this turn
            turn_messages = [f"Turn {turn + 1} message A", f"Turn {turn + 1} message B"]
            game_state.messages.extend(turn_messages)
            expected_history.extend(turn_messages)
            
            # End the turn
            game_state.end_turn()
        
        # Verify all expected messages are in history
        self.assertEqual(len(game_state.event_log_history), len(expected_history),
                        f"History should contain all {len(expected_history)} messages")
        
        # Verify specific messages are present
        for expected_msg in expected_history:
            self.assertIn(expected_msg, game_state.event_log_history,
                         f"Message '{expected_msg}' should be in history")
        
        # Verify turn headers are present
        turn_headers = [entry for entry in game_state.event_log_history if "=== Turn" in entry]
        self.assertEqual(len(turn_headers), 3, "Should have 3 turn headers")


if __name__ == '__main__':
    unittest.main()