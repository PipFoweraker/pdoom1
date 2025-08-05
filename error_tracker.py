"""
Error Tracking System for P(Doom)

This module provides a centralized error tracking system that handles:
- Tracking repeated errors for easter egg detection
- Managing beep timing and cooldown
- Playing error beep sounds
- UI feedback integration

This refactors the duplicate error tracking logic from OverlayManager and GameState.
"""

import pygame
from typing import List, Tuple, Optional


class ErrorTracker:
    """
    Centralized error tracking system for easter egg detection and feedback.
    
    Tracks repeated identical errors within a time window and triggers
    easter egg behavior (beep sound + UI feedback) after a threshold.
    """
    
    def __init__(self, sound_manager=None, message_callback=None):
        """
        Initialize the error tracker.
        
        Args:
            sound_manager: SoundManager instance for playing beep sounds
            message_callback: Callable to add messages to the game log
        """
        # Error tracking configuration
        self.recent_errors: List[Tuple[str, int]] = []  # (error_msg, timestamp)
        self.error_repeat_threshold = 3
        self.error_time_window = 180  # frames (6 seconds at 30fps)
        
        # Beep timing and cooldown
        self.last_error_beep_time = -1000000  # Initialize to far in the past to allow first beep
        self.beep_cooldown = 2000  # 2 seconds in milliseconds
        
        # Dependencies
        self.sound_manager = sound_manager
        self.message_callback = message_callback
    
    def track_error(self, error_message: str, timestamp: Optional[int] = None) -> bool:
        """
        Track an error and potentially trigger easter egg behavior.
        
        Args:
            error_message: The error message that occurred
            timestamp: Time of error (current frame time if None)
            
        Returns:
            bool: True if this triggered the easter egg (beep was played)
        """
        current_time_ms = pygame.time.get_ticks()
        
        if timestamp is None:
            timestamp = current_time_ms // (1000 // 30)  # Convert to frame count
            
        # Clean old errors outside time window
        cutoff_time = timestamp - self.error_time_window
        self.recent_errors = [(msg, t) for msg, t in self.recent_errors if t > cutoff_time]
        
        # Add new error
        self.recent_errors.append((error_message, timestamp))
        
        # Check for repeated identical errors
        identical_count = sum(1 for msg, _ in self.recent_errors if msg == error_message)
        
        # Trigger easter egg if threshold reached
        if identical_count >= self.error_repeat_threshold:
            return self._trigger_easter_egg(current_time_ms)
            
        return False
    
    def _trigger_easter_egg(self, current_time_ms: int) -> bool:
        """
        Trigger the easter egg behavior (beep + UI feedback).
        
        Args:
            current_time_ms: Current time in milliseconds
            
        Returns:
            bool: True if easter egg was triggered (beep was played)
        """
        # Check cooldown to prevent spam beeping
        if (current_time_ms - self.last_error_beep_time) > self.beep_cooldown:
            # Play beep sound if sound manager is available
            if self.sound_manager:
                self.sound_manager.play_error_beep()
            
            # Add UI feedback message if callback is available
            if self.message_callback:
                self.message_callback("🔊 Error pattern detected! (Easter egg activated)")
            
            # Update cooldown timer
            self.last_error_beep_time = current_time_ms
            return True
            
        return False
    
    def get_error_count(self, error_message: str) -> int:
        """
        Get the count of a specific error message in the current time window.
        
        Args:
            error_message: The error message to count
            
        Returns:
            int: Number of times this error has occurred recently
        """
        return sum(1 for msg, _ in self.recent_errors if msg == error_message)
    
    def clear_errors(self):
        """Clear all tracked errors."""
        self.recent_errors.clear()
    
    def set_sound_manager(self, sound_manager):
        """Set or update the sound manager."""
        self.sound_manager = sound_manager
    
    def set_message_callback(self, callback):
        """Set or update the message callback."""
        self.message_callback = callback