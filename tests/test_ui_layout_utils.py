"""
Test module for UI layout utilities.

Tests the layout calculation functionality to ensure consistency
and correctness of UI positioning.
"""

import unittest
import pygame
from src.ui.layout_utils import (
    ButtonLayout, UILayoutManager, ResponsiveLayout,
    create_standard_menu_layout, create_back_button_layout
)


class TestUILayoutUtils(unittest.TestCase):
    """Test cases for UI layout utilities."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
    
    def test_button_layout_properties(self):
        """Test ButtonLayout data class properties."""
        button = ButtonLayout(100, 200, 300, 50)
        
        self.assertEqual(button.x, 100)
        self.assertEqual(button.y, 200)
        self.assertEqual(button.width, 300)
        self.assertEqual(button.height, 50)
        
        # Test computed properties
        self.assertEqual(button.center_x, 250)  # 100 + 300/2
        self.assertEqual(button.center_y, 225)  # 200 + 50/2
        
        # Test rect property
        rect = button.rect
        self.assertEqual(rect.x, 100)
        self.assertEqual(rect.y, 200)
        self.assertEqual(rect.width, 300)
        self.assertEqual(rect.height, 50)
    
    def test_menu_button_calculation(self):
        """Test standard menu button layout calculation."""
        w, h = 1200, 800
        num_buttons = 3
        
        buttons = UILayoutManager.calculate_menu_buttons(w, h, num_buttons, 'main_menu')
        
        self.assertEqual(len(buttons), 3)
        
        # Check first button positioning
        first_button = buttons[0]
        expected_width = int(w * 0.4)  # main_menu uses 0.4 ratio
        expected_height = int(h * 0.08)  # main_menu uses 0.08 ratio
        
        self.assertEqual(first_button.width, expected_width)
        self.assertEqual(first_button.height, expected_height)
        
        # Should be centered horizontally
        expected_x = w // 2 - expected_width // 2
        self.assertEqual(first_button.x, expected_x)
        
        # Check vertical spacing
        spacing = int(h * 0.1)  # main_menu uses 0.1 spacing
        self.assertEqual(buttons[1].y - buttons[0].y, spacing)
        self.assertEqual(buttons[2].y - buttons[1].y, spacing)
    
    def test_centered_button_calculation(self):
        """Test centered button calculation."""
        w, h = 1200, 800
        button = UILayoutManager.calculate_centered_button(w, h, 0.3, 0.06, 0.5)
        
        expected_width = int(w * 0.3)
        expected_height = int(h * 0.06)
        expected_x = w // 2 - expected_width // 2
        expected_y = int(h * 0.5)
        
        self.assertEqual(button.width, expected_width)
        self.assertEqual(button.height, expected_height)
        self.assertEqual(button.x, expected_x)
        self.assertEqual(button.y, expected_y)
    
    def test_button_click_detection(self):
        """Test button click detection."""
        buttons = [
            ButtonLayout(100, 100, 200, 50),  # Button 0
            ButtonLayout(100, 200, 200, 50),  # Button 1  
            ButtonLayout(100, 300, 200, 50),  # Button 2
        ]
        
        # Test click on first button
        clicked = UILayoutManager.find_clicked_button((150, 125), buttons)
        self.assertEqual(clicked, 0)
        
        # Test click on third button
        clicked = UILayoutManager.find_clicked_button((200, 320), buttons)
        self.assertEqual(clicked, 2)
        
        # Test click outside any button
        clicked = UILayoutManager.find_clicked_button((50, 50), buttons)
        self.assertEqual(clicked, -1)
        
        # Test click between buttons
        clicked = UILayoutManager.find_clicked_button((150, 175), buttons)
        self.assertEqual(clicked, -1)
    
    def test_different_layout_types(self):
        """Test different menu layout configurations."""
        w, h = 1200, 800
        
        # Test submenu layout (wider buttons)
        submenu_buttons = UILayoutManager.calculate_menu_buttons(w, h, 2, 'submenu')
        expected_width = int(w * 0.5)  # submenu uses 0.5 ratio
        self.assertEqual(submenu_buttons[0].width, expected_width)
        
        # Test compact layout (smaller buttons)
        compact_buttons = UILayoutManager.calculate_menu_buttons(w, h, 2, 'compact')
        expected_width = int(w * 0.3)  # compact uses 0.3 ratio
        self.assertEqual(compact_buttons[0].width, expected_width)
        
        # Test invalid layout name (should fallback to main_menu)
        fallback_buttons = UILayoutManager.calculate_menu_buttons(w, h, 2, 'nonexistent')
        expected_width = int(w * 0.4)  # main_menu uses 0.4 ratio
        self.assertEqual(fallback_buttons[0].width, expected_width)
    
    def test_responsive_layout(self):
        """Test responsive layout calculations."""
        # Test font scaling
        base_size = 20
        scaled_size = ResponsiveLayout.scale_font_size(base_size, 1600, 800)
        self.assertEqual(scaled_size, 40)  # Should double for 2x height
        
        # Test minimum font size
        tiny_size = ResponsiveLayout.scale_font_size(base_size, 200, 800)
        self.assertEqual(tiny_size, 12)  # Should not go below minimum
        
        # Test spacing calculations
        normal_spacing = ResponsiveLayout.get_responsive_spacing(800, 'normal')
        self.assertEqual(normal_spacing, 16)  # 800 * 0.02
        
        tight_spacing = ResponsiveLayout.get_responsive_spacing(800, 'tight')
        self.assertEqual(tight_spacing, 8)  # 800 * 0.01
        
        loose_spacing = ResponsiveLayout.get_responsive_spacing(800, 'loose')
        self.assertEqual(loose_spacing, 32)  # 800 * 0.04
    
    def test_convenience_functions(self):
        """Test convenience layout functions."""
        w, h = 1200, 800
        
        # Test standard menu layout
        menu_items = ['Start', 'Settings', 'Exit']
        buttons = create_standard_menu_layout(w, h, menu_items)
        self.assertEqual(len(buttons), 3)
        
        # Test back button layout
        back_button = create_back_button_layout(w, h)
        margin = UILayoutManager.get_safe_margin(w, h)
        self.assertEqual(back_button.x, margin)
        self.assertEqual(back_button.y, margin)
    
    def test_safe_margin_calculation(self):
        """Test safe margin calculation."""
        # Test with square screen
        margin = UILayoutManager.get_safe_margin(800, 800)
        self.assertEqual(margin, 16)  # 800 * 0.02
        
        # Test with rectangular screen (should use smaller dimension)
        margin = UILayoutManager.get_safe_margin(1200, 600)
        self.assertEqual(margin, 12)  # 600 * 0.02
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()


if __name__ == '__main__':
    unittest.main()
