'''
Unit tests for leaderboard type safety and attribute access patterns.

This test module specifically addresses the Mac TypeError bug (issue #299) where
technical_debt was incorrectly accessed as a scalar instead of an object attribute.
It ensures safe attribute access patterns across the leaderboard system.
'''

import unittest
from unittest.mock import Mock
from src.scores.enhanced_leaderboard import EnhancedLeaderboardManager
from src.core.research_quality import TechnicalDebt


class TestLeaderboardTypeSafety(unittest.TestCase):
    '''Test safe attribute access patterns in leaderboard system.'''
    
    def setUp(self):
        '''Set up test environment with mock game state.'''
        self.leaderboard_manager = EnhancedLeaderboardManager()
        
        # Create a comprehensive mock game state
        self.mock_game_state = Mock()
        self.mock_game_state.seed = 'test-seed'
        self.mock_game_state.player_name = 'Test Player'
        self.mock_game_state.lab_name = 'Test Labs'
        self.mock_game_state.money = 50000
        self.mock_game_state.staff = 10
        self.mock_game_state.reputation = 75
        self.mock_game_state.doom = 25
        self.mock_game_state.compute = 100
        
        # Create proper TechnicalDebt object
        self.technical_debt_obj = TechnicalDebt()
        self.technical_debt_obj.accumulated_debt = 15
        self.mock_game_state.technical_debt = self.technical_debt_obj
    
    def test_safe_technical_debt_access_with_valid_object(self):
        '''Test that technical debt is correctly extracted from TechnicalDebt object.'''
        result = self.leaderboard_manager._safe_get_technical_debt_total(self.mock_game_state)
        self.assertEqual(result, 15)
        self.assertIsInstance(result, int)
    
    def test_safe_technical_debt_access_with_missing_attribute(self):
        '''Test graceful handling when technical_debt attribute is missing.'''
        # Remove technical_debt attribute
        delattr(self.mock_game_state, 'technical_debt')
        
        result = self.leaderboard_manager._safe_get_technical_debt_total(self.mock_game_state)
        self.assertEqual(result, 0)
        self.assertIsInstance(result, int)
    
    def test_safe_technical_debt_access_with_none_value(self):
        '''Test graceful handling when technical_debt is None.'''
        self.mock_game_state.technical_debt = None
        
        result = self.leaderboard_manager._safe_get_technical_debt_total(self.mock_game_state)
        self.assertEqual(result, 0)
        self.assertIsInstance(result, int)
    
    def test_safe_technical_debt_access_with_invalid_object(self):
        '''Test graceful handling when technical_debt object lacks accumulated_debt.'''
        invalid_debt_obj = Mock()
        # Deliberately don't add accumulated_debt attribute
        self.mock_game_state.technical_debt = invalid_debt_obj
        
        result = self.leaderboard_manager._safe_get_technical_debt_total(self.mock_game_state)
        self.assertEqual(result, 0)
        self.assertIsInstance(result, int)
    
    def test_safe_technical_debt_access_with_string_value_mac_bug(self):
        '''Test the specific Mac bug scenario where accumulated_debt might be a string.'''
        # Simulate the bug scenario
        string_debt_obj = Mock()
        string_debt_obj.accumulated_debt = '15'  # String instead of int
        self.mock_game_state.technical_debt = string_debt_obj
        
        result = self.leaderboard_manager._safe_get_technical_debt_total(self.mock_game_state)
        self.assertEqual(result, 15)  # Should convert string to int
        self.assertIsInstance(result, int)
    
    def test_safe_technical_debt_access_with_non_numeric_string(self):
        '''Test graceful handling of non-numeric string values.'''
        invalid_debt_obj = Mock()
        invalid_debt_obj.accumulated_debt = 'invalid'
        self.mock_game_state.technical_debt = invalid_debt_obj
        
        result = self.leaderboard_manager._safe_get_technical_debt_total(self.mock_game_state)
        self.assertEqual(result, 0)
        self.assertIsInstance(result, int)
    
    def test_safe_research_papers_access_with_missing_attribute(self):
        '''Test graceful handling when research_papers_published doesn't exist.'''
        # research_papers_published doesn't exist in current game state
        result = self.leaderboard_manager._safe_get_research_papers_count(self.mock_game_state)
        self.assertEqual(result, 0)
        self.assertIsInstance(result, int)
    
    def test_safe_research_papers_access_with_valid_attribute(self):
        '''Test extraction when research_papers_published exists.'''
        self.mock_game_state.research_papers_published = 5
        
        result = self.leaderboard_manager._safe_get_research_papers_count(self.mock_game_state)
        self.assertEqual(result, 5)
        self.assertIsInstance(result, int)
    
    def test_safe_research_papers_access_with_string_value(self):
        '''Test conversion when research_papers_published is a string.'''
        self.mock_game_state.research_papers_published = '3'
        
        result = self.leaderboard_manager._safe_get_research_papers_count(self.mock_game_state)
        self.assertEqual(result, 3)
        self.assertIsInstance(result, int)
    
    def test_safe_research_papers_access_with_invalid_string(self):
        '''Test graceful handling of invalid string values.'''
        self.mock_game_state.research_papers_published = 'invalid'
        
        result = self.leaderboard_manager._safe_get_research_papers_count(self.mock_game_state)
        self.assertEqual(result, 0)
        self.assertIsInstance(result, int)
    
    def test_session_creation_with_safe_accessors(self):
        '''Test that session creation uses safe accessor methods properly.'''
        self.leaderboard_manager.start_game_session(self.mock_game_state)
        
        session = self.leaderboard_manager.current_session
        self.assertIsNotNone(session)
        self.assertEqual(session.technical_debt_accumulated, 15)
        self.assertEqual(session.research_papers_published, 0)  # Default since not implemented
        self.assertIsInstance(session.technical_debt_accumulated, int)
        self.assertIsInstance(session.research_papers_published, int)
    
    def test_verbose_method_naming_prevents_confusion(self):
        '''Test that verbose method names clearly indicate what they return.'''
        # Method names should be self-documenting
        self.assertTrue(hasattr(self.leaderboard_manager, '_safe_get_technical_debt_total'))
        self.assertTrue(hasattr(self.leaderboard_manager, '_safe_get_research_papers_count'))
        
        # These methods should return int values, not objects
        debt_result = self.leaderboard_manager._safe_get_technical_debt_total(self.mock_game_state)
        papers_result = self.leaderboard_manager._safe_get_research_papers_count(self.mock_game_state)
        
        self.assertIsInstance(debt_result, int)
        self.assertIsInstance(papers_result, int)
        self.assertNotIsInstance(debt_result, TechnicalDebt)  # Should NOT be the object
    
    def test_exception_handling_in_safe_accessors(self):
        '''Test that all exceptions are properly caught and handled.'''
        # Create a mock that raises various exceptions
        problematic_game_state = Mock()
        problematic_game_state.technical_debt = Mock()
        problematic_game_state.technical_debt.accumulated_debt = Mock(side_effect=ValueError('Test error'))
        
        # Should not raise exceptions, should return default values
        debt_result = self.leaderboard_manager._safe_get_technical_debt_total(problematic_game_state)
        papers_result = self.leaderboard_manager._safe_get_research_papers_count(problematic_game_state)
        
        self.assertEqual(debt_result, 0)
        self.assertEqual(papers_result, 0)
        self.assertIsInstance(debt_result, int)
        self.assertIsInstance(papers_result, int)


