"""
Tests for Game Flow Improvements (Issue #37)

Tests cover:
- Action delay system for N-tick delayed actions
- Daily news feed for turn impact feedback
- Turn spending tracking and display
- Enhanced turn progression feedback
"""

import unittest
import sys
import os

# Add the parent directory to sys.path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game_state import GameState


class TestDelayedActions(unittest.TestCase):
    """Test the delayed action system."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
    
    def test_add_delayed_action(self):
        """Test adding a delayed action."""
        # Add a delayed action that resolves in 2 turns
        self.game_state.add_delayed_action(
            "Research Grant", 
            2, 
            {'money': 500, 'reputation': 10}
        )
        
        # Should have one delayed action
        self.assertEqual(len(self.game_state.delayed_actions), 1)
        
        # Check action details
        action = self.game_state.delayed_actions[0]
        self.assertEqual(action['action_name'], "Research Grant")
        self.assertEqual(action['resolve_turn'], self.game_state.turn + 2)
        self.assertEqual(action['effects']['money'], 500)
        self.assertEqual(action['effects']['reputation'], 10)
    
    def test_delayed_action_resolution(self):
        """Test that delayed actions resolve at the correct time."""
        initial_money = self.game_state.money
        initial_reputation = self.game_state.reputation
        
        # Add a delayed action
        self.game_state.add_delayed_action(
            "Research Grant", 
            2, 
            {'money': 500, 'reputation': 10}
        )
        
        # Process delayed actions - should not resolve yet
        resolved = self.game_state.process_delayed_actions()
        self.assertEqual(len(resolved), 0)
        self.assertEqual(self.game_state.money, initial_money)
        self.assertEqual(self.game_state.reputation, initial_reputation)
        
        # Advance turn and check again
        self.game_state.turn += 1
        resolved = self.game_state.process_delayed_actions()
        self.assertEqual(len(resolved), 0)
        
        # Advance to resolution turn
        self.game_state.turn += 1
        resolved = self.game_state.process_delayed_actions()
        self.assertEqual(len(resolved), 1)
        
        # Check effects were applied
        self.assertEqual(self.game_state.money, initial_money + 500)
        self.assertEqual(self.game_state.reputation, initial_reputation + 10)
        
        # Action should be removed from delayed list
        self.assertEqual(len(self.game_state.delayed_actions), 0)


class TestDailyNews(unittest.TestCase):
    """Test the daily news feed system."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
    
    def test_daily_news_generation(self):
        """Test that daily news is generated."""
        news = self.game_state.get_daily_news()
        self.assertIsInstance(news, str)
        self.assertTrue(news.startswith("📰 Day"))
        self.assertTrue(len(news) > 20)  # Should be a meaningful message
    
    def test_daily_news_consistency(self):
        """Test that daily news is consistent for the same turn and seed."""
        news1 = self.game_state.get_daily_news()
        news2 = self.game_state.get_daily_news()
        self.assertEqual(news1, news2)
        
        # Different turn should give different news
        self.game_state.turn += 1
        news3 = self.game_state.get_daily_news()
        self.assertNotEqual(news1, news3)


class TestSpendTracking(unittest.TestCase):
    """Test the spend tracking display system."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
        self.game_state.money = 10000  # Ensure we have enough money
    
    def test_spend_tracking_initialization(self):
        """Test that spend tracking fields are initialized."""
        self.assertFalse(self.game_state.spend_this_turn_display_shown)
        self.assertFalse(self.game_state.spend_display_permanent)
        self.assertEqual(self.game_state.spend_this_turn, 0)
    
    def test_spend_tracking_single_action(self):
        """Test that spend tracking doesn't trigger for single actions."""
        # Simulate spending money
        self.game_state._add('money', -100)
        
        # Update spend tracking
        self.game_state.update_spend_tracking()
        
        # Should not trigger display for single action
        self.assertFalse(self.game_state.spend_this_turn_display_shown)
    
    def test_spend_tracking_multiple_actions(self):
        """Test spend tracking triggers for multiple spending actions."""
        # Simulate multiple spending actions
        self.game_state.selected_actions = [
            {'money_cost': 100, 'name': 'Action 1'},
            {'money_cost': 200, 'name': 'Action 2'}
        ]
        
        # Simulate spending
        self.game_state._add('money', -100)
        self.game_state._add('money', -200)
        
        # Should track total spending
        self.assertEqual(self.game_state.spend_this_turn, 300)


class TestGameFlowIntegration(unittest.TestCase):
    """Test integration of game flow improvements with turn progression."""
    
    def setUp(self):
        self.game_state = GameState("test_seed")
        self.game_state.money = 10000  # Ensure sufficient funds
    
    def test_end_turn_includes_improvements(self):
        """Test that end_turn includes the new game flow features."""
        # Add a delayed action
        self.game_state.add_delayed_action("Test Action", 1, {'money': 100})
        
        # Record initial state
        initial_messages = len(self.game_state.messages)
        
        # End turn
        self.game_state.end_turn()
        
        # Check that news was added
        has_news = any("📰" in msg for msg in self.game_state.messages)
        self.assertTrue(has_news, "Daily news should be added to messages")
        
        # Check that delayed action was processed
        resolved_message = any("Test Action completed" in msg for msg in self.game_state.messages)
        self.assertTrue(resolved_message, "Delayed action completion should be in messages")
        
        # Spend tracking should be reset
        self.assertEqual(self.game_state.spend_this_turn, 0)


if __name__ == '__main__':
    unittest.main()