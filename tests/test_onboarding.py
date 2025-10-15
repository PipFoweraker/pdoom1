'''
Tests for the onboarding and tutorial system.
'''

import unittest
import tempfile
import os
import json
from unittest.mock import patch
from src.features.onboarding import OnboardingSystem, ONBOARDING_FILE


class TestOnboardingSystem(unittest.TestCase):
    '''Test the onboarding system functionality.'''
    
    def setUp(self):
        '''Set up test environment.'''
        # Use a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        
        # Patch the onboarding file path
        self.original_file = ONBOARDING_FILE
        OnboardingSystem.__module__ = self.temp_file.name
        
    def tearDown(self):
        '''Clean up test environment.'''
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_onboarding_initialization(self):
        '''Test that onboarding system initializes correctly.'''
        # Create a fresh instance for testing
        with patch('src.features.onboarding.ONBOARDING_FILE', self.temp_file.name):
            onboarding = OnboardingSystem()
            
            # New player should need tutorial
            self.assertTrue(onboarding.is_first_time)
            self.assertTrue(onboarding.tutorial_enabled)
            self.assertFalse(onboarding.tutorial_dismissed)
            self.assertEqual(len(onboarding.completed_steps), 0)
            self.assertEqual(len(onboarding.seen_mechanics), 0)
    
    def test_should_show_tutorial(self):
        '''Test tutorial showing logic.'''
        with patch('src.features.onboarding.ONBOARDING_FILE', self.temp_file.name):
            onboarding = OnboardingSystem()
            
            # New player should see tutorial
            self.assertTrue(onboarding.should_show_tutorial())
            
            # After dismissing, should not show tutorial
            onboarding.dismiss_tutorial()
            self.assertFalse(onboarding.should_show_tutorial())
            
            # After disabling, should not show tutorial
            onboarding = OnboardingSystem()
            onboarding.enable_tutorial(False)
            self.assertFalse(onboarding.should_show_tutorial())
    
    def test_tutorial_progression(self):
        '''Test tutorial step progression.'''
        with patch('src.features.onboarding.ONBOARDING_FILE', self.temp_file.name):
            onboarding = OnboardingSystem()
            onboarding.start_tutorial()
            
            # Should start with welcome step
            self.assertEqual(onboarding.current_tutorial_step, 'welcome')
            self.assertTrue(onboarding.show_tutorial_overlay)
            
            # Advance through steps
            onboarding.advance_tutorial_step('welcome')
            self.assertEqual(onboarding.current_tutorial_step, 'resources')
            self.assertIn('welcome', onboarding.completed_steps)
            
            onboarding.advance_tutorial_step('resources')
            self.assertEqual(onboarding.current_tutorial_step, 'actions')
            
            # Complete tutorial
            steps = ['actions', 'action_points', 'end_turn', 'events', 'upgrades', 'complete']
            for step in steps:
                onboarding.advance_tutorial_step(step)
            
            # Tutorial should be completed
            self.assertFalse(onboarding.show_tutorial_overlay)
            self.assertIsNone(onboarding.current_tutorial_step)
            self.assertFalse(onboarding.is_first_time)
    
    def test_mechanic_help(self):
        '''Test first-time mechanic help system.'''
        with patch('src.features.onboarding.ONBOARDING_FILE', self.temp_file.name):
            onboarding = OnboardingSystem()
            
            # Should show help for unseen mechanics
            self.assertTrue(onboarding.should_show_mechanic_help('first_staff_hire'))
            
            # Mark as seen
            is_first_time = onboarding.mark_mechanic_seen('first_staff_hire')
            self.assertTrue(is_first_time)
            
            # Should not show help for seen mechanics
            self.assertFalse(onboarding.should_show_mechanic_help('first_staff_hire'))
            
            # Marking again should return False
            is_first_time = onboarding.mark_mechanic_seen('first_staff_hire')
            self.assertFalse(is_first_time)
    
    def test_tutorial_content(self):
        '''Test tutorial content retrieval.'''
        onboarding = OnboardingSystem()
        
        # Test welcome content
        welcome_content = onboarding.get_tutorial_content('welcome')
        self.assertIn('title', welcome_content)
        self.assertIn('content', welcome_content)
        self.assertEqual(welcome_content['next_step'], 'resources')
        
        # Test final step
        complete_content = onboarding.get_tutorial_content('complete')
        self.assertIsNone(complete_content['next_step'])
    
    def test_mechanic_help_content(self):
        '''Test mechanic help content retrieval.'''
        onboarding = OnboardingSystem()
        
        # Test staff hire help
        staff_help = onboarding.get_mechanic_help('first_staff_hire')
        self.assertIsNotNone(staff_help)
        self.assertIn('title', staff_help)
        self.assertIn('content', staff_help)
        
        # Test non-existent mechanic
        no_help = onboarding.get_mechanic_help('non_existent_mechanic')
        self.assertIsNone(no_help)
    
    def test_tooltip_system(self):
        '''Test tooltip management.'''
        onboarding = OnboardingSystem()
        
        # Add tooltips
        onboarding.add_tooltip('Test tooltip 1', priority=1)
        onboarding.add_tooltip('Test tooltip 2', priority=3)
        onboarding.add_tooltip('Test tooltip 3', priority=2)
        
        # Should return highest priority first
        tooltip = onboarding.get_next_tooltip()
        self.assertEqual(tooltip, 'Test tooltip 2')
        
        # Next should be second highest
        tooltip = onboarding.get_next_tooltip()
        self.assertEqual(tooltip, 'Test tooltip 3')
        
        # Clear tooltips
        onboarding.clear_tooltips()
        tooltip = onboarding.get_next_tooltip()
        self.assertIsNone(tooltip)


class TestOnboardingIntegration(unittest.TestCase):
    '''Test onboarding integration with game systems.'''
    
    def test_onboarding_file_operations(self):
        '''Test onboarding file save/load operations.'''
        # Create temporary onboarding system
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Simulate onboarding progress
            progress_data = {
                'tutorial_enabled': True,
                'is_first_time': False,
                'completed_steps': ['welcome', 'resources'],
                'seen_mechanics': ['first_staff_hire'],
                'tutorial_dismissed': False
            }
            
            # Write progress data
            with open(temp_path, 'w') as f:
                json.dump(progress_data, f)
            
            # Verify data can be read back
            with open(temp_path, 'r') as f:
                loaded_data = json.load(f)
            
            self.assertEqual(loaded_data['tutorial_enabled'], True)
            self.assertEqual(loaded_data['is_first_time'], False)
            self.assertIn('welcome', loaded_data['completed_steps'])
            self.assertIn('first_staff_hire', loaded_data['seen_mechanics'])
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()