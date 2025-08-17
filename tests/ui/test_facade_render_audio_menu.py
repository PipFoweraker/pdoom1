"""
Tests for UIFacade render_audio_menu method.

Headless smoke tests to ensure the audio menu rendering works without exceptions
through the UIFacade interface.
"""

import unittest
import pygame
from pdoom1.ui.facade import UIFacade


class TestFacadeRenderAudioMenu(unittest.TestCase):
    """Test UIFacade render_audio_menu method in headless mode."""
    
    def setUp(self):
        """Set up test environment with headless pygame."""
        pygame.init()
        # Create minimal surface for headless testing
        self.screen = pygame.display.set_mode((1, 1), pygame.NOFRAME)
        self.ui_facade = UIFacade()
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_render_audio_menu_no_crash(self):
        """Test that render_audio_menu executes without exceptions."""
        audio_settings = {
            'master_enabled': True,
            'sfx_volume': 80
        }
        try:
            self.ui_facade.render_audio_menu(self.screen, 800, 600, 0, audio_settings, None)
        except Exception as e:
            self.fail(f"render_audio_menu raised an exception: {e}")
    
    def test_render_audio_menu_different_selections(self):
        """Test render_audio_menu with different selected items."""
        audio_settings = {
            'master_enabled': True,
            'sfx_volume': 80
        }
        # Audio menu has 5 items: Master Sound, SFX Volume, Sound Effects Settings, Test Sound, Back
        for selected_item in range(5):
            try:
                self.ui_facade.render_audio_menu(self.screen, 800, 600, selected_item, audio_settings, None)
            except Exception as e:
                self.fail(f"render_audio_menu with selected_item={selected_item} raised an exception: {e}")
    
    def test_render_audio_menu_different_settings(self):
        """Test render_audio_menu with different audio settings."""
        test_settings = [
            {'master_enabled': True, 'sfx_volume': 100},
            {'master_enabled': False, 'sfx_volume': 0},
            {'master_enabled': True, 'sfx_volume': 50},
            {'master_enabled': False, 'sfx_volume': 75},
            # Test with missing keys (should have defaults)
            {},
            {'master_enabled': True},
            {'sfx_volume': 60}
        ]
        
        for settings in test_settings:
            try:
                self.ui_facade.render_audio_menu(self.screen, 800, 600, 0, settings, None)
            except Exception as e:
                self.fail(f"render_audio_menu with settings {settings} raised an exception: {e}")
    
    def test_render_audio_menu_with_sound_manager(self):
        """Test render_audio_menu with sound manager parameter."""
        audio_settings = {
            'master_enabled': True,
            'sfx_volume': 80
        }
        
        # Test with None sound manager
        try:
            self.ui_facade.render_audio_menu(self.screen, 800, 600, 0, audio_settings, None)
        except Exception as e:
            self.fail(f"render_audio_menu with None sound manager raised an exception: {e}")
    
    def test_render_audio_menu_different_screen_sizes(self):
        """Test render_audio_menu with different screen dimensions."""
        audio_settings = {
            'master_enabled': True,
            'sfx_volume': 80
        }
        test_sizes = [(800, 600), (1024, 768), (1920, 1080), (640, 480)]
        for w, h in test_sizes:
            try:
                self.ui_facade.render_audio_menu(self.screen, w, h, 0, audio_settings, None)
            except Exception as e:
                self.fail(f"render_audio_menu with size {w}x{h} raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()