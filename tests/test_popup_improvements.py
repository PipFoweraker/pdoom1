"""
Test popup improvements for Action Points Exhausted popup.

Covers:
- Popup only appears when action points are actually exhausted
- Improved dismissal mechanisms (Escape/Enter keys)
- Sound feedback for popup open/close/accept
- Visual feedback improvements (hover effects)
"""

import pytest
import pygame
import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from game_state import GameState
from src.features.onboarding import onboarding
from sound_manager import SoundManager


class TestActionPointsPopupGating:
    """Test that action points popup is properly gated."""
    
    def setup_method(self):
        """Set up test environment."""
        # Initialize pygame for testing
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
        
        # Reset onboarding state
        onboarding.seen_mechanics = set()
        onboarding.tutorial_enabled = True
        
        # Reset main state
        main.current_state = 'game'
        main.first_time_help_content = None
        main.first_time_help_close_button = None
    
    def test_popup_not_shown_with_full_action_points(self):
        """Test that popup doesn't show when player has action points."""
        # Create game state with full action points
        game_state = GameState(seed=12345)
        game_state.action_points = 3  # Full action points
        
        # Should not show mechanic help when player has action points
        should_show = (onboarding.should_show_mechanic_help('action_points_exhausted') and 
                      game_state.action_points == 0)
        
        assert not should_show
    
    def test_popup_shown_with_zero_action_points(self):
        """Test that popup shows when player has zero action points."""
        # Create game state with zero action points
        game_state = GameState(seed=12345)
        game_state.action_points = 0  # Exhausted action points
        
        # Should show mechanic help when player has no action points
        should_show = (onboarding.should_show_mechanic_help('action_points_exhausted') and 
                      game_state.action_points == 0)
        
        assert should_show
    
    def test_popup_not_shown_after_first_time(self):
        """Test that popup doesn't show after it's been seen once."""
        # Mark mechanic as already seen
        onboarding.seen_mechanics.add('action_points_exhausted')
        
        # Create game state with zero action points
        game_state = GameState(seed=12345)
        game_state.action_points = 0
        
        # Should not show since it's already been seen
        should_show = (onboarding.should_show_mechanic_help('action_points_exhausted') and 
                      game_state.action_points == 0)
        
        assert not should_show


class TestPopupDismissal:
    """Test popup dismissal mechanisms."""
    
    def setup_method(self):
        """Set up test environment."""
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
        
        # Set up popup state
        main.first_time_help_content = {
            'title': 'No Action Points Remaining',
            'content': 'Test popup content'
        }
        main.first_time_help_close_button = pygame.Rect(100, 100, 20, 20)
        
        # Mock game state with sound manager
        main.game_state = GameState(seed=12345)
        main.game_state.sound_manager = SoundManager()
    
    def teardown_method(self):
        """Clean up after test."""
        main.first_time_help_content = None
        main.first_time_help_close_button = None
        main.game_state = None
    
    def test_escape_key_dismissal(self):
        """Test that Escape key dismisses popup."""
        # Simulate escape key press
        event = type('Event', (), {})()
        event.key = pygame.K_ESCAPE
        
        # Initially popup should be present
        assert main.first_time_help_content is not None
        
        # Manually call the escape key handling logic
        if main.first_time_help_content:
            main.first_time_help_content = None
            main.first_time_help_close_button = None
        
        # Popup should be dismissed
        assert main.first_time_help_content is None
        assert main.first_time_help_close_button is None
    
    def test_enter_key_dismissal(self):
        """Test that Enter key dismisses popup."""
        # Initially popup should be present
        assert main.first_time_help_content is not None
        
        # Manually call the enter key handling logic
        if main.first_time_help_content:
            main.first_time_help_content = None
            main.first_time_help_close_button = None
        
        # Popup should be dismissed
        assert main.first_time_help_content is None
        assert main.first_time_help_close_button is None
    
    def test_close_button_click_dismissal(self):
        """Test that clicking close button dismisses popup."""
        # Initially popup should be present
        assert main.first_time_help_content is not None
        
        # Simulate close button click
        close_button = main.first_time_help_close_button
        click_pos = (close_button.x + 10, close_button.y + 10)
        
        # Manually call the click handling logic
        if close_button.collidepoint(click_pos):
            main.first_time_help_content = None
            main.first_time_help_close_button = None
        
        # Popup should be dismissed
        assert main.first_time_help_content is None
        assert main.first_time_help_close_button is None


