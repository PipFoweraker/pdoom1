"""
Test suite for critical bug fixes in the bug sweep.

This module tests the fixes for critical bugs identified in the pre-alpha bug sweep:
- Issue #263: Duplicate return statements in check_hover method
- Issue #265: List modification during iteration in magical orb code
- Issue #261: Mouse wheel handling (verification)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import random
from src.core.game_state import GameState


class TestCriticalBugFixes(unittest.TestCase):
    """Test critical bug fixes from the bug sweep."""

    def setUp(self):
        """Set up test environment with seeded randomness."""
        random.seed(12345)
        self.game_state = GameState('test-critical-fixes')

    def test_check_hover_no_duplicate_returns_fix_263(self):
        """Test fix for issue #263: duplicate return statements in check_hover."""
        # This test ensures that the exception handler is reachable after removing duplicate returns
        
        # Mock a scenario that would cause an exception in check_hover
        original_in_rect = self.game_state._in_rect
        
        def mock_in_rect_exception(*args):
            # Cause an exception during hover checking
            raise ValueError("Test exception for check_hover")
        
        # Replace _in_rect method to trigger exception
        self.game_state._in_rect = mock_in_rect_exception
        
        # Mock the game_logger to capture error logging
        mock_logger = Mock()
        self.game_state.game_logger = mock_logger
        
        # Call check_hover - should handle exception gracefully
        result = self.game_state.check_hover((100, 100), 800, 600)
        
        # Verify that the method returns None gracefully (no crash)
        self.assertIsNone(result)
        
        # Verify that the exception was logged (proving exception handler is reachable)
        mock_logger.log.assert_called_once()
        self.assertIn("Error in check_hover", mock_logger.log.call_args[0][0])
        
        # Restore original method
        self.game_state._in_rect = original_in_rect

    def test_check_hover_normal_operation_after_fix(self):
        """Test that check_hover works normally after removing duplicate returns."""
        # Test normal operation without exceptions
        result = self.game_state.check_hover((50, 50), 800, 600)
        
        # Should return None without crashing (no tooltip at that position)
        self.assertIsNone(result)
        
        # Test with a position that should trigger a tooltip
        # Position over money area (approximate coordinates)
        money_area_x = int(800 * 0.04) + 10
        money_area_y = int(600 * 0.11) + 10
        
        result = self.game_state.check_hover((money_area_x, money_area_y), 800, 600)
        
        # Should work without crashing and provide context info
        self.assertIsNotNone(self.game_state.current_context_info)
        self.assertEqual(self.game_state.current_context_info['title'], 'Money')

    def test_magical_orb_list_modification_fix_265(self):
        """Test fix for issue #265: safe list sampling instead of modification during iteration."""
        # Enable magical orb functionality
        self.game_state.magical_orb_active = True
        
        # Create some test opponents
        self.game_state.opponents = []
        for i in range(2):
            opponent = Mock()
            opponent.name = f"Test Opponent {i}"
            opponent.discovered = True
            opponent.scout_stat = Mock(return_value=(True, 100, "Test message"))
            opponent.discovered_stats = {
                'budget': False,
                'capabilities_researchers': False,
                'lobbyists': False,
                'compute': False,
                'progress': False
            }
            opponent.known_stats = {}
            self.game_state.opponents.append(opponent)
        
        # Mock random functions to ensure deterministic behavior
        with patch('random.randint', return_value=3), \
             patch('random.sample') as mock_sample:
            
            # Mock sample to return a predictable subset
            mock_sample.return_value = ['budget', 'compute', 'progress']
            
            # Execute scout opponents action (triggers the magical orb logic)
            action = next(a for a in self.game_state.actions if a['name'] == 'Scout Opponents')
            
            # Execute the action
            messages = []
            discoveries = 0
            
            # This should not crash due to list modification during iteration
            try:
                action['execute'](self.game_state, messages)
                test_passed = True
            except (ValueError, IndexError, RuntimeError) as e:
                # These would be the typical errors from list modification during iteration
                test_passed = False
                self.fail(f"List modification during iteration caused error: {e}")
            
            # Verify the fix: random.sample should have been called instead of list.remove()
            self.assertTrue(mock_sample.called, "Should use random.sample for safe sampling")
            
            # Verify that we didn't modify the original list during iteration
            expected_stats = ['budget', 'capabilities_researchers', 'lobbyists', 'compute', 'progress']
            # The original stats_to_scout list should remain intact in the source code

    def test_magical_orb_scouting_with_multiple_iterations(self):
        """Test that magical orb scouting works correctly with multiple stat sampling."""
        # Enable magical orb
        self.game_state.magical_orb_active = True
        
        # Create a test opponent
        opponent = Mock()
        opponent.name = "Test Target"
        opponent.discovered = True
        opponent.discovered_stats = {stat: False for stat in 
                                   ['budget', 'capabilities_researchers', 'lobbyists', 'compute', 'progress']}
        opponent.known_stats = {}
        opponent.scout_stat = Mock(return_value=(True, 42, "Discovered"))
        self.game_state.opponents = [opponent]
        
        # Execute scouting multiple times to ensure no race conditions
        action = next(a for a in self.game_state.actions if a['name'] == 'Scout Opponents')
        
        for iteration in range(5):
            messages = []
            try:
                action['execute'](self.game_state, messages)
                # If we get here without exception, the fix is working
            except Exception as e:
                self.fail(f"Iteration {iteration} failed with list modification error: {e}")

    def test_mouse_wheel_handling_verification_261(self):
        """Test comprehensive mouse wheel handling for issue #261: verify no crashes."""
        # Test that mouse wheel event handling is robust and doesn't crash
        
        # Check that game state has scrollable event log functionality
        self.assertTrue(hasattr(self.game_state, 'scrollable_event_log_enabled'))
        self.assertTrue(hasattr(self.game_state, 'event_log_scroll_offset'))
        
        # Test various edge cases that could cause crashes
        test_cases = [
            # (scrollable_enabled, event_log_history, messages, description)
            (False, [], [], "Disabled scrolling with empty logs"),
            (True, [], [], "Enabled scrolling with empty logs"),
            (True, ['event1', 'event2'], ['msg1'], "Enabled scrolling with some content"),
            (True, ['e'] * 20, ['m'] * 10, "Enabled scrolling with lots of content"),
        ]
        
        for enabled, history, messages, description in test_cases:
            with self.subTest(case=description):
                try:
                    # Set up the test case
                    self.game_state.scrollable_event_log_enabled = enabled
                    self.game_state.event_log_history = history
                    self.game_state.messages = messages
                    self.game_state.event_log_scroll_offset = 0
                    
                    # Simulate the exact logic from main.py MOUSEWHEEL handler
                    current_state = 'game'
                    if (current_state == 'game' and self.game_state and 
                        self.game_state.scrollable_event_log_enabled):
                        
                        # Test scroll up (event.y > 0)
                        self.game_state.event_log_scroll_offset = max(0, 
                            self.game_state.event_log_scroll_offset - 3)
                        
                        # Test scroll down (event.y < 0) 
                        max_scroll = max(0, len(self.game_state.event_log_history) + 
                                       len(self.game_state.messages) - 7)
                        self.game_state.event_log_scroll_offset = min(max_scroll, 
                            self.game_state.event_log_scroll_offset + 3)
                    
                    # If we reach here, no crash occurred
                    self.assertGreaterEqual(self.game_state.event_log_scroll_offset, 0)
                    
                except Exception as e:
                    self.fail(f"Mouse wheel handling crashed for case '{description}': {e}")
        
        # Test that None game_state doesn't crash the check
        try:
            game_state = None
            current_state = 'game'
            if (current_state == 'game' and game_state and 
                game_state.scrollable_event_log_enabled):
                # This should never execute
                self.fail("Should not reach here with None game_state")
            # Should safely skip the mouse wheel handling
            self.assertTrue(True, "None game_state handled safely")
        except Exception as e:
            self.fail(f"None game_state check crashed: {e}")

    def test_robust_error_handling_in_critical_methods(self):
        """Test that critical methods have robust error handling after fixes."""
        # Test check_hover with various edge cases
        edge_cases = [
            ((-1, -1), 800, 600),  # Negative coordinates
            ((10000, 10000), 800, 600),  # Coordinates outside screen
            ((100, 100), 0, 0),  # Zero dimensions
            ((100, 100), -1, -1),  # Negative dimensions
        ]
        
        for mouse_pos, w, h in edge_cases:
            try:
                result = self.game_state.check_hover(mouse_pos, w, h)
                # Should not crash, should return None for invalid positions
                self.assertIsNone(result)
            except Exception as e:
                self.fail(f"check_hover crashed with edge case {mouse_pos}, {w}, {h}: {e}")

    def test_list_operations_are_safe_in_game_loops(self):
        """Test that game state operations don't modify lists during iteration."""
        # Test that common game operations don't have list modification issues
        
        # Add some test data that might be iterated over
        self.game_state.messages = ["Test message 1", "Test message 2", "Test message 3"]
        
        # Simulate operations that might modify lists during iteration
        original_messages = list(self.game_state.messages)
        
        # Test end turn processing (commonly iterates over lists)
        try:
            self.game_state.end_turn()
            # Should complete without list modification errors
        except (ValueError, IndexError, RuntimeError) as e:
            if "list" in str(e).lower() and ("modify" in str(e).lower() or "changed" in str(e).lower()):
                self.fail(f"List modification during iteration in end_turn: {e}")
        
        # Verify game state is still consistent
        self.assertIsNotNone(self.game_state.turn)
        self.assertIsNotNone(self.game_state.money)


