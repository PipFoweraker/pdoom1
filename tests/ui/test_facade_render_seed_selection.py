"""
Test UIFacade render_seed_selection method

This test validates that the UIFacade.render_seed_selection method executes
without exceptions in a headless environment, maintaining behaviour parity
with the original ui.draw_seed_selection function.
"""

import unittest
import pygame
from pdoom1.ui.facade import UIFacade


class TestFacadeRenderSeedSelection(unittest.TestCase):
    """Test UIFacade seed selection rendering functionality."""
    
    def setUp(self):
        """Set up test environment with headless pygame."""
        # Initialize pygame in headless mode
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        
        # Create test surface
        self.screen = pygame.Surface((800, 600))
        self.ui_facade = UIFacade()
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_render_seed_selection_executes_without_exception(self):
        """Test that render_seed_selection executes without exceptions."""
        # Test with minimal parameters (weekly seed selected)
        try:
            self.ui_facade.render_seed_selection(
                screen=self.screen,
                w=800,
                h=600,
                selected_item=0,
                seed_input="",
                sound_manager=None
            )
        except Exception as e:
            self.fail(f"render_seed_selection raised an exception: {e}")
    
    def test_render_seed_selection_with_custom_seed_selected(self):
        """Test seed selection rendering with custom seed option selected."""
        try:
            self.ui_facade.render_seed_selection(
                screen=self.screen,
                w=800,
                h=600,
                selected_item=1,  # Custom seed selected
                seed_input="test-seed-123",
                sound_manager=None
            )
        except Exception as e:
            self.fail(f"render_seed_selection with custom seed raised an exception: {e}")
    
    def test_render_seed_selection_with_empty_custom_seed(self):
        """Test seed selection rendering with custom seed selected but empty input."""
        try:
            self.ui_facade.render_seed_selection(
                screen=self.screen,
                w=800,
                h=600,
                selected_item=1,  # Custom seed selected
                seed_input="",  # Empty input
                sound_manager=None
            )
        except Exception as e:
            self.fail(f"render_seed_selection with empty custom seed raised an exception: {e}")
    
    def test_render_seed_selection_different_screen_sizes(self):
        """Test seed selection rendering with different screen dimensions."""
        test_sizes = [(640, 480), (1024, 768), (1920, 1080)]
        
        for w, h in test_sizes:
            with self.subTest(screen_size=(w, h)):
                test_screen = pygame.Surface((w, h))
                try:
                    self.ui_facade.render_seed_selection(
                        screen=test_screen,
                        w=w,
                        h=h,
                        selected_item=0,
                        seed_input="",
                        sound_manager=None
                    )
                except Exception as e:
                    self.fail(f"render_seed_selection failed for size {w}x{h}: {e}")


if __name__ == '__main__':
    unittest.main()