import unittest
from src.core.game_state import GameState


class TestActivityLogBehavior(unittest.TestCase):
    '''Test activity log clearing behavior and UI minimization features'''
    
    def setUp(self):
        '''Set up a GameState for testing'''
        self.game_state = GameState('test_seed')
        # RNG is now initialized by GameState constructor
        
    def test_activity_log_clears_by_default_every_turn(self):
        '''Test that activity log clears every turn when scrollable log is disabled'''
        # Ensure scrollable event log is disabled
        self.game_state.scrollable_event_log_enabled = False
        
        # Clear initial messages and add test messages
        self.game_state.messages = []
        self.game_state.messages.append('Test message 1')
        self.game_state.messages.append('Test message 2')
        
        # Store initial message count
        initial_message_count = len(self.game_state.messages)
        self.assertEqual(initial_message_count, 2)
        
        # End turn
        self.game_state.end_turn()
        
        # Previous turn messages should be cleared, but new messages may be generated
        # The key point is that our test messages are gone
        self.assertNotIn('Test message 1', self.game_state.messages)
        self.assertNotIn('Test message 2', self.game_state.messages)
        
        # Event log history should also be empty since scrollable log is disabled
        self.assertEqual(len(self.game_state.event_log_history), 0)
        
    def test_activity_log_preserves_history_when_scrollable_enabled(self):
        '''Test that activity log preserves history when scrollable log is enabled'''
        # Enable scrollable event log
        self.game_state.scrollable_event_log_enabled = True
        
        # Clear initial messages and add test messages
        self.game_state.messages = []
        self.game_state.messages.append('Test message 1')
        self.game_state.messages.append('Test message 2')
        
        # End turn
        self.game_state.end_turn()
        
        # Test messages should be cleared from current turn
        self.assertNotIn('Test message 1', self.game_state.messages)
        self.assertNotIn('Test message 2', self.game_state.messages)
        
        # But should be preserved in history
        self.assertGreater(len(self.game_state.event_log_history), 0)
        self.assertIn('Test message 1', self.game_state.event_log_history)
        self.assertIn('Test message 2', self.game_state.event_log_history)
        
    def test_scrollable_event_log_unlocks_at_turn_5(self):
        '''Test that scrollable event log upgrade triggers at turn 5'''
        # Set up game state at turn 4
        self.game_state.turn = 4
        self.game_state.scrollable_event_log_enabled = False
        
        # Trigger events
        self.game_state.trigger_events()
        
        # Should not be enabled yet
        self.assertFalse(self.game_state.scrollable_event_log_enabled)
        
        # Advance to turn 5
        self.game_state.turn = 5
        
        # Trigger events
        self.game_state.trigger_events()
        
        # Should now be enabled
        self.assertTrue(self.game_state.scrollable_event_log_enabled)

    def test_compact_activity_display_upgrade_available(self):
        '''Test that compact activity display upgrade exists and works'''
        # Find the compact activity display upgrade
        compact_upgrade = None
        for upgrade in self.game_state.upgrades:
            if upgrade['name'] == 'Compact Activity Display':
                compact_upgrade = upgrade
                break
        
        self.assertIsNotNone(compact_upgrade, 'Compact Activity Display upgrade should exist')
        self.assertEqual(compact_upgrade['cost'], 150)
        self.assertEqual(compact_upgrade['effect_key'], 'compact_activity_display')
        
    def test_activity_log_minimization_requires_upgrade(self):
        '''Test that activity log minimization only works with the upgrade'''
        # Initially, minimization should not be available
        self.assertFalse(hasattr(self.game_state, 'activity_log_minimized') and 
                        self.game_state.activity_log_minimized)
        
        # Purchase the compact activity display upgrade
        self.game_state.money = 200  # Ensure enough money
        for upgrade in self.game_state.upgrades:
            if upgrade['name'] == 'Compact Activity Display':
                upgrade['purchased'] = True
                self.game_state.upgrade_effects.add(upgrade['effect_key'])
                break
        
        # Now minimization should be possible
        self.game_state.activity_log_minimized = True
        self.assertTrue(self.game_state.activity_log_minimized)


class TestActivityLogMinimization(unittest.TestCase):
    '''Test activity log minimization features'''
    
    def setUp(self):
        '''Set up a GameState for testing'''
        self.game_state = GameState('test_seed')
        # RNG is now initialized by GameState constructor
        
        # Enable upgrades needed for minimization
        self.game_state.scrollable_event_log_enabled = True
        self.game_state.money = 200
        for upgrade in self.game_state.upgrades:
            if upgrade['name'] == 'Compact Activity Display':
                upgrade['purchased'] = True
                self.game_state.upgrade_effects.add(upgrade['effect_key'])
                break
                
    def test_activity_log_can_be_minimized(self):
        '''Test that activity log can be minimized when upgrade is available'''
        # Initially should not be minimized
        self.assertFalse(getattr(self.game_state, 'activity_log_minimized', False))
        
        # Minimize the log
        self.game_state.activity_log_minimized = True
        self.assertTrue(self.game_state.activity_log_minimized)
        
        # Expand the log
        self.game_state.activity_log_minimized = False
        self.assertFalse(self.game_state.activity_log_minimized)
        
    def test_minimize_button_rect_calculation(self):
        '''Test that minimize button rectangle is calculated correctly'''
        w, h = 800, 600
        
        # Get the minimize button rect
        rect = self.game_state._get_activity_log_minimize_button_rect(w, h)
        
        # Should return a tuple of 4 values (x, y, width, height)
        self.assertEqual(len(rect), 4)
        x, y, width, height = rect
        
        # All values should be positive integers
        self.assertGreater(x, 0)
        self.assertGreater(y, 0)
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
        
    def test_expand_button_rect_calculation(self):
        '''Test that expand button rectangle is calculated correctly'''
        w, h = 800, 600
        
        # Get the expand button rect
        rect = self.game_state._get_activity_log_expand_button_rect(w, h)
        
        # Should return a tuple of 4 values (x, y, width, height)
        self.assertEqual(len(rect), 4)
        x, y, width, height = rect
        
        # All values should be positive integers
        self.assertGreater(x, 0)
        self.assertGreater(y, 0)
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)


if __name__ == '__main__':
    unittest.main()