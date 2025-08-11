"""
Test tutorial choice menu improvements for keyboard and mouse navigation.

Covers:
- Keyboard navigation (arrow keys, enter/space)  
- Mouse hover selection
- Selection state tracking
- Visual feedback integration
"""

import pytest
import pygame
import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from ui import draw_tutorial_choice
from visual_feedback import ButtonState


class TestTutorialChoiceNavigation:
    """Test keyboard and mouse navigation for tutorial choice screen."""
    
    def setup_method(self):
        """Set up test environment."""
        # Initialize pygame for UI testing
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
        
        # Reset tutorial choice state
        main.tutorial_choice_selected_item = 0
        main.current_state = 'tutorial_choice'
        main.tutorial_enabled = False
        main.seed = 12345
    
    def test_initial_selection_state(self):
        """Test that tutorial choice starts with first item selected."""
        assert main.tutorial_choice_selected_item == 0
    
    def test_keyboard_down_navigation(self):
        """Test down arrow key navigation."""
        # Start at 0, should go to 1
        main.handle_tutorial_choice_keyboard(pygame.K_DOWN)
        assert main.tutorial_choice_selected_item == 1
        
        # At 1, should wrap to 0
        main.handle_tutorial_choice_keyboard(pygame.K_DOWN)
        assert main.tutorial_choice_selected_item == 0
    
    def test_keyboard_up_navigation(self):
        """Test up arrow key navigation."""
        # Start at 0, should wrap to 1
        main.handle_tutorial_choice_keyboard(pygame.K_UP)
        assert main.tutorial_choice_selected_item == 1
        
        # At 1, should go to 0
        main.handle_tutorial_choice_keyboard(pygame.K_UP)
        assert main.tutorial_choice_selected_item == 0
    
    def test_keyboard_left_right_navigation(self):
        """Test left/right arrow key navigation."""
        # Test right arrow
        main.handle_tutorial_choice_keyboard(pygame.K_RIGHT)
        assert main.tutorial_choice_selected_item == 1
        
        # Test left arrow
        main.handle_tutorial_choice_keyboard(pygame.K_LEFT)
        assert main.tutorial_choice_selected_item == 0
    
    def test_keyboard_enter_selection(self):
        """Test Enter key selection."""
        # Test selecting Yes (tutorial enabled)
        main.tutorial_choice_selected_item = 0
        main.handle_tutorial_choice_keyboard(pygame.K_RETURN)
        assert main.tutorial_enabled == True
        assert main.current_state == 'game'
    
    def test_keyboard_space_selection(self):
        """Test Space key selection."""
        # Reset state
        main.current_state = 'tutorial_choice'
        main.tutorial_enabled = False
        
        # Test selecting No (tutorial disabled)
        main.tutorial_choice_selected_item = 1
        main.handle_tutorial_choice_keyboard(pygame.K_SPACE)
        assert main.tutorial_enabled == False
        assert main.current_state == 'game'
    
    def test_keyboard_escape_navigation(self):
        """Test Escape key returns to seed selection."""
        main.handle_tutorial_choice_keyboard(pygame.K_ESCAPE)
        assert main.current_state == 'seed_selection'
    
    def test_mouse_hover_detection(self):
        """Test mouse hover updates selection."""
        w, h = 800, 600
        
        # Calculate button positions (matching main layout)
        button_width = int(w * 0.4)
        button_height = int(h * 0.08)
        start_y = int(h * 0.4)
        spacing = int(h * 0.12)
        center_x = w // 2
        
        # Test hovering over first button (Yes)
        button_x = center_x - button_width // 2
        button_y = start_y
        mouse_pos = (button_x + 10, button_y + 10)  # Inside first button
        
        main.handle_tutorial_choice_hover(mouse_pos, w, h)
        assert main.tutorial_choice_selected_item == 0
        
        # Test hovering over second button (No)
        button_y = start_y + spacing
        mouse_pos = (button_x + 10, button_y + 10)  # Inside second button
        
        main.handle_tutorial_choice_hover(mouse_pos, w, h)
        assert main.tutorial_choice_selected_item == 1
    
    def test_mouse_click_selection(self):
        """Test mouse click selection and state changes."""
        w, h = 800, 600
        
        # Calculate button positions
        button_width = int(w * 0.4)
        button_height = int(h * 0.08)
        start_y = int(h * 0.4)
        spacing = int(h * 0.12)
        center_x = w // 2
        button_x = center_x - button_width // 2
        
        # Test clicking Yes button
        button_y = start_y
        mouse_pos = (button_x + 10, button_y + 10)
        
        main.handle_tutorial_choice_click(mouse_pos, w, h)
        assert main.tutorial_choice_selected_item == 0
        assert main.tutorial_enabled == True
        assert main.current_state == 'game'
        
        # Reset for No button test
        main.current_state = 'tutorial_choice'
        main.tutorial_enabled = False
        
        # Test clicking No button
        button_y = start_y + spacing
        mouse_pos = (button_x + 10, button_y + 10)
        
        main.handle_tutorial_choice_click(mouse_pos, w, h)
        assert main.tutorial_choice_selected_item == 1
        assert main.tutorial_enabled == False
        assert main.current_state == 'game'
    
    def test_draw_function_respects_selection(self):
        """Test that draw function uses the selected item for visual feedback."""
        # This test ensures the draw function doesn't crash with selection
        screen = pygame.display.get_surface()
        w, h = 800, 600
        
        # Test with different selections
        for selected_item in [0, 1]:
            main.tutorial_choice_selected_item = selected_item
            try:
                draw_tutorial_choice(screen, w, h, selected_item)
                # If we get here without exception, the draw function works
                assert True
            except Exception as e:
                pytest.fail(f"Draw function failed with selection {selected_item}: {e}")


class TestTutorialChoiceIntegration:
    """Test integration with existing systems."""
    
    def setup_method(self):
        """Set up test environment."""
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
        main.tutorial_choice_selected_item = 0
    
    def test_selection_preserved_across_navigation(self):
        """Test that selection state is preserved when navigating away and back."""
        # Set selection to second item
        main.tutorial_choice_selected_item = 1
        original_selection = main.tutorial_choice_selected_item
        
        # Navigate away to seed selection
        main.current_state = 'seed_selection'
        
        # Navigate back to tutorial choice
        main.current_state = 'tutorial_choice'
        
        # Selection should be preserved
        assert main.tutorial_choice_selected_item == original_selection
    
    def test_keyboard_mouse_consistency(self):
        """Test that keyboard and mouse navigation produce consistent results."""
        w, h = 800, 600
        
        # Use keyboard to select second item
        main.tutorial_choice_selected_item = 0
        main.handle_tutorial_choice_keyboard(pygame.K_DOWN)
        keyboard_selection = main.tutorial_choice_selected_item
        
        # Reset and use mouse to select same item
        main.tutorial_choice_selected_item = 0
        
        # Calculate second button position
        button_width = int(w * 0.4)
        start_y = int(h * 0.4)
        spacing = int(h * 0.12)
        center_x = w // 2
        button_x = center_x - button_width // 2
        button_y = start_y + spacing
        mouse_pos = (button_x + 10, button_y + 10)
        
        main.handle_tutorial_choice_hover(mouse_pos, w, h)
        mouse_selection = main.tutorial_choice_selected_item
        
        # Should be consistent
        assert keyboard_selection == mouse_selection == 1