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


if __name__ == '__main__':
    unittest.main()