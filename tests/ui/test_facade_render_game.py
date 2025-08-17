"""
Tests for UIFacade render_game functionality

This module tests the UIFacade.render_game method to ensure it properly
coordinates rendering between ui.draw_ui and OverlayManager.render_elements
without behavioural changes from the original implementation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pygame
import unittest
from unittest.mock import Mock, patch, call
from game_state import GameState
from pdoom1.ui.facade import UIFacade


class TestUIFacadeRenderGame(unittest.TestCase):
    """Test UIFacade.render_game method functionality."""
    
    def setUp(self):
        """Set up test environment with headless pygame."""
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        self.screen = pygame.Surface((800, 600))
        self.game_state = GameState("test_seed")
        
    def tearDown(self):
        """Clean up pygame."""
        pygame.quit()
    
    def test_render_game_with_existing_overlay_manager(self):
        """Test render_game using existing overlay manager from game state."""
        # Create UI facade with game state's overlay manager
        ui_facade = UIFacade(self.game_state.overlay_manager)
        
        # Mock the draw_ui function and overlay manager render_elements
        with patch('ui.draw_ui') as mock_draw_ui:
            with patch.object(self.game_state.overlay_manager, 'render_elements') as mock_render:
                # Call render_game
                ui_facade.render_game(self.screen, self.game_state, 800, 600)
                
                # Verify draw_ui was called with correct parameters
                mock_draw_ui.assert_called_once_with(self.screen, self.game_state, 800, 600)
                
                # Verify overlay manager render_elements was called
                mock_render.assert_called_once_with(self.screen)
    
    def test_render_game_call_order(self):
        """Test that render_game calls draw_ui before render_elements."""
        ui_facade = UIFacade(self.game_state.overlay_manager)
        call_order = []
        
        def mock_draw_ui(*args):
            call_order.append('draw_ui')
            
        def mock_render(*args):
            call_order.append('render_elements')
        
        with patch('ui.draw_ui', side_effect=mock_draw_ui):
            with patch.object(self.game_state.overlay_manager, 'render_elements', side_effect=mock_render):
                ui_facade.render_game(self.screen, self.game_state, 800, 600)
                
                # Verify correct call order: draw_ui first, then render_elements
                self.assertEqual(call_order, ['draw_ui', 'render_elements'])
    
    def test_render_game_without_overlay_manager(self):
        """Test render_game when no overlay manager is provided."""
        # Create UI facade without overlay manager (uses internal one)
        ui_facade = UIFacade()
        
        with patch('ui.draw_ui') as mock_draw_ui:
            # The internal overlay manager should still work
            ui_facade.render_game(self.screen, self.game_state, 800, 600)
            
            # Verify draw_ui was called
            mock_draw_ui.assert_called_once_with(self.screen, self.game_state, 800, 600)
            
            # Note: We don't test the internal overlay manager render since it's not 
            # the main use case for this refactor
    
    def test_render_game_executes_without_error(self):
        """Test that render_game executes without error in headless environment."""
        ui_facade = UIFacade(self.game_state.overlay_manager)
        
        # This should not raise any exceptions
        try:
            ui_facade.render_game(self.screen, self.game_state, 800, 600)
        except Exception as e:
            self.fail(f"render_game raised an exception: {e}")
    
    def test_ui_facade_constructor_with_overlay_manager(self):
        """Test that UIFacade constructor accepts existing overlay manager."""
        overlay_manager = self.game_state.overlay_manager
        ui_facade = UIFacade(overlay_manager)
        
        # Verify the facade uses the provided overlay manager
        self.assertIs(ui_facade.overlay_manager, overlay_manager)
    
    def test_ui_facade_constructor_without_overlay_manager(self):
        """Test that UIFacade constructor creates internal overlay manager when none provided."""
        ui_facade = UIFacade()
        
        # Verify the facade has an overlay manager
        self.assertIsNotNone(ui_facade.overlay_manager)
        
        # Verify it's not the same as the game state's overlay manager
        self.assertIsNot(ui_facade.overlay_manager, self.game_state.overlay_manager)


if __name__ == '__main__':
    unittest.main()