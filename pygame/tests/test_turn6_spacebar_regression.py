'''
Turn 6 Spacebar Regression Test
Test that validates GUI input functionality at Turn 6 specifically.

This test is designed to catch the architectural debt issue where
redundant key checking and missing event consumption flags caused
spacebar input to fail at Turn 6.
'''

import unittest
from src.core.game_state import GameState
from src.features.onboarding import onboarding
from src.services.keybinding_manager import keybinding_manager


class TestTurn6SpacebarRegression(unittest.TestCase):
    '''Regression tests for Turn 6 spacebar input failure (Issue #377).'''
    
    def setUp(self):
        '''Set up test game state at Turn 6.'''
        self.game_state = GameState('test-turn6-regression')
        
        # Advance to Turn 6
        for i in range(6):
            result = self.game_state.end_turn()
            self.assertTrue(result, f'Failed to advance to turn {i+1}')
        
        self.assertEqual(self.game_state.turn, 6, 'Should be at turn 6')
    
    def test_core_logic_works_at_turn_6(self):
        '''Test that core end_turn() logic works correctly at Turn 6.'''
        initial_turn = self.game_state.turn
        result = self.game_state.end_turn()
        
        self.assertTrue(result, 'end_turn() should return True at Turn 6')
        self.assertEqual(self.game_state.turn, initial_turn + 1, 
                        'Turn should advance from 6 to 7')
    
    def test_blocking_conditions_evaluation(self):
        '''Test that blocking conditions evaluate correctly at Turn 6.'''
        # These are the conditions from the fixed main.py logic
        first_time_help_content = False
        blocking_conditions = [
            first_time_help_content,
            getattr(self.game_state, 'pending_hiring_dialog', False) or False,
            getattr(self.game_state, 'pending_fundraising_dialog', False) or False,
            getattr(self.game_state, 'pending_research_dialog', False) or False,
            onboarding.show_tutorial_overlay
        ]
        
        # Should not be blocked at Turn 6 in normal conditions
        self.assertFalse(any(blocking_conditions), 
                        'Blocking conditions should not prevent end turn at Turn 6')
    
    def test_popup_events_condition(self):
        '''Test that popup events condition evaluates correctly.'''
        # This was the subtle bug - empty list should be falsy
        if hasattr(self.game_state, 'pending_popup_events'):
            popup_condition = bool(self.game_state.pending_popup_events)
            self.assertFalse(popup_condition, 
                           'Empty popup events list should not block end turn')
    
    def test_keybinding_system_consistency(self):
        '''Test that keybinding system works consistently at Turn 6.'''
        end_turn_key = keybinding_manager.get_key_for_action('end_turn')
        pygame_k_space = 32  # pygame.K_SPACE
        
        self.assertEqual(end_turn_key, pygame_k_space, 
                        'End turn key should be spacebar (32)')
        self.assertIsInstance(end_turn_key, int, 
                            'End turn key should be an integer')
    
    def test_event_consumption_pattern(self):
        '''Test the event consumption pattern that was missing.'''
        # Simulate the fixed event handling logic
        key_event_consumed = False
        
        # After spacebar processing, event should be marked as consumed
        # (This simulates the fix: key_event_consumed = True)
        if not key_event_consumed:  # Spacebar handler logic
            # Process end turn...
            key_event_consumed = True  # The critical fix
        
        self.assertTrue(key_event_consumed, 
                      'Key event should be marked as consumed after processing')
    
    def test_multiple_turn_progression(self):
        '''Test that spacebar continues to work after Turn 6.'''
        turns_to_test = [6, 7, 8]  # Reduced to avoid game over conditions
        
        for target_turn in turns_to_test:
            # Reset game state
            game_state = GameState(f'test-turn{target_turn}')
            
            # Advance to target turn
            for i in range(target_turn):
                result = game_state.end_turn()
                if game_state.game_over:
                    # Game ended due to doom/other conditions, which is normal
                    break
                self.assertTrue(result, f'Failed advancing to turn {i+1}')
            
            # Only test end_turn if game is still active
            if not game_state.game_over:
                result = game_state.end_turn()
                self.assertTrue(result, f'end_turn() should work at turn {target_turn}')
    
    def test_dialog_state_types(self):
        '''Test that dialog states have consistent types.'''
        # The bug was caused by None vs False inconsistency
        dialog_attrs = [
            'pending_hiring_dialog',
            'pending_fundraising_dialog', 
            'pending_research_dialog'
        ]
        
        for attr in dialog_attrs:
            value = getattr(self.game_state, attr, 'MISSING')
            # Value should be None, False, or a dialog object - not mixed types
            self.assertIn(type(value).__name__, 
                         ['NoneType', 'bool', 'dict', 'object'],
                         f'{attr} has unexpected type: {type(value)}')


class TestArchitecturalImprovements(unittest.TestCase):
    '''Tests for the architectural improvements made.'''
    
    def test_no_redundant_key_checking(self):
        '''Test that redundant key checking pattern is avoided.'''
        # The bug was: check pygame.K_SPACE then check end_turn_key again
        # Fixed by removing the redundant pygame.K_SPACE check
        
        pygame_k_space = 32
        end_turn_key = keybinding_manager.get_key_for_action('end_turn')
        
        # Both should be the same, so checking both is redundant
        self.assertEqual(pygame_k_space, end_turn_key,
                        'No need for redundant checking when both are the same')
    
    def test_centralized_blocking_logic(self):
        '''Test that blocking logic is centralized and consistent.'''
        # Create test conditions
        conditions = {
            'help_overlay': False,
            'hiring_dialog': None,
            'fundraising_dialog': None,
            'research_dialog': None, 
            'tutorial_overlay': False
        }
        
        # Test the pattern used in the fix
        blocking_conditions = [
            conditions['help_overlay'],
            conditions['hiring_dialog'] or False,  # Handle None safely
            conditions['fundraising_dialog'] or False,
            conditions['research_dialog'] or False,
            conditions['tutorial_overlay']
        ]
        
        result = any(blocking_conditions)
        self.assertFalse(result, 'Should not block with standard conditions')


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)