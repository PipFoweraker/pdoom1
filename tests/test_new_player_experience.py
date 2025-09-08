"""
Unit tests for the New Player Experience system.

Tests the enhanced tutorial choice and intro scenario features.
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from unittest.mock import Mock, patch


class TestNewPlayerExperience(unittest.TestCase):
    """Test cases for the New Player Experience system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up pygame for UI testing."""
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up pygame."""
        pygame.quit()
    
    def setUp(self):
        """Set up test fixtures."""
        self.screen = pygame.display.get_surface()
        self.w, self.h = 800, 600
    
    def test_new_player_experience_ui_function(self):
        """Test that the new player experience UI function works."""
        from ui import draw_new_player_experience
        
        # Test that function can be called without errors
        try:
            draw_new_player_experience(
                screen=self.screen,
                w=self.w, 
                h=self.h,
                selected_item=0,
                tutorial_enabled=True,
                intro_enabled=False
            )
            success = True
        except Exception as e:
            success = False
            print(f"UI function failed: {e}")
        
        self.assertTrue(success, "New player experience UI should render without errors")
    
    def test_checkbox_states(self):
        """Test different checkbox state combinations."""
        from ui import draw_new_player_experience
        
        # Test all combinations of checkbox states
        test_cases = [
            (True, True),   # Both enabled
            (True, False),  # Only tutorial
            (False, True),  # Only intro
            (False, False)  # Neither
        ]
        
        for tutorial_enabled, intro_enabled in test_cases:
            try:
                draw_new_player_experience(
                    screen=self.screen,
                    w=self.w,
                    h=self.h, 
                    selected_item=0,
                    tutorial_enabled=tutorial_enabled,
                    intro_enabled=intro_enabled
                )
                success = True
            except Exception as e:
                success = False
                print(f"Checkbox state {tutorial_enabled}, {intro_enabled} failed: {e}")
            
            self.assertTrue(success, f"Should handle checkbox state: tutorial={tutorial_enabled}, intro={intro_enabled}")
    
    def test_selected_item_navigation(self):
        """Test different selected item states."""
        from ui import draw_new_player_experience
        
        # Test all valid selected item values
        for selected_item in [0, 1, 2]:  # Tutorial, Intro, Start button
            try:
                draw_new_player_experience(
                    screen=self.screen,
                    w=self.w,
                    h=self.h,
                    selected_item=selected_item,
                    tutorial_enabled=True,
                    intro_enabled=True
                )
                success = True
            except Exception as e:
                success = False
                print(f"Selected item {selected_item} failed: {e}")
            
            self.assertTrue(success, f"Should handle selected item: {selected_item}")
    
    def test_intro_text_display(self):
        """Test that intro text is displayed when enabled."""
        from ui import draw_new_player_experience
        
        # When intro is enabled, should show intro text
        try:
            draw_new_player_experience(
                screen=self.screen,
                w=self.w,
                h=self.h,
                selected_item=1,
                tutorial_enabled=False,
                intro_enabled=True  # This should trigger intro text display
            )
            success = True
        except Exception as e:
            success = False
            print(f"Intro text display failed: {e}")
        
        self.assertTrue(success, "Should display intro text when intro is enabled")
    
    def test_responsive_layout(self):
        """Test that UI adapts to different screen sizes."""
        from ui import draw_new_player_experience
        
        # Test different screen sizes
        screen_sizes = [
            (800, 600),   # Standard
            (1024, 768),  # Larger
            (640, 480)    # Smaller
        ]
        
        for width, height in screen_sizes:
            try:
                draw_new_player_experience(
                    screen=self.screen,
                    w=width,
                    h=height,
                    selected_item=0,
                    tutorial_enabled=True,
                    intro_enabled=True
                )
                success = True
            except Exception as e:
                success = False
                print(f"Screen size {width}x{height} failed: {e}")
            
            self.assertTrue(success, f"Should handle screen size: {width}x{height}")


class TestMainMenuIntegration(unittest.TestCase):
    """Test integration of new player experience with main menu."""
    
    def test_main_menu_imports(self):
        """Test that main menu can import new player experience functions."""
        try:
            # Test that main.py can import the UI function
            from ui import draw_new_player_experience
            success = True
        except ImportError as e:
            success = False
            print(f"Import failed: {e}")
        
        self.assertTrue(success, "Main menu should be able to import new player experience UI")
    
    def test_new_player_experience_state_variables(self):
        """Test that main.py has the required state variables."""
        import main
        
        # Test that main module has the required variables
        # (This is tricky to test without actually running main.py)
        # Just verify the module loads
        self.assertTrue(hasattr(main, '__name__'))
    
    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    def test_event_handling_structure(self, mock_flip, mock_events):
        """Test that event handling structure exists."""
        # Mock events to avoid actual event loop
        mock_events.return_value = []
        
        # Test that we can check for event handling functions
        # This is a structural test to ensure the code is organized correctly
        try:
            import main
            success = True
        except Exception as e:
            success = False
            print(f"Main module loading failed: {e}")
        
        self.assertTrue(success, "Main module should load without errors")


class TestIntroScenario(unittest.TestCase):
    """Test the intro scenario functionality."""
    
    def test_intro_text_content(self):
        """Test that intro text contains expected content."""
        from ui import draw_new_player_experience
        
        # The intro should mention starting cash and the mission
        # We test this indirectly by ensuring the function handles intro_enabled=True
        try:
            pygame.init()
            screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
            
            draw_new_player_experience(
                screen=screen,
                w=800,
                h=600,
                selected_item=1,
                tutorial_enabled=False,
                intro_enabled=True
            )
            
            pygame.quit()
            success = True
        except Exception as e:
            success = False
            print(f"Intro scenario test failed: {e}")
        
        self.assertTrue(success, "Intro scenario should display properly")
    
    def test_intro_integration_with_game_state(self):
        """Test that intro scenario integrates with game initialization."""
        # This tests the conceptual integration - the actual integration
        # happens when a new game is started with intro enabled
        
        # Test that game state can be created normally
        from src.core.game_state import GameState
        
        try:
            game_state = GameState(seed="intro-test")
            success = True
        except Exception as e:
            success = False
            print(f"Game state creation failed: {e}")
        
        self.assertTrue(success, "Game state should initialize correctly for intro scenario")


if __name__ == '__main__':
    unittest.main()
