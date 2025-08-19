"""
Tests for the overlay manager and visual feedback systems.
"""

import unittest
import pygame
from src.ui.overlay_manager import OverlayManager, UIElement, ZLayer, UIState, create_dialog, create_tooltip, create_modal
from src.features.visual_feedback import VisualFeedback, ButtonState, FeedbackStyle
from src.core.game_state import GameState


class TestOverlayManager(unittest.TestCase):
    """Test the overlay manager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Initialize pygame for testing (headless)
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        
        self.overlay_manager = OverlayManager()
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_overlay_manager_initialization(self):
        """Test that overlay manager initializes correctly."""
        self.assertIsInstance(self.overlay_manager, OverlayManager)
        self.assertEqual(len(self.overlay_manager.elements), 0)
        self.assertIsNone(self.overlay_manager.active_element)
        self.assertIsNone(self.overlay_manager.hover_element)
    
    def test_element_registration(self):
        """Test registering UI elements."""
        rect = pygame.Rect(10, 10, 100, 50)
        element = UIElement(
            id="test_element",
            layer=ZLayer.DIALOGS,
            rect=rect,
            title="Test Element"
        )
        
        success = self.overlay_manager.register_element(element)
        self.assertTrue(success)
        self.assertIn("test_element", self.overlay_manager.elements)
        self.assertIn("test_element", self.overlay_manager.z_order[ZLayer.DIALOGS])
    
    def test_duplicate_element_registration(self):
        """Test that duplicate IDs are rejected."""
        rect = pygame.Rect(10, 10, 100, 50)
        element1 = UIElement(id="duplicate", layer=ZLayer.DIALOGS, rect=rect)
        element2 = UIElement(id="duplicate", layer=ZLayer.TOOLTIPS, rect=rect)
        
        success1 = self.overlay_manager.register_element(element1)
        success2 = self.overlay_manager.register_element(element2)
        
        self.assertTrue(success1)
        self.assertFalse(success2)
        self.assertEqual(len(self.overlay_manager.elements), 1)
    
    def test_element_unregistration(self):
        """Test removing UI elements."""
        rect = pygame.Rect(10, 10, 100, 50)
        element = UIElement(id="removable", layer=ZLayer.DIALOGS, rect=rect)
        
        self.overlay_manager.register_element(element)
        self.assertIn("removable", self.overlay_manager.elements)
        
        success = self.overlay_manager.unregister_element("removable")
        self.assertTrue(success)
        self.assertNotIn("removable", self.overlay_manager.elements)
        
        # Test removing non-existent element
        success = self.overlay_manager.unregister_element("nonexistent")
        self.assertFalse(success)
    
    def test_z_order_management(self):
        """Test z-order and bring to front functionality."""
        rect = pygame.Rect(10, 10, 100, 50)
        element1 = UIElement(id="back", layer=ZLayer.DIALOGS, rect=rect)
        element2 = UIElement(id="front", layer=ZLayer.DIALOGS, rect=rect)
        
        self.overlay_manager.register_element(element1)
        self.overlay_manager.register_element(element2)
        
        # element2 should be last (front) initially
        layer_order = self.overlay_manager.z_order[ZLayer.DIALOGS]
        self.assertEqual(layer_order[-1], "front")
        
        # Bring element1 to front
        self.overlay_manager.bring_to_front("back")
        self.assertEqual(layer_order[-1], "back")
        self.assertEqual(self.overlay_manager.active_element, "back")
    
    def test_element_state_changes(self):
        """Test changing element states (minimize, expand, etc.)."""
        rect = pygame.Rect(10, 10, 100, 50)
        minimized_rect = pygame.Rect(10, 10, 100, 20)
        expanded_rect = pygame.Rect(5, 5, 110, 60)
        
        element = UIElement(
            id="stateful",
            layer=ZLayer.DIALOGS,
            rect=rect,
            minimized_rect=minimized_rect,
            expanded_rect=expanded_rect
        )
        
        self.overlay_manager.register_element(element)
        
        # Test minimize
        success = self.overlay_manager.set_element_state("stateful", UIState.MINIMIZED)
        self.assertTrue(success)
        self.assertEqual(element.state, UIState.ANIMATING)  # Should be animating
        self.assertEqual(element.target_rect, minimized_rect)
        
        # Test expand
        success = self.overlay_manager.set_element_state("stateful", UIState.EXPANDED)
        self.assertTrue(success)
        self.assertEqual(element.state, UIState.ANIMATING)
        self.assertEqual(element.target_rect, expanded_rect)
    
    def test_error_tracking(self):
        """Test the error tracking system for easter egg."""
        # Test single error
        triggered = self.overlay_manager.add_error("Test error", 100)
        self.assertFalse(triggered)
        
        # Test repeated errors (should trigger after 3)
        triggered = self.overlay_manager.add_error("Repeated error", 100)
        self.assertFalse(triggered)
        
        triggered = self.overlay_manager.add_error("Repeated error", 110)
        self.assertFalse(triggered)
        
        triggered = self.overlay_manager.add_error("Repeated error", 120)
        self.assertTrue(triggered)  # Third occurrence should trigger
    
    def test_animation_updates(self):
        """Test animation system."""
        rect = pygame.Rect(10, 10, 100, 50)
        target_rect = pygame.Rect(50, 50, 100, 50)
        
        element = UIElement(
            id="animated",
            layer=ZLayer.DIALOGS,
            rect=rect,
            target_rect=target_rect,
            state=UIState.ANIMATING,
            animation_progress=0.0
        )
        
        self.overlay_manager.register_element(element)
        
        # Update animations multiple times
        for _ in range(10):
            self.overlay_manager.update_animations()
        
        # Should have progressed
        self.assertGreater(element.animation_progress, 0.0)
        
        # Continue until completion
        while element.state == UIState.ANIMATING:
            self.overlay_manager.update_animations()
        
        # Should be complete
        self.assertEqual(element.state, UIState.NORMAL)
        self.assertEqual(element.rect, target_rect)


class TestVisualFeedback(unittest.TestCase):
    """Test the visual feedback system."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
        self.visual_feedback = VisualFeedback()
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_visual_feedback_initialization(self):
        """Test that visual feedback system initializes correctly."""
        self.assertIsInstance(self.visual_feedback, VisualFeedback)
        self.assertEqual(self.visual_feedback.font_scale_factor, 1.0)
        self.assertIn(ButtonState.NORMAL, self.visual_feedback.color_schemes)
        self.assertIn(ButtonState.HOVER, self.visual_feedback.color_schemes)
    
    def test_button_drawing(self):
        """Test drawing buttons with different states."""
        rect = pygame.Rect(10, 10, 100, 30)
        
        # Test normal button
        drawn_rect = self.visual_feedback.draw_button(
            self.screen, rect, "Test", ButtonState.NORMAL
        )
        self.assertIsInstance(drawn_rect, pygame.Rect)
        self.assertEqual(drawn_rect.topleft, rect.topleft)
        
        # Test pressed button (should be offset)
        pressed_rect = self.visual_feedback.draw_button(
            self.screen, rect, "Pressed", ButtonState.PRESSED
        )
        self.assertGreater(pressed_rect.x, rect.x)
        self.assertGreater(pressed_rect.y, rect.y)
        
        # Test hover button (should be lifted)
        hover_rect = self.visual_feedback.draw_button(
            self.screen, rect, "Hover", ButtonState.HOVER
        )
        self.assertLess(hover_rect.y, rect.y)
    
    def test_font_scaling(self):
        """Test font scaling for accessibility."""
        original_scale = self.visual_feedback.font_scale_factor
        
        # Test valid scaling
        self.visual_feedback.set_font_scale(1.5)
        self.assertEqual(self.visual_feedback.font_scale_factor, 1.5)
        
        # Test clamping
        self.visual_feedback.set_font_scale(3.0)  # Should clamp to 2.0
        self.assertEqual(self.visual_feedback.font_scale_factor, 2.0)
        
        self.visual_feedback.set_font_scale(0.1)  # Should clamp to 0.5
        self.assertEqual(self.visual_feedback.font_scale_factor, 0.5)
    
    def test_icon_button_drawing(self):
        """Test drawing icon buttons."""
        rect = pygame.Rect(10, 10, 40, 40)
        
        drawn_rect = self.visual_feedback.draw_icon_button(
            self.screen, rect, "★", ButtonState.NORMAL
        )
        self.assertIsInstance(drawn_rect, pygame.Rect)
    
    def test_panel_drawing(self):
        """Test drawing panels with title bars."""
        rect = pygame.Rect(10, 10, 200, 150)
        
        interactive_rects = self.visual_feedback.draw_panel(
            self.screen, rect, "Test Panel", ButtonState.NORMAL, minimizable=True
        )
        
        self.assertIsInstance(interactive_rects, dict)
        if "minimize" in interactive_rects:
            self.assertIsInstance(interactive_rects["minimize"], pygame.Rect)


