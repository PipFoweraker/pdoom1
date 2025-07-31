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


if __name__ == '__main__':
    unittest.main()