import unittest
from src.core.game_state import GameState
from src.core.action_rules import ActionRules, manager_unlock_rule, scout_unlock_rule, search_unlock_rule


class TestActionRulesSystem(unittest.TestCase):
    '''Test the action rules system for managing action availability'''
    
    def setUp(self):
        '''Set up a GameState for testing'''
        self.game_state = GameState('test_seed')
        # RNG is now initialized by GameState constructor

    # === Turn-based Rules Tests ===
    
    def test_requires_turn(self):
        '''Test turn-based rule requirements'''
        # Should not be available before turn 5
        self.game_state.turn = 4
        self.assertFalse(ActionRules.requires_turn(self.game_state, min_turn=5))
        
        # Should be available at turn 5
        self.game_state.turn = 5
        self.assertTrue(ActionRules.requires_turn(self.game_state, min_turn=5))
        
        # Should be available after turn 5
        self.game_state.turn = 10
        self.assertTrue(ActionRules.requires_turn(self.game_state, min_turn=5))

    # === Resource-based Rules Tests ===
    
    def test_requires_staff(self):
        '''Test staff-based rule requirements'''
        # Should not be available with insufficient staff
        self.game_state.staff = 8
        self.assertFalse(ActionRules.requires_staff(self.game_state, min_staff=9))
        
        # Should be available with exact staff count
        self.game_state.staff = 9
        self.assertTrue(ActionRules.requires_staff(self.game_state, min_staff=9))
        
        # Should be available with more staff
        self.game_state.staff = 15
        self.assertTrue(ActionRules.requires_staff(self.game_state, min_staff=9))

    def test_requires_money(self):
        '''Test money-based rule requirements'''
        self.game_state.money = 100
        self.assertFalse(ActionRules.requires_money(self.game_state, min_money=150))
        
        self.game_state.money = 150
        self.assertTrue(ActionRules.requires_money(self.game_state, min_money=150))
        
        self.game_state.money = 200
        self.assertTrue(ActionRules.requires_money(self.game_state, min_money=150))

    def test_requires_reputation(self):
        '''Test reputation-based rule requirements'''
        self.game_state.reputation = 10
        self.assertFalse(ActionRules.requires_reputation(self.game_state, min_reputation=15))
        
        self.game_state.reputation = 15
        self.assertTrue(ActionRules.requires_reputation(self.game_state, min_reputation=15))
        
        self.game_state.reputation = 20
        self.assertTrue(ActionRules.requires_reputation(self.game_state, min_reputation=15))

    # === Milestone-based Rules Tests ===
    
    def test_requires_milestone_triggered(self):
        '''Test milestone-based rule requirements'''
        # Initially milestone should not be triggered
        self.assertFalse(ActionRules.requires_milestone_triggered(
            self.game_state, 'manager_milestone_triggered'))
        
        # After triggering milestone, rule should return True
        self.game_state.manager_milestone_triggered = True
        self.assertTrue(ActionRules.requires_milestone_triggered(
            self.game_state, 'manager_milestone_triggered'))

    def test_requires_board_members(self):
        '''Test board member rule requirements'''
        # Initially no board members
        self.game_state.board_members = 0
        self.assertFalse(ActionRules.requires_board_members(self.game_state))
        
        # With board members installed
        self.game_state.board_members = 2
        self.assertTrue(ActionRules.requires_board_members(self.game_state))
        
        # Test minimum requirement
        self.assertTrue(ActionRules.requires_board_members(self.game_state, min_board_members=1))
        self.assertTrue(ActionRules.requires_board_members(self.game_state, min_board_members=2))
        self.assertFalse(ActionRules.requires_board_members(self.game_state, min_board_members=3))

    # === Upgrade-based Rules Tests ===
    
    def test_requires_upgrade(self):
        '''Test upgrade-based rule requirements'''
        # Initially no upgrades purchased
        self.assertFalse(ActionRules.requires_upgrade(self.game_state, 'better_computers'))
        
        # After purchasing upgrade
        self.game_state.upgrade_effects.add('better_computers')
        self.assertTrue(ActionRules.requires_upgrade(self.game_state, 'better_computers'))

    def test_requires_scrollable_log(self):
        '''Test scrollable log rule requirements'''
        # Initially scrollable log disabled
        self.game_state.scrollable_event_log_enabled = False
        self.assertFalse(ActionRules.requires_scrollable_log(self.game_state))
        
        # After enabling scrollable log
        self.game_state.scrollable_event_log_enabled = True
        self.assertTrue(ActionRules.requires_scrollable_log(self.game_state))

    # === Composite Rules Tests ===
    
    def test_requires_staff_and_turn(self):
        '''Test composite rule requiring both staff and turn'''
        # Neither condition met
        self.game_state.staff = 5
        self.game_state.turn = 3
        self.assertFalse(ActionRules.requires_staff_and_turn(
            self.game_state, min_staff=9, min_turn=5))
        
        # Only staff condition met
        self.game_state.staff = 9
        self.game_state.turn = 3
        self.assertFalse(ActionRules.requires_staff_and_turn(
            self.game_state, min_staff=9, min_turn=5))
        
        # Only turn condition met
        self.game_state.staff = 5
        self.game_state.turn = 5
        self.assertFalse(ActionRules.requires_staff_and_turn(
            self.game_state, min_staff=9, min_turn=5))
        
        # Both conditions met
        self.game_state.staff = 9
        self.game_state.turn = 5
        self.assertTrue(ActionRules.requires_staff_and_turn(
            self.game_state, min_staff=9, min_turn=5))

    def test_requires_any_specialized_staff(self):
        '''Test specialized staff rule requirements'''
        # No specialized staff
        self.game_state.admin_staff = 0
        self.game_state.research_staff = 0
        self.game_state.ops_staff = 0
        self.assertFalse(ActionRules.requires_any_specialized_staff(self.game_state))
        
        # One admin staff
        self.game_state.admin_staff = 1
        self.assertTrue(ActionRules.requires_any_specialized_staff(self.game_state))
        
        # Multiple types of specialized staff
        self.game_state.research_staff = 2
        self.game_state.ops_staff = 1
        self.assertTrue(ActionRules.requires_any_specialized_staff(self.game_state, min_count=3))
        self.assertTrue(ActionRules.requires_any_specialized_staff(self.game_state, min_count=4))
        self.assertFalse(ActionRules.requires_any_specialized_staff(self.game_state, min_count=5))

    # === Negation and Complex Logic Tests ===
    
    def test_not_yet_triggered(self):
        '''Test negation rule for milestones'''
        # Initially milestone not triggered, rule should return True
        self.assertTrue(ActionRules.not_yet_triggered(
            self.game_state, 'manager_milestone_triggered'))
        
        # After triggering milestone, rule should return False
        self.game_state.manager_milestone_triggered = True
        self.assertFalse(ActionRules.not_yet_triggered(
            self.game_state, 'manager_milestone_triggered'))

    def test_combine_and(self):
        '''Test AND logic combination'''
        rule1 = lambda gs: gs.staff >= 5
        rule2 = lambda gs: gs.turn >= 3
        rule3 = lambda gs: gs.money >= 100
        
        # Set up conditions
        self.game_state.staff = 6
        self.game_state.turn = 4
        self.game_state.money = 150
        
        # All rules pass
        self.assertTrue(ActionRules.combine_and(self.game_state, rule1, rule2, rule3))
        
        # One rule fails
        self.game_state.money = 50
        self.assertFalse(ActionRules.combine_and(self.game_state, rule1, rule2, rule3))

    def test_combine_or(self):
        '''Test OR logic combination'''
        rule1 = lambda gs: gs.staff >= 10  # High requirement
        rule2 = lambda gs: gs.turn >= 10   # High requirement
        rule3 = lambda gs: gs.money >= 1000  # High requirement
        
        # Set up conditions where only one rule passes
        self.game_state.staff = 12  # This rule passes
        self.game_state.turn = 2    # This rule fails
        self.game_state.money = 50  # This rule fails
        
        # Should return True because at least one rule passes
        self.assertTrue(ActionRules.combine_or(self.game_state, rule1, rule2, rule3))
        
        # All rules fail
        self.game_state.staff = 5
        self.assertFalse(ActionRules.combine_or(self.game_state, rule1, rule2, rule3))


