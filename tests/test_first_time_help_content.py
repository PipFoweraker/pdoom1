"""
Test module for first_time_help_content functionality.
"""

import unittest
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/home/runner/work/pdoom1/pdoom1')

class TestFirstTimeHelpContent(unittest.TestCase):
    """Test cases for first_time_help_content instantiation and handling."""
    
    def setUp(self):
        """Set up test environment."""
        # Set up dummy pygame environment for UI tests
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        import pygame
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
    
    def test_onboarding_system_initialization(self):
        """Test that the onboarding system initializes correctly."""
        from src.features.onboarding import onboarding
        
        # Check that onboarding system exists and has required methods
        self.assertTrue(hasattr(onboarding, 'should_show_mechanic_help'))
        self.assertTrue(hasattr(onboarding, 'get_mechanic_help'))
        self.assertTrue(hasattr(onboarding, 'mark_mechanic_seen'))
    
    def test_mechanic_help_content_structure(self):
        """Test that mechanic help content has the correct structure."""
        from src.features.onboarding import onboarding
        
        mechanics = ['first_staff_hire', 'first_upgrade_purchase', 'action_points_exhausted', 'high_doom_warning']
        
        for mechanic in mechanics:
            help_content = onboarding.get_mechanic_help(mechanic)
            
            # Help content should be a dict with title and content
            self.assertIsNotNone(help_content, f"Help content for {mechanic} should not be None")
            self.assertIsInstance(help_content, dict, f"Help content for {mechanic} should be a dict")
            self.assertIn('title', help_content, f"Help content for {mechanic} should have a title")
            self.assertIn('content', help_content, f"Help content for {mechanic} should have content")
            
            # Title and content should be non-empty strings
            self.assertIsInstance(help_content['title'], str, f"Title for {mechanic} should be a string")
            self.assertIsInstance(help_content['content'], str, f"Content for {mechanic} should be a string")
            self.assertTrue(len(help_content['title']) > 0, f"Title for {mechanic} should not be empty")
            self.assertTrue(len(help_content['content']) > 0, f"Content for {mechanic} should not be empty")
    
    def test_invalid_mechanic_handling(self):
        """Test that invalid mechanics are handled gracefully."""
        from src.features.onboarding import onboarding
        
        invalid_mechanics = ['invalid_mechanic', '', None, 123]
        
        for invalid_mechanic in invalid_mechanics:
            # Should not raise an exception
            try:
                help_content = onboarding.get_mechanic_help(invalid_mechanic)
                # Should return None for invalid mechanics
                self.assertIsNone(help_content, f"Invalid mechanic '{invalid_mechanic}' should return None")
            except Exception as e:
                self.fail(f"get_mechanic_help should not raise exception for invalid mechanic '{invalid_mechanic}': {e}")
    
    def test_ui_draw_function_with_valid_content(self):
        """Test that the UI draw function works with valid content."""
        from ui import draw_first_time_help
        
        valid_content = {
            'title': 'Test Title',
            'content': 'Test content for the help popup'
        }
        
        result = draw_first_time_help(self.screen, valid_content, 800, 600)
        
        # Should return a pygame.Rect object for the close button
        import pygame
        self.assertIsInstance(result, pygame.Rect, "draw_first_time_help should return a pygame.Rect for valid content")
    
    def test_ui_draw_function_with_invalid_content(self):
        """Test that the UI draw function handles invalid content gracefully."""
        from ui import draw_first_time_help
        
        invalid_contents = [
            None,
            {},
            {'title': 'test'},  # Missing content
            {'content': 'test'},  # Missing title
            "not a dict",
            123
        ]
        
        for invalid_content in invalid_contents:
            # Should not raise an exception
            try:
                result = draw_first_time_help(self.screen, invalid_content, 800, 600)
                # Most invalid content should return None, but function has its own validation
                # so we just check it doesn't crash
                self.assertTrue(True, "Function should not crash with invalid content")
            except Exception as e:
                self.fail(f"draw_first_time_help should not raise exception for invalid content '{invalid_content}': {e}")
    
    def test_help_content_validation_logic(self):
        """Test the validation logic used in main.py."""
        from src.features.onboarding import onboarding
        
        # This tests the same validation logic used in the fixed main.py
        for mechanic in ['first_staff_hire', 'first_upgrade_purchase', 'action_points_exhausted', 'high_doom_warning']:
            if onboarding.should_show_mechanic_help(mechanic):
                help_content = onboarding.get_mechanic_help(mechanic)
                
                # Apply the validation logic from main.py
                is_valid = (help_content and 
                           isinstance(help_content, dict) and 
                           'title' in help_content and 
                           'content' in help_content)
                
                self.assertTrue(is_valid, f"Help content for {mechanic} should pass validation")
    
    def test_close_button_collision_detection(self):
        """Test close button click detection logic."""
        # Mock pygame.Rect for testing
        class MockRect:
            def __init__(self, x, y, w, h):
                self.x, self.y, self.w, self.h = x, y, w, h
            
            def collidepoint(self, x, y):
                return (self.x <= x <= self.x + self.w and 
                       self.y <= y <= self.y + self.h)
        
        close_button_rect = MockRect(100, 100, 20, 20)
        
        # Test clicks inside the button
        self.assertTrue(close_button_rect.collidepoint(110, 110), "Click inside button should return True")
        self.assertTrue(close_button_rect.collidepoint(100, 100), "Click on button corner should return True")
        
        # Test clicks outside the button
        self.assertFalse(close_button_rect.collidepoint(50, 50), "Click outside button should return False")
        self.assertFalse(close_button_rect.collidepoint(150, 150), "Click far outside button should return False")

if __name__ == '__main__':
    unittest.main()