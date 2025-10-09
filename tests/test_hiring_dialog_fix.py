# !/usr/bin/env python3
"""
Test specifically for issue #177: Verifying that hiring staff screen buttons are clickable.
"""
import unittest
import pygame
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.game_state import GameState
from ui import draw_hiring_dialog

class TestHiringDialogButtons(unittest.TestCase):
    """Test that hiring dialog buttons are clickable as described in issue #177."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800), pygame.HIDDEN)
        
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
        
    def test_hiring_buttons_clickable(self):
        """Test that 'generalist', 'researcher', 'engineer' etc buttons are clickable."""
        # Create game state with sufficient resources
        game_state = GameState('test-hire-buttons')
        game_state.money = 1000
        game_state.action_points = 10
        
        # Trigger hiring dialog
        game_state._trigger_hiring_dialog()
        self.assertIsNotNone(game_state.pending_hiring_dialog, "Hiring dialog should be active")
        
        # Generate UI rects (this is what happens during drawing)
        rects = draw_hiring_dialog(self.screen, game_state.pending_hiring_dialog, 1200, 800)
        
        # Verify we have clickable employee option rects
        employee_rects = [r for r in rects if r['type'] == 'employee_option']
        self.assertGreater(len(employee_rects), 0, "Should have clickable employee option buttons")
        
        # Get available employee types
        available_types = game_state.pending_hiring_dialog["available_subtypes"]
        type_names = [t["data"]["name"] for t in available_types]
        
        # Verify expected employee types are available and clickable
        self.assertIn("Generalist", type_names, "Generalist should be available for hiring")
        self.assertIn("Researcher", type_names, "Researcher should be available for hiring") 
        self.assertIn("Engineer", type_names, "Engineer should be available for hiring")
        
        # Test that each employee button has a valid clickable rect
        for employee_rect in employee_rects:
            self.assertIn('subtype_id', employee_rect, "Employee rect should have subtype_id")
            self.assertIsInstance(employee_rect['rect'], pygame.Rect, "Should have valid pygame Rect")
            self.assertGreater(employee_rect['rect'].width, 0, "Rect should have positive width")
            self.assertGreater(employee_rect['rect'].height, 0, "Rect should have positive height")
    
    def test_cancel_button_clickable(self):
        """Test that Cancel/Back button is functional."""
        # Create game state with hiring dialog
        game_state = GameState('test-cancel')
        game_state.money = 1000
        game_state.action_points = 10
        game_state._trigger_hiring_dialog()
        
        # Generate UI rects
        rects = draw_hiring_dialog(self.screen, game_state.pending_hiring_dialog, 1200, 800)
        
        # Verify cancel button exists and is clickable
        cancel_rects = [r for r in rects if r['type'] == 'cancel']
        self.assertEqual(len(cancel_rects), 1, "Should have exactly one cancel button")
        
        cancel_rect = cancel_rects[0]
        self.assertIsInstance(cancel_rect['rect'], pygame.Rect, "Cancel button should have valid rect")
        self.assertGreater(cancel_rect['rect'].width, 0, "Cancel rect should have positive width")
        self.assertGreater(cancel_rect['rect'].height, 0, "Cancel rect should have positive height")
    
    def test_employee_hiring_simulation(self):
        """Test full hiring flow to ensure buttons lead to successful actions."""
        # Create game state
        game_state = GameState('test-hire-flow')
        game_state.money = 1000
        game_state.action_points = 10
        initial_staff = game_state.staff
        
        # Trigger hiring dialog
        game_state._trigger_hiring_dialog()
        available_types = game_state.pending_hiring_dialog["available_subtypes"]
        
        # Find generalist employee (should always be available)
        generalist = None
        for subtype in available_types:
            if subtype["data"]["name"] == "Generalist":
                generalist = subtype
                break
        
        self.assertIsNotNone(generalist, "Generalist employee should be available")
        
        # Simulate clicking on generalist button
        success, message = game_state.select_employee_subtype(generalist["id"])
        
        # Verify hiring was successful
        self.assertTrue(success, f"Hiring should succeed: {message}")
        self.assertGreater(game_state.staff, initial_staff, "Staff count should increase")
        self.assertIsNone(game_state.pending_hiring_dialog, "Dialog should be dismissed after hiring")
    
    def test_escape_key_functionality(self):
        """Test that ESC key can dismiss hiring dialog."""
        # Create game state with hiring dialog
        game_state = GameState('test-escape')
        game_state.money = 1000
        game_state.action_points = 10
        game_state._trigger_hiring_dialog()
        
        self.assertIsNotNone(game_state.pending_hiring_dialog, "Dialog should be active")
        
        # Simulate ESC key dismissal
        game_state.dismiss_hiring_dialog()
        
        self.assertIsNone(game_state.pending_hiring_dialog, "Dialog should be dismissed by ESC")

if __name__ == '__main__':
    unittest.main()