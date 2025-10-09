# !/usr/bin/env python3
"""
Integration test for the modal dialog click blocking fix.

This test simulates the actual click handling logic from main.py to verify 
that the fix prevents click fall-through while preserving normal dialog functionality.
"""
import unittest
import pygame
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game_state import GameState
from ui import draw_hiring_dialog


def simulate_main_click_handling(game_state, mouse_x, mouse_y, screen_w, screen_h, cached_hiring_dialog_rects):
    """
    Simulate the click handling logic from main.py to test the fix.
    Returns True if click was processed, False if blocked.
    """
    if game_state and game_state.pending_hiring_dialog and cached_hiring_dialog_rects is not None:
        hiring_handled = False
        for rect_info in cached_hiring_dialog_rects:
            if rect_info['rect'].collidepoint(mouse_x, mouse_y):
                if rect_info['type'] == 'employee_option':
                    # Player selected an employee subtype
                    game_state.select_employee_subtype(rect_info['subtype_id'])
                    hiring_handled = True
                    break
                elif rect_info['type'] == 'cancel':
                    # Player cancelled the hiring dialog
                    game_state.dismiss_hiring_dialog()
                    hiring_handled = True
                    break
        
        if hiring_handled:
            return True  # Hiring dialog handled the click
        else:
            # When hiring dialog is open, check if click is inside dialog area
            # Calculate dialog rect (same as in ui.py draw_hiring_dialog)
            dialog_width = int(screen_w * 0.8)
            dialog_height = int(screen_h * 0.85)
            dialog_x = (screen_w - dialog_width) // 2
            dialog_y = (screen_h - dialog_height) // 2
            dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
            
            if dialog_rect.collidepoint(mouse_x, mouse_y):
                # Click is inside dialog area but not on a button - do nothing (modal behavior)
                return False  # Click blocked
            # Click is outside dialog area - block it (modal behavior)
            # Don't pass to regular game handling to prevent clicking through dialog
            return False  # Click blocked
    else:
        # Regular game mouse handling would happen here
        return True  # Click would be processed normally


