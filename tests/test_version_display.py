"""
Tests for version display functionality.

This module tests the public version display in UI footer and header areas.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import unittest
from unittest.mock import patch, MagicMock
from ui import draw_version_footer, draw_version_header


class TestVersionDisplay(unittest.TestCase):
    """Test version display functionality."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        """Clean up pygame."""
        pygame.quit()

    def test_version_footer_display(self):
        """Test version display in footer."""
        # Should complete without error
        draw_version_footer(self.screen, 800, 600)

    def test_version_header_display(self):
        """Test version display in header."""
        # Should complete without error
        draw_version_header(self.screen, 800, 600)

    @patch('version.get_display_version')
    def test_version_footer_with_mock_version(self, mock_get_version):
        """Test version footer with mocked version."""
        mock_get_version.return_value = "v1.2.3"
        
        # Should complete without error
        draw_version_footer(self.screen, 800, 600)
        
        # Version function should be called
        mock_get_version.assert_called_once()

    @patch('version.get_display_version')
    def test_version_header_with_mock_version(self, mock_get_version):
        """Test version header with mocked version."""
        mock_get_version.return_value = "v1.2.3"
        
        # Should complete without error
        draw_version_header(self.screen, 800, 600)
        
        # Version function should be called
        mock_get_version.assert_called_once()

    @patch('version.get_display_version', side_effect=ImportError)
    def test_version_fallback_on_import_error(self, mock_get_version):
        """Test fallback to 'dev' when version import fails."""
        # Should complete without error and fallback to 'dev'
        draw_version_footer(self.screen, 800, 600)

    def test_version_positioning_footer(self):
        """Test version positioning in different screen sizes."""
        # Test with small screen
        draw_version_footer(self.screen, 400, 300)
        
        # Test with large screen
        draw_version_footer(self.screen, 1600, 1200)
        
        # Should complete without error

    def test_version_positioning_header(self):
        """Test version positioning in header for different screen sizes."""
        # Test with small screen
        draw_version_header(self.screen, 400, 300)
        
        # Test with large screen
        draw_version_header(self.screen, 1600, 1200)
        
        # Should complete without error

    def test_version_with_custom_font(self):
        """Test version display with custom font."""
        custom_font = pygame.font.SysFont('Arial', 14)
        
        draw_version_footer(self.screen, 800, 600, custom_font)
        draw_version_header(self.screen, 800, 600, custom_font)
        
        # Should complete without error

    def test_version_responsive_sizing(self):
        """Test that version text scales with screen size."""
        # The functions should handle different screen sizes gracefully
        # and scale font size accordingly
        
        # Very small screen
        draw_version_footer(self.screen, 200, 150)
        
        # Very large screen
        draw_version_footer(self.screen, 2400, 1800)
        
        # Should complete without error


class TestVersionIntegration(unittest.TestCase):
    """Test version display integration with main UI."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        """Clean up pygame."""
        pygame.quit()

    def test_version_in_main_menu(self):
        """Test that version can be displayed in main menu context."""
        from ui import draw_main_menu
        
        # Mock sound manager
        sound_manager = MagicMock()
        sound_manager.is_enabled.return_value = True
        
        # Should complete without error (version is drawn within main menu)
        draw_main_menu(self.screen, 800, 600, 0, sound_manager)

    def test_version_in_game_ui(self):
        """Test that version can be displayed in game UI context."""
        from ui import draw_ui
        
        # Mock game state with proper attributes
        game_state = MagicMock()
        game_state.money = 1000
        game_state.staff = 5
        game_state.reputation = 50
        game_state.doom = 25
        game_state.max_doom = 100
        game_state.action_points = 3
        game_state.max_action_points = 3
        game_state.turn = 1
        game_state.game_over = False
        game_state.messages = []
        game_state.actions = []
        game_state.available_upgrades = []
        game_state.purchased_upgrades = []
        game_state.scrollable_event_log_enabled = False
        game_state.event_log_history = []
        game_state.ap_glow_timer = 0
        game_state.ui_transitions = []
        game_state.employee_blobs = []
        game_state.pending_popup_events = []
        
        # Additional required attributes for the UI
        game_state.compute = 0
        game_state.research_progress = 0
        game_state.opponents = []
        game_state.overlay_manager = MagicMock()
        game_state.overlay_manager.get_element_at_position.return_value = None
        
        # Fix for accounting software attributes
        game_state.accounting_software_bought = False
        game_state.last_balance_change = 0
        
        # Should complete without error (version is drawn within game UI)
        draw_ui(self.screen, game_state, 800, 600)


if __name__ == '__main__':
    unittest.main()