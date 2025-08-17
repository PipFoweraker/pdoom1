"""
Tests for UIFacade render_loading method.

Headless smoke tests to ensure the loading screen rendering works without exceptions
through the UIFacade interface.
"""

import unittest
import pygame
from pdoom1.ui.facade import UIFacade


class TestFacadeRenderLoading(unittest.TestCase):
    """Test UIFacade render_loading method in headless mode."""
    
    def setUp(self):
        """Set up test environment with headless pygame."""
        pygame.init()
        # Create minimal surface for headless testing
        self.screen = pygame.display.set_mode((1, 1), pygame.NOFRAME)
        self.ui_facade = UIFacade()
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_render_loading_no_crash(self):
        """Test that render_loading executes without exceptions."""
        try:
            self.ui_facade.render_loading(self.screen, 800, 600)
        except Exception as e:
            self.fail(f"render_loading raised an exception: {e}")
    
    def test_render_loading_with_progress(self):
        """Test render_loading with different progress values."""
        progress_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        for progress in progress_values:
            try:
                self.ui_facade.render_loading(self.screen, 800, 600, progress)
            except Exception as e:
                self.fail(f"render_loading with progress={progress} raised an exception: {e}")
    
    def test_render_loading_with_status_text(self):
        """Test render_loading with custom status text."""
        status_texts = [
            "Loading...",
            "Initializing systems...",
            "Loading configuration...",
            "Setting up audio...",
            "Ready!"
        ]
        for status_text in status_texts:
            try:
                self.ui_facade.render_loading(self.screen, 800, 600, 0.5, status_text)
            except Exception as e:
                self.fail(f"render_loading with status_text='{status_text}' raised an exception: {e}")
    
    def test_render_loading_with_font(self):
        """Test render_loading with custom font parameter."""
        try:
            # Test with None (default font)
            self.ui_facade.render_loading(self.screen, 800, 600, 0.5, "Test", None)
            
            # Test with custom font
            custom_font = pygame.font.SysFont('Consolas', 20)
            self.ui_facade.render_loading(self.screen, 800, 600, 0.5, "Test", custom_font)
        except Exception as e:
            self.fail(f"render_loading with font parameter raised an exception: {e}")
    
    def test_render_loading_edge_cases(self):
        """Test render_loading with edge case values."""
        edge_cases = [
            (-0.1, "Negative progress"),  # Should clamp to 0
            (1.1, "Over 100% progress"),  # Should clamp to 1
            (0.5, ""),                    # Empty status text
        ]
        for progress, status in edge_cases:
            try:
                self.ui_facade.render_loading(self.screen, 800, 600, progress, status)
            except Exception as e:
                self.fail(f"render_loading with edge case ({progress}, '{status}') raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()