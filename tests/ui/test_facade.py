"""
Tests for the UI Facade - Stable interface to UI subsystem

These tests verify that the UIFacade correctly proxies operations to the
internal OverlayManager and provides a stable interface for UI operations.
"""

import unittest
import pygame
from pdoom1.ui.facade import UIFacade
from pdoom1.ui.overlay_manager import UIElement, ZLayer, UIState


class TestUIFacade(unittest.TestCase):
    """Test the UI facade functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Initialise pygame for testing (headless)
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        
        self.ui_facade = UIFacade()
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_facade_initialisation(self):
        """Test that UIFacade initialises correctly."""
        self.assertIsInstance(self.ui_facade, UIFacade)
        self.assertIsNotNone(self.ui_facade._overlay_manager)
        self.assertIsNotNone(self.ui_facade.overlay_manager)
    
    def test_register_element_proxy(self):
        """Test that register_element proxies to internal OverlayManager."""
        rect = pygame.Rect(10, 10, 100, 50)
        element = UIElement(id="test_element", layer=ZLayer.DIALOGS, rect=rect)
        
        # Test registration through facade
        result = self.ui_facade.register_element(element)
        self.assertTrue(result)
        
        # Verify element is registered in internal overlay manager
        self.assertIn("test_element", self.ui_facade._overlay_manager.elements)
        self.assertEqual(
            self.ui_facade._overlay_manager.elements["test_element"],
            element
        )
    
    def test_unregister_element_proxy(self):
        """Test that unregister_element proxies to internal OverlayManager."""
        rect = pygame.Rect(10, 10, 100, 50)
        element = UIElement(id="test_element", layer=ZLayer.DIALOGS, rect=rect)
        
        # Register element first
        self.ui_facade.register_element(element)
        self.assertIn("test_element", self.ui_facade._overlay_manager.elements)
        
        # Test unregistration through facade
        result = self.ui_facade.unregister_element("test_element")
        self.assertTrue(result)
        
        # Verify element is removed from internal overlay manager
        self.assertNotIn("test_element", self.ui_facade._overlay_manager.elements)
    
    def test_bring_to_front_proxy(self):
        """Test that bring_to_front proxies to internal OverlayManager."""
        rect = pygame.Rect(10, 10, 100, 50)
        element1 = UIElement(id="element1", layer=ZLayer.DIALOGS, rect=rect)
        element2 = UIElement(id="element2", layer=ZLayer.DIALOGS, rect=rect)
        
        # Register elements
        self.ui_facade.register_element(element1)
        self.ui_facade.register_element(element2)
        
        # Test bring_to_front through facade
        result = self.ui_facade.bring_to_front("element1")
        self.assertTrue(result)
        
        # Verify element is brought to front in internal overlay manager
        layer_order = self.ui_facade._overlay_manager.z_order[ZLayer.DIALOGS]
        self.assertEqual(layer_order[-1], "element1")
        self.assertEqual(self.ui_facade._overlay_manager.active_element, "element1")
    
    def test_render_elements_proxy(self):
        """Test that render_elements proxies to internal OverlayManager."""
        # Create a test surface
        test_surface = pygame.Surface((800, 600))
        
        # Register a test element
        rect = pygame.Rect(10, 10, 100, 50)
        element = UIElement(id="test_element", layer=ZLayer.DIALOGS, rect=rect)
        self.ui_facade.register_element(element)
        
        # Test render through facade (should not crash)
        try:
            self.ui_facade.render_elements(test_surface)
            render_success = True
        except Exception:
            render_success = False
        
        self.assertTrue(render_success, "render_elements should complete without errors")
    
    def test_update_animations_proxy(self):
        """Test that update_animations proxies to internal OverlayManager."""
        # Register an element with animation
        rect = pygame.Rect(10, 10, 100, 50)
        element = UIElement(
            id="test_element", 
            layer=ZLayer.DIALOGS, 
            rect=rect,
            state=UIState.ANIMATING,
            target_rect=pygame.Rect(20, 20, 100, 50),
            animation_progress=0.5
        )
        self.ui_facade.register_element(element)
        
        # Test animation update through facade (should not crash)
        try:
            self.ui_facade.update_animations()
            animation_success = True
        except Exception:
            animation_success = False
        
        self.assertTrue(animation_success, "update_animations should complete without errors")
    
    def test_handle_mouse_event_proxy(self):
        """Test that handle_mouse_event proxies to internal OverlayManager."""
        # Create a mock mouse event
        mouse_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (50, 50), "button": 1})
        
        # Register an element that could receive the event
        rect = pygame.Rect(10, 10, 100, 50)
        element = UIElement(id="test_element", layer=ZLayer.DIALOGS, rect=rect)
        self.ui_facade.register_element(element)
        
        # Test mouse event handling through facade
        result = self.ui_facade.handle_mouse_event(mouse_event, 800, 600)
        
        # Result should be the element ID that handled the event or None
        self.assertIn(result, ["test_element", None])
    
    def test_handle_keyboard_event_proxy(self):
        """Test that handle_keyboard_event proxies to internal OverlayManager."""
        # Create a mock keyboard event (Tab for navigation)
        keyboard_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_TAB, "mod": 0})
        
        # Register focusable elements
        rect = pygame.Rect(10, 10, 100, 50)
        element = UIElement(id="test_element", layer=ZLayer.DIALOGS, rect=rect, clickable=True)
        self.ui_facade.register_element(element)
        
        # Test keyboard event handling through facade
        result = self.ui_facade.handle_keyboard_event(keyboard_event)
        
        # Result should be boolean indicating if event was handled
        self.assertIsInstance(result, bool)
    
    def test_toggle_minimize_proxy(self):
        """Test that toggle_minimize proxies to internal OverlayManager."""
        rect = pygame.Rect(10, 10, 100, 50)
        minimized_rect = pygame.Rect(10, 10, 100, 20)
        element = UIElement(
            id="test_element", 
            layer=ZLayer.DIALOGS, 
            rect=rect,
            minimized_rect=minimized_rect
        )
        
        # Register element
        self.ui_facade.register_element(element)
        
        # Test toggle minimize through facade
        result = self.ui_facade.toggle_minimize("test_element")
        self.assertTrue(result)
        
        # Verify element state in internal overlay manager
        internal_element = self.ui_facade._overlay_manager.elements["test_element"]
        # Should be animating towards minimized state
        self.assertEqual(internal_element.state, UIState.ANIMATING)
    
    def test_overlay_manager_property_access(self):
        """Test that the overlay_manager property provides access to internal manager."""
        internal_manager = self.ui_facade.overlay_manager
        self.assertIs(internal_manager, self.ui_facade._overlay_manager)
        
        # Test that we can use it for advanced operations
        rect = pygame.Rect(10, 10, 100, 50)
        element = UIElement(id="test_element", layer=ZLayer.DIALOGS, rect=rect)
        
        # Register through property access
        result = internal_manager.register_element(element)
        self.assertTrue(result)
        
        # Verify it's accessible through facade as well
        self.assertIn("test_element", self.ui_facade._overlay_manager.elements)


if __name__ == '__main__':
    unittest.main()