'''
Input Event Management System - Extracted from main.py monolith

This module handles all keyboard event processing, extracted from the massive
main.py event handling section to improve maintainability and testability.

Key functionality:
- End turn keyboard handling (spacebar/enter)
- Dialog dismiss handling (ESC, arrows, backspace)
- Tutorial and onboarding navigation
- Action shortcuts and hotkeys
- Debug and development keys
- Modal blocking condition management

Following patterns established in:
- MediaPRSystemManager for clean extraction
- DialogManager for state management
- TurnManager for processing logic
'''

from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING
import pygame
from enum import Enum

if TYPE_CHECKING:
    from src.core.game_state import GameState


class KeyEventResult(Enum):
    '''Results of key event processing.'''
    CONSUMED = 'consumed'          # Event was handled, don't process further
    NOT_HANDLED = 'not_handled'    # Event not handled by this manager
    BLOCKED = 'blocked'            # Event was blocked by modal state
    ERROR = 'error'                # Error occurred during processing


class InputEventManager:
    '''
    Centralized keyboard event management for P(Doom).
    
    Handles all keyboard input processing with proper event consumption tracking,
    modal blocking logic, and clean separation from UI rendering concerns.
    '''
    
    def __init__(self, game_state: 'GameState') -> None:
        '''Initialize the input event manager.
        
        Args:
            game_state: Reference to the main game state for accessing game data
        '''
        self.game_state = game_state
        
        # Event consumption tracking
        self.last_consumed_event_time = 0
        self.event_consumption_timeout = 100  # milliseconds
        
        # Escape handling state (for quit confirmation)
        self.escape_count = 0
        self.escape_timer = 0
        self.escape_threshold = 3
        self.escape_timeout = 2000  # 2 seconds
    
    def handle_keydown_event(self, event: pygame.event.Event, 
                           first_time_help_content: Any,
                           onboarding_manager: Any,
                           overlay_handlers: Dict[str, Any]) -> KeyEventResult:
        '''
        Main entry point for handling keyboard events.
        
        Args:
            event: pygame keyboard event
            first_time_help_content: Current help popup content (if any)
            onboarding_manager: Tutorial/onboarding system
            overlay_handlers: Dictionary of overlay management functions
            
        Returns:
            KeyEventResult indicating how the event was processed
        '''
        if not self.game_state:
            return KeyEventResult.ERROR
        
        # Help key (H) - always available regardless of modal state
        if event.key == pygame.K_h:
            return self._handle_help_key(overlay_handlers)
        
        # Tutorial keyboard handling (takes precedence when active)
        if onboarding_manager and onboarding_manager.show_tutorial_overlay:
            return self._handle_tutorial_keys(event, onboarding_manager)
        
        # First-time help popup handling
        if first_time_help_content:
            return self._handle_help_popup_keys(event, first_time_help_content, overlay_handlers)
        
        # Dialog dismiss handling (ESC, arrows, backspace for various dialogs)
        dialog_result = self._handle_dialog_dismiss_keys(event)
        if dialog_result != KeyEventResult.NOT_HANDLED:
            return dialog_result
        
        # Main menu toggle (M key)
        if event.key == pygame.K_m and self._is_in_game():
            return self._handle_menu_key(overlay_handlers)
        
        # Screenshot functionality ([ key)
        if event.key == pygame.K_LEFTBRACKET:
            return self._handle_screenshot_key()
        
        # Debug console toggle
        if self._handle_debug_console_keypress(event.key):
            return KeyEventResult.CONSUMED
        
        # Dev tools menu (F11)
        if event.key == pygame.K_F11:
            return self._handle_dev_tools_key()
        
        # Escape handling (quit confirmation system)
        if event.key == pygame.K_ESCAPE:
            return self._handle_escape_key()
        
        # Enter to confirm quit (when multiple escapes pressed)
        if event.key == pygame.K_RETURN and self.escape_count >= self.escape_threshold - 1:
            return self._handle_quit_confirmation()
        
        # End turn handling (spacebar/enter) - CRITICAL for game flow
        end_turn_result = self._handle_end_turn_keys(event, first_time_help_content, onboarding_manager)
        if end_turn_result != KeyEventResult.NOT_HANDLED:
            return end_turn_result
        
        # Action shortcuts and regular game controls
        if not onboarding_manager.show_tutorial_overlay:
            return self._handle_game_keys(event, overlay_handlers)
        
        return KeyEventResult.NOT_HANDLED
    
    def _handle_help_key(self, overlay_handlers: Dict[str, Any]) -> KeyEventResult:
        '''Handle help key (H) - always available.'''
        try:
            load_markdown_file = overlay_handlers.get('load_markdown_file')
            push_navigation_state = overlay_handlers.get('push_navigation_state')
            
            if load_markdown_file and push_navigation_state:
                overlay_content = load_markdown_file('docs/PLAYERGUIDE.md')
                # Set overlay state in handlers
                overlay_handlers['overlay_content'] = overlay_content
                overlay_handlers['overlay_title'] = 'Player Guide'
                push_navigation_state('overlay')
                return KeyEventResult.CONSUMED
        except Exception:
            pass
        return KeyEventResult.ERROR
    
    def _handle_tutorial_keys(self, event: pygame.event.Event, 
                            onboarding_manager: Any) -> KeyEventResult:
        '''Handle keyboard input during tutorial/onboarding.'''
        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # Advance tutorial step
            onboarding_manager.advance_stepwise_tutorial()
            return KeyEventResult.CONSUMED
        elif event.key == pygame.K_BACKSPACE:
            # Go back in tutorial
            onboarding_manager.go_back_stepwise_tutorial()
            return KeyEventResult.CONSUMED
        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_s:
            # Skip tutorial (ESC or S key)
            onboarding_manager.dismiss_tutorial()
            return KeyEventResult.CONSUMED
        
        return KeyEventResult.NOT_HANDLED
    
    def _handle_help_popup_keys(self, event: pygame.event.Event, 
                              first_time_help_content: Any,
                              overlay_handlers: Dict[str, Any]) -> KeyEventResult:
        '''Handle keyboard input for help popups.'''
        if event.key == pygame.K_ESCAPE:
            # Close help popup
            if overlay_handlers.get('current_help_mechanic'):
                onboarding = overlay_handlers.get('onboarding')
                if onboarding:
                    onboarding.mark_mechanic_seen(overlay_handlers['current_help_mechanic'])
            
            # Play sound
            if hasattr(self.game_state, 'sound_manager'):
                self.game_state.sound_manager.play_sound('popup_close')
            
            # Clear help state
            overlay_handlers['first_time_help_content'] = None
            overlay_handlers['first_time_help_close_button'] = None
            overlay_handlers['current_help_mechanic'] = None
            return KeyEventResult.CONSUMED
            
        elif event.key == pygame.K_RETURN:
            # Accept help popup
            if overlay_handlers.get('current_help_mechanic'):
                onboarding = overlay_handlers.get('onboarding')
                if onboarding:
                    onboarding.mark_mechanic_seen(overlay_handlers['current_help_mechanic'])
            
            # Play sound
            if hasattr(self.game_state, 'sound_manager'):
                self.game_state.sound_manager.play_sound('popup_accept')
            
            # Clear help state
            overlay_handlers['first_time_help_content'] = None
            overlay_handlers['first_time_help_close_button'] = None
            overlay_handlers['current_help_mechanic'] = None
            return KeyEventResult.CONSUMED
        
        return KeyEventResult.NOT_HANDLED
    
    def _handle_dialog_dismiss_keys(self, event: pygame.event.Event) -> KeyEventResult:
        '''Handle dialog dismiss keys (ESC, arrows, backspace).'''
        dismiss_keys = [pygame.K_LEFT, pygame.K_BACKSPACE, pygame.K_ESCAPE]
        
        if event.key not in dismiss_keys:
            return KeyEventResult.NOT_HANDLED
        
        # Check each dialog type and dismiss if active
        dialog_dismissed = False
        
        # Hiring dialog
        if getattr(self.game_state, 'pending_hiring_dialog', None):
            self.game_state.dismiss_hiring_dialog()
            dialog_dismissed = True
        
        # Intelligence dialog
        elif getattr(self.game_state, 'pending_intelligence_dialog', None):
            self.game_state.dismiss_intelligence_dialog()
            dialog_dismissed = True
        
        # Fundraising dialog
        elif getattr(self.game_state, 'pending_fundraising_dialog', None):
            self.game_state.dismiss_fundraising_dialog()
            dialog_dismissed = True
        
        # Research dialog
        elif getattr(self.game_state, 'pending_research_dialog', None):
            self.game_state.dismiss_research_dialog()
            dialog_dismissed = True
        
        if dialog_dismissed:
            # Play popup close sound
            if hasattr(self.game_state, 'sound_manager'):
                self.game_state.sound_manager.play_sound('popup_close')
            return KeyEventResult.CONSUMED
        
        return KeyEventResult.NOT_HANDLED
    
    def _handle_menu_key(self, overlay_handlers: Dict[str, Any]) -> KeyEventResult:
        '''Handle main menu key (M) - toggle pause/main menu.'''
        if self._is_in_game():
            overlay_handlers['current_state'] = 'escape_menu'
            return KeyEventResult.CONSUMED
        return KeyEventResult.NOT_HANDLED
    
    def _handle_screenshot_key(self) -> KeyEventResult:
        '''Handle screenshot key ([) - save current screen.'''
        try:
            import datetime
            import os
            
            # Create screenshots directory if it doesn't exist
            screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Generate timestamp for filename
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = os.path.join(screenshots_dir, f'pdoom_screenshot_{timestamp}.png')
            
            # Save the current screen (this needs to be handled by caller)
            # Note: Screen saving needs to be done by the main game loop
            
            # Play UI sound if available
            if hasattr(self.game_state, 'sound_manager'):
                self.game_state.sound_manager.play_sound('ui_accept')
            
            return KeyEventResult.CONSUMED
        except Exception:
            return KeyEventResult.ERROR
    
    def _handle_debug_console_keypress(self, key: int) -> bool:
        '''Handle debug console toggle key. Returns True if handled.'''
        try:
            # Import debug console handler (if available)
            # This is a placeholder for the actual debug console implementation
            return False
        except ImportError:
            return False
    
    def _handle_dev_tools_key(self) -> KeyEventResult:
        '''Handle dev tools key (F11) - only available in dev mode.'''
        try:
            from src.services.dev_mode import is_dev_mode_enabled
            if is_dev_mode_enabled():
                # Future: Open dev tools menu
                if self.game_state:
                    self.game_state.add_message('System: Dev tools menu not yet implemented (F11)')
                    if hasattr(self.game_state, 'sound_manager'):
                        self.game_state.sound_manager.play_sound('error_beep')
                return KeyEventResult.CONSUMED
        except ImportError:
            pass
        return KeyEventResult.NOT_HANDLED
    
    def _handle_escape_key(self) -> KeyEventResult:
        '''Handle escape key - quit confirmation system.'''
        current_time = pygame.time.get_ticks()
        
        # Reset escape count if too much time has passed
        if current_time - self.escape_timer > self.escape_timeout:
            self.escape_count = 0
        
        self.escape_count += 1
        self.escape_timer = current_time
        
        if self.escape_count >= self.escape_threshold:
            # Show quit confirmation after multiple escapes
            return KeyEventResult.CONSUMED  # Caller should handle state change
        else:
            # First few escapes - show pause/menu hint
            if hasattr(self.game_state, 'messages'):
                remaining = self.escape_threshold - self.escape_count
                if remaining == 1:
                    self.game_state.add_message(f'Press ESCAPE {remaining} more time to access quit menu, or press ENTER to confirm quit')
                else:
                    self.game_state.add_message(f'Press ESCAPE {remaining} more times to access quit menu')
            
            # Play UI sound
            if hasattr(self.game_state, 'sound_manager'):
                self.game_state.sound_manager.play_sound('ui_click')
            
            return KeyEventResult.CONSUMED
    
    def _handle_quit_confirmation(self) -> KeyEventResult:
        '''Handle quit confirmation (ENTER after multiple escapes).'''
        # This should trigger quit - caller handles the actual quit
        return KeyEventResult.CONSUMED
    
    def _handle_end_turn_keys(self, event: pygame.event.Event, 
                            first_time_help_content: Any,
                            onboarding_manager: Any) -> KeyEventResult:
        '''Handle end turn keys (spacebar/enter) - CRITICAL for game flow.'''
        if self.game_state.game_over:
            return KeyEventResult.NOT_HANDLED
        
        # Get configured end turn key
        try:
            from src.services.keybinding_manager import keybinding_manager
            end_turn_key = keybinding_manager.get_key_for_action('end_turn')
        except ImportError:
            end_turn_key = pygame.K_SPACE  # fallback
        
        # Check if this is an end turn key
        is_end_turn_key = (event.key == end_turn_key or 
                          (event.key == pygame.K_RETURN and end_turn_key == pygame.K_SPACE))
        
        if not is_end_turn_key:
            return KeyEventResult.NOT_HANDLED
        
        # Check blocking conditions
        blocking_conditions = [
            first_time_help_content,  # Help overlay is blocking
            getattr(self.game_state, 'pending_hiring_dialog', None),
            getattr(self.game_state, 'pending_fundraising_dialog', None),
            getattr(self.game_state, 'pending_research_dialog', None),
            getattr(self.game_state, 'pending_intelligence_dialog', None),
            onboarding_manager and onboarding_manager.show_tutorial_overlay
        ]
        
        if any(blocking_conditions):
            # Provide clear feedback about why end turn is blocked
            self._provide_end_turn_blocking_feedback(
                first_time_help_content, onboarding_manager
            )
            return KeyEventResult.BLOCKED
        
        # Check for popup events - allow end turn but give feedback
        if (hasattr(self.game_state, 'pending_popup_events') and 
            self.game_state.pending_popup_events):
            self.game_state.messages.append('Please resolve the pending events before ending turn')
            if hasattr(self.game_state, 'sound_manager'):
                self.game_state.sound_manager.play_sound('error_beep')
            return KeyEventResult.BLOCKED
        
        # Try to end turn
        if not self.game_state.end_turn():
            # Turn was rejected (already processing or other reason)
            return KeyEventResult.BLOCKED
        
        return KeyEventResult.CONSUMED
    
    def _provide_end_turn_blocking_feedback(self, first_time_help_content: Any,
                                          onboarding_manager: Any) -> None:
        '''Provide clear feedback about why end turn is blocked.'''
        if first_time_help_content:
            self.game_state.add_message('Close the help popup first (ESC or click X)')
        elif getattr(self.game_state, 'pending_hiring_dialog', None):
            self.game_state.add_message('Close the hiring dialog first (ESC or click outside)')
        elif getattr(self.game_state, 'pending_fundraising_dialog', None):
            self.game_state.add_message('Close the funding dialog first (ESC or click outside)')
        elif getattr(self.game_state, 'pending_research_dialog', None):
            self.game_state.add_message('Close the research dialog first (ESC or click outside)')
        elif getattr(self.game_state, 'pending_intelligence_dialog', None):
            self.game_state.add_message('Close the intelligence dialog first (ESC or click outside)')
        elif onboarding_manager and onboarding_manager.show_tutorial_overlay:
            self.game_state.add_message('Complete or skip the tutorial step first')
        
        if hasattr(self.game_state, 'sound_manager'):
            self.game_state.sound_manager.play_sound('error_beep')
    
    def _handle_game_keys(self, event: pygame.event.Event,
                         overlay_handlers: Dict[str, Any]) -> KeyEventResult:
        '''Handle regular game keys (action shortcuts, etc.).'''
        # Action shortcuts using customizable keybindings
        if self._is_in_game() and not self.game_state.game_over:
            try:
                from src.services.keybinding_manager import keybinding_manager
                
                # Check if this key is bound to an action
                for action_index in range(min(9, len(self.game_state.actions))):
                    action_key = keybinding_manager.get_action_number_key(action_index)
                    if action_key and event.key == action_key:
                        # Check if this would be an undo operation
                        was_undo = action_index in self.game_state.selected_gameplay_actions
                        
                        # Try to execute the action
                        success = self.game_state.execute_gameplay_action_by_keyboard(action_index)
                        if success and not was_undo:
                            # Play AP spend sound for successful new selections (not undos)
                            if hasattr(self.game_state, 'sound_manager'):
                                self.game_state.sound_manager.play_ap_spend_sound()
                        return KeyEventResult.CONSUMED
            except ImportError:
                pass
        
        # Additional game-specific keys
        if event.key == pygame.K_c:
            # Clear stuck popup events
            if self.game_state.clear_stuck_popup_events():
                self.game_state.add_message('Emergency UI cleanup: Stuck events cleared')
            else:
                self.game_state.add_message('No stuck popup events found')
            return KeyEventResult.CONSUMED
        
        # Arrow key scrolling for event log
        if (self.game_state and 
            getattr(self.game_state, 'scrollable_event_log_enabled', False)):
            if event.key == pygame.K_UP:
                self.game_state.event_log_scroll_offset = max(
                    0, self.game_state.event_log_scroll_offset - 1
                )
                return KeyEventResult.CONSUMED
            elif event.key == pygame.K_DOWN:
                max_scroll = max(0, len(self.game_state.event_log_history) + 
                               len(self.game_state.messages) - 7)
                self.game_state.event_log_scroll_offset = min(
                    max_scroll, self.game_state.event_log_scroll_offset + 1
                )
                return KeyEventResult.CONSUMED
        
        return KeyEventResult.NOT_HANDLED
    
    def _is_in_game(self) -> bool:
        '''Check if we're currently in the main game state.'''
        # This would need to be passed in or accessed via overlay_handlers
        # For now, assume we're in game if we have a valid game_state
        return self.game_state is not None
    
    def get_escape_count(self) -> int:
        '''Get current escape key count for quit confirmation.'''
        return self.escape_count
    
    def should_show_escape_menu(self) -> bool:
        '''Check if escape menu should be shown.'''
        return self.escape_count >= self.escape_threshold
    
    def should_quit_game(self) -> bool:
        '''Check if game should quit (for ENTER confirmation).'''
        return self.escape_count >= self.escape_threshold - 1
    
    def reset_escape_state(self) -> None:
        '''Reset escape key state.'''
        self.escape_count = 0
        self.escape_timer = 0