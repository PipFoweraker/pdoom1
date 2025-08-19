"""
Tests for loading screen functionality.

This module tests the loading screen component with accessibility support.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import unittest
from src.ui.screens import draw_loading_screen


class TestLoadingScreen(unittest.TestCase):
    """Test loading screen functionality."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        """Clean up pygame."""
        pygame.quit()

    def test_loading_screen_basic(self):
        """Test basic loading screen display."""
        # Should complete without error
        draw_loading_screen(self.screen, 800, 600)

    def test_loading_screen_with_progress(self):
        """Test loading screen with different progress values."""
        # Test various progress values
        for progress in [0.0, 0.25, 0.5, 0.75, 1.0]:
            draw_loading_screen(self.screen, 800, 600, progress, f"Loading {int(progress*100)}%")

    def test_loading_screen_with_status_text(self):
        """Test loading screen with custom status text."""
        status_messages = [
            "Initializing...",
            "Loading configuration...",
            "Setting up audio...",
            "Loading UI components...",
            "Ready!"
        ]
        
        for message in status_messages:
            draw_loading_screen(self.screen, 800, 600, 0.5, message)

    def test_loading_screen_accessibility(self):
        """Test loading screen accessibility features."""
        # Status text should be clear and informative
        draw_loading_screen(self.screen, 800, 600, 0.3, "Loading game assets...")
        
        # Should work with empty status text
        draw_loading_screen(self.screen, 800, 600, 0.7, "")

    def test_loading_screen_responsive_sizing(self):
        """Test loading screen on different screen sizes."""
        # Small screen
        draw_loading_screen(self.screen, 400, 300, 0.5, "Loading...")
        
        # Large screen
        draw_loading_screen(self.screen, 1600, 1200, 0.5, "Loading...")

    def test_loading_screen_progress_bounds(self):
        """Test loading screen with out-of-bounds progress values."""
        # Progress below 0 should be clamped
        draw_loading_screen(self.screen, 800, 600, -0.5, "Loading...")
        
        # Progress above 1 should be clamped
        draw_loading_screen(self.screen, 800, 600, 1.5, "Loading...")

    def test_loading_screen_with_custom_font(self):
        """Test loading screen with custom font."""
        custom_font = pygame.font.SysFont('Arial', 18)
        draw_loading_screen(self.screen, 800, 600, 0.6, "Custom font test", custom_font)

    def test_loading_screen_elements(self):
        """Test that loading screen contains expected elements."""
        # The function should render title, progress bar, status text, and percentage
        # We can't directly test the visual output, but we can ensure the function
        # completes without error for various inputs
        
        # Test with zero progress
        draw_loading_screen(self.screen, 800, 600, 0.0, "Starting...")
        
        # Test with full progress
        draw_loading_screen(self.screen, 800, 600, 1.0, "Complete!")

    def test_loading_screen_color_contrast(self):
        """Test loading screen has good color contrast for accessibility."""
        # The function uses high contrast colors:
        # - Dark background (20, 20, 30)
        # - White title text (255, 255, 255)
        # - Light gray status text (200, 200, 200)
        # - Blue progress bar (100, 150, 255)
        
        # Ensure function works (we can't directly test colors in unit test)
        draw_loading_screen(self.screen, 800, 600, 0.4, "High contrast test")


class TestLoadingScreenIntegration(unittest.TestCase):
    """Test loading screen integration scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        """Clean up pygame."""
        pygame.quit()

    def test_loading_phases_simulation(self):
        """Test simulated loading phases like in main.py."""
        phases = [
            (0.2, "Initializing systems..."),
            (0.4, "Loading configuration..."),
            (0.6, "Setting up audio..."),
            (0.8, "Loading UI components..."),
            (1.0, "Ready!")
        ]
        
        for progress, status in phases:
            draw_loading_screen(self.screen, 800, 600, progress, status)

    def test_fast_load_scenario(self):
        """Test fast load scenario where loading completes quickly."""
        # Simulate rapid loading
        for i in range(5):
            progress = (i + 1) / 5
            status = f"Phase {i + 1}/5..."
            draw_loading_screen(self.screen, 800, 600, progress, status)

    def test_loading_screen_role_status(self):
        """Test that loading screen provides status role equivalent."""
        # The loading screen provides clear status information through:
        # 1. Status text
        # 2. Progress percentage
        # 3. Progress bar visual
        
        # Test informative status messages
        informative_statuses = [
            "Initializing game engine...",
            "Loading player data...",
            "Preparing game world...",
            "Almost ready..."
        ]
        
        for status in informative_statuses:
            draw_loading_screen(self.screen, 800, 600, 0.5, status)


if __name__ == '__main__':
    unittest.main()