'''
Unit tests for InputEventManager - Keyboard event processing

Tests the extracted keyboard input handling logic to ensure proper
event consumption, blocking condition evaluation, and end turn processing.

Follows patterns established in test_turn6_spacebar_regression.py and
provides comprehensive coverage for the input event management system.
'''

import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame

from src.core.input_event_manager import InputEventManager, KeyEventResult
from src.core.game_state import GameState


class TestInputEventManager(unittest.TestCase):
    '''Unit tests for InputEventManager keyboard event processing.'''
    
    def setUp(self):
        '''Set up test fixtures with mock game state and managers.'''
        self.game_state = Mock(spec=GameState)
        self.game_state.game_over = False
        self.game_state.messages = []
        self.game_state.pending_hiring_dialog = None
        self.game_state.pending_fundraising_dialog = None
        self.game_state.pending_research_dialog = None
        self.game_state.pending_intelligence_dialog = None
        self.game_state.pending_popup_events = []
        
        # Mock sound manager
        self.game_state.sound_manager = Mock()
        self.game_state.add_message = Mock()
        self.game_state.end_turn = Mock(return_value=True)
        
        # Mock methods
        self.game_state.dismiss_hiring_dialog = Mock()
        self.game_state.dismiss_fundraising_dialog = Mock()
        self.game_state.dismiss_research_dialog = Mock()
        self.game_state.dismiss_intelligence_dialog = Mock()
        self.game_state.clear_stuck_popup_events = Mock(return_value=True)
        
        # Action handling mocks
        self.game_state.actions = ['Action 1', 'Action 2', 'Action 3']
        self.game_state.selected_gameplay_actions = set()
        self.game_state.execute_gameplay_action_by_keyboard = Mock(return_value=True)
        
        # Event log mocks
        self.game_state.scrollable_event_log_enabled = False
        self.game_state.event_log_scroll_offset = 0
        self.game_state.event_log_history = []
        
        self.input_manager = InputEventManager(self.game_state)
        
        # Mock overlay handlers
        self.overlay_handlers = {
            'load_markdown_file': Mock(return_value='Test help content'),
            'push_navigation_state': Mock(),
            'overlay_content': None,
            'overlay_title': None,
            'current_state': 'game',
            'first_time_help_content': None,
            'first_time_help_close_button': None,
            'current_help_mechanic': None,
            'onboarding': Mock()
        }
        
        # Mock onboarding manager
        self.onboarding_manager = Mock()
        self.onboarding_manager.show_tutorial_overlay = False
        self.onboarding_manager.advance_stepwise_tutorial = Mock()
        self.onboarding_manager.go_back_stepwise_tutorial = Mock()
        self.onboarding_manager.dismiss_tutorial = Mock()
    
    def _create_keydown_event(self, key: int) -> pygame.event.Event:
        '''Helper to create a keydown event for testing.'''
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = key
        return event
    
    def test_help_key_always_available(self):
        '''Test that help key (H) works regardless of modal state.'''
        event = self._create_keydown_event(pygame.K_h)
        
        # Should work even with blocking dialogs
        self.game_state.pending_hiring_dialog = {'type': 'hiring'}
        
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.overlay_handlers['load_markdown_file'].assert_called_once_with('docs/PLAYERGUIDE.md')
        self.overlay_handlers['push_navigation_state'].assert_called_once_with('overlay')
    
    def test_tutorial_key_handling(self):
        '''Test tutorial keyboard navigation.'''
        self.onboarding_manager.show_tutorial_overlay = True
        
        # Test advance (SPACE)
        event = self._create_keydown_event(pygame.K_SPACE)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.onboarding_manager.advance_stepwise_tutorial.assert_called_once()
        
        # Test back (BACKSPACE)
        event = self._create_keydown_event(pygame.K_BACKSPACE)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.onboarding_manager.go_back_stepwise_tutorial.assert_called_once()
        
        # Test skip (ESC)
        event = self._create_keydown_event(pygame.K_ESCAPE)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.onboarding_manager.dismiss_tutorial.assert_called_once()
    
    def test_help_popup_handling(self):
        '''Test first-time help popup keyboard handling.'''
        first_time_help = {'content': 'Test help'}
        self.overlay_handlers['current_help_mechanic'] = 'test_mechanic'
        
        # Test ESC to close
        event = self._create_keydown_event(pygame.K_ESCAPE)
        result = self.input_manager.handle_keydown_event(
            event, first_time_help, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.game_state.sound_manager.play_sound.assert_called_with('popup_close')
        self.assertIsNone(self.overlay_handlers['first_time_help_content'])
        
        # Test RETURN to accept
        first_time_help = {'content': 'Test help'}
        self.overlay_handlers['current_help_mechanic'] = 'test_mechanic'
        
        event = self._create_keydown_event(pygame.K_RETURN)
        result = self.input_manager.handle_keydown_event(
            event, first_time_help, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.game_state.sound_manager.play_sound.assert_called_with('popup_accept')
    
    def test_dialog_dismiss_keys(self):
        '''Test dialog dismissal with ESC/arrow/backspace keys.'''
        dismiss_keys = [pygame.K_ESCAPE, pygame.K_LEFT, pygame.K_BACKSPACE]
        
        for key in dismiss_keys:
            with self.subTest(key=key):
                # Reset mocks
                self.game_state.dismiss_hiring_dialog.reset_mock()
                self.game_state.sound_manager.reset_mock()
                
                # Set up hiring dialog
                self.game_state.pending_hiring_dialog = {'type': 'hiring'}
                
                event = self._create_keydown_event(key)
                result = self.input_manager.handle_keydown_event(
                    event, None, self.onboarding_manager, self.overlay_handlers
                )
                
                self.assertEqual(result, KeyEventResult.CONSUMED)
                self.game_state.dismiss_hiring_dialog.assert_called_once()
                self.game_state.sound_manager.play_sound.assert_called_with('popup_close')
    
    def test_end_turn_key_success(self):
        '''Test successful end turn processing.'''
        with patch('src.services.keybinding_manager.keybinding_manager') as mock_kb:
            mock_kb.get_key_for_action.return_value = pygame.K_SPACE
            
            event = self._create_keydown_event(pygame.K_SPACE)
            result = self.input_manager.handle_keydown_event(
                event, None, self.onboarding_manager, self.overlay_handlers
            )
            
            self.assertEqual(result, KeyEventResult.CONSUMED)
            self.game_state.end_turn.assert_called_once()
    
    def test_end_turn_blocked_by_dialog(self):
        '''Test end turn blocked by active dialog.'''
        with patch('src.services.keybinding_manager.keybinding_manager') as mock_kb:
            mock_kb.get_key_for_action.return_value = pygame.K_SPACE
            
            # Block with hiring dialog
            self.game_state.pending_hiring_dialog = {'type': 'hiring'}
            
            event = self._create_keydown_event(pygame.K_SPACE)
            result = self.input_manager.handle_keydown_event(
                event, None, self.onboarding_manager, self.overlay_handlers
            )
            
            self.assertEqual(result, KeyEventResult.BLOCKED)
            self.game_state.end_turn.assert_not_called()
            self.game_state.add_message.assert_called()
            self.game_state.sound_manager.play_sound.assert_called_with('error_beep')
    
    def test_end_turn_blocked_by_tutorial(self):
        '''Test end turn blocked by active tutorial.'''
        with patch('src.services.keybinding_manager.keybinding_manager') as mock_kb:
            mock_kb.get_key_for_action.return_value = pygame.K_SPACE
            
            # Block with tutorial
            self.onboarding_manager.show_tutorial_overlay = True
            
            event = self._create_keydown_event(pygame.K_SPACE)
            result = self.input_manager.handle_keydown_event(
                event, None, self.onboarding_manager, self.overlay_handlers
            )
            
            # Should be handled by tutorial handler, not end turn
            self.assertEqual(result, KeyEventResult.CONSUMED)
            self.onboarding_manager.advance_stepwise_tutorial.assert_called_once()
            self.game_state.end_turn.assert_not_called()
    
    def test_end_turn_blocked_by_popup_events(self):
        '''Test end turn blocked by pending popup events.'''
        with patch('src.services.keybinding_manager.keybinding_manager') as mock_kb:
            mock_kb.get_key_for_action.return_value = pygame.K_SPACE
            
            # Add pending popup events
            self.game_state.pending_popup_events = [{'type': 'event'}]
            
            event = self._create_keydown_event(pygame.K_SPACE)
            result = self.input_manager.handle_keydown_event(
                event, None, self.onboarding_manager, self.overlay_handlers
            )
            
            self.assertEqual(result, KeyEventResult.BLOCKED)
            self.game_state.end_turn.assert_not_called()
    
    def test_enter_as_alternative_end_turn(self):
        '''Test ENTER as alternative to SPACE for end turn.'''
        with patch('src.services.keybinding_manager.keybinding_manager') as mock_kb:
            mock_kb.get_key_for_action.return_value = pygame.K_SPACE  # Space is primary
            
            event = self._create_keydown_event(pygame.K_RETURN)
            result = self.input_manager.handle_keydown_event(
                event, None, self.onboarding_manager, self.overlay_handlers
            )
            
            self.assertEqual(result, KeyEventResult.CONSUMED)
            self.game_state.end_turn.assert_called_once()
    
    def test_action_shortcuts(self):
        '''Test action shortcuts (1-9 keys).'''
        with patch('src.services.keybinding_manager.keybinding_manager') as mock_kb:
            mock_kb.get_action_number_key.return_value = pygame.K_1
            
            # Not in tutorial mode
            self.onboarding_manager.show_tutorial_overlay = False
            
            event = self._create_keydown_event(pygame.K_1)
            result = self.input_manager.handle_keydown_event(
                event, None, self.onboarding_manager, self.overlay_handlers
            )
            
            self.assertEqual(result, KeyEventResult.CONSUMED)
            self.game_state.execute_gameplay_action_by_keyboard.assert_called_with(0)
    
    def test_action_shortcut_with_sound(self):
        '''Test action shortcut plays sound for new selections.'''
        with patch('src.services.keybinding_manager.keybinding_manager') as mock_kb:
            mock_kb.get_action_number_key.return_value = pygame.K_1
            
            # Not in tutorial, not selected yet
            self.onboarding_manager.show_tutorial_overlay = False
            self.game_state.selected_gameplay_actions = set()  # Not selected
            
            event = self._create_keydown_event(pygame.K_1)
            result = self.input_manager.handle_keydown_event(
                event, None, self.onboarding_manager, self.overlay_handlers
            )
            
            self.assertEqual(result, KeyEventResult.CONSUMED)
            self.game_state.sound_manager.play_ap_spend_sound.assert_called_once()
    
    def test_clear_stuck_events_key(self):
        '''Test 'C' key for clearing stuck popup events.'''
        self.onboarding_manager.show_tutorial_overlay = False
        
        event = self._create_keydown_event(pygame.K_c)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.game_state.clear_stuck_popup_events.assert_called_once()
        self.game_state.add_message.assert_called()
    
    def test_event_log_scrolling(self):
        '''Test arrow key scrolling for event log.'''
        self.onboarding_manager.show_tutorial_overlay = False
        self.game_state.scrollable_event_log_enabled = True
        self.game_state.event_log_history = ['event1', 'event2', 'event3']
        self.game_state.messages = ['msg1', 'msg2']
        self.game_state.event_log_scroll_offset = 1
        
        # Test UP arrow (scroll up)
        event = self._create_keydown_event(pygame.K_UP)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.assertEqual(self.game_state.event_log_scroll_offset, 0)
        
        # Test DOWN arrow (scroll down)
        event = self._create_keydown_event(pygame.K_DOWN)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.assertTrue(self.game_state.event_log_scroll_offset >= 0)
    
    def test_escape_key_progression(self):
        '''Test escape key quit confirmation system.'''
        # First escape
        event = self._create_keydown_event(pygame.K_ESCAPE)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.assertEqual(self.input_manager.get_escape_count(), 1)
        
        # Second escape
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.assertEqual(self.input_manager.get_escape_count(), 2)
        
        # Third escape (should reach threshold)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.assertTrue(self.input_manager.should_show_escape_menu())
    
    def test_quit_confirmation_with_enter(self):
        '''Test ENTER to confirm quit after multiple escapes.'''
        # Simulate multiple escapes
        event = self._create_keydown_event(pygame.K_ESCAPE)
        for _ in range(3):
            self.input_manager.handle_keydown_event(
                event, None, self.onboarding_manager, self.overlay_handlers
            )
        
        # Now test ENTER
        event = self._create_keydown_event(pygame.K_RETURN)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.assertTrue(self.input_manager.should_quit_game())
    
    def test_screenshot_key(self):
        '''Test screenshot key ([) functionality.'''
        event = self._create_keydown_event(pygame.K_LEFTBRACKET)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.game_state.sound_manager.play_sound.assert_called_with('ui_accept')
    
    def test_menu_key(self):
        '''Test menu key (M) for pause/main menu.'''
        event = self._create_keydown_event(pygame.K_m)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.assertEqual(self.overlay_handlers['current_state'], 'escape_menu')
    
    @patch('src.services.dev_mode.is_dev_mode_enabled')
    def test_dev_tools_key_in_dev_mode(self, mock_dev_mode):
        '''Test F11 dev tools key when in dev mode.'''
        mock_dev_mode.return_value = True
        
        event = self._create_keydown_event(pygame.K_F11)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        self.game_state.add_message.assert_called()
        self.game_state.sound_manager.play_sound.assert_called_with('error_beep')
    
    @patch('src.services.dev_mode.is_dev_mode_enabled')
    def test_dev_tools_key_not_in_dev_mode(self, mock_dev_mode):
        '''Test F11 dev tools key when not in dev mode.'''
        mock_dev_mode.return_value = False
        
        event = self._create_keydown_event(pygame.K_F11)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.NOT_HANDLED)
    
    def test_game_over_blocks_end_turn(self):
        '''Test that game over state blocks end turn.'''
        with patch('src.services.keybinding_manager.keybinding_manager') as mock_kb:
            mock_kb.get_key_for_action.return_value = pygame.K_SPACE
            
            self.game_state.game_over = True
            
            event = self._create_keydown_event(pygame.K_SPACE)
            result = self.input_manager.handle_keydown_event(
                event, None, self.onboarding_manager, self.overlay_handlers
            )
            
            self.assertEqual(result, KeyEventResult.NOT_HANDLED)
            self.game_state.end_turn.assert_not_called()
    
    def test_multiple_dialog_dismissal_priority(self):
        '''Test that only one dialog is dismissed per key press.'''
        # Set up multiple dialogs
        self.game_state.pending_hiring_dialog = {'type': 'hiring'}
        self.game_state.pending_fundraising_dialog = {'type': 'fundraising'}
        
        event = self._create_keydown_event(pygame.K_ESCAPE)
        result = self.input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.CONSUMED)
        # Should only call one dismiss method
        total_calls = (self.game_state.dismiss_hiring_dialog.call_count +
                      self.game_state.dismiss_fundraising_dialog.call_count)
        self.assertEqual(total_calls, 1)
    
    def test_invalid_game_state(self):
        '''Test handling with invalid game state.'''
        input_manager = InputEventManager(None)
        
        event = self._create_keydown_event(pygame.K_SPACE)
        result = input_manager.handle_keydown_event(
            event, None, self.onboarding_manager, self.overlay_handlers
        )
        
        self.assertEqual(result, KeyEventResult.ERROR)
    
    def test_escape_timeout_reset(self):
        '''Test that escape count resets after timeout.'''
        with patch('pygame.time.get_ticks') as mock_time:
            # First escape
            mock_time.return_value = 0
            event = self._create_keydown_event(pygame.K_ESCAPE)
            self.input_manager.handle_keydown_event(
                event, None, self.onboarding_manager, self.overlay_handlers
            )
            
            self.assertEqual(self.input_manager.get_escape_count(), 1)
            
            # Long time later (past timeout)
            mock_time.return_value = 3000  # 3 seconds
            self.input_manager.handle_keydown_event(
                event, None, self.onboarding_manager, self.overlay_handlers
            )
            
            # Should have reset and started over
            self.assertEqual(self.input_manager.get_escape_count(), 1)


if __name__ == '__main__':
    unittest.main()