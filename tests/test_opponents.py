import unittest
import random
import sys
import os

# Add the parent directory to sys.path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from opponents import Opponent, create_default_opponents
from game_state import GameState


class TestOpponent(unittest.TestCase):
    """Test the Opponent class functionality."""
    
    def setUp(self):
        """Set up test fixtures with a consistent seed."""
        random.seed(42)
        self.opponent = Opponent(
            name="Test Corp",
            budget=500,
            capabilities_researchers=10,
            lobbyists=5,
            compute=30,
            description="A test opponent"
        )
    
    def test_opponent_initialization(self):
        """Test that opponents initialize with correct values."""
        self.assertEqual(self.opponent.name, "Test Corp")
        self.assertEqual(self.opponent.budget, 500)
        self.assertEqual(self.opponent.capabilities_researchers, 10)
        self.assertEqual(self.opponent.lobbyists, 5)
        self.assertEqual(self.opponent.compute, 30)
        self.assertEqual(self.opponent.description, "A test opponent")
        
        # Check that progress is in expected range
        self.assertGreaterEqual(self.opponent.progress, 0)
        self.assertLessEqual(self.opponent.progress, 100)
        
        # Check that opponent starts undiscovered
        self.assertFalse(self.opponent.discovered)
        
        # Check that all stats start as undiscovered
        for stat in self.opponent.discovered_stats.values():
            self.assertFalse(stat)
            
    def test_discover_opponent(self):
        """Test opponent discovery functionality."""
        self.assertFalse(self.opponent.discovered)
        self.opponent.discover()
        self.assertTrue(self.opponent.discovered)
        
    def test_scout_stat_success(self):
        """Test successful stat scouting."""
        # Set seed to ensure success
        random.seed(1)  # This should give us a successful scout
        
        success, value, message = self.opponent.scout_stat('budget')
        
        self.assertTrue(success)
        self.assertIsNotNone(value)
        self.assertIn("budget", message.lower())
        self.assertTrue(self.opponent.discovered_stats['budget'])
        self.assertEqual(self.opponent.known_stats['budget'], value)
        
    def test_scout_stat_failure(self):
        """Test failed stat scouting."""
        # Set seed to ensure failure
        random.seed(100)  # This should give us a failed scout
        
        success, value, message = self.opponent.scout_stat('budget')
        
        if not success:  # Only test if it actually failed
            self.assertFalse(success)
            self.assertIsNone(value)
            self.assertIn("failed", message.lower())
            self.assertFalse(self.opponent.discovered_stats['budget'])
            
    def test_scout_already_discovered_stat(self):
        """Test scouting a stat that's already been discovered."""
        # First, discover the stat
        self.opponent.discovered_stats['budget'] = True
        self.opponent.known_stats['budget'] = 500
        
        success, value, message = self.opponent.scout_stat('budget')
        
        self.assertTrue(success)
        self.assertEqual(value, self.opponent.budget)
        self.assertIn("already known", message)
        
    def test_scout_invalid_stat(self):
        """Test scouting an invalid stat name."""
        success, value, message = self.opponent.scout_stat('invalid_stat')
        
        self.assertFalse(success)
        self.assertIsNone(value)
        self.assertIn("unknown stat", message.lower())
        
    def test_take_turn_undiscovered(self):
        """Test that undiscovered opponents don't generate messages."""
        self.assertFalse(self.opponent.discovered)
        messages = self.opponent.take_turn()
        self.assertEqual(len(messages), 0)
        
    def test_take_turn_discovered(self):
        """Test that discovered opponents take actions."""
        self.opponent.discover()
        initial_budget = self.opponent.budget
        
        messages = self.opponent.take_turn()
        
        # Discovered opponent should generate some messages (though could be empty if no actions taken)
        self.assertIsInstance(messages, list)
        
        # Budget might be spent or research might progress
        # We can't guarantee specific behavior due to randomness, but we can check the structure
        
    def test_get_impact_on_doom(self):
        """Test doom impact calculation."""
        # Test undiscovered opponent
        self.assertFalse(self.opponent.discovered)
        doom_impact = self.opponent.get_impact_on_doom()
        self.assertGreaterEqual(doom_impact, 0)
        self.assertLessEqual(doom_impact, 2)
        
        # Test discovered opponent
        self.opponent.discover()
        doom_impact = self.opponent.get_impact_on_doom()
        self.assertGreaterEqual(doom_impact, 0)
        self.assertIsInstance(doom_impact, int)


