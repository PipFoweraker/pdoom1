import unittest
import random
from unittest.mock import patch
from game_state import GameState


class TestMilestoneEvents(unittest.TestCase):
    """Test milestone-triggered events and related mechanics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game_state = GameState("test_milestone_seed")
        # Disable random events for deterministic testing
        random.seed(42)
    
    def test_manager_milestone_at_ninth_employee(self):
        """Test that manager milestone triggers when hiring 9th employee."""
        # Start with fewer than 9 employees
        self.game_state.staff = 8
        self.game_state.employee_blobs = []
        self.game_state._initialize_employee_blobs()
        self.assertFalse(self.game_state.first_manager_hired)
        self.assertEqual(self.game_state.managers, 0)
        
        # Hire 9th employee - should trigger manager milestone
        self.game_state._add('staff', 1)
        
        # Check that milestone was triggered
        self.assertTrue(self.game_state.first_manager_hired)
        self.assertEqual(self.game_state.managers, 1)
        
        # Check that one employee was converted to manager
        manager_blobs = [b for b in self.game_state.employee_blobs if b.get('type') == 'manager']
        self.assertEqual(len(manager_blobs), 1)
        
        # Check for milestone message
        milestone_messages = [msg for msg in self.game_state.messages if 'MILESTONE' in msg]
        self.assertTrue(len(milestone_messages) > 0)
    
    def test_manager_milestone_only_triggers_once(self):
        """Test that manager milestone only triggers once."""
        # Set up for milestone
        self.game_state.staff = 8
        self.game_state.employee_blobs = []
        self.game_state._initialize_employee_blobs()
        
        # Hire 9th employee
        self.game_state._add('staff', 1)
        first_manager_count = self.game_state.managers
        
        # Hire more employees - should not trigger again
        self.game_state._add('staff', 5)
        self.assertEqual(self.game_state.managers, first_manager_count)
    
    def test_employee_productivity_without_manager(self):
        """Test that employees beyond 9 without manager become unproductive."""
        # Set up with 12 employees, no managers, and enough compute
        self.game_state.staff = 12
        self.game_state.managers = 0
        self.game_state.first_manager_hired = True  # Skip milestone trigger
        self.game_state.compute = 15
        self.game_state.employee_blobs = []
        for i in range(12):
            blob = {
                'id': i, 'x': 400 + (i % 3) * 60, 'y': 500 + (i // 3) * 60,
                'target_x': 400 + (i % 3) * 60, 'target_y': 500 + (i // 3) * 60,
                'has_compute': False, 'productivity': 0.0, 'animation_progress': 1.0,
                'type': 'employee', 'managed': False, 'unproductive_reason': None
            }
            self.game_state.employee_blobs.append(blob)
        
        # Update productivity
        self.game_state._update_employee_productivity()
        
        # Check that employees beyond 9 are marked as unproductive due to no manager
        unmanaged_employees = [b for b in self.game_state.employee_blobs 
                              if b.get('unproductive_reason') == 'no_manager']
        self.assertEqual(len(unmanaged_employees), 3)  # 12 - 9 = 3 unmanaged
    
    def test_employee_productivity_with_manager(self):
        """Test that employees are productive when managed."""
        # Set up with 12 employees, 1 manager, and enough compute
        self.game_state.staff = 12
        self.game_state.managers = 1
        self.game_state.compute = 15
        self.game_state.employee_blobs = []
        
        # Add 11 regular employees and 1 manager
        for i in range(11):
            blob = {
                'id': i, 'x': 400 + (i % 3) * 60, 'y': 500 + (i // 3) * 60,
                'target_x': 400 + (i % 3) * 60, 'target_y': 500 + (i // 3) * 60,
                'has_compute': False, 'productivity': 0.0, 'animation_progress': 1.0,
                'type': 'employee', 'managed': False, 'unproductive_reason': None
            }
            self.game_state.employee_blobs.append(blob)
        
        # Add manager
        manager_blob = {
            'id': 11, 'x': 400, 'y': 500, 'target_x': 400, 'target_y': 500,
            'has_compute': False, 'productivity': 0.0, 'animation_progress': 1.0,
            'type': 'manager', 'managed': False, 'unproductive_reason': None
        }
        self.game_state.employee_blobs.append(manager_blob)
        
        # Update productivity
        self.game_state._update_employee_productivity()
        
        # Check that all 11 employees are managed 
        # (first 9 auto-managed + 2 more managed by the 1 manager)
        managed_employees = [b for b in self.game_state.employee_blobs 
                           if b.get('managed') and b.get('type') == 'employee']
        self.assertEqual(len(managed_employees), 11)
        
        # Check that no employees are unmanaged since we have enough management
        unmanaged_employees = [b for b in self.game_state.employee_blobs 
                              if b.get('unproductive_reason') == 'no_manager']
        self.assertEqual(len(unmanaged_employees), 0)
    
    def test_board_member_spending_threshold(self):
        """Test board member event triggers when spending > $10k without accounting software."""
        # Ensure accounting software is not bought
        self.game_state.accounting_software_bought = False
        self.game_state.board_member_search_unlocked = False
        
        # Simulate spending > $10k in one turn
        self.game_state.spend_this_turn = 12000
        
        # Check board member threshold
        triggered = self.game_state._check_board_member_threshold()
        
        self.assertTrue(triggered)
        self.assertTrue(self.game_state.board_member_search_unlocked)
        self.assertEqual(self.game_state.audit_risk_level, 25)
        
        # Check for audit alert message
        audit_messages = [msg for msg in self.game_state.messages if 'AUDIT ALERT' in msg]
        self.assertTrue(len(audit_messages) > 0)
    
    def test_board_member_threshold_blocked_by_accounting_software(self):
        """Test board member event doesn't trigger with accounting software."""
        # Buy accounting software
        self.game_state.accounting_software_bought = True
        self.game_state.board_member_search_unlocked = False
        
        # Simulate spending > $10k in one turn
        self.game_state.spend_this_turn = 15000
        
        # Check board member threshold
        triggered = self.game_state._check_board_member_threshold()
        
        self.assertFalse(triggered)
        self.assertFalse(self.game_state.board_member_search_unlocked)
        self.assertEqual(self.game_state.audit_risk_level, 0)
    
    def test_search_for_board_member_success(self):
        """Test successful board member search."""
        # Set up board member search
        self.game_state.board_member_search_unlocked = True
        self.game_state.board_members = 0
        initial_blob_count = len(self.game_state.employee_blobs)
        
        # Mock successful search (20% chance)
        with patch('random.random', return_value=0.1):  # < 0.2 = success
            success = self.game_state._search_for_board_member()
        
        self.assertTrue(success)
        self.assertEqual(self.game_state.board_members, 1)
        self.assertEqual(len(self.game_state.employee_blobs), initial_blob_count + 1)
        
        # Check that a board member blob was added
        board_members = [b for b in self.game_state.employee_blobs if b.get('type') == 'board_member']
        self.assertEqual(len(board_members), 1)
    
    def test_search_for_board_member_failure(self):
        """Test failed board member search."""
        # Set up board member search
        self.game_state.board_member_search_unlocked = True
        self.game_state.board_members = 0
        initial_blob_count = len(self.game_state.employee_blobs)
        
        # Mock failed search (80% chance)
        with patch('random.random', return_value=0.5):  # >= 0.2 = failure
            success = self.game_state._search_for_board_member()
        
        self.assertFalse(success)
        self.assertEqual(self.game_state.board_members, 0)
        self.assertEqual(len(self.game_state.employee_blobs), initial_blob_count)
    
    def test_audit_risk_elimination_with_two_board_members(self):
        """Test that audit risk is eliminated when 2 board members are found."""
        # Set up audit risk
        self.game_state.audit_risk_level = 50
        self.game_state.board_members = 1
        
        # Find second board member
        with patch('random.random', return_value=0.1):  # Success
            self.game_state._search_for_board_member()
        
        self.assertEqual(self.game_state.board_members, 2)
        self.assertEqual(self.game_state.audit_risk_level, 0)
        
        # Check for compliance message
        compliance_messages = [msg for msg in self.game_state.messages if 'compliance achieved' in msg.lower()]
        self.assertTrue(len(compliance_messages) > 0)
    
    def test_accounting_software_upgrade_functionality(self):
        """Test accounting software upgrade purchase and effects."""
        # Check initial state
        self.assertFalse(self.game_state.accounting_software_bought)
        
        # Simulate purchasing accounting software upgrade
        self.game_state.money = 1000
        self.game_state.accounting_software_bought = True
        self.game_state.upgrade_effects.add("accounting_software")
        
        # Test that balance changes are now tracked
        self.game_state._add('money', -100)
        self.assertEqual(self.game_state.last_balance_change, -100)
        
        # Test that spending threshold doesn't trigger
        self.game_state.spend_this_turn = 15000
        triggered = self.game_state._check_board_member_threshold()
        self.assertFalse(triggered)


class TestSpendingTracking(unittest.TestCase):
    """Test spending tracking for board member threshold."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game_state = GameState("test_spending_seed")
    
    def test_spending_tracked_on_money_deduction(self):
        """Test that spending is tracked when money is deducted."""
        initial_spending = self.game_state.spend_this_turn
        
        # Deduct money (negative value)
        self.game_state._add('money', -500)
        
        self.assertEqual(self.game_state.spend_this_turn, initial_spending + 500)
    
    def test_spending_not_tracked_on_money_addition(self):
        """Test that money addition doesn't affect spending tracking."""
        initial_spending = self.game_state.spend_this_turn
        
        # Add money (positive value)
        self.game_state._add('money', 500)
        
        self.assertEqual(self.game_state.spend_this_turn, initial_spending)
    
    def test_spending_reset_each_turn(self):
        """Test that spending is reset at the start of each turn."""
        # Accumulate some spending
        self.game_state._add('money', -1000)
        self.assertGreater(self.game_state.spend_this_turn, 0)
        
        # End turn (which should reset spending)
        self.game_state.end_turn()
        
        self.assertEqual(self.game_state.spend_this_turn, 0)


if __name__ == '__main__':
    unittest.main()