'''
Tests for Stepwise Tutorial System (Issue #127)

Tests cover:
- Stepwise tutorial sequence and navigation
- UI element visibility control
- Back/forward navigation functionality
- Tutorial state management
'''

import unittest
import sys
import os

# Add the parent directory to sys.path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.features.onboarding import OnboardingSystem


class TestStepwiseTutorial(unittest.TestCase):
    '''Test the stepwise tutorial system.'''
    
    def setUp(self):
        self.onboarding = OnboardingSystem()
        # Reset to first-time state for testing
        self.onboarding.is_first_time = True
        self.onboarding.tutorial_dismissed = False
        self.onboarding.completed_steps = set()
        self.onboarding.revealed_elements = set()
    
    def test_tutorial_sequence_structure(self):
        '''Test that the tutorial sequence is properly structured.'''
        sequence = self.onboarding.get_stepwise_tutorial_sequence()
        # Should have the expected number of steps (denser, fewer steps)
        self.assertGreaterEqual(len(sequence), 5, 'Should have at least 5 tutorial steps in the new denser system')
        self.assertLess(len(sequence), 20, 'Should have at most 20 tutorial steps')
        # Each step should have required fields
        for i, step in enumerate(sequence):
            self.assertIn('id', step, f'Step {i} missing 'id'')
            self.assertIn('title', step, f'Step {i} missing 'title'')
            self.assertIn('content', step, f'Step {i} missing 'content'')
            self.assertIn('reveal_elements', step, f'Step {i} missing 'reveal_elements'')
            self.assertIsInstance(step['reveal_elements'], list, f'Step {i} reveal_elements should be a list')
    
    def test_stepwise_tutorial_start(self):
        '''Test starting the stepwise tutorial.'''
        # Should not be showing tutorial initially
        self.assertFalse(self.onboarding.show_tutorial_overlay)
        
        # Start tutorial
        self.onboarding.start_stepwise_tutorial()
        
        # Should now be showing tutorial
        self.assertTrue(self.onboarding.show_tutorial_overlay)
        self.assertEqual(self.onboarding.current_step_index, 0)
        self.assertEqual(len(self.onboarding.tutorial_navigation_history), 0)
    
    def test_tutorial_advancement(self):
        '''Test advancing through tutorial steps.'''
        # Start tutorial
        self.onboarding.start_stepwise_tutorial()
        initial_step = self.onboarding.current_step_index
        
        # Advance to next step
        self.onboarding.advance_stepwise_tutorial()
        
        # Should have moved to next step
        self.assertEqual(self.onboarding.current_step_index, initial_step + 1)
        self.assertEqual(len(self.onboarding.tutorial_navigation_history), 1)
    
    def test_tutorial_back_navigation(self):
        '''Test going back in the tutorial.'''
        # Start and advance a few steps
        self.onboarding.start_stepwise_tutorial()
        self.onboarding.advance_stepwise_tutorial()
        self.onboarding.advance_stepwise_tutorial()
        
        current_step = self.onboarding.current_step_index
        
        # Go back
        self.onboarding.go_back_stepwise_tutorial()
        
        # Should have gone back one step
        self.assertEqual(self.onboarding.current_step_index, current_step - 1)
    
    def test_ui_element_visibility(self):
        '''Test UI element visibility control.'''
        # Start tutorial
        self.onboarding.start_stepwise_tutorial()
        
        # Initially no elements should be visible
        self.assertFalse(self.onboarding.should_show_ui_element('money_display'))
        self.assertFalse(self.onboarding.should_show_ui_element('staff_display'))
        
        # After advancing to money step, money should be visible
        # Find the money display step
        sequence = self.onboarding.get_stepwise_tutorial_sequence()
        money_step_index = None
        for i, step in enumerate(sequence):
            if 'money_display' in step['reveal_elements']:
                money_step_index = i
                break
        
        if money_step_index is not None:
            self.onboarding.current_step_index = money_step_index
            self.onboarding._reveal_current_step_elements()
            
            self.assertTrue(self.onboarding.should_show_ui_element('money_display'))
    
    def test_tutorial_data_retrieval(self):
        '''Test getting current tutorial step data.'''
        # Start tutorial
        self.onboarding.start_stepwise_tutorial()
        
        # Get current step data
        step_data = self.onboarding.get_current_stepwise_tutorial_data()
        
        self.assertIsNotNone(step_data)
        self.assertIn('title', step_data)
        self.assertIn('content', step_data)
        self.assertIn('can_go_back', step_data)
        self.assertIn('can_go_forward', step_data)
        self.assertIn('step_number', step_data)
        self.assertIn('total_steps', step_data)
        
        # First step should not allow going back
        self.assertFalse(step_data['can_go_back'])
        self.assertEqual(step_data['step_number'], 1)
    
    def test_tutorial_completion(self):
        '''Test tutorial completion.'''
        # Start tutorial
        self.onboarding.start_stepwise_tutorial()
        
        # Advance to the last step
        sequence = self.onboarding.get_stepwise_tutorial_sequence()
        self.onboarding.current_step_index = len(sequence) - 1
        
        # Advance one more time to complete
        self.onboarding.advance_stepwise_tutorial()
        
        # Tutorial should be completed
        self.assertFalse(self.onboarding.show_tutorial_overlay)
        self.assertFalse(self.onboarding.is_first_time)


class TestTutorialIntegration(unittest.TestCase):
    '''Test tutorial integration with the rest of the system.'''
    
    def setUp(self):
        self.onboarding = OnboardingSystem()
    
    def test_tutorial_disabled_shows_all_elements(self):
        '''Test that when tutorial is disabled, all UI elements are visible.'''
        # Disable tutorial
        self.onboarding.show_tutorial_overlay = False
        
        # All elements should be visible
        self.assertTrue(self.onboarding.should_show_ui_element('money_display'))
        self.assertTrue(self.onboarding.should_show_ui_element('staff_display'))
        self.assertTrue(self.onboarding.should_show_ui_element('any_element'))


if __name__ == '__main__':
    unittest.main()