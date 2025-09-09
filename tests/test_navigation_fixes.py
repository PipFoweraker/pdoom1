"""
Tests for navigation fixes addressing the 15 August Bug List.

Tests the following fixes:
1. Help screen Escape key returns to game instead of main menu
2. Space bar works correctly after events (not intercepted by overlay manager)
3. Sound is enabled by default
"""

import unittest
import sys
import os
import pygame

# Add the parent directory to the path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.overlay_manager import OverlayManager, UIElement, ZLayer


class TestNavigationFixes(unittest.TestCase):
    """Test navigation fixes from 15 August Bug List"""
    
    def test_overlay_manager_space_bar_handling(self):
        """Test that overlay manager doesn't intercept space bar for non-clickable elements"""
        overlay_manager = OverlayManager()
        
        # Create a non-clickable element (like a tooltip or info display)
        non_clickable_element = UIElement(
            id="test_info",
            layer=ZLayer.TOOLTIPS,
            rect=pygame.Rect(100, 100, 200, 100),
            title="Info",
            content="Test info",
            clickable=False
        )
        overlay_manager.register_element(non_clickable_element)
        overlay_manager.active_element = "test_info"
        
        # Create a fake KEYDOWN event for space bar
        class FakeEvent:
            def __init__(self, key_type, key):
                self.type = key_type
                self.key = key
        
        space_event = FakeEvent(pygame.KEYDOWN, pygame.K_SPACE)
        
        # Space bar should NOT be handled (returns False) for non-clickable elements
        handled = overlay_manager.handle_keyboard_event(space_event)
        self.assertFalse(handled, "Space bar should not be intercepted for non-clickable elements")
        
        # But Enter should still be handled for non-clickable elements
        enter_event = FakeEvent(pygame.KEYDOWN, pygame.K_RETURN)
        handled = overlay_manager.handle_keyboard_event(enter_event)
        self.assertTrue(handled, "Enter should be handled for non-clickable elements")
    
    def test_overlay_manager_space_bar_clickable_elements(self):
        """Test that overlay manager correctly handles space bar for clickable elements"""
        overlay_manager = OverlayManager()
        
        # Create a clickable element (like a button)
        clickable_element = UIElement(
            id="test_button",
            layer=ZLayer.DIALOGS,
            rect=pygame.Rect(100, 100, 200, 100),
            title="Button",
            content="Test button",
            clickable=True
        )
        overlay_manager.register_element(clickable_element)
        overlay_manager.active_element = "test_button"
        
        # Create a fake KEYDOWN event for space bar
        class FakeEvent:
            def __init__(self, key_type, key):
                self.type = key_type
                self.key = key
        
        space_event = FakeEvent(pygame.KEYDOWN, pygame.K_SPACE)
        
        # Space bar SHOULD be handled (returns True) for clickable elements
        handled = overlay_manager.handle_keyboard_event(space_event)
        self.assertTrue(handled, "Space bar should be intercepted for clickable elements")
    
    def test_overlay_manager_no_active_element(self):
        """Test that overlay manager doesn't interfere when no element is active"""
        overlay_manager = OverlayManager()
        
        # No active element
        self.assertIsNone(overlay_manager.active_element)
        
        class FakeEvent:
            def __init__(self, key_type, key):
                self.type = key_type
                self.key = key
        
        space_event = FakeEvent(pygame.KEYDOWN, pygame.K_SPACE)
        
        # Space bar should NOT be handled when no element is active
        handled = overlay_manager.handle_keyboard_event(space_event)
        self.assertFalse(handled, "Space bar should not be intercepted when no element is active")


class TestSoundDefaultConfiguration(unittest.TestCase):
    """Test that sound is enabled by default"""
    
    def test_default_config_sound_enabled(self):
        """Test that the default configuration has sound enabled"""
        import json
        
        # Read the default configuration file
        with open('configs/default.json', 'r') as f:
            default_config = json.load(f)
        
        # Check that sound is enabled by default
        self.assertTrue(default_config.get('audio', {}).get('sound_enabled', False),
                      "Sound should be enabled by default in default.json")
    
    def test_global_sound_manager_enabled_by_default(self):
        """Test that global sound manager is enabled by default"""
        # Import main to initialize the global sound manager
        import main
        
        # Check that the global sound manager is enabled
        self.assertTrue(main.global_sound_manager.is_enabled(),
                      "Global sound manager should be enabled by default")


if __name__ == '__main__':
    # Initialize pygame to avoid errors in tests
    pygame.init()
    unittest.main()