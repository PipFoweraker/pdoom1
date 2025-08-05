"""
Tests for the ErrorTracker system

Tests cover:
- Error tracking and easter egg detection
- Beep timing and cooldown functionality
- Sound manager integration
- Message callback integration
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import pygame

from error_tracker import ErrorTracker


class TestErrorTracker(unittest.TestCase):
    
    def setUp(self):
        # Initialize pygame for time tracking
        pygame.init()
        
        # Create mock dependencies
        self.mock_sound_manager = Mock()
        self.mock_messages = []
        self.message_callback = lambda msg: self.mock_messages.append(msg)
        
        # Create error tracker instance
        self.error_tracker = ErrorTracker(
            sound_manager=self.mock_sound_manager,
            message_callback=self.message_callback
        )
    
    def tearDown(self):
        pygame.quit()
    
    def test_error_tracker_initialization(self):
        """Test that ErrorTracker initializes with correct defaults."""
        tracker = ErrorTracker()
        
        self.assertEqual(tracker.recent_errors, [])
        self.assertEqual(tracker.error_repeat_threshold, 3)
        self.assertEqual(tracker.error_time_window, 180)
        self.assertEqual(tracker.beep_cooldown, 2000)
        self.assertEqual(tracker.last_error_beep_time, -1000000)  # Far in the past
        self.assertIsNone(tracker.sound_manager)
        self.assertIsNone(tracker.message_callback)
    
    def test_error_tracking_single_error(self):
        """Test tracking a single error doesn't trigger easter egg."""
        result = self.error_tracker.track_error("Test error")
        
        self.assertFalse(result)
        self.assertEqual(len(self.error_tracker.recent_errors), 1)
        self.assertEqual(self.error_tracker.get_error_count("Test error"), 1)
        
        # Should not have triggered sound or message
        self.mock_sound_manager.play_error_beep.assert_not_called()
        self.assertEqual(len(self.mock_messages), 0)
    
    def test_error_tracking_repeated_errors(self):
        """Test that 3 repeated errors trigger easter egg."""
        error_msg = "Repeated error"
        
        # First two errors should not trigger
        result1 = self.error_tracker.track_error(error_msg)
        result2 = self.error_tracker.track_error(error_msg)
        self.assertFalse(result1)
        self.assertFalse(result2)
        
        # Third error should trigger easter egg
        with patch('pygame.time.get_ticks', return_value=1000):
            result3 = self.error_tracker.track_error(error_msg)
        
        self.assertTrue(result3)
        self.assertEqual(self.error_tracker.get_error_count(error_msg), 3)
        
        # Should have triggered sound and message
        self.mock_sound_manager.play_error_beep.assert_called_once()
        self.assertEqual(len(self.mock_messages), 1)
        self.assertIn("Easter egg activated", self.mock_messages[0])
    
    def test_error_tracking_different_errors(self):
        """Test that different errors don't contribute to each other's count."""
        self.error_tracker.track_error("Error A")
        self.error_tracker.track_error("Error B")
        self.error_tracker.track_error("Error A")
        self.error_tracker.track_error("Error B")
        
        # Track Error A one more time - this should trigger (count reaches 3)
        with patch('pygame.time.get_ticks', return_value=1000):
            result_a = self.error_tracker.track_error("Error A")
        
        # Each error should have the right count
        self.assertEqual(self.error_tracker.get_error_count("Error A"), 3)
        self.assertEqual(self.error_tracker.get_error_count("Error B"), 2)
        
        # Error A should have triggered
        self.assertTrue(result_a)
        
        # Now track Error B after cooldown period - this should also trigger (count reaches 3)
        with patch('pygame.time.get_ticks', return_value=4000):  # After cooldown
            result_b = self.error_tracker.track_error("Error B")
        
        self.assertTrue(result_b)  # Error B should trigger after cooldown
        self.assertEqual(self.error_tracker.get_error_count("Error B"), 3)
    
    def test_beep_cooldown(self):
        """Test that beep cooldown prevents spam."""
        error_msg = "Spam error"
        
        # Set up initial time
        with patch('pygame.time.get_ticks', return_value=1000):
            # Trigger first easter egg
            for _ in range(3):
                self.error_tracker.track_error(error_msg)
        
        # Clear errors and try again immediately (should be in cooldown)
        self.error_tracker.clear_errors()
        
        with patch('pygame.time.get_ticks', return_value=1500):  # Only 500ms later
            for _ in range(3):
                result = self.error_tracker.track_error(error_msg)
        
        # Should detect pattern but not play beep due to cooldown
        self.assertFalse(result)  # Last call should return False due to cooldown
        
        # Should have only called beep once (from first trigger)
        self.assertEqual(self.mock_sound_manager.play_error_beep.call_count, 1)
    
    def test_beep_after_cooldown(self):
        """Test that beep works again after cooldown period."""
        error_msg = "Cooldown test"
        
        # Trigger first easter egg
        with patch('pygame.time.get_ticks', return_value=1000):
            for _ in range(3):
                self.error_tracker.track_error(error_msg)
        
        # Clear errors and try again after cooldown period
        self.error_tracker.clear_errors()
        
        with patch('pygame.time.get_ticks', return_value=4000):  # 3000ms later (> 2000ms cooldown)
            for _ in range(3):
                result = self.error_tracker.track_error(error_msg)
        
        # Should trigger again
        self.assertTrue(result)
        
        # Should have called beep twice now
        self.assertEqual(self.mock_sound_manager.play_error_beep.call_count, 2)
    
    def test_time_window_cleanup(self):
        """Test that old errors are cleaned up after time window."""
        error_msg = "Old error"
        
        # Add errors at different times
        with patch('pygame.time.get_ticks', return_value=0):
            self.error_tracker.track_error(error_msg, timestamp=10)
            self.error_tracker.track_error(error_msg, timestamp=20)
        
        # Add error much later (outside time window of 180 frames)
        with patch('pygame.time.get_ticks', return_value=0):
            self.error_tracker.track_error(error_msg, timestamp=200)
        
        # Only the recent error should count
        self.assertEqual(self.error_tracker.get_error_count(error_msg), 1)
    
    def test_no_sound_manager(self):
        """Test that error tracking works without sound manager."""
        tracker = ErrorTracker(message_callback=self.message_callback)
        
        # Should still track and trigger easter egg
        with patch('pygame.time.get_ticks', return_value=1000):
            for _ in range(3):
                result = tracker.track_error("No sound test")
        
        self.assertTrue(result)
        self.assertEqual(len(self.mock_messages), 1)
    
    def test_no_message_callback(self):
        """Test that error tracking works without message callback."""
        tracker = ErrorTracker(sound_manager=self.mock_sound_manager)
        
        # Should still track and trigger easter egg
        with patch('pygame.time.get_ticks', return_value=1000):
            for _ in range(3):
                result = tracker.track_error("No message test")
        
        self.assertTrue(result)
        self.mock_sound_manager.play_error_beep.assert_called_once()
    
    def test_clear_errors(self):
        """Test clearing all tracked errors."""
        self.error_tracker.track_error("Error 1")
        self.error_tracker.track_error("Error 2")
        
        self.assertEqual(len(self.error_tracker.recent_errors), 2)
        
        self.error_tracker.clear_errors()
        
        self.assertEqual(len(self.error_tracker.recent_errors), 0)
        self.assertEqual(self.error_tracker.get_error_count("Error 1"), 0)
    
    def test_set_dependencies(self):
        """Test setting sound manager and message callback after initialization."""
        tracker = ErrorTracker()
        
        new_sound_manager = Mock()
        new_callback = Mock()
        
        tracker.set_sound_manager(new_sound_manager)
        tracker.set_message_callback(new_callback)
        
        self.assertEqual(tracker.sound_manager, new_sound_manager)
        self.assertEqual(tracker.message_callback, new_callback)


if __name__ == '__main__':
    unittest.main()