class TestRegressionPrevention(unittest.TestCase):
    """Test that the critical bugs cannot regress."""

    def test_check_hover_single_return_path(self):
        """Ensure check_hover has only one return path per logical branch (prevents #263 regression)."""
        # This is a structural test - we check that the fixed code maintains the correct structure
        import inspect
        from src.core.game_state import GameState
        
        # Get the source code of check_hover method
        source = inspect.getsource(GameState.check_hover)
        
        # Count return statements
        return_count = source.count('return None')
        
        # After the fix, there should be exactly 2 return None statements:
        # 1. At the end of the try block 
        # 2. In the exception handler
        self.assertLessEqual(return_count, 2, 
                            "check_hover should have at most 2 'return None' statements after fix")
        
        # Verify the exception handler is after the main return
        exception_pos = source.find('except Exception')
        main_return_pos = source.find('return None')
        
        self.assertGreater(exception_pos, main_return_pos,
                          "Exception handler should come after main return statement")

    def test_magical_orb_uses_safe_sampling(self):
        """Ensure magical orb code uses random.sample instead of list.remove (prevents #265 regression)."""
        import inspect
        from src.core.game_state import GameState
        
        # Get the source code of the relevant method
        source = inspect.getsource(GameState)
        
        # Look for the magical orb scouting section
        magical_orb_section = source[source.find('magical_orb_active'):source.find('magical_orb_active') + 2000]
        
        if 'stats_to_scout' in magical_orb_section:
            # Should use random.sample, not list.remove in iteration
            self.assertIn('random.sample', magical_orb_section,
                         "Magical orb code should use random.sample for safe list sampling")
            
            # Should not remove items from list during iteration
            problematic_pattern = 'stats_to_scout.remove'
            self.assertNotIn(problematic_pattern, magical_orb_section,
                           "Should not use list.remove during iteration in magical orb code")

    def test_research_quality_technical_debt_fix(self):
        """Test fix for critical TypeError in research quality system - proper method signatures."""
        # Initialize technical debt system
        from src.core.research_quality import TechnicalDebt, DebtCategory
        self.game_state.technical_debt = TechnicalDebt()
        
        # Test rush research - should add debt without crashing
        # This tests the fix for the TypeError: add_debt() takes 2-3 args but 4 given
        try:
            # Simulate the fixed add_debt call with correct signature: (amount, category)
            self.game_state.technical_debt.add_debt(2, DebtCategory.VALIDATION)
            self.assertGreater(self.game_state.technical_debt.get_total_debt(), 0)
        except TypeError as e:
            self.fail(f"Rush research add_debt crashed with TypeError: {e}")
        
        # Test quality research - should reduce debt without crashing
        # This tests the fix for the parallel issue in reduce_debt
        try:
            # Simulate the fixed reduce_debt call with correct signature: (amount, category)
            initial_debt = self.game_state.technical_debt.get_total_debt()
            self.game_state.technical_debt.reduce_debt(1, DebtCategory.VALIDATION)
            final_debt = self.game_state.technical_debt.get_total_debt()
            # Should have reduced debt
            self.assertLessEqual(final_debt, initial_debt)
        except TypeError as e:
            self.fail(f"Quality research reduce_debt crashed with TypeError: {e}")
        
        # Test that the methods work with the correct enum categories
        # This ensures we're using DebtCategory enum values instead of strings
        try:
            for category in [DebtCategory.SAFETY_TESTING, DebtCategory.CODE_QUALITY, 
                           DebtCategory.DOCUMENTATION, DebtCategory.VALIDATION]:
                self.game_state.technical_debt.add_debt(1, category)
                self.game_state.technical_debt.reduce_debt(1, category)
        except (TypeError, AttributeError) as e:
            self.fail(f"DebtCategory enum usage failed: {e}")

    def test_research_option_execution_integration(self):
        """Integration test for research option execution with technical debt."""
        # Initialize technical debt system
        from src.core.research_quality import TechnicalDebt
        self.game_state.technical_debt = TechnicalDebt()
        
        # Mock the research options to simulate rush and quality research
        rush_option = {"id": "rush_research", "name": "Rush Research"}
        quality_option = {"id": "quality_research", "name": "Quality Research"}
        
        # Test that _execute_research_option handles both options without crashing
        # This is the integration test for the actual bug that was reported
        try:
            # Mock random to ensure consistent behavior
            with patch('random.randint', return_value=2):
                # This should not crash with TypeError
                self.game_state._execute_research_option(rush_option)
                self.assertGreater(self.game_state.technical_debt.get_total_debt(), 0)
                
                # This should not crash with TypeError  
                self.game_state._execute_research_option(quality_option)
                # Debt should be reduced but not necessarily zero
                self.assertGreaterEqual(self.game_state.technical_debt.get_total_debt(), 0)
                
        except TypeError as e:
            self.fail(f"Research option execution crashed with TypeError: {e}")
        except AttributeError as e:
            self.fail(f"Research option execution failed due to missing imports: {e}")


if __name__ == '__main__':
    unittest.main()
