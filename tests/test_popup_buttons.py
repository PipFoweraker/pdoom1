"""
Tests for event popup button functionality.

This test module specifically validates that event popup buttons are clickable
and properly connected to event actions.
"""

import unittest
import pygame
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from event_system import Event, EventType, EventAction
from game_state import GameState
from ui import draw_popup_events


class TestPopupButtons(unittest.TestCase):
    """Test popup button clickability and functionality."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
        self.game_state = GameState("test_seed")
        
        # Create a test popup event
        def test_effect(gs):
            gs.messages.append("Test event executed")
        
        def test_reduce_effect(gs):
            gs.messages.append("Test event reduced")
            
        def test_trigger(gs):
            return True
            
        self.test_event = Event(
            name="Test Popup Event",
            desc="This is a test popup event with clickable buttons.",
            trigger=test_trigger,
            effect=test_effect,
            event_type=EventType.POPUP,
            available_actions=[EventAction.ACCEPT, EventAction.DEFER, EventAction.REDUCE, EventAction.DISMISS],
            reduce_effect=test_reduce_effect
        )
        
        # Add event to game state pending popup events
        self.game_state.pending_popup_events = [self.test_event]
        
        # Set up fonts
        self.font = pygame.font.SysFont('Consolas', 16)
        self.big_font = pygame.font.SysFont('Consolas', 20, bold=True)
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_popup_event_present(self):
        """Test that popup events are properly set up."""
        self.assertEqual(len(self.game_state.pending_popup_events), 1)
        self.assertEqual(self.game_state.pending_popup_events[0], self.test_event)
        self.assertEqual(self.test_event.event_type, EventType.POPUP)
    
    def test_popup_event_has_actions(self):
        """Test that popup event has the expected actions."""
        expected_actions = [EventAction.ACCEPT, EventAction.DEFER, EventAction.REDUCE, EventAction.DISMISS]
        self.assertEqual(self.test_event.available_actions, expected_actions)
    
    def test_draw_popup_events_basic(self):
        """Test that draw_popup_events can be called without errors."""
        # This should not raise any exceptions
        try:
            draw_popup_events(self.screen, self.game_state, 800, 600, self.font, self.big_font)
        except Exception as e:
            self.fail(f"draw_popup_events raised an exception: {e}")
    
    def test_handle_popup_event_action_accept(self):
        """Test handling ACCEPT action on popup event."""
        initial_message_count = len(self.game_state.messages)
        
        self.game_state.handle_popup_event_action(self.test_event, EventAction.ACCEPT)
        
        # Event should be removed from pending list
        self.assertEqual(len(self.game_state.pending_popup_events), 0)
        
        # Effect should have been executed
        self.assertGreater(len(self.game_state.messages), initial_message_count)
        self.assertIn("Test event executed", self.game_state.messages)
    
    def test_handle_popup_event_action_reduce(self):
        """Test handling REDUCE action on popup event."""
        initial_message_count = len(self.game_state.messages)
        
        self.game_state.handle_popup_event_action(self.test_event, EventAction.REDUCE)
        
        # Event should be removed from pending list
        self.assertEqual(len(self.game_state.pending_popup_events), 0)
        
        # Reduce effect should have been executed
        self.assertGreater(len(self.game_state.messages), initial_message_count)
        self.assertIn("Test event reduced", self.game_state.messages)
    
    def test_handle_popup_event_action_dismiss(self):
        """Test handling DISMISS action on popup event."""
        initial_message_count = len(self.game_state.messages)
        
        self.game_state.handle_popup_event_action(self.test_event, EventAction.DISMISS)
        
        # Event should be removed from pending list
        self.assertEqual(len(self.game_state.pending_popup_events), 0)
        
        # Dismiss message should be added
        self.assertGreater(len(self.game_state.messages), initial_message_count)
        self.assertIn("Dismissed: Test Popup Event", self.game_state.messages)
    
    def test_handle_popup_event_action_defer(self):
        """Test handling DEFER action on popup event."""
        initial_message_count = len(self.game_state.messages)
        
        self.game_state.handle_popup_event_action(self.test_event, EventAction.DEFER)
        
        # Event should be removed from pending list
        self.assertEqual(len(self.game_state.pending_popup_events), 0)
        
        # Event should be added to deferred queue
        deferred_events = self.game_state.deferred_events.get_deferred_events()
        self.assertEqual(len(deferred_events), 1)
        self.assertTrue(deferred_events[0].is_deferred)
        
        # Defer message should be added
        self.assertGreater(len(self.game_state.messages), initial_message_count)
        self.assertIn("Deferred: Test Popup Event", self.game_state.messages)


class TestPopupButtonDetection(unittest.TestCase):
    """Test popup button click detection and coordinates."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
        
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_popup_button_coordinates_calculation(self):
        """Test that popup button coordinates are calculated correctly."""
        # Standard popup dimensions based on ui.py
        w, h = 800, 600
        popup_width = int(w * 0.6)  # 480
        popup_height = int(h * 0.4)  # 240
        popup_x = (w - popup_width) // 2  # 160
        popup_y = (h - popup_height) // 2  # 180
        
        # Button parameters
        button_y = popup_y + popup_height - 80  # 340
        button_width = 120
        button_height = 40
        button_spacing = 20
        
        # Test with 4 actions (Accept, Defer, Reduce, Dismiss)
        num_actions = 4
        total_width = num_actions * button_width + (num_actions - 1) * button_spacing
        start_x = popup_x + (popup_width - total_width) // 2
        
        # Calculate expected button positions
        expected_buttons = []
        for i in range(num_actions):
            button_x = start_x + i * (button_width + button_spacing)
            expected_buttons.append(pygame.Rect(button_x, button_y, button_width, button_height))
        
        # Verify calculations are reasonable
        self.assertEqual(len(expected_buttons), 4)
        self.assertGreater(expected_buttons[0].x, popup_x)  # First button is within popup
        self.assertLess(expected_buttons[-1].right, popup_x + popup_width)  # Last button is within popup
        self.assertEqual(all(btn.y == button_y for btn in expected_buttons), True)  # All same y
        self.assertEqual(all(btn.width == button_width for btn in expected_buttons), True)  # All same width


if __name__ == '__main__':
    unittest.main()