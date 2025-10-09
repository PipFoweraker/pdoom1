'''
Comprehensive tests for hotfix batch: Mac TypeError, GameClock bounds, and hiring dialog UX.

This test module validates the fixes implemented in the hotfix batch deployment,
ensuring all critical bugs are resolved and no regressions are introduced.
'''

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from src.services.game_clock import GameClock
from src.scores.enhanced_leaderboard import EnhancedLeaderboardManager
from src.core.research_quality import TechnicalDebt
from src.core.game_state import GameState


class TestHotfixBatch(unittest.TestCase):
    '''Test all fixes in the hotfix batch deployment.'''

    def setUp(self):
        '''Set up test environment.'''
        self.game_clock = GameClock()
        self.leaderboard_manager = EnhancedLeaderboardManager()
        
    def test_mac_technical_debt_fix_verified(self):
        '''Verify the Mac TypeError fix is working.'''
        # Create game state with technical debt
        gs = GameState('test-hotfix-mac')
        gs.technical_debt.add_debt(15)
        
        # Test the fixed leaderboard manager methods
        debt_total = self.leaderboard_manager._safe_get_technical_debt_total(gs)
        papers_count = self.leaderboard_manager._safe_get_research_papers_count(gs)
        
        self.assertEqual(debt_total, 15)
        self.assertIsInstance(debt_total, int)
        self.assertEqual(papers_count, 0)
        self.assertIsInstance(papers_count, int)
        
        # Test session creation doesn't crash
        self.leaderboard_manager.start_game_session(gs)
        self.assertIsNotNone(self.leaderboard_manager.current_session)
        self.assertEqual(self.leaderboard_manager.current_session.technical_debt_accumulated, 15)
    
    def test_gameclock_bounds_checking_fix(self):
        '''Test GameClock array bounds checking prevents IndexError.'''
        # Test normal dates (should work as before)
        normal_date = datetime(2024, 6, 15)  # June 15, valid month
        result = self.game_clock.format_date(normal_date)
        self.assertIn('Jun', result)
        self.assertIn('02024', result)
        
        # Test edge case: month = 1 (January, index 0)
        january_date = datetime(2024, 1, 1)
        result = self.game_clock.format_date(january_date)
        self.assertIn('Jan', result)
        
        # Test edge case: month = 12 (December, index 11)
        december_date = datetime(2024, 12, 31)
        result = self.game_clock.format_date(december_date)
        self.assertIn('Dec', result)
        
        # Test bounds protection with invalid datetime object
        # Create a mock datetime with invalid month
        invalid_date = Mock()
        invalid_date.day = 15
        invalid_date.month = 0  # Invalid month (would cause IndexError)
        invalid_date.year = 2024
        
        # Should not crash, should use bounds checking
        result = self.game_clock.format_date(invalid_date)
        self.assertIn('Jan', result)  # Should default to first month (index 0)
        
        # Test bounds protection with month > 12
        invalid_date.month = 15  # Invalid month > 12
        result = self.game_clock.format_date(invalid_date)
        self.assertIn('Dec', result)  # Should default to last month (index 11)
        
        # Test bounds protection with negative month
        invalid_date.month = -5  # Invalid negative month
        result = self.game_clock.format_date(invalid_date)
        self.assertIn('Jan', result)  # Should default to first month (index 0)
    
    def test_gameclock_instance_method_bounds_checking(self):
        '''Test instance method also has bounds checking.'''
        # Set up GameClock with current date
        self.game_clock.current_date = datetime(2024, 6, 15)
        
        # Normal case
        result = self.game_clock.get_formatted_date()
        self.assertIn('Jun', result)
        
        # Test with mock invalid date
        invalid_date = Mock()
        invalid_date.day = 1
        invalid_date.month = 0  # Invalid
        invalid_date.year = 2024
        
        self.game_clock.current_date = invalid_date
        result = self.game_clock.get_formatted_date()
        self.assertIn('Jan', result)  # Should use bounds checking
    
    def test_hiring_dialog_esc_functionality_exists(self):
        '''Test that hiring dialog ESC functionality is properly implemented.'''
        gs = GameState('test-hiring-esc')
        
        # Set up a pending hiring dialog
        gs.pending_hiring_dialog = {
            'available_subtypes': [{'id': 'test', 'data': {'name': 'Test Employee'}}],
            'title': 'Test Hiring',
            'description': 'Test hiring dialog'
        }
        
        # Verify dialog is active
        self.assertIsNotNone(gs.pending_hiring_dialog)
        
        # Test dismiss functionality
        gs.dismiss_hiring_dialog()
        
        # Verify dialog is dismissed
        self.assertIsNone(gs.pending_hiring_dialog)
    
    def test_hiring_dialog_insufficient_funds_handling(self):
        '''Test that hiring dialog properly handles insufficient funds.'''
        gs = GameState('test-hiring-funds')
        
        # Set up low money scenario
        gs.money = 100  # Low money
        gs.action_points = 1
        
        # Trigger hiring dialog
        gs._trigger_hiring_dialog()
        
        # Should still create dialog (allowing user to see options and cancel)
        self.assertIsNotNone(gs.pending_hiring_dialog)
        
        # Verify user can dismiss dialog with ESC
        gs.dismiss_hiring_dialog()
        self.assertIsNone(gs.pending_hiring_dialog)
    
    def test_all_safe_accessor_methods_error_handling(self):
        '''Test that all safe accessor methods handle errors gracefully.'''
        # Test with None game state
        debt_result = self.leaderboard_manager._safe_get_technical_debt_total(None)
        papers_result = self.leaderboard_manager._safe_get_research_papers_count(None)
        
        self.assertEqual(debt_result, 0)
        self.assertEqual(papers_result, 0)
        
        # Test with empty mock game state
        empty_state = Mock()
        debt_result = self.leaderboard_manager._safe_get_technical_debt_total(empty_state)
        papers_result = self.leaderboard_manager._safe_get_research_papers_count(empty_state)
        
        self.assertEqual(debt_result, 0)
        self.assertEqual(papers_result, 0)
        
        # Test with problematic game state that raises exceptions
        problematic_state = Mock()
        problematic_state.technical_debt = Mock(side_effect=ValueError('Test error'))
        
        debt_result = self.leaderboard_manager._safe_get_technical_debt_total(problematic_state)
        self.assertEqual(debt_result, 0)  # Should return 0, not crash
    
    def test_hotfix_integration_no_regressions(self):
        '''Test that fixes don't introduce regressions in normal gameplay.'''
        gs = GameState('test-integration')
        
        # Test normal game state creation
        self.assertIsNotNone(gs.technical_debt)
        self.assertEqual(gs.technical_debt.accumulated_debt, 0)
        
        # Test technical debt operations
        gs.technical_debt.add_debt(5)
        self.assertEqual(gs.technical_debt.accumulated_debt, 5)
        
        # Test leaderboard operations
        lm = EnhancedLeaderboardManager()
        lm.start_game_session(gs)
        self.assertEqual(lm.current_session.technical_debt_accumulated, 5)
        
        # Test date formatting operations
        gc = GameClock()
        formatted_date = gc.get_formatted_date()
        self.assertIsInstance(formatted_date, str)
        self.assertGreater(len(formatted_date), 0)
        
        # Test dialog operations
        self.assertIsNone(gs.pending_hiring_dialog)
        gs._trigger_hiring_dialog()
        if gs.pending_hiring_dialog:  # May not trigger if no employees available
            gs.dismiss_hiring_dialog()
            self.assertIsNone(gs.pending_hiring_dialog)


