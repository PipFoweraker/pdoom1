"""
Tests for the keybinding management system.
"""

import unittest
import os
import tempfile

# Try to import pygame safely for CI environments
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from src.services.keybinding_manager import KeybindingManager, get_action_key_display, is_action_key_pressed


class TestKeybindingManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with temporary config file."""
        # Only initialize pygame if available and set up dummy display
        if PYGAME_AVAILABLE:
            try:
                # Set SDL to use dummy drivers for headless testing
                os.environ['SDL_VIDEODRIVER'] = 'dummy'
                os.environ['SDL_AUDIODRIVER'] = 'dummy'
                pygame.init()
            except:
                # If pygame init fails, tests will still work with dummy constants
                pass
        
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = KeybindingManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary files."""
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
    
    def test_default_keybindings_loaded(self):
        """Test that default keybindings are properly loaded."""
        # Import pygame here to use constants
        if PYGAME_AVAILABLE:
            import pygame
        else:
            # Use dummy constants for testing
            from src.services.keybinding_manager import pygame
        
        # Test action keys
        self.assertEqual(self.manager.get_key_for_action("action_1"), pygame.K_1)
        self.assertEqual(self.manager.get_key_for_action("action_2"), pygame.K_2)
        self.assertEqual(self.manager.get_key_for_action("action_9"), pygame.K_9)
        
        # Test special keys
        self.assertEqual(self.manager.get_key_for_action("end_turn"), pygame.K_SPACE)
        self.assertEqual(self.manager.get_key_for_action("help_guide"), pygame.K_h)
        self.assertEqual(self.manager.get_key_for_action("quit_to_menu"), pygame.K_ESCAPE)
    
    def test_set_keybinding(self):
        """Test setting custom keybindings."""
        # Import pygame constants
        if PYGAME_AVAILABLE:
            import pygame
        else:
            from src.services.keybinding_manager import pygame
            
        # Change action_1 from '1' to 'q'
        result = self.manager.set_keybinding("action_1", pygame.K_q)
        self.assertTrue(result)
        self.assertEqual(self.manager.get_key_for_action("action_1"), pygame.K_q)
        
        # Verify we can get action from key
        self.assertEqual(self.manager.get_action_for_key(pygame.K_q), "action_1")
    
    def test_invalid_action_binding(self):
        """Test that binding invalid actions fails."""
        if PYGAME_AVAILABLE:
            import pygame
        else:
            from src.services.keybinding_manager import pygame
            
        result = self.manager.set_keybinding("invalid_action", pygame.K_q)
        self.assertFalse(result)
    
    def test_protected_keys(self):
        """Test that protected keys cannot be bound."""
        if PYGAME_AVAILABLE:
            import pygame
        else:
            from src.services.keybinding_manager import pygame
            
        result = self.manager.set_keybinding("action_1", pygame.K_TAB)
        self.assertFalse(result)
        
        # Should still have default binding
        self.assertEqual(self.manager.get_key_for_action("action_1"), pygame.K_1)
    
    def test_conflict_detection(self):
        """Test detection of keybinding conflicts."""
        if PYGAME_AVAILABLE:
            import pygame
        else:
            from src.services.keybinding_manager import pygame
            
        # Set action_1 to 'q'
        self.manager.set_keybinding("action_1", pygame.K_q)
        
        # Check conflicts when trying to bind action_2 to 'q'
        conflicts = self.manager.get_conflicts("action_2", pygame.K_q)
        self.assertIn("action_1", conflicts)
    
    def test_key_display_names(self):
        """Test human-readable key display names."""
        self.assertEqual(self.manager.get_action_display_key("end_turn"), "Space")
        self.assertEqual(self.manager.get_action_display_key("quit_to_menu"), "Esc")
        self.assertEqual(self.manager.get_action_display_key("action_1"), "1")
        self.assertEqual(self.manager.get_action_display_key("help_guide"), "H")
    
    def test_action_number_keys(self):
        """Test action number key helpers."""
        if PYGAME_AVAILABLE:
            import pygame
        else:
            from src.services.keybinding_manager import pygame
            
        # Test getting key for action index
        self.assertEqual(self.manager.get_action_number_key(0), pygame.K_1)  # action_1
        self.assertEqual(self.manager.get_action_number_key(1), pygame.K_2)  # action_2
        self.assertEqual(self.manager.get_action_number_key(8), pygame.K_9)  # action_9
        
        # Test invalid indices
        self.assertIsNone(self.manager.get_action_number_key(-1))
        self.assertIsNone(self.manager.get_action_number_key(9))
    
    def test_is_action_key(self):
        """Test checking if a key matches an action."""
        if PYGAME_AVAILABLE:
            import pygame
        else:
            from src.services.keybinding_manager import pygame
            
        self.assertTrue(self.manager.is_action_key(pygame.K_1, 0))  # action_1
        self.assertTrue(self.manager.is_action_key(pygame.K_2, 1))  # action_2
        self.assertFalse(self.manager.is_action_key(pygame.K_1, 1))  # wrong action
        self.assertFalse(self.manager.is_action_key(pygame.K_q, 0))  # wrong key
    
    def test_save_and_load_keybindings(self):
        """Test saving and loading custom keybindings."""
        if PYGAME_AVAILABLE:
            import pygame
        else:
            from src.services.keybinding_manager import pygame
            
        # Set custom binding
        self.manager.set_keybinding("action_1", pygame.K_q)
        self.manager.set_keybinding("end_turn", pygame.K_e)
        
        # Save keybindings
        success = self.manager.save_keybindings()
        self.assertTrue(success)
        
        # Create new manager with same config file
        new_manager = KeybindingManager(self.temp_file.name)
        
        # Verify custom bindings were loaded
        self.assertEqual(new_manager.get_key_for_action("action_1"), pygame.K_q)
        self.assertEqual(new_manager.get_key_for_action("end_turn"), pygame.K_e)
        
        # Verify defaults are still intact for unchanged bindings
        self.assertEqual(new_manager.get_key_for_action("action_2"), pygame.K_2)
    
    def test_reset_to_defaults(self):
        """Test resetting all keybindings to defaults."""
        if PYGAME_AVAILABLE:
            import pygame
        else:
            from src.services.keybinding_manager import pygame
            
        # Set custom bindings
        self.manager.set_keybinding("action_1", pygame.K_q)
        self.manager.set_keybinding("end_turn", pygame.K_e)
        
        # Reset to defaults
        self.manager.reset_to_defaults()
        
        # Verify defaults are restored
        self.assertEqual(self.manager.get_key_for_action("action_1"), pygame.K_1)
        self.assertEqual(self.manager.get_key_for_action("end_turn"), pygame.K_SPACE)


class TestKeybindingConvenienceFunctions(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        # Only initialize pygame if available
        if PYGAME_AVAILABLE:
            try:
                os.environ['SDL_VIDEODRIVER'] = 'dummy'
                os.environ['SDL_AUDIODRIVER'] = 'dummy'
                pygame.init()
            except:
                pass
    
    def test_get_action_key_display(self):
        """Test convenience function for action key display."""
        self.assertEqual(get_action_key_display(0), "1")  # action_1
        self.assertEqual(get_action_key_display(1), "2")  # action_2
        self.assertEqual(get_action_key_display(8), "9")  # action_9
        self.assertEqual(get_action_key_display(9), "?")  # invalid index
    
    def test_is_action_key_pressed(self):
        """Test convenience function for action key checking."""
        if PYGAME_AVAILABLE:
            import pygame
        else:
            from src.services.keybinding_manager import pygame
            
        self.assertTrue(is_action_key_pressed(pygame.K_1, 0))
        self.assertTrue(is_action_key_pressed(pygame.K_2, 1))
        self.assertFalse(is_action_key_pressed(pygame.K_1, 1))


if __name__ == '__main__':
    unittest.main()