"""
Tests for keyboard shortcuts functionality.
"""
import unittest
from src.services.keyboard_shortcuts import (
    get_main_menu_shortcuts, 
    get_in_game_shortcuts,
    get_all_shortcuts,
    format_shortcut_list,
    MAIN_MENU_SHORTCUTS,
    IN_GAME_SHORTCUTS
)


class TestKeyboardShortcuts(unittest.TestCase):
    
    def test_main_menu_shortcuts_not_empty(self):
        """Test that main menu shortcuts are defined and not empty."""
        shortcuts = get_main_menu_shortcuts()
        self.assertIsInstance(shortcuts, list)
        self.assertGreater(len(shortcuts), 0)
        
    def test_in_game_shortcuts_not_empty(self):
        """Test that in-game shortcuts are defined and not empty."""
        shortcuts = get_in_game_shortcuts()
        self.assertIsInstance(shortcuts, list)
        self.assertGreater(len(shortcuts), 0)
        
    def test_shortcut_structure(self):
        """Test that shortcuts have the correct structure (key, description) tuples."""
        for shortcut in get_main_menu_shortcuts():
            self.assertIsInstance(shortcut, tuple)
            self.assertEqual(len(shortcut), 2)
            key, desc = shortcut
            self.assertIsInstance(key, str)
            self.assertIsInstance(desc, str)
            self.assertGreater(len(key), 0)
            self.assertGreater(len(desc), 0)
            
        for shortcut in get_in_game_shortcuts():
            self.assertIsInstance(shortcut, tuple)
            self.assertEqual(len(shortcut), 2)
            key, desc = shortcut
            self.assertIsInstance(key, str)
            self.assertIsInstance(desc, str)
            self.assertGreater(len(key), 0)
            self.assertGreater(len(desc), 0)
    
    def test_get_all_shortcuts(self):
        """Test that get_all_shortcuts returns properly structured data."""
        all_shortcuts = get_all_shortcuts()
        self.assertIsInstance(all_shortcuts, dict)
        self.assertIn('main_menu', all_shortcuts)
        self.assertIn('in_game', all_shortcuts)
        
    def test_format_shortcut_list(self):
        """Test that format_shortcut_list formats shortcuts correctly."""
        test_shortcuts = [("A", "Action A"), ("Ctrl+B", "Action B")]
        formatted = format_shortcut_list(test_shortcuts)
        
        self.assertIsInstance(formatted, list)
        self.assertEqual(len(formatted), 2)
        
        # Check formatting includes key and description
        self.assertIn("A", formatted[0])
        self.assertIn("Action A", formatted[0])
        self.assertIn("Ctrl+B", formatted[1])
        self.assertIn("Action B", formatted[1])
        
    def test_shortcuts_include_essential_controls(self):
        """Test that essential controls are included in shortcuts."""
        main_menu = get_main_menu_shortcuts()
        in_game = get_in_game_shortcuts()
        
        # Convert to strings for easier checking
        main_menu_str = str(main_menu).lower()
        in_game_str = str(in_game).lower()
        
        # Main menu should include navigation and selection
        self.assertIn('enter', main_menu_str)
        self.assertIn('esc', main_menu_str)
        
        # In-game should include key actions
        self.assertIn('space', in_game_str)
        self.assertIn('esc', in_game_str)
    
    def test_constants_match_functions(self):
        """Test that constant definitions match function returns."""
        self.assertEqual(MAIN_MENU_SHORTCUTS, get_main_menu_shortcuts())
        self.assertEqual(IN_GAME_SHORTCUTS, get_in_game_shortcuts())


if __name__ == '__main__':
    unittest.main()