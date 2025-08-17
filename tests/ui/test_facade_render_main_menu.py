"""
Tests for UIFacade render_main_menu method.

Headless smoke tests to ensure the main menu rendering works without exceptions
through the UIFacade interface.
"""

import unittest
import pygame
from pdoom1.ui.facade import UIFacade


class TestFacadeRenderMainMenu(unittest.TestCase):
    """Test UIFacade render_main_menu method in headless mode."""
    
    def setUp(self):
        """Set up test environment with headless pygame."""
        pygame.init()
        # Create minimal surface for headless testing
        self.screen = pygame.display.set_mode((1, 1), pygame.NOFRAME)
        self.ui_facade = UIFacade()
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_render_main_menu_no_crash(self):
        """Test that render_main_menu executes without exceptions."""
        try:
            self.ui_facade.render_main_menu(self.screen, 800, 600, 0)
        except Exception as e:
            self.fail(f"render_main_menu raised an exception: {e}")
    
    def test_render_main_menu_with_sound_manager(self):
        """Test render_main_menu with sound manager parameter."""
        # Mock sound manager - since we're in headless mode, None is acceptable
        try:
            self.ui_facade.render_main_menu(self.screen, 800, 600, 1, None)
        except Exception as e:
            self.fail(f"render_main_menu with sound manager raised an exception: {e}")
    
    def test_render_main_menu_different_selections(self):
        """Test render_main_menu with different selected items."""
        for selected_item in range(5):  # Main menu has 5 items
            try:
                self.ui_facade.render_main_menu(self.screen, 800, 600, selected_item)
            except Exception as e:
                self.fail(f"render_main_menu with selected_item={selected_item} raised an exception: {e}")
    
    def test_render_main_menu_different_screen_sizes(self):
        """Test render_main_menu with different screen dimensions."""
        test_sizes = [(800, 600), (1024, 768), (1920, 1080), (640, 480)]
        for w, h in test_sizes:
            try:
                self.ui_facade.render_main_menu(self.screen, w, h, 0)
            except Exception as e:
                self.fail(f"render_main_menu with size {w}x{h} raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()