class TestConvenienceRuleFunctions(unittest.TestCase):
    '''Test the convenience rule functions used by specific actions'''
    
    def setUp(self):
        '''Set up a GameState for testing'''
        self.game_state = GameState('test_seed')
        # RNG is now initialized by GameState constructor

    def test_manager_unlock_rule(self):
        '''Test the manager unlock rule function'''
        # Should not unlock with insufficient staff
        self.game_state.staff = 8
        self.assertFalse(manager_unlock_rule(self.game_state))
        
        # Should unlock with 9+ staff
        self.game_state.staff = 9
        self.assertTrue(manager_unlock_rule(self.game_state))
        
        self.game_state.staff = 15
        self.assertTrue(manager_unlock_rule(self.game_state))

    def test_scout_unlock_rule(self):
        '''Test the scout unlock rule function'''
        # Should not unlock before turn 5
        self.game_state.turn = 4
        self.assertFalse(scout_unlock_rule(self.game_state))
        
        # Should unlock at turn 5+
        self.game_state.turn = 5
        self.assertTrue(scout_unlock_rule(self.game_state))
        
        self.game_state.turn = 10
        self.assertTrue(scout_unlock_rule(self.game_state))

    def test_search_unlock_rule(self):
        '''Test the search unlock rule function'''
        # Should not unlock without board members
        self.game_state.board_members = 0
        self.assertFalse(search_unlock_rule(self.game_state))
        
        # Should unlock with board members
        self.game_state.board_members = 1
        self.assertTrue(search_unlock_rule(self.game_state))
        
        self.game_state.board_members = 3
        self.assertTrue(search_unlock_rule(self.game_state))


