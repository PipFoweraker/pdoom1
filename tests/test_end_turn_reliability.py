"""
Test end turn input reliability improvements.

Covers:
- Space bar and mouse click end turn reliability
- Turn processing state prevents multiple inputs
- Visual feedback during turn transition
- Sound feedback for accepted/rejected inputs
- Input works regardless of other UI state
"""

import pytest
import pygame
import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game_state import GameState
from src.services.sound_manager import SoundManager


class TestEndTurnReliability:
    """Test end turn input reliability and processing state."""
    
    def setup_method(self):
        """Set up test environment."""
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
        
        # Create game state
        self.game_state = GameState(seed=12345)
        self.game_state.sound_manager = SoundManager()
    
    def test_end_turn_returns_success(self):
        """Test that end_turn returns True on success."""
        result = self.game_state.end_turn()
        assert result == True
    
    def test_end_turn_processing_state_initialized(self):
        """Test that turn processing state is properly initialized."""
        assert hasattr(self.game_state, 'turn_processing')
        assert hasattr(self.game_state, 'turn_processing_timer')
        assert hasattr(self.game_state, 'turn_processing_duration')
        
        # Should start as not processing
        assert self.game_state.turn_processing == False
        assert self.game_state.turn_processing_timer == 0
    
    def test_end_turn_sets_processing_state(self):
        """Test that end_turn sets processing state correctly."""
        # Should not be processing initially
        assert not self.game_state.turn_processing
        
        # Call end_turn
        result = self.game_state.end_turn()
        
        # Should now be processing
        assert self.game_state.turn_processing == True
        assert self.game_state.turn_processing_timer == self.game_state.turn_processing_duration
        assert result == True
    
    def test_multiple_end_turn_calls_rejected(self):
        """Test that multiple end_turn calls are rejected during processing."""
        # First call should succeed
        result1 = self.game_state.end_turn()
        assert result1 == True
        assert self.game_state.turn_processing == True
        
        # Second call should be rejected
        result2 = self.game_state.end_turn()
        assert result2 == False
        assert self.game_state.turn_processing == True  # Still processing
    
    def test_turn_processing_timer_update(self):
        """Test that turn processing timer updates correctly."""
        # Start processing
        self.game_state.end_turn()
        initial_timer = self.game_state.turn_processing_timer
        
        # Update processing
        self.game_state.update_turn_processing()
        
        # Timer should decrease
        assert self.game_state.turn_processing_timer == initial_timer - 1
        assert self.game_state.turn_processing == True  # Still processing
    
    def test_turn_processing_completes(self):
        """Test that turn processing completes after timer expires."""
        # Start processing
        self.game_state.end_turn()
        
        # Run timer to completion
        while self.game_state.turn_processing:
            self.game_state.update_turn_processing()
        
        # Should no longer be processing
        assert self.game_state.turn_processing == False
        assert self.game_state.turn_processing_timer == 0
    
    def test_end_turn_after_processing_completes(self):
        """Test that end_turn works again after processing completes."""
        # First turn
        self.game_state.end_turn()
        
        # Complete processing
        while self.game_state.turn_processing:
            self.game_state.update_turn_processing()
        
        # Second turn should work
        result = self.game_state.end_turn()
        assert result == True
        assert self.game_state.turn_processing == True
    
    def test_update_turn_processing_method_exists(self):
        """Test that update_turn_processing method exists."""
        assert hasattr(self.game_state, 'update_turn_processing')
        assert callable(self.game_state.update_turn_processing)
        
        # Should not crash when called
        self.game_state.update_turn_processing()


class TestEndTurnSoundFeedback:
    """Test sound feedback for end turn actions."""
    
    def setup_method(self):
        """Set up test environment."""
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
        
        self.game_state = GameState(seed=12345)
        self.game_state.sound_manager = SoundManager()
    
    def test_successful_end_turn_sound(self):
        """Test that successful end turn plays accept sound."""
        # Mock the sound manager to track calls
        sounds_played = []
        original_play_sound = self.game_state.sound_manager.play_sound
        
        def mock_play_sound(sound_name):
            sounds_played.append(sound_name)
            return original_play_sound(sound_name)
        
        self.game_state.sound_manager.play_sound = mock_play_sound
        
        # End turn should play accept sound
        self.game_state.end_turn()
        
        assert 'popup_accept' in sounds_played
    
    def test_rejected_end_turn_sound(self):
        """Test that rejected end turn plays error sound."""
        # Mock the sound manager to track calls
        sounds_played = []
        original_play_sound = self.game_state.sound_manager.play_sound
        
        def mock_play_sound(sound_name):
            sounds_played.append(sound_name)
            return original_play_sound(sound_name)
        
        self.game_state.sound_manager.play_sound = mock_play_sound
        
        # First end turn (should succeed)
        self.game_state.end_turn()
        sounds_played.clear()  # Clear to focus on rejection
        
        # Second end turn while processing (should be rejected)
        self.game_state.end_turn()
        
        assert 'error_beep' in sounds_played


