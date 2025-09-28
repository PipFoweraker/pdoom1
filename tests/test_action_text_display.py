"""
Test for Action List Text Display Issues (#315, #257)

Verifies that text rendering improvements fix the reported issues:
1. Text overflow in small button rects
2. Inconsistent font sizing
3. Long action names properly truncated
4. Good readability in both modes

Run with: python -m pytest tests/test_action_text_display.py -v
"""

import unittest
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from src.ui.text_utils import get_optimal_action_text, truncate_text_for_rect, get_optimal_compact_text
from src.core.game_state import GameState
import ui


class TestActionTextDisplay(unittest.TestCase):
    
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        self.font = pygame.font.SysFont('Consolas', 16)
        
    def test_text_truncation(self):
        """Test that long text is properly truncated with ellipsis"""
        long_text = "This is a very long action name that should definitely be truncated"
        truncated = truncate_text_for_rect(long_text, self.font, 100)
        
        # Should be truncated and end with ellipsis
        self.assertTrue(len(truncated) < len(long_text))
        self.assertTrue(truncated.endswith("..."))
        
        # Truncated text should fit in the specified width
        text_width = self.font.size(truncated)[0]
        self.assertLessEqual(text_width, 100)
        
    def test_optimal_action_text_short_name(self):
        """Test optimal text for action with short name"""
        action = {"name": "Buy"}
        text, font_size = get_optimal_action_text(action, 0, 200)
        
        # Short name should include shortcut key
        self.assertIn("[", text)
        self.assertIn("]", text) 
        self.assertIn("Buy", text)
        
    def test_optimal_action_text_long_name(self):
        """Test optimal text for action with very long name"""
        action = {"name": "Conduct Comprehensive Research Into Advanced AI Safety"}
        text, font_size = get_optimal_action_text(action, 5, 150)  # Small width
        
        # Long name should be truncated
        self.assertTrue(len(text) < len(action["name"]))
        
        # Should fit in specified width
        font = pygame.font.SysFont('Consolas', font_size, bold=True)
        text_width = font.size(text)[0]
        self.assertLessEqual(text_width, 150 - 10)  # Account for margin
        
    def test_optimal_action_text_no_shortcut(self):
        """Test optimal text for action without shortcut (index >= 9)"""
        action = {"name": "Advanced Action"}
        text, font_size = get_optimal_action_text(action, 10, 200)  # Index 10, no shortcut
        
        # Should not include bracket notation for shortcut
        self.assertNotIn("[", text)
        self.assertNotIn("]", text)
        
    def test_compact_text_parameters(self):
        """Test compact UI text parameters are reasonable"""
        action = {"name": "Test Action"}
        params = get_optimal_compact_text(action, 0, 60, 30)  # Small button
        
        # Icon and key sizes should be reasonable for small button
        self.assertGreaterEqual(params['icon_size'], 12)
        self.assertLessEqual(params['icon_size'], 30)
        self.assertGreaterEqual(params['key_size'], 8)
        self.assertLessEqual(params['key_size'], 15)
        
    def test_ui_renders_without_crash(self):
        """Test that UI renders without crashing with text fixes"""
        game_state = GameState('test-text-display')
        
        # Test tutorial mode
        game_state.tutorial_enabled = True
        try:
            ui.draw_ui(self.screen, game_state, 1200, 800)
            tutorial_success = True
        except Exception:
            tutorial_success = False
            
        # Test compact mode  
        game_state.tutorial_enabled = False
        try:
            ui.draw_ui(self.screen, game_state, 1200, 800)
            compact_success = True
        except Exception:
            compact_success = False
            
        self.assertTrue(tutorial_success, "Tutorial mode should render without crashing")
        self.assertTrue(compact_success, "Compact mode should render without crashing")
        
    def test_text_fits_in_small_buttons(self):
        """Test that text properly handles very small button sizes"""
        action = {"name": "Research"}
        
        # Very small width - should still produce valid text
        text, font_size = get_optimal_action_text(action, 0, 50)
        self.assertIsNotNone(text)
        self.assertGreater(len(text), 0)
        self.assertGreaterEqual(font_size, 10)  # Should not go below minimum
        
    def test_visual_feedback_text_handling(self):
        """Test that visual feedback system handles text overflow"""
        from src.features.visual_feedback import visual_feedback, ButtonState, FeedbackStyle
        
        rect = pygame.Rect(10, 10, 100, 30)  # Small button
        long_text = "Very Long Button Text That Should Be Handled Properly"
        
        # Should not crash with long text
        try:
            visual_feedback.draw_button(self.screen, rect, long_text, ButtonState.NORMAL, FeedbackStyle.BUTTON)
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success, "Visual feedback should handle long text without crashing")


if __name__ == '__main__':
    unittest.main()