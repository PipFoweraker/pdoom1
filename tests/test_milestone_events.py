import unittest
import random
from game_state import GameState


class TestManagerMilestone(unittest.TestCase):
    """Test the manager milestone system and static effects"""
    
    def setUp(self):
        """Set up a GameState for testing"""
        random.seed(42)  # Consistent results
        self.game_state = GameState("test_seed")
        
    def test_manager_milestone_trigger_at_9_staff(self):
        """Test that manager action unlocks at 9+ staff"""
        # Initially manager action should not be available
        manager_action = None
        for action in self.game_state.actions:
            if action["name"] == "Hire Manager":
                manager_action = action
                break
        
        self.assertIsNotNone(manager_action, "Hire Manager action should exist")
        
        # Should not be available with fewer than 9 staff
        self.game_state.staff = 8
        self.assertFalse(manager_action["rules"](self.game_state), 
                        "Manager action should not be available with 8 staff")
        
        # Should be available with 9+ staff
        self.game_state.staff = 9
        self.assertTrue(manager_action["rules"](self.game_state),
                       "Manager action should be available with 9+ staff")
                       
    def test_manager_hiring_mechanics(self):
        """Test that hiring managers works correctly"""
        # Set up for manager hiring
        self.game_state.staff = 9
        initial_staff = self.game_state.staff
        initial_managers = len(self.game_state.managers)
        
        # Hire a manager
        self.game_state._hire_manager()
        
        # Check that staff count increased and manager was added
        self.assertEqual(self.game_state.staff, initial_staff + 1)
        self.assertEqual(len(self.game_state.managers), initial_managers + 1)
        self.assertTrue(self.game_state.manager_milestone_triggered)
        
        # Check manager blob properties
        manager_blob = self.game_state.managers[0]
        self.assertEqual(manager_blob['type'], 'manager')
        self.assertEqual(manager_blob['management_capacity'], 9)
        self.assertEqual(manager_blob['productivity'], 1.0)
        
    def test_manager_employee_assignment(self):
        """Test that managers properly assign employees"""
        # Set up scenario with 12 employees
        self.game_state.staff = 12
        # Clear existing blobs first
        self.game_state.employee_blobs = []
        self.game_state._initialize_employee_blobs()
        
        # Add a manager
        self.game_state._hire_manager()
        
        # Check that employees are properly assigned
        employees = [blob for blob in self.game_state.employee_blobs if blob['type'] == 'employee']
        managers = [blob for blob in self.game_state.employee_blobs if blob['type'] == 'manager']
        
        self.assertEqual(len(employees), 12)
        self.assertEqual(len(managers), 1)
        
        # Manager should be managing 9 employees, 3 should be unmanaged
        managed_count = sum(1 for emp in employees if emp['managed_by'] is not None)
        unmanaged_count = sum(1 for emp in employees if emp['unproductive_reason'] == 'no_manager')
        
        self.assertEqual(managed_count, 9)
        self.assertEqual(unmanaged_count, 3)
        
    def test_multiple_manager_clusters(self):
        """Test that multiple managers can handle large teams"""
        # Set up scenario with 20 employees
        self.game_state.staff = 20
        # Clear existing blobs first
        self.game_state.employee_blobs = []
        self.game_state._initialize_employee_blobs()
        
        # Add two managers
        self.game_state._hire_manager()
        self.game_state._hire_manager()
        
        employees = [blob for blob in self.game_state.employee_blobs if blob['type'] == 'employee']
        managers = [blob for blob in self.game_state.employee_blobs if blob['type'] == 'manager']
        
        self.assertEqual(len(employees), 20)
        self.assertEqual(len(managers), 2)
        
        # All employees should be managed (2 managers * 9 capacity = 18 managed, 2 unmanaged)
        managed_count = sum(1 for emp in employees if emp['managed_by'] is not None)
        unmanaged_count = sum(1 for emp in employees if emp['unproductive_reason'] == 'no_manager')
        
        self.assertEqual(managed_count, 18)
        self.assertEqual(unmanaged_count, 2)
        
    def test_special_event_triggers_at_9_staff(self):
        """Test that special event triggers when reaching 9 staff for the first time"""
        # Start with 8 staff
        self.game_state.staff = 8
        self.assertFalse(self.game_state.manager_milestone_triggered)
        
        # Add one more staff to reach 9
        old_message_count = len(self.game_state.messages)
        self.game_state._add('staff', 1)
        
        # Trigger events to process the special event
        self.game_state.trigger_events()
        
        # Check that milestone was triggered
        self.assertTrue(self.game_state.manager_milestone_triggered)
        
        # Check that special event messages were added
        new_messages = self.game_state.messages[old_message_count:]
        self.assertTrue(any("SPECIAL EVENT" in msg for msg in new_messages))
        self.assertTrue(any("9 employees" in msg for msg in new_messages))
        self.assertTrue(any("Manager" in msg for msg in new_messages))