class TestActionRulesIntegration(unittest.TestCase):
    '''Test that the action rules system integrates correctly with the actions'''
    
    def setUp(self):
        '''Set up a GameState for testing'''
        self.game_state = GameState('test_seed')
        # RNG is now initialized by GameState constructor

    def test_manager_action_uses_new_rule_system(self):
        '''Test that the manager action uses the new rule system'''
        # Find the manager action
        manager_action = None
        for action in self.game_state.actions:
            if action['name'] == 'Hire Manager':
                manager_action = action
                break
        
        self.assertIsNotNone(manager_action, 'Hire Manager action should exist')
        
        # Test that it uses the new rule function
        self.assertEqual(manager_action['rules'], manager_unlock_rule)
        
        # Test rule behavior
        self.game_state.staff = 8
        self.assertFalse(manager_action['rules'](self.game_state))
        
        self.game_state.staff = 9
        self.assertTrue(manager_action['rules'](self.game_state))

    def test_scout_action_uses_new_rule_system(self):
        '''Test that the scout action uses the new rule system'''
        # Find the scout action
        scout_action = None
        for action in self.game_state.actions:
            if action['name'] == 'Scout Opponents':
                scout_action = action
                break
        
        self.assertIsNotNone(scout_action, 'Scout Opponents action should exist')
        
        # Test that it uses the new rule function
        self.assertEqual(scout_action['rules'], scout_unlock_rule)
        
        # Test rule behavior
        self.game_state.turn = 4
        self.assertFalse(scout_action['rules'](self.game_state))
        
        self.game_state.turn = 5
        self.assertTrue(scout_action['rules'](self.game_state))

    def test_search_action_uses_new_rule_system(self):
        '''Test that the search action uses the new rule system'''
        # Find the search action
        search_action = None
        for action in self.game_state.actions:
            if action['name'] == 'Search':
                search_action = action
                break
        
        self.assertIsNotNone(search_action, 'Search action should exist')
        
        # Test that it uses the new rule function
        self.assertEqual(search_action['rules'], search_unlock_rule)
        
        # Test rule behavior
        self.game_state.board_members = 0
        self.assertFalse(search_action['rules'](self.game_state))
        
        self.game_state.board_members = 2
        self.assertTrue(search_action['rules'](self.game_state))


if __name__ == '__main__':
    unittest.main()