class TestGameStateIntegration(unittest.TestCase):
    """Test integration of overlay manager with game state."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        self.game_state = GameState("test_seed")
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_game_state_has_overlay_manager(self):
        """Test that GameState includes overlay manager."""
        self.assertIsInstance(self.game_state.overlay_manager, OverlayManager)
    
    def test_error_tracking_integration(self):
        """Test error tracking through GameState."""
        # Test tracking an error
        triggered = self.game_state.track_error("Test error message")
        self.assertFalse(triggered)  # First occurrence shouldn't trigger
        
        # Test insufficient resources handling
        triggered = self.game_state.handle_insufficient_resources("money", 100, 50)
        self.assertFalse(triggered)
        
        # Check that message was added
        self.assertGreater(len(self.game_state.messages), 1)
        self.assertIn("Need $100", self.game_state.messages[-1])
    
    def test_action_validation(self):
        """Test action validation with error reporting."""
        # Test with insufficient money
        self.game_state.money = 10
        can_perform, error_msg = self.game_state.validate_action_requirements(0)
        
        # The result depends on the specific action, but should return validation info
        self.assertIsInstance(can_perform, bool)
        self.assertIsInstance(error_msg, str)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions for creating UI elements."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        self.overlay_manager = OverlayManager()
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_create_dialog(self):
        """Test dialog creation utility."""
        element = create_dialog(
            self.overlay_manager,
            "test_dialog",
            "Test Dialog",
            "Dialog content",
            10, 10, 200, 150
        )
        
        self.assertIsInstance(element, UIElement)
        self.assertEqual(element.id, "test_dialog")
        self.assertEqual(element.layer, ZLayer.DIALOGS)
        self.assertEqual(element.title, "Test Dialog")
        self.assertIn("test_dialog", self.overlay_manager.elements)
    
    def test_create_tooltip(self):
        """Test tooltip creation utility."""
        element = create_tooltip(
            self.overlay_manager,
            "test_tooltip",
            "Tooltip text",
            100, 100
        )
        
        self.assertIsInstance(element, UIElement)
        self.assertEqual(element.id, "test_tooltip")
        self.assertEqual(element.layer, ZLayer.TOOLTIPS)
        self.assertFalse(element.clickable)  # Tooltips shouldn't be clickable
        self.assertIn("test_tooltip", self.overlay_manager.elements)
    
    def test_create_modal(self):
        """Test modal creation utility."""
        element = create_modal(
            self.overlay_manager,
            "test_modal",
            "Test Modal",
            "Modal content",
            800, 600
        )
        
        self.assertIsInstance(element, UIElement)
        self.assertEqual(element.id, "test_modal")
        self.assertEqual(element.layer, ZLayer.MODALS)
        self.assertIn("test_modal", self.overlay_manager.elements)


if __name__ == '__main__':
    unittest.main()