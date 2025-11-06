'''
Tests for the end-game menu functionality.

This module tests the new end-game menu that replaces the old 'click to restart' behavior.
Tests cover menu navigation, state transitions, and proper integration with existing systems.
'''

import unittest
import sys
import os

# Add the parent directory to the path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import main module functions for testing
from main import (
    handle_end_game_menu_click,
    handle_end_game_menu_keyboard,
    create_settings_content,
    end_game_menu_items
)

# Mock pygame to avoid initialization issues in tests
import pygame
pygame.init()


class TestEndGameMenuFunctionality(unittest.TestCase):
    '''Test the end-game menu navigation and functionality.'''
    
    def setUp(self):
        '''Set up test environment for each test.'''
        # Import main module globals
        import main
        
        # Reset global state
        main.current_state = 'end_game_menu'
        main.end_game_selected_item = 0
        main.seed = 'test-seed-123'
        main.overlay_content = None
        main.overlay_title = None
        
        # Store reference to main module for state checking
        self.main_module = main
    
    def test_end_game_menu_items_defined(self):
        '''Test that end-game menu items are properly defined.'''
        expected_items = ['View Full Leaderboard', 'Play Again', 'Main Menu', 'Settings', 'Submit Feedback']
        self.assertEqual(end_game_menu_items, expected_items)
        self.assertEqual(len(end_game_menu_items), 5)
    
    def test_settings_content_creation(self):
        '''Test that settings content is created successfully.'''
        content = create_settings_content()
        self.assertIsInstance(content, str)
        self.assertIn('Settings', content)
        self.assertIn('Game Settings', content)
        self.assertIn('Audio Settings', content)
        self.assertIn('Gameplay Settings', content)
        self.assertIn('Accessibility', content)
        self.assertIn('Controls', content)
    
    def test_keyboard_navigation_up_down(self):
        '''Test keyboard navigation in end-game menu.'''
        # Test down navigation
        self.main_module.end_game_selected_item = 0
        handle_end_game_menu_keyboard(pygame.K_DOWN)
        self.assertEqual(self.main_module.end_game_selected_item, 1)
        
        # Test wrapping at bottom
        self.main_module.end_game_selected_item = 4  # Last item index (5 items = indices 0-4)
        handle_end_game_menu_keyboard(pygame.K_DOWN)
        self.assertEqual(self.main_module.end_game_selected_item, 0)
        
        # Test up navigation
        self.main_module.end_game_selected_item = 1
        handle_end_game_menu_keyboard(pygame.K_UP)
        self.assertEqual(self.main_module.end_game_selected_item, 0)
        
        # Test wrapping at top
        self.main_module.end_game_selected_item = 0
        handle_end_game_menu_keyboard(pygame.K_UP)
        self.assertEqual(self.main_module.end_game_selected_item, 4)  # Last item index (5 items = indices 0-4)
    
    def test_view_high_scores_action(self):
        '''Test view high scores functionality.'''
        self.main_module.end_game_selected_item = 0
        handle_end_game_menu_keyboard(pygame.K_RETURN)
        self.assertEqual(self.main_module.current_state, 'high_score')
    
    def test_relaunch_game_action(self):
        '''Test relaunch game functionality.'''
        self.main_module.end_game_selected_item = 1
        handle_end_game_menu_keyboard(pygame.K_RETURN)
        self.assertEqual(self.main_module.current_state, 'game')
    
    def test_main_menu_action(self):
        '''Test return to main menu functionality.'''
        self.main_module.end_game_selected_item = 2
        handle_end_game_menu_keyboard(pygame.K_RETURN)
        self.assertEqual(self.main_module.current_state, 'main_menu')
    
    def test_settings_action(self):
        '''Test settings menu access.'''
        self.main_module.end_game_selected_item = 3
        handle_end_game_menu_keyboard(pygame.K_RETURN)
        self.assertEqual(self.main_module.current_state, 'overlay')
        self.assertEqual(self.main_module.overlay_title, 'Settings')
        self.assertIsNotNone(self.main_module.overlay_content)
        self.assertIn('Settings', self.main_module.overlay_content)
    
    def test_submit_feedback_action(self):
        '''Test submit feedback functionality.'''
        self.main_module.end_game_selected_item = 4
        handle_end_game_menu_keyboard(pygame.K_RETURN)
        self.assertEqual(self.main_module.current_state, 'bug_report')
        # Should pre-select feedback type (index 2)
        self.assertEqual(self.main_module.bug_report_data['type_index'], 2)
    
    def test_submit_bug_action(self):
        '''Test submit bug functionality.'''
        self.main_module.end_game_selected_item = 5
        handle_end_game_menu_keyboard(pygame.K_RETURN)
        self.assertEqual(self.main_module.current_state, 'bug_report')
        # Should pre-select bug type (index 0)
        self.assertEqual(self.main_module.bug_report_data['type_index'], 0)
    
    def test_escape_key_returns_to_main_menu(self):
        '''Test that escape key returns to main menu.'''
        handle_end_game_menu_keyboard(pygame.K_ESCAPE)
        self.assertEqual(self.main_module.current_state, 'main_menu')
    
    def test_settings_navigation_returns_to_end_game_menu(self):
        '''Test that exiting settings returns to end game menu, not main menu.'''
        # Start from end game menu
        self.main_module.current_state = 'end_game_menu'
        self.main_module.navigation_stack = []  # Ensure clean stack
        
        # Navigate to settings
        self.main_module.end_game_selected_item = 3  # Settings option
        handle_end_game_menu_keyboard(pygame.K_RETURN)
        
        # Should be in overlay state with settings content
        self.assertEqual(self.main_module.current_state, 'overlay')
        self.assertEqual(self.main_module.overlay_title, 'Settings')
        
        # Simulate pressing escape in overlay (simulate overlay keyboard handling)
        from main import pop_navigation_state
        result = pop_navigation_state()
        
        # Should return True (successful pop) and be back in end_game_menu
        self.assertTrue(result, 'Should successfully pop from navigation stack')
        self.assertEqual(self.main_module.current_state, 'end_game_menu', 
                        'Should return to end_game_menu, not main_menu')


