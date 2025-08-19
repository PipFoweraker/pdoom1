"""
Tests for window management functionality.

This module tests the enhanced OverlayManager with drag, layering, and minimize features.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import unittest
from unittest.mock import patch, MagicMock
from src.ui.overlay_manager import OverlayManager, UIElement, ZLayer, UIState
from ui_new.components.windows import draw_window_with_header


class TestWindowManagement(unittest.TestCase):
    """Test window management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.window_manager = OverlayManager()

    def tearDown(self):
        """Clean up pygame."""
        pygame.quit()

    def test_window_manager_initialization(self):
        """Test window manager initializes correctly."""
        self.assertEqual(len(self.window_manager.elements), 0)
        self.assertIsNone(self.window_manager.dragging_element)
        self.assertEqual(self.window_manager.last_mouse_pos, (0, 0))

    def test_register_draggable_element(self):
        """Test registering a draggable UI element."""
        element = UIElement(
            id="test_window",
            layer=ZLayer.DIALOGS,
            rect=pygame.Rect(100, 100, 200, 150),
            title="Test Window",
            draggable=True
        )
        
        result = self.window_manager.register_element(element)
        self.assertTrue(result)
        self.assertIn("test_window", self.window_manager.elements)
        self.assertTrue(self.window_manager.elements["test_window"].draggable)

    def test_drag_functionality(self):
        """Test window dragging functionality."""
        element = UIElement(
            id="drag_test",
            layer=ZLayer.DIALOGS,
            rect=pygame.Rect(100, 100, 200, 150),
            title="Drag Test",
            draggable=True
        )
        element.header_rect = pygame.Rect(100, 100, 200, 30)  # Header area
        
        self.window_manager.register_element(element)
        
        # Test starting drag
        result = self.window_manager._start_drag("drag_test", (150, 115))
        self.assertTrue(result)
        self.assertEqual(self.window_manager.dragging_element, "drag_test")
        self.assertTrue(element.being_dragged)

    def test_drag_motion(self):
        """Test drag motion updates element position."""
        element = UIElement(
            id="motion_test",
            layer=ZLayer.DIALOGS,
            rect=pygame.Rect(100, 100, 200, 150),
            title="Motion Test",
            draggable=True
        )
        
        self.window_manager.register_element(element)
        self.window_manager._start_drag("motion_test", (150, 115))
        self.window_manager.last_mouse_pos = (150, 115)
        
        # Simulate drag motion
        original_x = element.rect.x
        original_y = element.rect.y
        
        self.window_manager._handle_drag_motion((170, 135))
        
        # Element should have moved
        self.assertEqual(element.rect.x, original_x + 20)
        self.assertEqual(element.rect.y, original_y + 20)

    def test_minimize_functionality(self):
        """Test window minimization."""
        element = UIElement(
            id="minimize_test",
            layer=ZLayer.DIALOGS,
            rect=pygame.Rect(100, 100, 200, 150),
            title="Minimize Test"
        )
        
        self.window_manager.register_element(element)
        
        # Test minimizing
        result = self.window_manager.toggle_minimize("minimize_test")
        self.assertTrue(result)
        
        # Element should be in minimizing animation or minimized state
        self.assertIn(element.state, [UIState.MINIMIZED, UIState.ANIMATING])

    def test_bring_to_front(self):
        """Test bringing elements to front."""
        element1 = UIElement(id="back", layer=ZLayer.DIALOGS, rect=pygame.Rect(0, 0, 100, 100))
        element2 = UIElement(id="front", layer=ZLayer.DIALOGS, rect=pygame.Rect(0, 0, 100, 100))
        
        self.window_manager.register_element(element1)
        self.window_manager.register_element(element2)
        
        # Bring first element to front
        self.window_manager.bring_to_front("back")
        
        # Should be at end of layer list (front)
        layer_list = self.window_manager.z_order[ZLayer.DIALOGS]
        self.assertEqual(layer_list[-1], "back")
        self.assertEqual(self.window_manager.active_element, "back")

    def test_click_to_focus(self):
        """Test clicking on element brings it to front."""
        element = UIElement(
            id="focus_test",
            layer=ZLayer.DIALOGS,
            rect=pygame.Rect(100, 100, 200, 150),
            title="Focus Test"
        )
        
        self.window_manager.register_element(element)
        
        # Simulate click
        handled_id = self.window_manager._handle_element_click("focus_test", (150, 115))
        
        self.assertEqual(handled_id, "focus_test")
        self.assertEqual(self.window_manager.active_element, "focus_test")

    def test_non_draggable_element(self):
        """Test that non-draggable elements don't start drag."""
        element = UIElement(
            id="static_test",
            layer=ZLayer.DIALOGS,
            rect=pygame.Rect(100, 100, 200, 150),
            title="Static Test",
            draggable=False
        )
        
        self.window_manager.register_element(element)
        
        # Try to start drag
        result = self.window_manager._start_drag("static_test", (150, 115))
        self.assertFalse(result)
        self.assertIsNone(self.window_manager.dragging_element)


class TestWindowDrawing(unittest.TestCase):
    """Test window drawing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        """Clean up pygame."""
        pygame.quit()

    def test_window_header_drawing(self):
        """Test drawing window with header."""
        rect = pygame.Rect(100, 100, 300, 200)
        header_rect, minimize_rect = draw_window_with_header(
            self.screen, rect, "Test Window", "Content", False
        )
        
        # Header should be at top of window
        self.assertEqual(header_rect.x, rect.x)
        self.assertEqual(header_rect.y, rect.y)
        self.assertEqual(header_rect.width, rect.width)
        self.assertEqual(header_rect.height, 30)
        
        # Minimize button should be in header
        self.assertTrue(minimize_rect.x > header_rect.x)
        self.assertTrue(minimize_rect.right <= header_rect.right)
        self.assertTrue(minimize_rect.y >= header_rect.y)
        self.assertTrue(minimize_rect.bottom <= header_rect.bottom)

    def test_minimized_window_drawing(self):
        """Test drawing minimized window."""
        rect = pygame.Rect(100, 100, 300, 200)
        header_rect, minimize_rect = draw_window_with_header(
            self.screen, rect, "Minimized", "Content", True
        )
        
        # Should still return header and button rects
        self.assertIsNotNone(header_rect)
        self.assertIsNotNone(minimize_rect)

    def test_window_with_content(self):
        """Test drawing window with text content."""
        rect = pygame.Rect(100, 100, 300, 200)
        content = "Line 1\nLine 2\nLine 3"
        
        header_rect, minimize_rect = draw_window_with_header(
            self.screen, rect, "Content Test", content, False
        )
        
        # Should complete without error
        self.assertIsNotNone(header_rect)
        self.assertIsNotNone(minimize_rect)


if __name__ == '__main__':
    unittest.main()