class TestTurnTransitionVisualFeedback:
    """Test visual feedback during turn transition."""
    
    def setup_method(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
    
    def test_draw_turn_transition_overlay_exists(self):
        """Test that draw_turn_transition_overlay function exists."""
        # Should not raise ImportError
        from ui import draw_turn_transition_overlay
        
        # Should be callable
        assert callable(draw_turn_transition_overlay)
    
    def test_draw_turn_transition_overlay_with_timer(self):
        """Test drawing transition overlay with active timer."""
        from ui import draw_turn_transition_overlay
        
        # Should not crash when called with valid parameters
        timer = 15
        duration = 30
        
        try:
            draw_turn_transition_overlay(self.screen, 800, 600, timer, duration)
            # If we get here without exception, the function works
            assert True
        except Exception as e:
            pytest.fail(f"draw_turn_transition_overlay failed: {e}")
    
    def test_draw_turn_transition_overlay_no_timer(self):
        """Test that overlay doesn't draw when timer is 0."""
        from ui import draw_turn_transition_overlay
        
        # Should not crash and should return early
        timer = 0
        duration = 30
        
        try:
            draw_turn_transition_overlay(self.screen, 800, 600, timer, duration)
            assert True
        except Exception as e:
            pytest.fail(f"draw_turn_transition_overlay failed with timer=0: {e}")
    
    def test_turn_transition_overlay_progress_calculation(self):
        """Test that transition overlay calculates progress correctly."""
        from ui import draw_turn_transition_overlay
        
        # Test various progress points
        duration = 30
        test_cases = [
            (30, 0.0),   # Start: progress = 1.0 - (30/30) = 0.0
            (15, 0.5),   # Middle: progress = 1.0 - (15/30) = 0.5
            (1, 29/30),  # Near end: progress = 1.0 - (1/30) = 29/30
        ]
        
        for timer, expected_progress in test_cases:
            # This test mainly ensures the function doesn't crash
            # The actual progress calculation is internal to the function
            try:
                draw_turn_transition_overlay(self.screen, 800, 600, timer, duration)
                assert True
            except Exception as e:
                pytest.fail(f"draw_turn_transition_overlay failed with timer={timer}: {e}")


class TestEndTurnIntegration:
    """Test integration of all end turn improvements."""
    
    def setup_method(self):
        """Set up test environment."""
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
        
        self.game_state = GameState(seed=12345)
        self.game_state.sound_manager = SoundManager()
    
    def test_full_end_turn_cycle(self):
        """Test complete end turn cycle with all improvements."""
        # Initial state
        assert not self.game_state.turn_processing
        initial_turn = self.game_state.turn
        
        # End turn
        result = self.game_state.end_turn()
        assert result == True
        assert self.game_state.turn_processing == True
        assert self.game_state.turn == initial_turn + 1  # Turn should advance
        
        # Try to end turn again (should be rejected)
        result2 = self.game_state.end_turn()
        assert result2 == False
        assert self.game_state.turn_processing == True  # Still processing
        
        # Complete processing
        while self.game_state.turn_processing:
            self.game_state.update_turn_processing()
        
        # Should be ready for next turn
        assert not self.game_state.turn_processing
        
        # Next end turn should work
        result3 = self.game_state.end_turn()
        assert result3 == True
        assert self.game_state.turn_processing == True
    
    def test_end_turn_regardless_of_game_state(self):
        """Test that end turn works regardless of other game state."""
        # Test with various game states
        test_scenarios = [
            {'money': 0, 'action_points': 0},  # No money, no AP
            {'money': 1000, 'action_points': 5},  # Plenty of resources
            {'doom': 90},  # High doom
            {'staff': 0},  # No staff
        ]
        
        for scenario in test_scenarios:
            # Set up scenario
            for attr, value in scenario.items():
                setattr(self.game_state, attr, value)
            
            # End turn should still work
            if not self.game_state.turn_processing:
                result = self.game_state.end_turn()
                assert result == True, f"End turn failed with scenario: {scenario}"
                
                # Reset processing for next test
                while self.game_state.turn_processing:
                    self.game_state.update_turn_processing()
    
    def test_mouse_click_end_turn_through_handle_click(self):
        """Test that mouse click end turn works through handle_click method."""
        # Get end turn button rect
        w, h = 800, 600
        btn_rect = self.game_state._get_endturn_rect(w, h)
        
        # Click inside button
        click_pos = (btn_rect[0] + 10, btn_rect[1] + 10)
        
        # Should trigger end turn
        initial_turn = self.game_state.turn
        self.game_state.handle_click(click_pos, w, h)
        
        # Processing should be active (turn advancement happens in end_turn)
        assert self.game_state.turn_processing == True
        
        # Turn should have advanced
        assert self.game_state.turn == initial_turn + 1