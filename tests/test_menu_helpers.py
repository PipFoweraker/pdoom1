'''
Test module for menu helper utilities.

Tests the new menu helper functions for collision detection,
navigation, and mouse wheel handling.
'''

import unittest
import pygame
from src.ui.menu_helpers import (
    get_menu_button_collision,
    handle_menu_navigation,
    handle_mouse_wheel_menu_navigation
)


class TestMenuHelpers(unittest.TestCase):
    '''Test cases for menu helper utilities.'''
    
    def setUp(self):
        '''Set up test environment.'''
        pygame.init()  # Initialize pygame for key constants
        self.menu_items = ['Launch Lab', 'Settings', 'Exit']
        self.screen_w = 800
        self.screen_h = 600
    
    def test_menu_button_collision_hit(self):
        '''Test menu button collision detection with valid hit.'''
        # Center of screen should hit first button with default ratios
        center_x = self.screen_w // 2
        first_button_y = int(self.screen_h * 0.35)  # start_y_ratio default
        
        result = get_menu_button_collision(
            (center_x, first_button_y + 20), 
            self.menu_items, 
            self.screen_w, 
            self.screen_h
        )
        
        self.assertEqual(result, 0, 'Should hit first menu button')
    
    def test_menu_button_collision_miss(self):
        '''Test menu button collision detection with no hit.'''
        # Far left should miss all buttons
        result = get_menu_button_collision(
            (10, 10), 
            self.menu_items, 
            self.screen_w, 
            self.screen_h
        )
        
        self.assertIsNone(result, 'Should not hit any menu button')
    
    def test_menu_button_collision_second_button(self):
        '''Test hitting second menu button.'''
        center_x = self.screen_w // 2
        spacing = int(self.screen_h * 0.1)  # spacing_ratio default
        first_button_y = int(self.screen_h * 0.35)
        second_button_y = first_button_y + spacing
        
        result = get_menu_button_collision(
            (center_x, second_button_y + 20), 
            self.menu_items, 
            self.screen_w, 
            self.screen_h
        )
        
        self.assertEqual(result, 1, 'Should hit second menu button')
    
    def test_menu_navigation_up(self):
        '''Test keyboard navigation moving up.'''
        result = handle_menu_navigation(
            pygame.K_UP, 
            1,  # current selection
            self.menu_items
        )
        
        self.assertEqual(result, 0, 'Should move selection up')
    
    def test_menu_navigation_down(self):
        '''Test keyboard navigation moving down.'''
        result = handle_menu_navigation(
            pygame.K_DOWN, 
            0,  # current selection
            self.menu_items
        )
        
        self.assertEqual(result, 1, 'Should move selection down')
    
    def test_menu_navigation_wrap_around(self):
        '''Test navigation wraps around at edges.'''
        # Test wrapping from first to last
        result = handle_menu_navigation(
            pygame.K_UP, 
            0,  # current selection (first item)
            self.menu_items
        )
        
        self.assertEqual(result, 2, 'Should wrap to last item')
        
        # Test wrapping from last to first
        result = handle_menu_navigation(
            pygame.K_DOWN, 
            2,  # current selection (last item)
            self.menu_items
        )
        
        self.assertEqual(result, 0, 'Should wrap to first item')
    
    def test_menu_navigation_left_right(self):
        '''Test left/right keys work same as up/down.'''
        # Left should work like up
        result = handle_menu_navigation(
            pygame.K_LEFT, 
            1,
            self.menu_items
        )
        
        self.assertEqual(result, 0, 'Left should work like up')
        
        # Right should work like down
        result = handle_menu_navigation(
            pygame.K_RIGHT, 
            0,
            self.menu_items
        )
        
        self.assertEqual(result, 1, 'Right should work like down')
    
    def test_menu_navigation_with_callback(self):
        '''Test navigation with selection callback.'''
        callback_called = False
        selected_item = None
        
        def test_callback(item):
            nonlocal callback_called, selected_item
            callback_called = True
            selected_item = item
        
        result = handle_menu_navigation(
            pygame.K_RETURN,
            1,  # current selection
            self.menu_items,
            on_select=test_callback
        )
        
        self.assertEqual(result, 1, 'Selection should not change')
        self.assertTrue(callback_called, 'Callback should be called')
        self.assertEqual(selected_item, 1, 'Correct item should be passed to callback')
    
    def test_mouse_wheel_navigation_up(self):
        '''Test mouse wheel up navigation.'''
        result = handle_mouse_wheel_menu_navigation(
            1,  # wheel up (positive Y)
            1,  # current selection
            self.menu_items
        )
        
        self.assertEqual(result, 0, 'Wheel up should move selection up')
    
    def test_mouse_wheel_navigation_down(self):
        '''Test mouse wheel down navigation.'''
        result = handle_mouse_wheel_menu_navigation(
            -1,  # wheel down (negative Y)
            0,   # current selection
            self.menu_items
        )
        
        self.assertEqual(result, 1, 'Wheel down should move selection down')
    
    def test_mouse_wheel_navigation_wrap(self):
        '''Test mouse wheel navigation wraps around.'''
        # Test wrap from first to last
        result = handle_mouse_wheel_menu_navigation(
            1,  # wheel up
            0,  # first item
            self.menu_items
        )
        
        self.assertEqual(result, 2, 'Should wrap to last item')
        
        # Test wrap from last to first
        result = handle_mouse_wheel_menu_navigation(
            -1,  # wheel down
            2,   # last item
            self.menu_items
        )
        
        self.assertEqual(result, 0, 'Should wrap to first item')
    
    def test_mouse_wheel_no_movement(self):
        '''Test mouse wheel with no movement.'''
        result = handle_mouse_wheel_menu_navigation(
            0,  # no wheel movement
            1,  # current selection
            self.menu_items
        )
        
        self.assertEqual(result, 1, 'Selection should not change with no wheel movement')
    
    def test_custom_button_dimensions(self):
        '''Test collision detection with custom button dimensions.'''
        # Test with smaller buttons
        result = get_menu_button_collision(
            (400, 300),  # center of screen
            self.menu_items,
            self.screen_w,
            self.screen_h,
            button_width_ratio=0.2,  # smaller width
            button_height_ratio=0.05,  # smaller height
            start_y_ratio=0.4,  # different start position
            spacing_ratio=0.08  # tighter spacing
        )
        
        # Should still detect collision with adjusted parameters
        self.assertIsNotNone(result, 'Should detect collision with custom dimensions')


if __name__ == '__main__':
    unittest.main()