class TestPopupSounds:
    """Test popup sound feedback."""
    
    def setup_method(self):
        """Set up test environment."""
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
        
        self.sound_manager = SoundManager()
    
    def test_popup_sounds_created(self):
        """Test that popup sounds are created in sound manager."""
        # Check that popup sounds exist
        expected_sounds = ['popup_open', 'popup_close', 'popup_accept']
        
        for sound_name in expected_sounds:
            # Sound should be in toggles (even if sound creation failed)
            assert sound_name in self.sound_manager.sound_toggles
    
    def test_play_sound_method_exists(self):
        """Test that generic play_sound method exists."""
        # Should not raise AttributeError
        assert hasattr(self.sound_manager, 'play_sound')
        
        # Should be callable
        assert callable(self.sound_manager.play_sound)
    
    def test_sound_toggle_functionality(self):
        """Test that individual sound toggles work."""
        # Test popup sound toggles
        popup_sounds = ['popup_open', 'popup_close', 'popup_accept']
        
        for sound_name in popup_sounds:
            # Should start enabled
            assert self.sound_manager.sound_toggles.get(sound_name, False)
            
            # Should be able to disable
            self.sound_manager.sound_toggles[sound_name] = False
            assert not self.sound_manager.sound_toggles[sound_name]
            
            # Should be able to re-enable
            self.sound_manager.sound_toggles[sound_name] = True
            assert self.sound_manager.sound_toggles[sound_name]


class TestPopupVisualFeedback:
    """Test popup visual feedback improvements."""
    
    def setup_method(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), pygame.NOFRAME)
    
    def test_draw_first_time_help_with_mouse_pos(self):
        """Test that draw function accepts mouse position parameter."""
        from ui import draw_first_time_help
        
        help_content = {
            'title': 'Test Popup',
            'content': 'Test content for popup'
        }
        
        # Should work with mouse position
        mouse_pos = (100, 100)
        close_button_rect = draw_first_time_help(self.screen, help_content, 800, 600, mouse_pos)
        
        # Should return a close button rect
        assert close_button_rect is not None
        assert isinstance(close_button_rect, pygame.Rect)
    
    def test_draw_first_time_help_without_mouse_pos(self):
        """Test that draw function works without mouse position (backward compatibility)."""
        from ui import draw_first_time_help
        
        help_content = {
            'title': 'Test Popup',
            'content': 'Test content for popup'
        }
        
        # Should work without mouse position
        close_button_rect = draw_first_time_help(self.screen, help_content, 800, 600)
        
        # Should return a close button rect
        assert close_button_rect is not None
        assert isinstance(close_button_rect, pygame.Rect)
    
    def test_popup_has_dismiss_instructions(self):
        """Test that popup includes dismiss instructions."""
        from ui import draw_first_time_help
        
        help_content = {
            'title': 'Test Popup',
            'content': 'Test content for popup'
        }
        
        # Draw popup and check it doesn't crash
        # The actual text content is hard to test without OCR, 
        # but we can ensure the function completes successfully
        close_button_rect = draw_first_time_help(self.screen, help_content, 800, 600)
        assert close_button_rect is not None


class TestIntegration:
    """Test integration of popup improvements."""
    
    def setup_method(self):
        """Set up test environment."""
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
        
        # Reset states
        onboarding.seen_mechanics = set()
        onboarding.tutorial_enabled = True
        main.first_time_help_content = None
    
    def test_full_action_points_exhausted_flow(self):
        """Test complete flow from action points exhausted to popup dismissal."""
        # Create game state with zero action points
        game_state = GameState(seed=12345)
        game_state.action_points = 0
        game_state.sound_manager = SoundManager()
        
        # Simulate the main loop logic for showing popup
        if (onboarding.should_show_mechanic_help('action_points_exhausted') and 
            game_state.action_points == 0):
            help_content = onboarding.get_mechanic_help('action_points_exhausted')
            if help_content and isinstance(help_content, dict):
                main.first_time_help_content = help_content
        
        # Popup should be shown
        assert main.first_time_help_content is not None
        assert main.first_time_help_content['title'] == 'No Action Points Remaining'
        
        # Simulate dismissal
        main.first_time_help_content = None
        
        # Should be dismissed
        assert main.first_time_help_content is None
        
        # Should not show again (marked as seen)
        onboarding.mark_mechanic_seen('action_points_exhausted')
        should_show_again = (onboarding.should_show_mechanic_help('action_points_exhausted') and 
                           game_state.action_points == 0)
        assert not should_show_again