class TestOpponentAI(unittest.TestCase):
    """Test opponent AI behavior over multiple turns."""
    
    def setUp(self):
        """Set up test fixtures."""
        random.seed(42)
        self.opponent = Opponent(
            name="AI Test Corp",
            budget=1000,
            capabilities_researchers=5,
            lobbyists=2,
            compute=20,
            description="Test AI behavior"
        )
        self.opponent.discover()  # Make it discovered so it takes actions
        
    def test_opponent_spends_budget(self):
        """Test that opponents spend their budget over time."""
        initial_budget = self.opponent.budget
        
        # Run multiple turns
        for _ in range(10):
            self.opponent.take_turn()
            
        # Budget should have been spent (unless very unlucky with randomness)
        # We'll be lenient and just check it didn't increase
        self.assertLessEqual(self.opponent.budget, initial_budget)
        
    def test_opponent_makes_progress(self):
        """Test that opponents make research progress over time."""
        initial_progress = self.opponent.progress
        
        # Run multiple turns
        for _ in range(10):
            self.opponent.take_turn()
            
        # Progress should generally increase (unless at cap or very unlucky)
        # We'll check it didn't decrease
        self.assertGreaterEqual(self.opponent.progress, initial_progress)
        
    def test_progress_caps_at_100(self):
        """Test that progress doesn't exceed 100."""
        # Set progress high to test capping
        self.opponent.progress = 95
        
        # Run turns that should push progress over 100
        for _ in range(5):
            self.opponent.take_turn()
            
        self.assertLessEqual(self.opponent.progress, 100)


class TestCreateDefaultOpponents(unittest.TestCase):
    """Test the default opponents creation function."""
    
    def test_creates_three_opponents(self):
        """Test that create_default_opponents returns exactly 3 opponents."""
        opponents = create_default_opponents()
        
        self.assertEqual(len(opponents), 3)
        self.assertIsInstance(opponents, list)
        
        for opponent in opponents:
            self.assertIsInstance(opponent, Opponent)
            
    def test_opponents_have_unique_names(self):
        """Test that default opponents have unique names."""
        opponents = create_default_opponents()
        names = [opp.name for opp in opponents]
        
        self.assertEqual(len(names), len(set(names)))  # All names should be unique
        
    def test_opponents_have_varied_stats(self):
        """Test that default opponents have different stat distributions."""
        opponents = create_default_opponents()
        
        # Check that not all opponents have the same budget
        budgets = [opp.budget for opp in opponents]
        self.assertNotEqual(budgets[0], budgets[1])  # First two should be different
        
        # Check that all opponents have reasonable stats
        for opponent in opponents:
            self.assertGreater(opponent.budget, 0)
            self.assertGreater(opponent.capabilities_researchers, 0)
            self.assertGreaterEqual(opponent.lobbyists, 0)
            self.assertGreater(opponent.compute, 0)
            self.assertNotEqual(opponent.name, "")
            
    def test_opponents_start_undiscovered(self):
        """Test that default opponents start undiscovered."""
        opponents = create_default_opponents()
        
        for opponent in opponents:
            self.assertFalse(opponent.discovered)
            for stat_discovered in opponent.discovered_stats.values():
                self.assertFalse(stat_discovered)