class TestBoardMemberMilestone(unittest.TestCase):
    """Test the board member milestone system and static effects"""
    
    def setUp(self):
        """Set up a GameState for testing"""
        random.seed(42)  # Consistent results
        self.game_state = GameState("test_seed")
        
    def test_board_member_trigger_on_high_spending(self):
        """Test that board members are installed on high spending without accounting software"""
        # Ensure no accounting software
        self.game_state.accounting_software_bought = False
        
        # Simulate high spending
        self.game_state.spend_this_turn = 15000
        
        # Check milestone trigger
        self.game_state._check_board_member_milestone()
        
        self.assertEqual(self.game_state.board_members, 2)
        self.assertTrue(self.game_state.board_milestone_triggered)
        self.assertGreater(self.game_state.audit_risk_level, 0)
        
    def test_board_member_blocked_by_accounting_software(self):
        """Test that accounting software blocks board member trigger"""
        # Set accounting software as purchased
        self.game_state.accounting_software_bought = True
        
        # Simulate high spending
        self.game_state.spend_this_turn = 15000
        
        # Check milestone trigger
        self.game_state._check_board_member_milestone()
        
        # Should not trigger with accounting software
        self.assertEqual(self.game_state.board_members, 0)
        self.assertFalse(self.game_state.board_milestone_triggered)
        
    def test_search_action_unlocks_with_board_members(self):
        """Test that search action is unlocked when board members are installed"""
        # Find search action
        search_action = None
        for action in self.game_state.actions:
            if action["name"] == "Search":
                search_action = action
                break
        
        self.assertIsNotNone(search_action, "Search action should exist")
        
        # Should not be available without board members
        self.game_state.board_members = 0
        self.assertFalse(search_action["rules"](self.game_state),
                        "Search action should not be available without board members")
        
        # Should be available with board members
        self.game_state.board_members = 2
        self.assertTrue(search_action["rules"](self.game_state),
                       "Search action should be available with board members")
                       
    def test_board_search_success_and_failure(self):
        """Test board search action outcomes"""
        # Set up board members
        self.game_state.board_members = 2
        self.game_state.audit_risk_level = 5
        
        initial_messages = len(self.game_state.messages)
        
        # Test search (should have some outcome)
        self.game_state._board_search()
        
        # Should have added a message
        self.assertGreater(len(self.game_state.messages), initial_messages)
        
    def test_audit_risk_penalties(self):
        """Test that audit risk applies proper penalties"""
        # Set up scenario with board members but no accounting software
        self.game_state.board_members = 2
        self.game_state.accounting_software_bought = False
        self.game_state.audit_risk_level = 10
        
        initial_reputation = self.game_state.reputation
        initial_money = self.game_state.money
        
        # Run audit risk check
        self.game_state._check_board_member_milestone()
        
        # Should have penalties for high audit risk
        self.assertLess(self.game_state.reputation, initial_reputation)
        self.assertLess(self.game_state.money, initial_money)


class TestAccountingSoftware(unittest.TestCase):
    """Test the accounting software upgrade and its effects"""
    
    def setUp(self):
        """Set up a GameState for testing"""
        random.seed(42)  # Consistent results  
        self.game_state = GameState("test_seed")
        
    def test_accounting_software_upgrade_exists(self):
        """Test that accounting software appears as an upgrade"""
        # Find accounting software upgrade
        acct_upgrade = None
        for upgrade in self.game_state.upgrades:
            if upgrade["name"] == "Accounting Software":
                acct_upgrade = upgrade
                break
        
        self.assertIsNotNone(acct_upgrade, "Accounting Software upgrade should exist")
        self.assertEqual(acct_upgrade["cost"], 500)
        self.assertEqual(acct_upgrade["effect_key"], "accounting_software")
        
    def test_spending_tracking_per_turn(self):
        """Test that spending is tracked properly per turn"""
        initial_spend = self.game_state.spend_this_turn
        
        # Simulate spending money (negative amount)
        self.game_state._add('money', -1000)
        
        self.assertEqual(self.game_state.spend_this_turn, initial_spend + 1000)
        
        # Reset at turn end should work
        self.game_state.spend_this_turn = 0
        self.assertEqual(self.game_state.spend_this_turn, 0)
        
    def test_cash_flow_tracking_with_accounting_software(self):
        """Test that cash flow is tracked when accounting software is purchased"""
        # Purchase accounting software
        self.game_state.accounting_software_bought = True
        
        # Test positive change
        self.game_state._add('money', 500)
        self.assertEqual(self.game_state.last_balance_change, 500)
        
        # Test negative change
        self.game_state._add('money', -200)
        self.assertEqual(self.game_state.last_balance_change, -200)
        

class TestStaticEffects(unittest.TestCase):
    """Test static effects of the milestone system"""
    
    def setUp(self):
        """Set up a GameState for testing"""
        random.seed(42)  # Consistent results
        self.game_state = GameState("test_seed")
        
    def test_unmanaged_employee_productivity_penalty(self):
        """Test that unmanaged employees beyond 9 are unproductive"""
        # Set up scenario with 12 employees, 1 manager
        self.game_state.staff = 12
        self.game_state._initialize_employee_blobs()
        self.game_state._hire_manager()
        
        # Run productivity update
        self.game_state._update_employee_productivity()
        
        # Check that some employees are marked as unproductive due to no manager
        unmanaged_employees = [blob for blob in self.game_state.employee_blobs 
                             if blob.get('unproductive_reason') == 'no_manager']
        
        self.assertGreater(len(unmanaged_employees), 0, 
                          "Should have unmanaged employees with productivity penalty")
        
        # All unmanaged employees should have 0 productivity
        for employee in unmanaged_employees:
            self.assertEqual(employee['productivity'], 0.0)
            
    def test_manager_always_productive(self):
        """Test that managers are always productive"""
        # Add a manager
        self.game_state.staff = 10
        self.game_state._hire_manager()
        
        # Run productivity update with no compute
        self.game_state.compute = 0
        self.game_state._update_employee_productivity()
        
        # Manager should still be productive
        managers = [blob for blob in self.game_state.employee_blobs if blob['type'] == 'manager']
        self.assertEqual(len(managers), 1)
        
        manager = managers[0]
        self.assertEqual(manager['productivity'], 1.0)
        self.assertTrue(manager['has_compute'])


if __name__ == '__main__':
    unittest.main()