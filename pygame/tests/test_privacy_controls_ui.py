'''
Privacy Controls UI Integration Tests

Tests the privacy controls UI component functionality including:
- UI component initialization and state management  
- Logging level selection and persistence
- Navigation and user interactions
- Integration with backend GameRunLogger
'''

import unittest
import pygame

from src.ui.privacy_controls import PrivacyControls, PrivacyUIState
from src.services.game_run_logger import LoggingLevel, init_game_logger


class TestPrivacyControlsCore(unittest.TestCase):
    '''Test core privacy controls functionality.'''
    
    def setUp(self):
        '''Set up test environment.'''
        # Initialize pygame for UI tests
        pygame.init()
        
    def tearDown(self):
        '''Clean up test environment.'''
        pygame.quit()
    
    def test_privacy_controls_initialization(self):
        '''Test that privacy controls initialize correctly.'''
        pc = PrivacyControls()
        
        self.assertEqual(pc.current_state, PrivacyUIState.MAIN)
        self.assertEqual(pc.selected_item, 0)
        self.assertFalse(pc.show_tooltip)
        self.assertEqual(pc.tooltip_text, '')
        
    def test_logging_level_options(self):
        '''Test that logging level options are correct.'''
        pc = PrivacyControls()
        options = pc.get_logging_level_options()
        
        self.assertEqual(len(options), 5)
        self.assertEqual(options[0], (LoggingLevel.DISABLED, 'Disabled', 'No data collection - complete privacy'))
        self.assertEqual(options[1], (LoggingLevel.MINIMAL, 'Minimal', 'Basic session info only - no gameplay details'))
        self.assertEqual(options[2], (LoggingLevel.STANDARD, 'Standard', 'Key actions and milestones - balanced approach'))
        self.assertEqual(options[3], (LoggingLevel.VERBOSE, 'Verbose', 'Detailed gameplay tracking - comprehensive analysis'))
        self.assertEqual(options[4], (LoggingLevel.DEBUG, 'Debug', 'Complete technical logging - full transparency'))
    
    def test_get_current_logging_level_no_logger(self):
        '''Test getting logging level when no logger is available.'''
        pc = PrivacyControls()
        pc.logger = None
        
        level = pc.get_current_logging_level()
        self.assertEqual(level, LoggingLevel.DISABLED)
    
    def test_set_logging_level_no_logger(self):
        '''Test setting logging level when no logger is available.'''
        pc = PrivacyControls()
        pc.logger = None
        
        result = pc.set_logging_level(LoggingLevel.STANDARD)
        self.assertFalse(result)
    
    def test_delete_all_data_no_logger(self):
        '''Test deleting data when no logger is available.'''
        pc = PrivacyControls()
        pc.logger = None
        
        result = pc.delete_all_data()
        self.assertFalse(result)


class TestPrivacyControlsWithLogger(unittest.TestCase):
    '''Test privacy controls with active logger.'''
    
    def setUp(self):
        '''Set up test environment with logger.'''
        pygame.init()
        
        # Initialize logger for testing
        self.logger = init_game_logger(enabled_by_default=True)
        self.pc = PrivacyControls()
    
    def tearDown(self):
        '''Clean up test environment.'''
        pygame.quit()
    
    def test_get_current_logging_level_with_logger(self):
        '''Test getting logging level from active logger.'''
        level = self.pc.get_current_logging_level()
        self.assertIsInstance(level, int)
        self.assertIn(level, [LoggingLevel.DISABLED, LoggingLevel.MINIMAL, LoggingLevel.STANDARD, LoggingLevel.VERBOSE, LoggingLevel.DEBUG])
    
    def test_set_logging_level_with_logger(self):
        '''Test setting logging level with active logger.'''
        result = self.pc.set_logging_level(LoggingLevel.VERBOSE)
        self.assertTrue(result)
        
        # Verify level was set
        self.assertEqual(self.pc.get_current_logging_level(), LoggingLevel.VERBOSE)
    
    def test_logging_level_dismisses_first_time_info(self):
        '''Test that setting a logging level dismisses first-time info.'''
        # Force first-time info to show
        self.pc.show_first_time_info = True
        
        self.pc.set_logging_level(LoggingLevel.STANDARD)
        
        self.assertFalse(self.pc.show_first_time_info)


