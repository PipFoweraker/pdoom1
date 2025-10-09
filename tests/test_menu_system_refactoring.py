'''
Test module for menu system refactoring.

Tests the extracted menu handling functionality to ensure
the refactoring doesn't break existing behavior.
'''

import unittest
import pygame
from src.ui.menu_handlers.menu_system import (
    NavigationManager, MenuClickHandler, MenuKeyboardHandler,
    get_weekly_seed, load_markdown_file
)


class TestMenuSystemRefactoring(unittest.TestCase):
    '''Test cases for the refactored menu system.'''
    
    def setUp(self):
        '''Set up test environment.'''
        self.nav_manager = NavigationManager()
        pygame.init()  # Initialize pygame for key constants
    
    def test_navigation_manager(self):
        '''Test navigation stack management.'''
        # Initial state
        self.assertEqual(self.nav_manager.get_depth(), 0)
        
        # Push state
        new_state = self.nav_manager.push_state('main_menu', 'settings')
        self.assertEqual(new_state, 'settings')
        self.assertEqual(self.nav_manager.get_depth(), 1)
        
        # Pop state
        previous_state = self.nav_manager.pop_state('settings')
        self.assertEqual(previous_state, 'main_menu')
        self.assertEqual(self.nav_manager.get_depth(), 0)
        
        # Pop from empty stack
        same_state = self.nav_manager.pop_state('main_menu')
        self.assertEqual(same_state, 'main_menu')
    
    def test_weekly_seed_generation(self):
        '''Test weekly seed generation.'''
        seed = get_weekly_seed()
        
        # Should be a string with year and week
        self.assertIsInstance(seed, str)
        self.assertTrue(len(seed) >= 6)  # YYYYWW format
        self.assertTrue(seed.startswith('2025'))  # Current year
    
    def test_menu_click_handler(self):
        '''Test menu click detection.'''
        menu_items = ['Start Game', 'Settings', 'Exit']
        
        # Test valid click (approximate center of first button)
        result = MenuClickHandler.handle_main_menu_click(
            (600, 280),  # Approximate button center
            1200, 800,   # Screen dimensions
            menu_items
        )
        
        # Should detect a menu selection
        self.assertIn('action', result)
        
        # Test click outside menu area
        result = MenuClickHandler.handle_main_menu_click(
            (50, 50),    # Top left corner
            1200, 800,
            menu_items
        )
        
        self.assertEqual(result['action'], 'none')
    
    def test_menu_keyboard_handler(self):
        '''Test keyboard navigation.'''
        menu_items = ['Start Game', 'Settings', 'Exit']
        
        # Test down arrow
        result = MenuKeyboardHandler.handle_main_menu_keyboard(
            pygame.K_DOWN, 0, menu_items
        )
        self.assertEqual(result['new_selected_item'], 1)
        self.assertEqual(result['action'], 'navigate')
        
        # Test up arrow with wrapping
        result = MenuKeyboardHandler.handle_main_menu_keyboard(
            pygame.K_UP, 0, menu_items
        )
        self.assertEqual(result['new_selected_item'], 2)  # Wraps to last item
        
        # Test enter key
        result = MenuKeyboardHandler.handle_main_menu_keyboard(
            pygame.K_RETURN, 1, menu_items
        )
        self.assertEqual(result['action'], 'select')
        self.assertEqual(result['index'], 1)
    
    def test_load_markdown_file_error_handling(self):
        '''Test markdown file loading with non-existent file.'''
        content = load_markdown_file('nonexistent_file.md')
        self.assertIn('Could not load', content)
    
    def tearDown(self):
        '''Clean up after tests.'''
        pygame.quit()


if __name__ == '__main__':
    unittest.main()
