"""
Tests for sound system fixes addressing issue #89.

Tests the following requirements:
- Sound should be on by default
- Sound icon should be larger 
- Sound icon should be displayed and toggleable at the loading screen
- Sound icon should be displayed and toggleable at the main screen
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sound_manager import SoundManager
from game_state import GameState

class TestSoundIssue89(unittest.TestCase):
    """Test sound system fixes for issue #89"""

    def setUp(self):
        """Set up test fixtures"""
        pass

    def test_sound_manager_enabled_by_default(self):
        """Test that SoundManager is enabled by default (Issue #89)"""
        sound_manager = SoundManager()
        self.assertTrue(sound_manager.is_enabled(), 
                       "Sound should be enabled by default")

    def test_game_state_sound_enabled_by_default(self):
        """Test that GameState has sound enabled by default (Issue #89)"""
        game_state = GameState(seed=12345)
        self.assertTrue(game_state.sound_manager.is_enabled(),
                       "Game state sound manager should be enabled by default")

    def test_sound_manager_toggle_functionality(self):
        """Test that sound can be toggled on and off"""
        sound_manager = SoundManager()
        
        # Initially enabled
        self.assertTrue(sound_manager.is_enabled())
        
        # Toggle off
        new_state = sound_manager.toggle()
        self.assertFalse(new_state)
        self.assertFalse(sound_manager.is_enabled())
        
        # Toggle back on
        new_state = sound_manager.toggle()
        self.assertTrue(new_state)
        self.assertTrue(sound_manager.is_enabled())

    def test_sound_manager_set_enabled(self):
        """Test explicit sound enable/disable functionality"""
        sound_manager = SoundManager()
        
        # Explicitly disable
        sound_manager.set_enabled(False)
        self.assertFalse(sound_manager.is_enabled())
        
        # Explicitly enable
        sound_manager.set_enabled(True)
        self.assertTrue(sound_manager.is_enabled())

    def test_individual_sound_toggles_work(self):
        """Test that individual sound effects can be toggled"""
        sound_manager = SoundManager()
        
        # All sounds should be enabled by default
        for sound_name in sound_manager.get_sound_names():
            self.assertTrue(sound_manager.is_sound_enabled(sound_name),
                          f"Sound '{sound_name}' should be enabled by default")
        
        # Toggle a specific sound off
        sound_manager.set_sound_enabled('blob', False)
        self.assertFalse(sound_manager.is_sound_enabled('blob'))
        self.assertTrue(sound_manager.is_sound_enabled('ap_spend'))  # Others still on
        
        # Toggle it back on
        sound_manager.set_sound_enabled('blob', True)
        self.assertTrue(sound_manager.is_sound_enabled('blob'))

    def test_main_menu_ui_functions_exist(self):
        """Test that UI functions for main menu sound button exist"""
        # Test that we can import the UI functions we added
        try:
            from ui import draw_mute_button_standalone, draw_main_menu
            # Test the new function signature works
            # We can't actually test drawing without a screen, but we can test the import
            self.assertTrue(callable(draw_mute_button_standalone))
            self.assertTrue(callable(draw_main_menu))
        except ImportError as e:
            self.fail(f"Failed to import required UI functions: {e}")

    def test_global_sound_manager_integration(self):
        """Test that global sound manager can be imported from main"""
        try:
            import main
            # Check that global sound manager exists and is a SoundManager
            self.assertIsInstance(main.global_sound_manager, SoundManager)
            
            # Check that it's enabled by default (config setting)
            self.assertTrue(main.global_sound_manager.is_enabled())
            
        except (ImportError, AttributeError) as e:
            self.fail(f"Failed to access global sound manager: {e}")

class TestSoundSystemIntegration(unittest.TestCase):
    """Integration tests for sound system with game state"""

    def test_sync_sound_state_between_managers(self):
        """Test that sound state can be synced between global and game managers"""
        # Create managers
        global_manager = SoundManager()
        game_state = GameState(seed=12345)
        
        # Change global state
        global_manager.set_enabled(False)
        
        # Sync to game state (this simulates what happens in main.py)
        game_state.sound_manager.set_enabled(global_manager.is_enabled())
        
        # Verify sync worked
        self.assertFalse(game_state.sound_manager.is_enabled())
        self.assertEqual(global_manager.is_enabled(), game_state.sound_manager.is_enabled())

    def test_sound_plays_without_error(self):
        """Test that sound methods can be called without throwing errors"""
        sound_manager = SoundManager()
        
        # These should not throw exceptions even if audio hardware isn't available
        try:
            sound_manager.play_blob_sound()
            sound_manager.play_ap_spend_sound()
            sound_manager.play_money_spend_sound()
            sound_manager.play_error_beep()
            sound_manager.play_zabinga_sound()
        except Exception as e:
            self.fail(f"Sound methods should not throw exceptions: {e}")

if __name__ == '__main__':
    unittest.main()