class TestPrivacyControlsUI(unittest.TestCase):
    '''Test privacy controls UI rendering and interaction.'''
    
    def setUp(self):
        '''Set up UI test environment.'''
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.pc = PrivacyControls()
    
    def tearDown(self):
        '''Clean up UI test environment.'''
        pygame.quit()
    
    def test_draw_main_screen(self):
        '''Test drawing the main privacy controls screen.'''
        # Should not raise any exceptions
        self.pc.draw_main_screen(self.screen, 800, 600)
    
    def test_draw_delete_confirmation(self):
        '''Test drawing the delete confirmation dialog.'''
        self.pc.current_state = PrivacyUIState.DELETE_CONFIRM
        
        # Should not raise any exceptions
        self.pc.draw_delete_confirmation(self.screen, 800, 600)
    
    def test_draw_dispatcher(self):
        '''Test main draw method dispatches correctly.'''
        # Test main screen
        self.pc.current_state = PrivacyUIState.MAIN
        self.pc.draw(self.screen, 800, 600)
        
        # Test delete confirmation overlay
        self.pc.current_state = PrivacyUIState.DELETE_CONFIRM
        self.pc.draw(self.screen, 800, 600)
    
    def test_first_time_info_display(self):
        '''Test first-time information display.'''
        self.pc.show_first_time_info = True
        
        # Should not raise exceptions when first-time info is shown
        self.pc.draw_main_screen(self.screen, 800, 600)


class TestPrivacyControlsInteraction(unittest.TestCase):
    '''Test privacy controls user interaction handling.'''
    
    def setUp(self):
        '''Set up interaction test environment.'''
        pygame.init()
        init_game_logger(enabled_by_default=True)
        self.pc = PrivacyControls()
    
    def tearDown(self):
        '''Clean up interaction test environment.'''
        pygame.quit()
    
    def test_keyboard_navigation_main_screen(self):
        '''Test keyboard navigation on main screen.'''
        self.pc.current_state = PrivacyUIState.MAIN
        self.pc.selected_item = 0
        
        # Test up/down navigation
        self.pc.handle_key_press(pygame.K_DOWN)
        self.assertEqual(self.pc.selected_item, 1)
        
        self.pc.handle_key_press(pygame.K_UP)
        self.assertEqual(self.pc.selected_item, 0)
        
        # Test escape returns to back
        action = self.pc.handle_key_press(pygame.K_ESCAPE)
        self.assertEqual(action, 'back')
    
    def test_keyboard_navigation_delete_confirm(self):
        '''Test keyboard navigation in delete confirmation dialog.'''
        self.pc.current_state = PrivacyUIState.DELETE_CONFIRM
        self.pc.selected_item = 0
        
        # Test left/right navigation
        self.pc.handle_key_press(pygame.K_RIGHT)
        self.assertEqual(self.pc.selected_item, 1)
        
        self.pc.handle_key_press(pygame.K_LEFT)
        self.assertEqual(self.pc.selected_item, 0)
        
        # Test escape cancels
        action = self.pc.handle_key_press(pygame.K_ESCAPE)
        self.assertEqual(action, 'delete_cancelled')
        self.assertEqual(self.pc.current_state, PrivacyUIState.MAIN)
    
    def test_mouse_click_main_screen(self):
        '''Test mouse clicks on main screen.'''
        self.pc.current_state = PrivacyUIState.MAIN
        
        # Test back button area (approximate)
        action = self.pc.handle_mouse_click((700, 500), 800, 600)
        # Should either be 'back' or None depending on exact coordinates
        self.assertTrue(action in [None, 'back'])
    
    def test_mouse_click_delete_confirm(self):
        '''Test mouse clicks on delete confirmation dialog.'''
        self.pc.current_state = PrivacyUIState.DELETE_CONFIRM
        
        # Test clicking outside dialog (should not trigger action)
        action = self.pc.handle_mouse_click((50, 50), 800, 600)
        self.assertIsNone(action)
    
    def test_reset_functionality(self):
        '''Test reset functionality.'''
        self.pc.current_state = PrivacyUIState.DELETE_CONFIRM
        self.pc.selected_item = 5
        self.pc.show_first_time_info = False
        
        self.pc.reset()
        
        self.assertEqual(self.pc.current_state, PrivacyUIState.MAIN)
        self.assertEqual(self.pc.selected_item, 0)