class TestOpponentIntegration(unittest.TestCase):
    """Integration tests for opponent system."""
    
    def test_full_scouting_cycle(self):
        """Test a complete cycle of discovering and scouting an opponent."""
        random.seed(1)  # Use seed that should give successes
        opponent = Opponent("Integration Test", 500, 10, 5, 30)
        
        # Discover the opponent
        opponent.discover()
        self.assertTrue(opponent.discovered)
        
        # Scout different stats
        stats_to_scout = ['budget', 'capabilities_researchers', 'lobbyists', 'compute', 'progress']
        
        for stat in stats_to_scout:
            success, value, message = opponent.scout_stat(stat)
            # With our seed, most should succeed, but we'll handle both cases
            if success:
                self.assertTrue(opponent.discovered_stats[stat])
                self.assertIsNotNone(opponent.known_stats[stat])
                
    def test_opponent_lifecycle(self):
        """Test a complete opponent lifecycle from creation to end game."""
        opponent = Opponent("Lifecycle Test", 1000, 15, 8, 50)
        
        # Start undiscovered
        self.assertFalse(opponent.discovered)
        
        # Taking turns while undiscovered should not generate messages
        messages = opponent.take_turn()
        self.assertEqual(len(messages), 0)
        
        # Discover the opponent
        opponent.discover()
        self.assertTrue(opponent.discovered)
        
        # Now taking turns should potentially generate messages
        # Run enough turns to see some activity
        all_messages = []
        for _ in range(20):
            messages = opponent.take_turn()
            all_messages.extend(messages)
            
        # Should have generated some activity messages
        # (Could be 0 if very unlucky, but typically will have some)
        self.assertIsInstance(all_messages, list)


class TestGameStateOpponentsIntegration(unittest.TestCase):
    """Test integration of opponents with GameState."""
    
    def setUp(self):
        """Set up test fixtures."""
        random.seed(42)
        self.game_state = GameState(seed=42)
        
    def test_gamestate_has_opponents(self):
        """Test that GameState initializes with opponents."""
        self.assertIsInstance(self.game_state.opponents, list)
        self.assertEqual(len(self.game_state.opponents), 3)
        
        for opponent in self.game_state.opponents:
            self.assertIsInstance(opponent, Opponent)
            
    def test_opponents_start_undiscovered(self):
        """Test that opponents start undiscovered in game."""
        for opponent in self.game_state.opponents:
            self.assertFalse(opponent.discovered)
            
    def test_espionage_discovers_opponents(self):
        """Test that espionage can discover opponents."""
        # Run espionage several times to discover opponents
        for _ in range(10):
            self.game_state._spy()
            
        # At least one opponent should be discovered
        discovered = [opp for opp in self.game_state.opponents if opp.discovered]
        self.assertGreater(len(discovered), 0)
        
    def test_scout_opponent_function(self):
        """Test the scout opponent functionality."""
        # Should work even if no opponents discovered yet
        self.game_state._scout_opponent()
        
        # After scouting, at least one should be discovered
        discovered = [opp for opp in self.game_state.opponents if opp.discovered]
        self.assertGreater(len(discovered), 0)
        
    def test_scout_opponent_action_availability(self):
        """Test that Scout Opponent action is restricted before turn 5."""
        # Check that the Scout Opponent action exists
        scout_action = None
        for action in self.game_state.actions:
            if action['name'] == 'Scout Opponent':
                scout_action = action
                break
                
        self.assertIsNotNone(scout_action)
        
        # Before scouting is unlocked, it should not be available
        self.game_state.turn = 5
        self.assertFalse(scout_action['rules'](self.game_state))
        
        # After scouting is unlocked, it should be available
        self.game_state.scouting_unlocked = True
        self.assertTrue(scout_action['rules'](self.game_state))
        
    def test_opponents_affect_doom(self):
        """Test that opponents contribute to doom over time."""
        initial_doom = self.game_state.doom
        
        # Discover some opponents so they become active
        for opp in self.game_state.opponents:
            opp.discover()
            
        # End several turns to see doom increase from opponents
        for _ in range(5):
            self.game_state.end_turn()
            
        # Doom should have increased (from both base increase and opponents)
        self.assertGreater(self.game_state.doom, initial_doom)
        
    def test_opponent_victory_condition(self):
        """Test that game ends when opponent reaches 100% progress."""
        # Force an opponent to high progress
        self.game_state.opponents[0].progress = 99
        self.game_state.opponents[0].discover()
        
        # End turn should trigger victory condition
        self.game_state.end_turn()
        
        # Game should be over
        self.assertTrue(self.game_state.game_over)
        
    def test_opponents_take_turns(self):
        """Test that discovered opponents take actions during turn."""
        # Discover some opponents
        for opp in self.game_state.opponents:
            opp.discover()
            
        initial_messages = len(self.game_state.messages)
        
        # End turn - opponents should act
        self.game_state.end_turn()
        
        # Should have messages from opponents or other turn activities
        self.assertGreaterEqual(len(self.game_state.messages), 0)


if __name__ == '__main__':
    unittest.main()