class TestTechnicalDebtObjectIntegrity(unittest.TestCase):
    '''Test that TechnicalDebt objects maintain proper types.'''
    
    def test_technical_debt_accumulated_is_always_int(self):
        '''Ensure TechnicalDebt.accumulated_debt is always an integer.'''
        debt = TechnicalDebt()
        
        # Initial value should be int
        self.assertIsInstance(debt.accumulated_debt, int)
        self.assertEqual(debt.accumulated_debt, 0)
        
        # After adding debt
        debt.add_debt(5)
        self.assertIsInstance(debt.accumulated_debt, int)
        self.assertEqual(debt.accumulated_debt, 5)
        
        # After reducing debt
        debt.reduce_debt(2)
        self.assertIsInstance(debt.accumulated_debt, int)
        self.assertEqual(debt.accumulated_debt, 3)
    
    def test_technical_debt_operations_preserve_type(self):
        '''Test that all TechnicalDebt operations maintain integer types.'''
        debt = TechnicalDebt()
        
        # Test various operations
        debt.add_debt(10)
        self.assertIsInstance(debt.accumulated_debt, int)
        
        debt.reduce_debt(3)
        self.assertIsInstance(debt.accumulated_debt, int)
        
        # Test edge cases
        debt.reduce_debt(100)  # More than available
        self.assertIsInstance(debt.accumulated_debt, int)
        self.assertGreaterEqual(debt.accumulated_debt, 0)


if __name__ == '__main__':
    unittest.main()