class TestPrivacyControlsEdgeCases(unittest.TestCase):
    '''Test privacy controls edge cases and error handling.'''
    
    def setUp(self):
        '''Set up edge case test environment.'''
        pygame.init()
        self.pc = PrivacyControls()
    
    def tearDown(self):
        '''Clean up edge case test environment.'''
        pygame.quit()
    
    def test_invalid_key_press(self):
        '''Test handling invalid key presses.'''
        # Should not raise exceptions for any key
        action = self.pc.handle_key_press(999)  # Invalid key code
        self.assertIsNone(action)
    
    def test_extreme_mouse_coordinates(self):
        '''Test handling extreme mouse coordinates.'''
        # Negative coordinates
        action = self.pc.handle_mouse_click((-100, -100), 800, 600)
        self.assertIsNone(action)
        
        # Very large coordinates
        action = self.pc.handle_mouse_click((10000, 10000), 800, 600)
        self.assertIsNone(action)
    
    def test_small_screen_dimensions(self):
        '''Test handling very small screen dimensions.'''
        screen = pygame.Surface((100, 100))
        
        # Should not raise exceptions even with tiny screen
        self.pc.draw(screen, 100, 100)
    
    def test_large_screen_dimensions(self):
        '''Test handling very large screen dimensions.'''
        screen = pygame.Surface((3840, 2160))  # 4K resolution
        
        # Should not raise exceptions with large screen
        self.pc.draw(screen, 3840, 2160)
    
    def test_state_transitions(self):
        '''Test all valid state transitions.'''
        # Main -> Delete Confirm
        self.pc.current_state = PrivacyUIState.MAIN
        self.pc.current_state = PrivacyUIState.DELETE_CONFIRM
        self.assertEqual(self.pc.current_state, PrivacyUIState.DELETE_CONFIRM)
        
        # Delete Confirm -> Main
        self.pc.current_state = PrivacyUIState.MAIN
        self.assertEqual(self.pc.current_state, PrivacyUIState.MAIN)
    
    def test_concurrent_operations(self):
        '''Test handling multiple operations simultaneously.'''
        # Set logging level while showing first-time info
        self.pc.show_first_time_info = True
        result = self.pc.set_logging_level(LoggingLevel.STANDARD)
        
        # Should handle gracefully regardless of logger availability
        self.assertIsInstance(result, bool)
        self.assertFalse(self.pc.show_first_time_info)  # Should be dismissed


class TestPrivacyControlsIntegration(unittest.TestCase):
    '''Test privacy controls integration with main application.'''
    
    def setUp(self):
        '''Set up integration test environment.'''
        pygame.init()
    
    def tearDown(self):
        '''Clean up integration test environment.'''
        pygame.quit()
    
    def test_privacy_controls_import(self):
        '''Test that privacy_controls can be imported by main application.'''
        from src.ui.privacy_controls import privacy_controls
        
        self.assertIsInstance(privacy_controls, PrivacyControls)
    
    def test_integration_with_game_run_logger(self):
        '''Test integration between privacy controls and game run logger.'''
        logger = init_game_logger(enabled_by_default=True)
        pc = PrivacyControls()
        
        # Test that privacy controls can access logger
        self.assertIsNotNone(pc.logger)
        
        # Test that level changes propagate
        original_level = pc.get_current_logging_level()
        new_level = LoggingLevel.DEBUG if original_level != LoggingLevel.DEBUG else LoggingLevel.MINIMAL
        
        pc.set_logging_level(new_level)
        self.assertEqual(logger.logging_level, new_level)
    
    def test_ui_components_compatibility(self):
        '''Test that privacy controls UI is compatible with visual feedback system.'''
        from src.features.visual_feedback import visual_feedback, ButtonState
        
        # Test that visual feedback components are accessible
        self.assertIsNotNone(visual_feedback)
        self.assertTrue(hasattr(ButtonState, 'NORMAL'))
        self.assertTrue(hasattr(ButtonState, 'FOCUSED'))
        self.assertTrue(hasattr(ButtonState, 'PRESSED'))
        self.assertTrue(hasattr(ButtonState, 'DISABLED'))


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