class TestHotfixRegressionPrevention(unittest.TestCase):
    '''Prevent regressions of the original bugs.'''
    
    def test_mac_bug_cannot_regress(self):
        '''Ensure Mac TypeError cannot regress by testing old problematic patterns.'''
        lm = EnhancedLeaderboardManager()
        
        # Test the old problematic pattern that caused Mac bug
        mock_gs = Mock()
        mock_gs.technical_debt = '15'  # String instead of object (old bug scenario)
        
        # New code should handle this gracefully
        result = lm._safe_get_technical_debt_total(mock_gs)
        self.assertEqual(result, 0)  # Should return 0, not crash
        
    def test_gameclock_indexerror_cannot_regress(self):
        '''Ensure GameClock IndexError cannot regress.'''
        gc = GameClock()
        
        # Test all the scenarios that could cause IndexError
        test_months = [0, -1, 13, 15, 100, -100]
        
        for invalid_month in test_months:
            mock_date = Mock()
            mock_date.day = 1
            mock_date.month = invalid_month
            mock_date.year = 2024
            
            # Should not raise IndexError
            try:
                result = gc.format_date(mock_date)
                self.assertIsInstance(result, str)
                self.assertGreater(len(result), 0)
            except IndexError:
                self.fail(f'IndexError raised for month {invalid_month} - bounds checking failed')


if __name__ == '__main__':
    unittest.main()
