"""
Tests for keyboard shortcuts UI integration.
"""
import unittest
import pygame
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui import draw_main_menu
from keyboard_shortcuts import get_main_menu_shortcuts, get_in_game_shortcuts


class TestKeyboardShortcutsUI(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        # Create a test surface
        self.test_surface = pygame.Surface((800, 600))
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    @patch('ui.get_main_menu_shortcuts')
    @patch('ui.get_in_game_shortcuts')  
    def test_draw_main_menu_calls_shortcut_functions(self, mock_in_game, mock_main_menu):
        """Test that draw_main_menu calls the keyboard shortcut functions."""
        # Set up mocks
        mock_main_menu.return_value = [("Test", "Test shortcut")]
        mock_in_game.return_value = [("Game", "Game shortcut")]
        
        # Call the function
        draw_main_menu(self.test_surface, 800, 600, 0)
        
        # Verify the functions were called
        mock_main_menu.assert_called_once()
        mock_in_game.assert_called_once()
        
    def test_shortcuts_data_available_for_ui(self):
        """Test that shortcut data is available and properly structured for UI use."""
        main_shortcuts = get_main_menu_shortcuts()
        in_game_shortcuts = get_in_game_shortcuts()
        
        # Check that we have shortcuts
        self.assertGreater(len(main_shortcuts), 0)
        self.assertGreater(len(in_game_shortcuts), 0)
        
        # Check that shortcuts can be processed for UI display
        for key, desc in main_shortcuts:
            self.assertIsInstance(key, str)
            self.assertIsInstance(desc, str)
            # Check that strings are not empty and reasonable length for UI
            self.assertGreater(len(key), 0)
            self.assertGreater(len(desc), 0)
            self.assertLess(len(key), 20)  # Keys shouldn't be too long
            self.assertLess(len(desc), 50)  # Descriptions should fit on screen
            
    def test_main_menu_with_shortcuts_no_errors(self):
        """Test that drawing main menu with shortcuts doesn't raise errors."""
        try:
            # This should not raise any exceptions
            draw_main_menu(self.test_surface, 800, 600, 0)
        except Exception as e:
            self.fail(f"draw_main_menu raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()