class TestEndGameMenuClicks(unittest.TestCase):
    '''Test mouse click handling for end-game menu.'''
    
    def setUp(self):
        '''Set up test environment for each test.'''
        import main
        self.main_module = main
        
        # Reset global state
        main.current_state = 'end_game_menu'
        main.end_game_selected_item = 0
        main.seed = 'test-seed-123'
        main.overlay_content = None
        main.overlay_title = None
    
    def test_click_positions_calculated_correctly(self):
        '''Test that click handling doesn't crash with various positions.'''
        # Test clicks in various screen positions
        test_positions = [
            (100, 100),   # Top left
            (400, 300),   # Center
            (700, 500),   # Bottom right
            (0, 0),       # Edge case
        ]
        
        for pos in test_positions:
            # Should not raise exceptions
            try:
                handle_end_game_menu_click(pos, 800, 600)
            except Exception as e:
                self.fail(f'Click handling failed for position {pos}: {e}')


class TestEndGameMenuIntegration(unittest.TestCase):
    '''Test integration with existing game systems.'''
    
    def test_bug_report_form_reset(self):
        '''Test that bug report form is properly reset.'''
        import main
        
        # Set some existing data
        main.bug_report_data = {
            'type_index': 1,
            'title': 'old title',
            'description': 'old description',
            'steps': 'old steps',
            'expected': 'old expected',
            'actual': 'old actual',
            'attribution': True,
            'name': 'old name',
            'contact': 'old contact'
        }
        
        # Trigger feedback action
        main.end_game_selected_item = 4
        handle_end_game_menu_keyboard(pygame.K_RETURN)
        
        # Check that form was reset except for type
        self.assertEqual(main.bug_report_data['type_index'], 2)  # feedback type
        self.assertEqual(main.bug_report_data['title'], '')
        self.assertEqual(main.bug_report_data['description'], '')
        self.assertEqual(main.bug_report_data['attribution'], False)
    
    def test_settings_content_comprehensive(self):
        '''Test that settings content covers all expected sections.'''
        content = create_settings_content()
        
        # Check for major sections
        expected_sections = [
            'Game Settings',
            'Audio Settings', 
            'Gameplay Settings',
            'Accessibility',
            'Data & Privacy',
            'Controls'
        ]
        
        for section in expected_sections:
            self.assertIn(section, content, f'Missing section: {section}')
        
        # Check for specific setting mentions
        expected_settings = [
            'Display Mode',
            'FPS',
            'Action Points',
            'Keyboard Navigation',
            'Local Highscores',
            'Space',
            'Arrow Keys'
        ]
        
        for setting in expected_settings:
            self.assertIn(setting, content, f'Missing setting: {setting}')


if __name__ == '__main__':
    unittest.main()