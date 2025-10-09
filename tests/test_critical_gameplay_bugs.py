"""
Test critical gameplay bugs fixes for Issue #382.

This test suite validates the fixes for:
1. Action Points counting bug - AP inflation from 3 to 4
2. Fundraising mechanics bug - function signature error

The fixes implement a new AP architecture:
- Base AP = 1 (player inherent capacity)
- Staff bonus = staff_count * 0.5
- Admin bonus = admin_staff * 1.0
- Proper rounding for fractional values
"""

import unittest
from src.core.game_state import GameState
from src.core import actions


class TestCriticalGameplayBugFixes(unittest.TestCase):
    """Test suite for critical gameplay bug fixes."""

    def setUp(self):
        """Set up test fixtures."""
        self.game_state = GameState('test-seed-critical-bugs')

    def test_action_points_initialization(self):
        """Test that action points initialize correctly with new architecture."""
        # Default game starts with 2 staff
        self.assertEqual(self.game_state.staff, 2)
        
        # With new architecture: 1 base + 2 staff * 0.5 = 2 AP
        expected_ap = 1 + (2 * 0.5)  # 2 AP
        self.assertEqual(self.game_state.action_points, expected_ap)
        self.assertEqual(self.game_state.max_action_points, expected_ap)

    def test_action_points_calculation_various_staff(self):
        """Test action points calculation with different staff counts."""
        test_cases = [
            (0, 1),    # 1 + 0 * 0.5 = 1
            (1, 2),    # 1 + 1 * 0.5 = 1.5 -> rounds to 2
            (2, 2),    # 1 + 2 * 0.5 = 2
            (3, 2),    # 1 + 3 * 0.5 = 2.5 -> rounds to 2  
            (4, 3),    # 1 + 4 * 0.5 = 3
            (5, 4),    # 1 + 5 * 0.5 = 3.5 -> rounds to 4
            (10, 6),   # 1 + 10 * 0.5 = 6
        ]
        
        original_staff = self.game_state.staff
        
        for staff_count, expected_ap in test_cases:
            with self.subTest(staff=staff_count):
                self.game_state.staff = staff_count
                calculated_ap = self.game_state.calculate_max_ap()
                self.assertEqual(calculated_ap, expected_ap,
                    f"Staff {staff_count}: expected {expected_ap} AP, got {calculated_ap} AP")
        
        # Restore original state
        self.game_state.staff = original_staff

    def test_action_points_refresh_consistency(self):
        """Test that action points refresh consistently every turn."""
        # Test multiple turns to ensure consistency
        expected_ap = self.game_state.calculate_max_ap()
        
        for turn in range(1, 6):
            with self.subTest(turn=turn):
                # Consume some AP
                self.game_state.action_points = 0
                
                # Advance turn
                self.game_state.end_turn()
                
                # Check AP is refreshed correctly
                self.assertEqual(self.game_state.action_points, expected_ap,
                    f"Turn {turn}: AP not refreshed correctly")

    def test_action_points_with_admin_staff(self):
        """Test action points calculation including admin staff bonuses."""
        # Set up test scenario
        self.game_state.staff = 2        # Regular staff: 2 * 0.5 = 1 AP
        self.game_state.admin_staff = 1  # Admin staff: 1 * 1.0 = 1 AP
        
        # Expected: 1 base + 1 staff + 1 admin = 3 AP
        expected_ap = 1 + (2 * 0.5) + (1 * 1.0)  # 3 AP
        calculated_ap = self.game_state.calculate_max_ap()
        
        self.assertEqual(calculated_ap, expected_ap,
            f"With admin staff: expected {expected_ap} AP, got {calculated_ap} AP")

    def test_fundraising_function_execution(self):
        """Test that fundraising function executes without signature errors."""
        initial_money = self.game_state.money
        
        # This should not raise any errors about function signature
        try:
            actions.execute_fundraising_action(self.game_state)
        except TypeError as e:
            if "positional argument" in str(e):
                self.fail(f"Fundraising function signature error: {e}")
            else:
                raise
        
        # Verify money increased
        self.assertGreater(self.game_state.money, initial_money,
            "Fundraising should increase money")

    def test_fundraising_multiple_executions(self):
        """Test fundraising can be executed multiple times without errors."""
        results = []
        
        for i in range(3):
            initial_money = self.game_state.money
            actions.execute_fundraising_action(self.game_state)
            raised = self.game_state.money - initial_money
            results.append(raised)
            
            # Each fundraising should raise some money
            self.assertGreater(raised, 0, f"Fundraising {i+1} should raise money")
        
        # All fundraising attempts should succeed
        self.assertEqual(len(results), 3, "All fundraising attempts should complete")
        self.assertTrue(all(r > 0 for r in results), "All fundraising should raise money")

    def test_action_points_maximum_cap(self):
        """Test that action points respect maximum cap from configuration."""
        from src.services.config_manager import get_current_config
        
        config = get_current_config()
        max_cap = config['action_points']['max_ap_per_turn']
        
        # Set staff to a very high number that would exceed cap
        self.game_state.staff = 50  # Would give 1 + 50 * 0.5 = 26 AP without cap
        
        calculated_ap = self.game_state.calculate_max_ap()
        
        # Should be capped at maximum
        self.assertLessEqual(calculated_ap, max_cap,
            f"AP should be capped at {max_cap}, got {calculated_ap}")

    def test_regression_no_four_ap_bug(self):
        """Regression test: ensure the original 4 AP bug is fixed."""
        # This is a regression test for the specific bug where
        # default game state incorrectly gave 4 AP instead of expected 2-3 AP
        
        # Default game with 2 staff should give 2 AP (1 base + 2*0.5)
        self.assertEqual(self.game_state.staff, 2)
        self.assertEqual(self.game_state.action_points, 2,
            "Default game should have 2 AP, not 4 AP (regression test)")
        
        # After turn advancement, should still be 2 AP
        self.game_state.action_points = 0
        self.game_state.end_turn()
        self.assertEqual(self.game_state.action_points, 2,
            "After turn advance should have 2 AP, not 4 AP (regression test)")

    def test_edge_case_zero_staff(self):
        """Test edge case with zero staff members."""
        self.game_state.staff = 0
        self.game_state.admin_staff = 0
        
        # Should have exactly 1 AP (player base capacity only)
        expected_ap = 1
        calculated_ap = self.game_state.calculate_max_ap()
        
        self.assertEqual(calculated_ap, expected_ap,
            "With zero staff, should have 1 AP (player base capacity)")

    def test_integration_ap_and_fundraising(self):
        """Integration test: verify AP and fundraising work together correctly."""
        # Start with known state
        initial_ap = self.game_state.action_points
        initial_money = self.game_state.money
        
        # Execute fundraising (should not affect AP)
        actions.execute_fundraising_action(self.game_state)
        
        # AP should be unchanged by fundraising
        self.assertEqual(self.game_state.action_points, initial_ap,
            "Fundraising should not affect action points")
        
        # Money should have increased
        self.assertGreater(self.game_state.money, initial_money,
            "Fundraising should increase money")
        
        # Advance turn and verify AP refresh still works
        self.game_state.action_points = 0
        self.game_state.end_turn()
        expected_ap = self.game_state.calculate_max_ap()
        self.assertEqual(self.game_state.action_points, expected_ap,
            "AP refresh should work correctly after fundraising")


if __name__ == '__main__':
    unittest.main()