class TestModalDialogClickBlocking(unittest.TestCase):
    """Integration test for the modal dialog click blocking fix."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800), pygame.HIDDEN)
        
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_hiring_dialog_blocks_clicks_outside_dialog(self):
        """Test that clicks outside the hiring dialog are blocked."""
        # Create game state with hiring dialog
        game_state = GameState('test-modal-blocking')
        game_state.money = 1000
        game_state.action_points = 10
        initial_turn = game_state.turn
        
        # Trigger hiring dialog
        game_state._trigger_hiring_dialog()
        self.assertIsNotNone(game_state.pending_hiring_dialog)
        
        # Draw the dialog to get clickable rects
        screen_w, screen_h = 1200, 800
        cached_hiring_dialog_rects = draw_hiring_dialog(
            self.screen, game_state.pending_hiring_dialog, screen_w, screen_h
        )
        
        # Test click outside dialog area (top-left corner)
        outside_click_x, outside_click_y = 10, 10
        click_processed = simulate_main_click_handling(
            game_state, outside_click_x, outside_click_y, screen_w, screen_h, cached_hiring_dialog_rects
        )
        
        # Click should be blocked
        self.assertFalse(click_processed, "Click outside dialog should be blocked")
        
        # Dialog should still be open
        self.assertIsNotNone(game_state.pending_hiring_dialog, "Dialog should remain open")
        
        # Turn should not have advanced
        self.assertEqual(game_state.turn, initial_turn, "Turn should not advance when click is blocked")
    
    def test_hiring_dialog_allows_clicks_on_dialog_buttons(self):
        """Test that clicks on dialog buttons still work."""
        # Create game state with hiring dialog
        game_state = GameState('test-modal-buttons')
        game_state.money = 1000
        game_state.action_points = 10
        
        # Trigger hiring dialog
        game_state._trigger_hiring_dialog()
        self.assertIsNotNone(game_state.pending_hiring_dialog)
        
        # Draw the dialog to get clickable rects
        screen_w, screen_h = 1200, 800
        cached_hiring_dialog_rects = draw_hiring_dialog(
            self.screen, game_state.pending_hiring_dialog, screen_w, screen_h
        )
        
        # Find cancel button
        cancel_rect = None
        for rect_info in cached_hiring_dialog_rects:
            if rect_info['type'] == 'cancel':
                cancel_rect = rect_info['rect']
                break
        
        self.assertIsNotNone(cancel_rect, "Cancel button should be available")
        
        # Click on cancel button
        cancel_click_x = cancel_rect.centerx
        cancel_click_y = cancel_rect.centery
        
        click_processed = simulate_main_click_handling(
            game_state, cancel_click_x, cancel_click_y, screen_w, screen_h, cached_hiring_dialog_rects
        )
        
        # Click should be processed
        self.assertTrue(click_processed, "Click on cancel button should be processed")
        
        # Dialog should be dismissed
        self.assertIsNone(game_state.pending_hiring_dialog, "Dialog should be dismissed after cancel")
    
    def test_hiring_dialog_blocks_clicks_inside_dialog_but_not_on_buttons(self):
        """Test that clicks inside dialog area but not on buttons are blocked."""
        # Create game state with hiring dialog
        game_state = GameState('test-modal-inside')
        game_state.money = 1000
        game_state.action_points = 10
        
        # Trigger hiring dialog
        game_state._trigger_hiring_dialog()
        self.assertIsNotNone(game_state.pending_hiring_dialog)
        
        # Draw the dialog to get clickable rects
        screen_w, screen_h = 1200, 800
        cached_hiring_dialog_rects = draw_hiring_dialog(
            self.screen, game_state.pending_hiring_dialog, screen_w, screen_h
        )
        
        # Calculate dialog area
        dialog_width = int(screen_w * 0.8)
        dialog_height = int(screen_h * 0.85)
        dialog_x = (screen_w - dialog_width) // 2
        dialog_y = (screen_h - dialog_height) // 2
        
        # Click inside dialog but not on any button (top area of dialog)
        inside_click_x = dialog_x + dialog_width // 2
        inside_click_y = dialog_y + 50  # Near top of dialog
        
        # Verify this click is inside dialog but not on any button
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        self.assertTrue(dialog_rect.collidepoint(inside_click_x, inside_click_y), 
                       "Click should be inside dialog area")
        
        # Verify click is not on any button
        on_button = False
        for rect_info in cached_hiring_dialog_rects:
            if rect_info['rect'].collidepoint(inside_click_x, inside_click_y):
                on_button = True
                break
        self.assertFalse(on_button, "Click should not be on any button")
        
        # Test the click
        click_processed = simulate_main_click_handling(
            game_state, inside_click_x, inside_click_y, screen_w, screen_h, cached_hiring_dialog_rects
        )
        
        # Click should be blocked (proper modal behavior)
        self.assertFalse(click_processed, "Click inside dialog but not on button should be blocked")
        
        # Dialog should remain open
        self.assertIsNotNone(game_state.pending_hiring_dialog, "Dialog should remain open")
    
    def test_normal_click_handling_when_no_dialog(self):
        """Test that normal clicking works when no dialog is open."""
        # Create game state without dialog
        game_state = GameState('test-normal-clicks')
        game_state.money = 1000
        game_state.action_points = 10
        
        # No dialog is open
        self.assertIsNone(game_state.pending_hiring_dialog)
        
        # Test click anywhere
        screen_w, screen_h = 1200, 800
        click_x, click_y = 400, 400
        
        click_processed = simulate_main_click_handling(
            game_state, click_x, click_y, screen_w, screen_h, None
        )
        
        # Click should be processed normally
        self.assertTrue(click_processed, "Click should be processed when no dialog is open")


if __name__ == '__main__':
    unittest.main()