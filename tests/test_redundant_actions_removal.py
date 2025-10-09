# !/usr/bin/env python3
'''
Test for issue #181: Ensure hiring dialog covers functionality of removed redundant actions.
'''
import unittest
import pygame
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.game_state import GameState

class TestRedundantActionsRemoval(unittest.TestCase):
    '''Test that hiring dialog adequately replaces removed direct hiring actions.'''

    def setUp(self):
        '''Set up test environment.'''
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))

    def tearDown(self):
        '''Clean up test environment.'''
        pygame.quit()

    def test_hiring_dialog_covers_all_removed_functionality(self):
        '''Test that hiring dialog includes all employee types from removed actions.'''
        game_state = GameState('test-removed-actions')
        game_state.money = 1000
        game_state.action_points = 10
        
        # Trigger hiring dialog
        game_state._trigger_hiring_dialog()
        available_types = game_state.pending_hiring_dialog['available_subtypes']
        type_names = [t['data']['name'] for t in available_types]
        
        # Verify all previously direct-hire employee types are available
        self.assertIn('Administrator', type_names, 'Administrator should be available (was Hire Admin Assistant)')
        self.assertIn('Researcher', type_names, 'Researcher should be available (was Hire Research Staff)')
        self.assertIn('Engineer', type_names, 'Engineer should be available (was Hire Operations Staff)')
        
    def test_hiring_dialog_functionality_equivalent(self):
        '''Test that hiring through dialog provides same effects as removed direct actions.'''
        game_state = GameState('test-functionality')
        game_state.money = 1000
        game_state.action_points = 10
        
        # Test Administrator hiring
        game_state._trigger_hiring_dialog()
        available_types = game_state.pending_hiring_dialog['available_subtypes']
        
        admin_subtype = None
        for subtype in available_types:
            if subtype['data']['name'] == 'Administrator':
                admin_subtype = subtype
                break
                
        self.assertIsNotNone(admin_subtype, 'Administrator subtype should be available')
        
        # Test successful hiring through dialog
        initial_staff = game_state.staff
        initial_admin_staff = game_state.admin_staff
        
        success, message = game_state.select_employee_subtype(admin_subtype['id'])
        
        self.assertTrue(success, f'Administrator hiring should succeed: {message}')
        self.assertGreater(game_state.staff, initial_staff, 'Staff count should increase')
        self.assertGreater(game_state.admin_staff, initial_admin_staff, 'Admin staff count should increase')
        
    def test_hiring_dialog_escape_functionality(self):
        '''Test that ESC key properly dismisses hiring dialog as required by issue.'''
        game_state = GameState('test-escape')
        game_state.money = 1000
        game_state.action_points = 10
        
        # Trigger dialog
        game_state._trigger_hiring_dialog()
        self.assertIsNotNone(game_state.pending_hiring_dialog, 'Dialog should be active')
        
        # Test ESC dismissal
        game_state.dismiss_hiring_dialog()
        self.assertIsNone(game_state.pending_hiring_dialog, 'Dialog should be dismissed by ESC')
        
    def test_no_redundant_direct_hire_actions(self):
        '''Test that redundant direct hire actions have been removed.'''
        game_state = GameState('test-no-redundant')
        action_names = [action['name'] for action in game_state.actions]
        
        # These actions should be removed as they're redundant with the hiring dialog
        self.assertNotIn('Hire Admin Assistant', action_names, 
                        'Hire Admin Assistant should be removed (redundant with hiring dialog)')
        self.assertNotIn('Hire Research Staff', action_names, 
                        'Hire Research Staff should be removed (redundant with hiring dialog)')
        self.assertNotIn('Hire Operations Staff', action_names, 
                        'Hire Operations Staff should be removed (redundant with hiring dialog)')
        
        # But the general hiring action should still exist
        self.assertIn('Hire Staff', action_names, 'General Hire Staff action should remain')

if __name__ == '__main__':
    unittest.main()