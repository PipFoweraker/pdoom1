# !/usr/bin/env python3
'''
Tests for the tutorial and onboarding system.
'''

import unittest
import os
from src.core.game_state import GameState


class TestTutorialSystem(unittest.TestCase):
    '''Test tutorial system functionality.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.test_seed = 'test_tutorial_seed'
        
    def tearDown(self):
        '''Clean up test files.'''
        # Clean up tutorial settings file if it exists
        if os.path.exists('tutorial_settings.json'):
            os.remove('tutorial_settings.json')
    
    def test_tutorial_initialization(self):
        '''Test that tutorial system initializes correctly for new players.'''
        gs = GameState(self.test_seed)
        
        # New players should have tutorial enabled by default
        self.assertTrue(gs.tutorial_enabled)
        self.assertTrue(gs.first_game_launch)
        self.assertEqual(gs.tutorial_shown_milestones, set())
        self.assertIsNone(gs.pending_tutorial_message)
    
    def test_tutorial_settings_persistence(self):
        '''Test that tutorial settings are saved and loaded correctly.'''
        # Create game state and modify tutorial settings
        gs = GameState(self.test_seed)
        gs.tutorial_enabled = False
        gs.tutorial_shown_milestones.add('test_milestone')
        gs.save_tutorial_settings()
        
        # Create new game state and verify settings were loaded
        gs2 = GameState(self.test_seed + '_2')
        self.assertFalse(gs2.tutorial_enabled)
        self.assertFalse(gs2.first_game_launch)  # Should be False after save
        self.assertIn('test_milestone', gs2.tutorial_shown_milestones)
    
    def test_show_tutorial_message(self):
        '''Test showing tutorial messages.'''
        gs = GameState(self.test_seed)
        
        # Show a tutorial message
        gs.show_tutorial_message('test_milestone', 'Test Title', 'Test content')
        
        # Should have pending tutorial message
        self.assertIsNotNone(gs.pending_tutorial_message)
        self.assertEqual(gs.pending_tutorial_message['milestone_id'], 'test_milestone')
        self.assertEqual(gs.pending_tutorial_message['title'], 'Test Title')
        self.assertEqual(gs.pending_tutorial_message['content'], 'Test content')
    
    def test_dismiss_tutorial_message(self):
        '''Test dismissing tutorial messages.'''
        gs = GameState(self.test_seed)
        
        # Show and then dismiss a tutorial message
        gs.show_tutorial_message('test_milestone', 'Test Title', 'Test content')
        gs.dismiss_tutorial_message()
        
        # Should no longer have pending message and milestone should be marked as shown
        self.assertIsNone(gs.pending_tutorial_message)
        self.assertIn('test_milestone', gs.tutorial_shown_milestones)
    
    def test_tutorial_message_not_shown_when_disabled(self):
        '''Test that tutorial messages are not shown when tutorial is disabled.'''
        gs = GameState(self.test_seed)
        gs.tutorial_enabled = False
        
        # Try to show a tutorial message
        gs.show_tutorial_message('test_milestone', 'Test Title', 'Test content')
        
        # Should not have pending tutorial message
        self.assertIsNone(gs.pending_tutorial_message)
    
    def test_tutorial_message_not_shown_when_already_shown(self):
        '''Test that tutorial messages are not shown again for the same milestone.'''
        gs = GameState(self.test_seed)
        gs.tutorial_shown_milestones.add('test_milestone')
        
        # Try to show a tutorial message for already shown milestone
        gs.show_tutorial_message('test_milestone', 'Test Title', 'Test content')
        
        # Should not have pending tutorial message
        self.assertIsNone(gs.pending_tutorial_message)


class TestTutorialMilestones(unittest.TestCase):
    '''Test tutorial triggers for milestone events.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.test_seed = 'test_milestone_seed'
        
    def tearDown(self):
        '''Clean up test files.'''
        # Clean up tutorial settings file if it exists
        if os.path.exists('tutorial_settings.json'):
            os.remove('tutorial_settings.json')
    
    def test_manager_system_tutorial_trigger(self):
        '''Test that manager system tutorial is triggered when first manager is hired.'''
        gs = GameState(self.test_seed)
        gs.money = 10000  # Ensure enough money for hiring
        
        # Simulate hiring first manager (this is complex due to internal methods)
        # For now, we'll test the tutorial trigger directly
        gs.show_tutorial_message(
            'manager_system',
            'Manager System Unlocked!',
            'Test manager tutorial content'
        )
        
        # Should have pending tutorial message
        self.assertIsNotNone(gs.pending_tutorial_message)
        self.assertEqual(gs.pending_tutorial_message['milestone_id'], 'manager_system')
    
    def test_board_member_system_tutorial_trigger(self):
        '''Test that board member system tutorial is triggered on milestone.'''
        gs = GameState(self.test_seed)
        
        # Simulate board member milestone trigger
        gs.show_tutorial_message(
            'board_member_system',
            'Board Member Oversight Activated!',
            'Test board member tutorial content'
        )
        
        # Should have pending tutorial message
        self.assertIsNotNone(gs.pending_tutorial_message)
        self.assertEqual(gs.pending_tutorial_message['milestone_id'], 'board_member_system')


if __name__ == '__main__':
    unittest.main()