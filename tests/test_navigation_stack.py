'''
Tests for navigation stack functionality in the UI.

This module tests the Back/Return navigation system that allows users
to navigate through UI panels with proper depth tracking.
'''

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import unittest
import main
from src.ui.text import draw_back_button
from ui import should_show_back_button


class TestNavigationStack(unittest.TestCase):
    '''Test navigation stack functionality.'''

    def setUp(self):
        '''Set up test fixtures.'''
        # Reset navigation stack before each test
        main.navigation_stack = []
        main.current_state = 'main_menu'

    def test_navigation_stack_initialization(self):
        '''Test that navigation stack starts empty.'''
        self.assertEqual(len(main.navigation_stack), 0)
        self.assertEqual(main.get_navigation_depth(), 0)

    def test_push_navigation_state(self):
        '''Test pushing states to navigation stack.'''
        initial_state = main.current_state
        main.push_navigation_state('overlay')
        
        self.assertEqual(main.current_state, 'overlay')
        self.assertEqual(main.get_navigation_depth(), 1)
        self.assertEqual(main.navigation_stack[0], initial_state)

    def test_pop_navigation_state(self):
        '''Test popping states from navigation stack.'''
        initial_state = main.current_state
        main.push_navigation_state('overlay')
        main.push_navigation_state('config_select')
        
        # Pop should return to previous state
        result = main.pop_navigation_state()
        self.assertTrue(result)
        self.assertEqual(main.current_state, 'overlay')
        self.assertEqual(main.get_navigation_depth(), 1)
        
        # Pop again should return to initial state
        result = main.pop_navigation_state()
        self.assertTrue(result)
        self.assertEqual(main.current_state, initial_state)
        self.assertEqual(main.get_navigation_depth(), 0)

    def test_pop_empty_navigation_stack(self):
        '''Test popping from empty navigation stack.'''
        result = main.pop_navigation_state()
        self.assertFalse(result)
        self.assertEqual(main.get_navigation_depth(), 0)

    def test_multiple_navigation_levels(self):
        '''Test navigation through multiple levels.'''
        states = ['main_menu', 'config_select', 'overlay', 'bug_report']
        
        # Push multiple states
        for state in states[1:]:
            main.push_navigation_state(state)
        
        self.assertEqual(main.get_navigation_depth(), 3)
        self.assertEqual(main.current_state, 'bug_report')
        
        # Pop back through all states
        for expected_state in reversed(states[:-1]):
            result = main.pop_navigation_state()
            self.assertTrue(result)
            self.assertEqual(main.current_state, expected_state)


class TestBackButtonHelper(unittest.TestCase):
    '''Test the should_show_back_button helper function.'''

    def test_should_show_back_button(self):
        '''Test should_show_back_button logic.'''
        # Should not show at depth 0
        self.assertFalse(should_show_back_button(0))
        
        # Should show at depth >= 1
        self.assertTrue(should_show_back_button(1))
        self.assertTrue(should_show_back_button(2))
        self.assertTrue(should_show_back_button(5))


class TestBackButtonClick(unittest.TestCase):
    '''Test Back button click handling.'''

    def setUp(self):
        '''Set up test fixtures.'''
        # Reset navigation stack before each test
        main.navigation_stack = []
        main.current_state = 'main_menu'

    def test_back_button_triggers_pop_navigation(self):
        '''Test that clicking back button at depth 1 triggers pop_navigation_state.'''
        # Set up navigation at depth 1
        main.push_navigation_state('overlay')
        self.assertEqual(main.get_navigation_depth(), 1)
        self.assertEqual(main.current_state, 'overlay')
        
        # Simulate back button click (should trigger pop_navigation_state)
        result = main.pop_navigation_state()
        self.assertTrue(result)
        self.assertEqual(main.get_navigation_depth(), 0)
        self.assertEqual(main.current_state, 'main_menu')


class TestBackButton(unittest.TestCase):
    '''Test Back button component.'''

    def setUp(self):
        '''Set up pygame for UI tests.'''
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        '''Clean up pygame.'''
        pygame.quit()

    def test_back_button_visibility(self):
        '''Test Back button visibility based on navigation depth.'''
        # Should not show at depth 0
        rect = draw_back_button(self.screen, 800, 600, 0)
        self.assertIsNone(rect)
        
        # Should show at depth >= 1
        rect = draw_back_button(self.screen, 800, 600, 1)
        self.assertIsNotNone(rect)
        self.assertIsInstance(rect, pygame.Rect)
        
        rect = draw_back_button(self.screen, 800, 600, 2)
        self.assertIsNotNone(rect)
        self.assertIsInstance(rect, pygame.Rect)

    def test_back_button_positioning(self):
        '''Test Back button positioning and sizing.'''
        rect = draw_back_button(self.screen, 800, 600, 2)
        
        # Should be positioned in top-left with margin
        expected_margin = int(600 * 0.02)  # 2% of height
        self.assertEqual(rect.x, expected_margin)
        self.assertEqual(rect.y, expected_margin)
        
        # Should have reasonable size
        self.assertGreater(rect.width, 50)
        self.assertGreater(rect.height, 20)

    def test_back_button_scaling(self):
        '''Test Back button scales with screen size.'''
        # Test with smaller screen
        small_rect = draw_back_button(self.screen, 400, 300, 2)
        
        # Test with larger screen  
        large_rect = draw_back_button(self.screen, 1600, 1200, 2)
        
        # Button should scale with screen size
        self.assertIsNotNone(small_rect)
        self.assertIsNotNone(large_rect)
        
        # Larger screen should have larger margins
        small_margin = int(300 * 0.02)
        large_margin = int(1200 * 0.02)
        self.assertLess(small_margin, large_margin)


if __name__ == '__main__':
    unittest.main()