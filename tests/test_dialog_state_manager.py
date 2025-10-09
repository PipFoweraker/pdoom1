'''
Unit tests for DialogStateManager - Modal dialog state management

Tests the centralized dialog state handling logic to ensure proper
modal blocking, state validation, and None vs False consistency.

Follows patterns established in test_turn6_spacebar_regression.py and
provides comprehensive coverage for dialog state management.
'''

import unittest
from unittest.mock import Mock, patch

from src.core.dialog_state_manager import DialogStateManager, DialogType, ModalState
from src.core.game_state import GameState


class TestDialogStateManager(unittest.TestCase):
    '''Unit tests for DialogStateManager modal dialog handling.'''
    
    def setUp(self):
        '''Set up test fixtures with mock game state.'''
        self.game_state = Mock(spec=GameState)
        
        # Initialize all dialog attributes to None (must set all for proper testing)
        self.game_state.pending_hiring_dialog = None
        self.game_state.pending_fundraising_dialog = None
        self.game_state.pending_research_dialog = None
        self.game_state.pending_intelligence_dialog = None
        self.game_state.pending_media_dialog = None
        self.game_state.pending_technical_debt_dialog = None
        
        # Ensure hasattr checks work correctly
        self.game_state.spec = [
            'pending_hiring_dialog', 'pending_fundraising_dialog', 
            'pending_research_dialog', 'pending_intelligence_dialog',
            'pending_media_dialog', 'pending_technical_debt_dialog',
            'dismiss_hiring_dialog', 'dismiss_fundraising_dialog',
            'dismiss_research_dialog', 'dismiss_intelligence_dialog'
        ]
        
        # Mock dialog dismiss methods
        self.game_state.dismiss_hiring_dialog = Mock()
        self.game_state.dismiss_fundraising_dialog = Mock()
        self.game_state.dismiss_research_dialog = Mock()
        self.game_state.dismiss_intelligence_dialog = Mock()
        
        self.dialog_manager = DialogStateManager(self.game_state)
    
    def test_no_active_dialogs_initially(self):
        '''Test that no dialogs are active initially.'''
        self.assertFalse(self.dialog_manager.has_blocking_dialog())
        self.assertEqual(len(self.dialog_manager.get_active_dialogs()), 0)
        self.assertIsNone(self.dialog_manager.get_blocking_dialog())
    
    def test_hiring_dialog_detection(self):
        '''Test detection of active hiring dialog.'''
        # Set hiring dialog as active
        self.game_state.pending_hiring_dialog = {'type': 'hiring', 'candidates': []}
        
        self.assertTrue(self.dialog_manager.is_dialog_active(DialogType.HIRING))
        self.assertTrue(self.dialog_manager.has_blocking_dialog())
        self.assertEqual(self.dialog_manager.get_blocking_dialog(), DialogType.HIRING)
        self.assertIn(DialogType.HIRING, self.dialog_manager.get_active_dialogs())
    
    def test_fundraising_dialog_detection(self):
        '''Test detection of active fundraising dialog.'''
        self.game_state.pending_fundraising_dialog = {'type': 'fundraising'}
        
        self.assertTrue(self.dialog_manager.is_dialog_active(DialogType.FUNDRAISING))
        self.assertTrue(self.dialog_manager.has_blocking_dialog())
        self.assertEqual(self.dialog_manager.get_blocking_dialog(), DialogType.FUNDRAISING)
    
    def test_research_dialog_detection(self):
        '''Test detection of active research dialog.'''
        self.game_state.pending_research_dialog = {'type': 'research'}
        
        self.assertTrue(self.dialog_manager.is_dialog_active(DialogType.RESEARCH))
        self.assertTrue(self.dialog_manager.has_blocking_dialog())
        self.assertEqual(self.dialog_manager.get_blocking_dialog(), DialogType.RESEARCH)
    
    def test_intelligence_dialog_detection(self):
        '''Test detection of active intelligence dialog.'''
        self.game_state.pending_intelligence_dialog = {'type': 'intelligence'}
        
        self.assertTrue(self.dialog_manager.is_dialog_active(DialogType.INTELLIGENCE))
        self.assertTrue(self.dialog_manager.has_blocking_dialog())
        self.assertEqual(self.dialog_manager.get_blocking_dialog(), DialogType.INTELLIGENCE)
    
    def test_none_vs_false_handling(self):
        '''Test that None and False are both treated as inactive.'''
        # Test None (correct inactive state)
        self.game_state.pending_hiring_dialog = None
        self.assertFalse(self.dialog_manager.is_dialog_active(DialogType.HIRING))
        
        # Test False (incorrect but should still be inactive)
        self.game_state.pending_hiring_dialog = False
        self.assertFalse(self.dialog_manager.is_dialog_active(DialogType.HIRING))
    
    def test_multiple_dialogs_priority(self):
        '''Test dialog priority when multiple dialogs are active.'''
        # Set up multiple dialogs
        self.game_state.pending_hiring_dialog = {'type': 'hiring'}
        self.game_state.pending_fundraising_dialog = {'type': 'fundraising'}
        
        active_dialogs = self.dialog_manager.get_active_dialogs()
        self.assertEqual(len(active_dialogs), 2)
        self.assertIn(DialogType.HIRING, active_dialogs)
        self.assertIn(DialogType.FUNDRAISING, active_dialogs)
        
        # Should return highest priority dialog (hiring comes before fundraising in priority)
        blocking_dialog = self.dialog_manager.get_blocking_dialog()
        self.assertEqual(blocking_dialog, DialogType.HIRING)
    
    @patch('src.features.onboarding.onboarding')
    def test_tutorial_priority(self, mock_onboarding):
        '''Test that tutorial has highest priority.'''
        # Set tutorial active
        mock_onboarding.show_tutorial_overlay = True
        
        # Also set a game dialog
        self.game_state.pending_hiring_dialog = {'type': 'hiring'}
        
        # Tutorial should have priority
        self.assertTrue(self.dialog_manager.is_dialog_active(DialogType.TUTORIAL))
        self.assertEqual(self.dialog_manager.get_blocking_dialog(), DialogType.TUTORIAL)
    
    def test_dismiss_hiring_dialog(self):
        '''Test dismissing hiring dialog.'''
        self.game_state.pending_hiring_dialog = {'type': 'hiring'}
        
        result = self.dialog_manager.dismiss_dialog(DialogType.HIRING)
        
        self.assertTrue(result)
        self.game_state.dismiss_hiring_dialog.assert_called_once()
    
    def test_dismiss_fundraising_dialog(self):
        '''Test dismissing fundraising dialog.'''
        self.game_state.pending_fundraising_dialog = {'type': 'fundraising'}
        
        result = self.dialog_manager.dismiss_dialog(DialogType.FUNDRAISING)
        
        self.assertTrue(result)
        self.game_state.dismiss_fundraising_dialog.assert_called_once()
    
    def test_dismiss_research_dialog(self):
        '''Test dismissing research dialog.'''
        self.game_state.pending_research_dialog = {'type': 'research'}
        
        result = self.dialog_manager.dismiss_dialog(DialogType.RESEARCH)
        
        self.assertTrue(result)
        self.game_state.dismiss_research_dialog.assert_called_once()
    
    def test_dismiss_intelligence_dialog(self):
        '''Test dismissing intelligence dialog.'''
        self.game_state.pending_intelligence_dialog = {'type': 'intelligence'}
        
        result = self.dialog_manager.dismiss_dialog(DialogType.INTELLIGENCE)
        
        self.assertTrue(result)
        self.game_state.dismiss_intelligence_dialog.assert_called_once()
    
    @patch('src.features.onboarding.onboarding')
    def test_dismiss_tutorial(self, mock_onboarding):
        '''Test dismissing tutorial.'''
        mock_onboarding.show_tutorial_overlay = True
        mock_onboarding.dismiss_tutorial = Mock()
        
        result = self.dialog_manager.dismiss_dialog(DialogType.TUTORIAL)
        
        self.assertTrue(result)
        mock_onboarding.dismiss_tutorial.assert_called_once()
    
    def test_dismiss_inactive_dialog(self):
        '''Test dismissing a dialog that isn't active.'''
        # No hiring dialog active
        self.game_state.pending_hiring_dialog = None
        
        result = self.dialog_manager.dismiss_dialog(DialogType.HIRING)
        
        # Should still call the dismiss method but return False since nothing was active
        self.assertFalse(result)
    
    def test_dismiss_all_dialogs(self):
        '''Test dismissing all active dialogs.'''
        # Set up multiple active dialogs
        self.game_state.pending_hiring_dialog = {'type': 'hiring'}
        self.game_state.pending_fundraising_dialog = {'type': 'fundraising'}
        self.game_state.pending_research_dialog = {'type': 'research'}
        
        dismissed_count = self.dialog_manager.dismiss_all_dialogs()
        
        # Should have dismissed 3 dialogs
        self.assertEqual(dismissed_count, 3)
        self.game_state.dismiss_hiring_dialog.assert_called_once()
        self.game_state.dismiss_fundraising_dialog.assert_called_once()
        self.game_state.dismiss_research_dialog.assert_called_once()
    
    def test_blocking_feedback_messages(self):
        '''Test appropriate blocking feedback messages.'''
        # Test hiring dialog feedback
        self.game_state.pending_hiring_dialog = {'type': 'hiring'}
        message = self.dialog_manager.get_blocking_feedback_message()
        self.assertIn('hiring dialog', message)
        
        # Test fundraising dialog feedback
        self.game_state.pending_hiring_dialog = None
        self.game_state.pending_fundraising_dialog = {'type': 'fundraising'}
        message = self.dialog_manager.get_blocking_feedback_message()
        self.assertIn('funding dialog', message)
        
        # Test research dialog feedback
        self.game_state.pending_fundraising_dialog = None
        self.game_state.pending_research_dialog = {'type': 'research'}
        message = self.dialog_manager.get_blocking_feedback_message()
        self.assertIn('research dialog', message)
    
    @patch('src.features.onboarding.onboarding')
    def test_tutorial_feedback_message(self, mock_onboarding):
        '''Test tutorial blocking feedback message.'''
        mock_onboarding.show_tutorial_overlay = True
        
        message = self.dialog_manager.get_blocking_feedback_message()
        self.assertIn('tutorial', message)
    
    def test_validate_dialog_states_no_issues(self):
        '''Test state validation with no issues.'''
        # All dialogs properly set to None
        issues = self.dialog_manager.validate_dialog_states()
        self.assertEqual(len(issues), 0)
    
    def test_validate_dialog_states_false_issue(self):
        '''Test state validation detects False values.'''
        # Set a dialog to False instead of None
        self.game_state.pending_hiring_dialog = False
        
        issues = self.dialog_manager.validate_dialog_states()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any('should be None' in issue for issue in issues))
    
    def test_emergency_cleanup(self):
        '''Test emergency cleanup of stuck dialog states.'''
        # Set up multiple stuck dialogs (some with data, some False)
        self.game_state.pending_hiring_dialog = {'stuck': True}
        self.game_state.pending_fundraising_dialog = False  # Wrong state
        self.game_state.pending_research_dialog = None  # Correct state
        
        cleanup_count = self.dialog_manager.emergency_cleanup()
        
        # Should have cleaned up 1 dialog (the one with data)
        self.assertEqual(cleanup_count, 1)
        
        # All should now be None
        self.assertIsNone(self.game_state.pending_hiring_dialog)
        self.assertIsNone(self.game_state.pending_fundraising_dialog)
        self.assertIsNone(self.game_state.pending_research_dialog)
    
    @patch('pygame.time.get_ticks')
    def test_blocking_state_caching(self, mock_time):
        '''Test that blocking state is cached for performance.'''
        mock_time.return_value = 0
        
        # First call should calculate
        self.game_state.pending_hiring_dialog = {'type': 'hiring'}
        result1 = self.dialog_manager.has_blocking_dialog()
        
        # Second call within timeout should use cache
        mock_time.return_value = 50  # Within 100ms timeout
        result2 = self.dialog_manager.has_blocking_dialog()
        
        self.assertEqual(result1, result2)
        self.assertTrue(result1)
        
        # Call after timeout should recalculate
        mock_time.return_value = 150  # Past 100ms timeout
        self.game_state.pending_hiring_dialog = None  # Change state
        result3 = self.dialog_manager.has_blocking_dialog()
        
        self.assertFalse(result3)  # Should detect the change
    
    def test_context_manager_usage(self):
        '''Test using dialog manager as context manager.'''
        with self.dialog_manager as dm:
            # Set up a dialog
            self.game_state.pending_hiring_dialog = {'type': 'hiring'}
            
            # Should detect it
            self.assertTrue(dm.has_blocking_dialog())
        
        # Context should exit cleanly
        self.assertIsNotNone(self.dialog_manager)
    
    def test_context_manager_validation_on_exit(self):
        '''Test context manager performs validation on exit.'''
        # This is more of a smoke test since the validation logic
        # is already tested separately
        with self.dialog_manager:
            self.game_state.pending_hiring_dialog = {'type': 'hiring'}
        
        # Should exit without errors
        self.assertTrue(True)
    
    def test_dialog_type_coverage(self):
        '''Test that all dialog types are properly handled.'''
        # This ensures we haven't missed any dialog types
        all_dialog_types = {
            DialogType.HIRING,
            DialogType.FUNDRAISING,
            DialogType.RESEARCH,
            DialogType.INTELLIGENCE,
            DialogType.MEDIA,
            DialogType.TECHNICAL_DEBT,
            DialogType.HELP,
            DialogType.TUTORIAL
        }
        
        # Test that each type can be checked
        for dialog_type in all_dialog_types:
            # Should not raise an exception
            self.dialog_manager.is_dialog_active(dialog_type)
            self.dialog_manager.dismiss_dialog(dialog_type)
    
    def test_get_active_dialogs_immutable(self):
        '''Test that get_active_dialogs returns an immutable copy.'''
        self.game_state.pending_hiring_dialog = {'type': 'hiring'}
        
        active_dialogs1 = self.dialog_manager.get_active_dialogs()
        active_dialogs2 = self.dialog_manager.get_active_dialogs()
        
        # Should be separate objects
        self.assertIsNot(active_dialogs1, active_dialogs2)
        
        # But with same content
        self.assertEqual(active_dialogs1, active_dialogs2)
        
        # Modifying returned set should not affect internal state
        active_dialogs1.clear()
        active_dialogs3 = self.dialog_manager.get_active_dialogs()
        self.assertGreater(len(active_dialogs3), 0)


if __name__ == '__main__':
    unittest.main()