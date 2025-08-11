"""
Test comprehensive integration of all pre-launch polish improvements.

Covers:
- All implemented features working together
- No crashes or errors in normal operation
- Sound system integration
- Audio menu functionality
- Onboarding defensive code
"""

import pytest
import pygame
import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from game_state import GameState
from onboarding import onboarding
from sound_manager import SoundManager
from ui import draw_audio_menu


class TestPreLaunchPolishIntegration:
    """Test integration of all pre-launch polish features."""
    
    def setup_method(self):
        """Set up test environment."""
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
        
        # Reset all states
        main.current_state = 'main_menu'
        main.tutorial_choice_selected_item = 0
        main.sounds_menu_selected_item = 0
        main.first_time_help_content = None
        onboarding.seen_mechanics = set()
        onboarding.tutorial_enabled = True
    
    def test_all_main_imports_work(self):
        """Test that all imports in main.py work without errors."""
        # This test ensures all our new imports don't break anything
        import main
        assert hasattr(main, 'draw_audio_menu')
        assert hasattr(main, 'handle_audio_menu_click')
        assert hasattr(main, 'handle_audio_menu_keyboard')
    
    def test_tutorial_choice_menu_improvements(self):
        """Test tutorial choice menu navigation works."""
        # Test keyboard navigation
        main.tutorial_choice_selected_item = 0
        main.handle_tutorial_choice_keyboard(pygame.K_DOWN)
        assert main.tutorial_choice_selected_item == 1
        
        # Test hover functionality
        main.handle_tutorial_choice_hover((400, 400), 800, 600)
        # Should work without errors
    
    def test_popup_improvements_integration(self):
        """Test popup improvements don't break game flow."""
        game_state = GameState(seed=12345)
        
        # Test that action points popup is properly gated
        game_state.action_points = 0
        should_show = (onboarding.should_show_mechanic_help('action_points_exhausted') and 
                      game_state.action_points == 0)
        
        # Should show when action points are exhausted
        assert should_show
        
        # Test sound manager has popup sounds
        assert 'popup_open' in game_state.sound_manager.sound_toggles
        assert 'popup_close' in game_state.sound_manager.sound_toggles
        assert 'popup_accept' in game_state.sound_manager.sound_toggles
    
    def test_end_turn_reliability_integration(self):
        """Test end turn reliability improvements work."""
        game_state = GameState(seed=12345)
        
        # Test turn processing state
        assert hasattr(game_state, 'turn_processing')
        assert hasattr(game_state, 'update_turn_processing')
        
        # Test end turn works
        result = game_state.end_turn()
        assert result == True
        assert game_state.turn_processing == True
        
        # Test timer update
        game_state.update_turn_processing()
        # Should work without errors
    
    def test_audio_menu_functionality(self):
        """Test audio menu functionality."""
        # Test audio settings structure
        assert 'master_enabled' in main.audio_settings
        assert 'sfx_volume' in main.audio_settings
        assert 'individual_sounds' in main.audio_settings
        
        # Test audio menu drawing
        screen = pygame.display.get_surface()
        sound_manager = SoundManager()
        
        try:
            draw_audio_menu(screen, 800, 600, 0, main.audio_settings, sound_manager)
            # Should not crash
            assert True
        except Exception as e:
            pytest.fail(f"Audio menu drawing failed: {e}")
    
    def test_audio_menu_navigation(self):
        """Test audio menu keyboard and mouse navigation."""
        # Test keyboard navigation
        main.sounds_menu_selected_item = 0
        main.handle_audio_menu_keyboard(pygame.K_DOWN)
        assert main.sounds_menu_selected_item == 1
        
        # Test mouse navigation
        main.handle_audio_menu_click((400, 300), 800, 600)
        # Should work without errors
    
    def test_onboarding_defensive_code(self):
        """Test onboarding system defensive coding."""
        # Test normal operation
        result = onboarding.get_mechanic_help('action_points_exhausted')
        assert result is not None
        assert isinstance(result, dict)
        assert 'title' in result
        assert 'content' in result
        
        # Test invalid inputs (should not crash)
        assert onboarding.get_mechanic_help(None) is None
        assert onboarding.get_mechanic_help("") is None
        assert onboarding.get_mechanic_help(123) is None
        assert onboarding.get_mechanic_help("nonexistent_mechanic") is None
        
        # Test that errors don't crash
        # The method should handle any internal errors gracefully
        try:
            onboarding.get_mechanic_help("action_points_exhausted")
            assert True  # Should not crash
        except Exception as e:
            pytest.fail(f"Onboarding get_mechanic_help crashed: {e}")
    
    def test_sound_system_integration(self):
        """Test sound system works with all new features."""
        sound_manager = SoundManager()
        
        # Test that all popup sounds exist in toggles
        popup_sounds = ['popup_open', 'popup_close', 'popup_accept']
        for sound in popup_sounds:
            assert sound in sound_manager.sound_toggles
        
        # Test play_sound method works
        try:
            sound_manager.play_sound('popup_accept')
            sound_manager.play_sound('error_beep')
            # Should not crash even if audio unavailable
            assert True
        except Exception as e:
            pytest.fail(f"Sound playing failed: {e}")
    
    def test_config_persistence_integration(self):
        """Test that audio settings can be persisted."""
        from config_manager import get_current_config
        
        config = get_current_config()
        
        # Should have audio section
        assert 'audio' in config
        assert 'sound_enabled' in config['audio']
        
        # Audio settings should be accessible
        assert isinstance(main.audio_settings, dict)
    
    def test_no_import_errors(self):
        """Test that all new imports work correctly."""
        # Test UI imports
        from ui import draw_turn_transition_overlay, draw_audio_menu
        
        # Test that functions are callable
        assert callable(draw_turn_transition_overlay)
        assert callable(draw_audio_menu)
        
        # Test main module imports all work
        import main
        assert hasattr(main, 'audio_settings')
        assert hasattr(main, 'sounds_menu_selected_item')


