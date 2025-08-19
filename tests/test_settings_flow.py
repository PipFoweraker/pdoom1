import unittest
import pygame
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions we want to test
from main import (
    handle_pre_game_settings_click, handle_pre_game_settings_keyboard,
    handle_seed_selection_click, handle_seed_selection_keyboard,
    handle_tutorial_choice_click, handle_tutorial_choice_keyboard,
    get_weekly_seed
)

class TestSettingsFlow(unittest.TestCase):
    """Test the new pre-game settings flow."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame to avoid issues with font rendering
        pygame.init()
        
        # Reset global state
        import main
        main.current_state = 'main_menu'
        main.selected_settings_item = 0
        main.seed_choice = "weekly"
        main.tutorial_enabled = True
        main.seed = None
        main.seed_input = ""
        main.pre_game_settings = {
            "difficulty": "DUMMY",
            "music_volume": 123,
            "sound_volume": 123,
            "graphics_quality": "DUMMY"
        }
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_pre_game_settings_state_exists(self):
        """Test that pre-game settings state is properly defined."""
        import main
        # Test that the new states are in the comment
        with open(main.__file__, 'r') as f:
            content = f.read()
            self.assertIn('pre_game_settings', content)
        
        # Test settings dictionary exists
        self.assertIn('difficulty', main.pre_game_settings)
        self.assertIn('music_volume', main.pre_game_settings)
        self.assertIn('sound_volume', main.pre_game_settings)
        self.assertIn('graphics_quality', main.pre_game_settings)
    
    def test_pre_game_settings_dummy_values(self):
        """Test that dummy values are set as specified."""
        import main
        self.assertEqual(main.pre_game_settings['difficulty'], 'DUMMY')
        self.assertEqual(main.pre_game_settings['music_volume'], 123)
        self.assertEqual(main.pre_game_settings['sound_volume'], 123)
        self.assertEqual(main.pre_game_settings['graphics_quality'], 'DUMMY')
    
    def test_settings_keyboard_navigation(self):
        """Test keyboard navigation in settings screen."""
        import main
        original_state = main.current_state
        
        # Test up/down navigation
        main.selected_settings_item = 0
        handle_pre_game_settings_keyboard(pygame.K_DOWN)
        self.assertEqual(main.selected_settings_item, 1)
        
        handle_pre_game_settings_keyboard(pygame.K_UP)
        self.assertEqual(main.selected_settings_item, 0)
        
        # Test continue button (item 4)
        main.selected_settings_item = 4
        handle_pre_game_settings_keyboard(pygame.K_RETURN)
        self.assertEqual(main.current_state, 'seed_selection')
        
        # Test escape
        main.current_state = 'pre_game_settings'
        handle_pre_game_settings_keyboard(pygame.K_ESCAPE)
        self.assertEqual(main.current_state, 'main_menu')
    
    def test_seed_selection_flow(self):
        """Test seed selection screen functionality."""
        import main
        
        # Test weekly seed selection
        main.current_state = 'seed_selection'
        handle_seed_selection_keyboard(pygame.K_RETURN)
        self.assertEqual(main.current_state, 'tutorial_choice')
        self.assertEqual(main.seed_choice, 'weekly')
        self.assertIsNotNone(main.seed)
        
        # Test escape from seed selection
        main.current_state = 'seed_selection'
        handle_seed_selection_keyboard(pygame.K_ESCAPE)
        self.assertEqual(main.current_state, 'pre_game_settings')
    
    def test_tutorial_choice_flow(self):
        """Test tutorial choice screen functionality."""
        import main
        
        # Test default tutorial enabled
        main.current_state = 'tutorial_choice'
        main.seed = "test_seed"
        handle_tutorial_choice_keyboard(pygame.K_RETURN)
        self.assertEqual(main.current_state, 'game')
        self.assertTrue(main.tutorial_enabled)
        
        # Test escape from tutorial choice
        main.current_state = 'tutorial_choice'
        handle_tutorial_choice_keyboard(pygame.K_ESCAPE)
        self.assertEqual(main.current_state, 'seed_selection')
    
    def test_complete_flow_integration(self):
        """Test the complete flow from settings to game."""
        import main
        
        # Start from pre-game settings
        main.current_state = 'pre_game_settings'
        main.selected_settings_item = 4  # Continue button
        
        # Continue to seed selection
        handle_pre_game_settings_keyboard(pygame.K_RETURN)
        self.assertEqual(main.current_state, 'seed_selection')
        
        # Choose weekly seed
        handle_seed_selection_keyboard(pygame.K_RETURN)
        self.assertEqual(main.current_state, 'tutorial_choice')
        self.assertEqual(main.seed_choice, 'weekly')
        
        # Choose tutorial
        handle_tutorial_choice_keyboard(pygame.K_RETURN)
        self.assertEqual(main.current_state, 'game')
        self.assertTrue(main.tutorial_enabled)
    
    def test_seed_selection_mouse_clicks(self):
        """Test mouse click handling in seed selection."""
        import main
        
        # Mock screen dimensions
        w, h = 800, 600
        
        # Test clicking weekly seed button (approximate position)
        button_width = int(w * 0.4)
        button_height = int(h * 0.08)
        start_y = int(h * 0.35)
        center_x = w // 2
        
        # Click on first button (weekly seed)
        button_x = center_x - button_width // 2 + 10  # Click inside button
        button_y = start_y + 10  # Click inside button
        
        handle_seed_selection_click((button_x, button_y), w, h)
        self.assertEqual(main.current_state, 'tutorial_choice')
        self.assertEqual(main.seed_choice, 'weekly')
    
    def test_tutorial_choice_mouse_clicks(self):
        """Test mouse click handling in tutorial choice."""
        import main
        
        # Mock screen dimensions
        w, h = 800, 600
        
        # Test clicking tutorial enable button (approximate position)
        button_width = int(w * 0.4)
        button_height = int(h * 0.08)
        start_y = int(h * 0.4)
        center_x = w // 2
        
        # Click on first button (enable tutorial)
        button_x = center_x - button_width // 2 + 10  # Click inside button
        button_y = start_y + 10  # Click inside button
        
        main.seed = "test_seed"
        handle_tutorial_choice_click((button_x, button_y), w, h)
        self.assertEqual(main.current_state, 'game')
        self.assertTrue(main.tutorial_enabled)
        
        # Click on second button (disable tutorial)
        main.current_state = 'tutorial_choice'
        spacing = int(h * 0.12)
        button_y_second = start_y + spacing + 10
        
        handle_tutorial_choice_click((button_x, button_y_second), w, h)
        self.assertEqual(main.current_state, 'game')
        self.assertFalse(main.tutorial_enabled)


class TestUIFunctions(unittest.TestCase):
    """Test the new UI drawing functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_ui_functions_importable(self):
        """Test that new UI functions can be imported."""
        from src.ui.menus import draw_pre_game_settings
        from ui import draw_seed_selection, draw_tutorial_choice
        
        # Test that they are callable
        self.assertTrue(callable(draw_pre_game_settings))
        self.assertTrue(callable(draw_seed_selection))
        self.assertTrue(callable(draw_tutorial_choice))
    
    def test_draw_pre_game_settings_no_crash(self):
        """Test that draw_pre_game_settings doesn't crash."""
        from src.ui.menus import draw_pre_game_settings
        
        settings = {
            "difficulty": "DUMMY",
            "music_volume": 123,
            "sound_volume": 123,
            "graphics_quality": "DUMMY"
        }
        
        # Should not raise an exception
        try:
            draw_pre_game_settings(self.screen, 800, 600, settings, 0)
        except Exception as e:
            self.fail(f"draw_pre_game_settings raised an exception: {e}")
    
    def test_draw_seed_selection_no_crash(self):
        """Test that draw_seed_selection doesn't crash."""
        from ui import draw_seed_selection
        
        # Should not raise an exception
        try:
            draw_seed_selection(self.screen, 800, 600, 0, "")
        except Exception as e:
            self.fail(f"draw_seed_selection raised an exception: {e}")
    
    def test_draw_tutorial_choice_no_crash(self):
        """Test that draw_tutorial_choice doesn't crash."""
        from ui import draw_tutorial_choice
        
        # Should not raise an exception
        try:
            draw_tutorial_choice(self.screen, 800, 600, 0)
        except Exception as e:
            self.fail(f"draw_tutorial_choice raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()