class TestGameLaunchStability:
    """Test that all improvements don't break game launch."""
    
    def test_game_state_creation(self):
        """Test game state creation with all improvements."""
        try:
            game_state = GameState(seed=12345)
            
            # Check all new attributes exist
            assert hasattr(game_state, 'turn_processing')
            assert hasattr(game_state, 'turn_processing_timer')
            assert hasattr(game_state, 'sound_manager')
            
            # Check methods exist
            assert hasattr(game_state, 'end_turn')
            assert hasattr(game_state, 'update_turn_processing')
            
            assert True
        except Exception as e:
            pytest.fail(f"Game state creation failed: {e}")
    
    def test_main_module_loading(self):
        """Test main module loads without errors."""
        try:
            import main
            
            # Check critical variables exist
            assert hasattr(main, 'audio_settings')
            assert hasattr(main, 'tutorial_choice_selected_item')
            assert hasattr(main, 'sounds_menu_selected_item')
            
            assert True
        except Exception as e:
            pytest.fail(f"Main module loading failed: {e}")
    
    def test_ui_module_enhancements(self):
        """Test UI module has all new functions."""
        from ui import (draw_tutorial_choice, draw_turn_transition_overlay, 
                        draw_audio_menu, draw_first_time_help)
        
        # All functions should be callable
        for func in [draw_tutorial_choice, draw_turn_transition_overlay, 
                     draw_audio_menu, draw_first_time_help]:
            assert callable(func)
    
    def test_onboarding_stability(self):
        """Test onboarding system is stable and defensive."""
        from onboarding import onboarding
        
        # Should handle all edge cases gracefully
        test_cases = [
            'action_points_exhausted',
            'nonexistent_mechanic',
            '',
            None,
            123,
            [],
            {}
        ]
        
        for test_case in test_cases:
            try:
                result = onboarding.get_mechanic_help(test_case)
                # Should either return valid dict or None, never crash
                assert result is None or (isinstance(result, dict) and 'title' in result)
            except Exception as e:
                pytest.fail(f"Onboarding failed for input {test_case}: {e}")


class TestFullFeatureIntegration:
    """Test all features working together in realistic scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        pygame.init()
        pygame.display.set_mode((800, 600), pygame.NOFRAME)
    
    def test_complete_tutorial_choice_flow(self):
        """Test complete tutorial choice flow with all improvements."""
        # Reset state
        main.tutorial_choice_selected_item = 0
        main.tutorial_enabled = False
        
        # Test keyboard navigation
        main.handle_tutorial_choice_keyboard(pygame.K_DOWN)  # Select "No"
        assert main.tutorial_choice_selected_item == 1
        
        # Test selection via Enter
        main.handle_tutorial_choice_keyboard(pygame.K_RETURN)
        assert main.tutorial_enabled == False
        assert main.current_state == 'game'
    
    def test_complete_audio_menu_flow(self):
        """Test complete audio menu flow."""
        # Start in audio menu
        main.current_state = 'sounds_menu'
        main.sounds_menu_selected_item = 0
        
        # Test master toggle
        original_enabled = main.audio_settings['master_enabled']
        main.handle_audio_menu_keyboard(pygame.K_RETURN)
        assert main.audio_settings['master_enabled'] != original_enabled
        
        # Test navigation
        main.handle_audio_menu_keyboard(pygame.K_DOWN)
        assert main.sounds_menu_selected_item == 1
        
        # Test volume adjustment
        main.handle_audio_menu_keyboard(pygame.K_RIGHT)
        # Should work without errors
    
    def test_complete_popup_flow(self):
        """Test complete popup flow with all improvements."""
        game_state = GameState(seed=12345)
        
        # Trigger action points exhausted condition
        game_state.action_points = 0
        
        # Should be able to show popup
        if onboarding.should_show_mechanic_help('action_points_exhausted'):
            help_content = onboarding.get_mechanic_help('action_points_exhausted')
            assert help_content is not None
            assert 'title' in help_content
            assert help_content['title'] == 'No Action Points Remaining'
    
    def test_complete_end_turn_flow(self):
        """Test complete end turn flow with all improvements."""
        game_state = GameState(seed=12345)
        
        # Test normal end turn
        initial_turn = game_state.turn
        result = game_state.end_turn()
        assert result == True
        assert game_state.turn == initial_turn + 1
        assert game_state.turn_processing == True
        
        # Test rejected end turn during processing
        result2 = game_state.end_turn()
        assert result2 == False
        
        # Complete processing
        while game_state.turn_processing:
            game_state.update_turn_processing()
        
        # Should be ready for next turn
        assert game_state.turn_processing == False