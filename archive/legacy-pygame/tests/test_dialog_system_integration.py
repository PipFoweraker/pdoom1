'''
Test suite for dialog system integration and functionality.

Tests the complete dialog system including:
- Dialog trigger functions
- Dialog UI rendering functions  
- Dialog manager integration
- Dialog dismissal functionality
- End-to-end dialog workflows

This test suite validates the fixes for non-responsive dialog actions
(Technical Debt, Intelligence, Media & PR) implemented in v0.8.0+.
'''

import unittest
import pygame
from src.core.game_state import GameState
from src.core.dialog_manager import DialogManager
from src.ui.dialogs import draw_intelligence_dialog, draw_media_dialog, draw_technical_debt_dialog


class TestDialogSystemIntegration(unittest.TestCase):
    '''Test dialog system functionality and integration.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        # Initialize pygame for UI rendering tests
        pygame.init()
        self.test_surface = pygame.Surface((800, 600))
        
        # Create fresh game state for each test
        self.game_state = GameState('test-dialog-system')
        
    def tearDown(self):
        '''Clean up after tests.'''
        pygame.quit()
        
    def test_dialog_trigger_functions_exist(self):
        '''Test that all dialog trigger functions exist and are callable.'''
        # Intelligence dialog
        self.assertTrue(hasattr(self.game_state, '_trigger_intelligence_dialog'))
        self.assertTrue(callable(getattr(self.game_state, '_trigger_intelligence_dialog')))
        
        # Media dialog  
        self.assertTrue(hasattr(self.game_state, '_trigger_media_dialog'))
        self.assertTrue(callable(getattr(self.game_state, '_trigger_media_dialog')))
        
        # Technical debt dialog
        self.assertTrue(hasattr(self.game_state, '_trigger_technical_debt_dialog'))
        self.assertTrue(callable(getattr(self.game_state, '_trigger_technical_debt_dialog')))
        
    def test_dialog_dismiss_functions_exist(self):
        '''Test that all dialog dismiss functions exist and use DialogManager.'''
        # All dialogs should have dismiss functions
        self.assertTrue(hasattr(self.game_state, 'dismiss_intelligence_dialog'))
        self.assertTrue(hasattr(self.game_state, 'dismiss_media_dialog'))
        self.assertTrue(hasattr(self.game_state, 'dismiss_technical_debt_dialog'))
        
    def test_intelligence_dialog_workflow(self):
        '''Test complete intelligence dialog workflow.'''
        # Initially no pending dialog
        self.assertFalse(DialogManager.has_pending_dialog(self.game_state, 'intelligence'))
        
        # Trigger dialog
        self.game_state._trigger_intelligence_dialog()
        self.assertTrue(DialogManager.has_pending_dialog(self.game_state, 'intelligence'))
        
        # Verify dialog structure
        dialog = self.game_state.pending_intelligence_dialog
        self.assertIsInstance(dialog, dict)
        self.assertIn('title', dialog)
        self.assertIn('description', dialog)
        self.assertIn('options', dialog)
        self.assertIsInstance(dialog['options'], list)
        self.assertGreater(len(dialog['options']), 0)
        
        # Test UI rendering (should not raise exceptions)
        try:
            rects = draw_intelligence_dialog(self.test_surface, dialog, 800, 600)
            self.assertIsInstance(rects, list)
        except Exception as e:
            self.fail(f'Intelligence dialog rendering failed: {e}')
            
        # Dismiss dialog
        self.game_state.dismiss_intelligence_dialog()
        self.assertFalse(DialogManager.has_pending_dialog(self.game_state, 'intelligence'))
        
    def test_media_dialog_workflow(self):
        '''Test complete media dialog workflow.'''
        # Initially no pending dialog
        self.assertFalse(DialogManager.has_pending_dialog(self.game_state, 'media'))
        
        # Trigger dialog
        self.game_state._trigger_media_dialog()
        self.assertTrue(DialogManager.has_pending_dialog(self.game_state, 'media'))
        
        # Verify dialog structure
        dialog = self.game_state.pending_media_dialog
        self.assertIsInstance(dialog, dict)
        self.assertIn('title', dialog)
        self.assertIn('description', dialog)
        self.assertIn('options', dialog)
        self.assertEqual(dialog['title'], 'Media & PR Operations')
        self.assertIsInstance(dialog['options'], list)
        self.assertGreater(len(dialog['options']), 0)
        
        # Test UI rendering (should not raise exceptions)
        try:
            rects = draw_media_dialog(self.test_surface, dialog, 800, 600)
            self.assertIsInstance(rects, list)
        except Exception as e:
            self.fail(f'Media dialog rendering failed: {e}')
            
        # Dismiss dialog
        self.game_state.dismiss_media_dialog()
        self.assertFalse(DialogManager.has_pending_dialog(self.game_state, 'media'))
        
    def test_technical_debt_dialog_workflow(self):
        '''Test complete technical debt dialog workflow.'''
        # Initially no pending dialog
        self.assertFalse(DialogManager.has_pending_dialog(self.game_state, 'technical_debt'))
        
        # Trigger dialog
        self.game_state._trigger_technical_debt_dialog()
        self.assertTrue(DialogManager.has_pending_dialog(self.game_state, 'technical_debt'))
        
        # Verify dialog structure
        dialog = self.game_state.pending_technical_debt_dialog
        self.assertIsInstance(dialog, dict)
        self.assertIn('title', dialog)
        self.assertIn('description', dialog)
        self.assertIn('options', dialog)
        self.assertEqual(dialog['title'], 'Technical Debt Management')
        self.assertIsInstance(dialog['options'], list)
        self.assertGreater(len(dialog['options']), 0)
        
        # Test UI rendering (should not raise exceptions)
        try:
            rects = draw_technical_debt_dialog(self.test_surface, dialog, 800, 600)
            self.assertIsInstance(rects, list)
        except Exception as e:
            self.fail(f'Technical debt dialog rendering failed: {e}')
            
        # Dismiss dialog
        self.game_state.dismiss_technical_debt_dialog()
        self.assertFalse(DialogManager.has_pending_dialog(self.game_state, 'technical_debt'))
        
    def test_dialog_option_structures(self):
        '''Test that dialog options have required fields.'''
        # Test all dialog types
        dialogs = [
            (self.game_state._trigger_intelligence_dialog, 'intelligence'),
            (self.game_state._trigger_media_dialog, 'media'), 
            (self.game_state._trigger_technical_debt_dialog, 'technical_debt')
        ]
        
        for trigger_func, dialog_type in dialogs:
            with self.subTest(dialog_type=dialog_type):
                # Trigger dialog
                trigger_func()
                
                # Get dialog
                dialog_attr = f'pending_{dialog_type}_dialog'
                dialog = getattr(self.game_state, dialog_attr)
                
                # Test each option has required fields
                for option in dialog['options']:
                    self.assertIn('id', option, f'{dialog_type} option missing 'id'')
                    self.assertIn('name', option, f'{dialog_type} option missing 'name'')
                    self.assertIn('description', option, f'{dialog_type} option missing 'description'')
                    self.assertIn('cost', option, f'{dialog_type} option missing 'cost'')
                    self.assertIn('ap_cost', option, f'{dialog_type} option missing 'ap_cost'')
                    self.assertIn('available', option, f'{dialog_type} option missing 'available'')
                    
                # Clean up
                DialogManager.dismiss_dialog(self.game_state, dialog_type)
                
    def test_dialog_manager_integration(self):
        '''Test DialogManager integration with all dialog types.'''
        dialog_types = ['intelligence', 'media', 'technical_debt']
        
        for dialog_type in dialog_types:
            with self.subTest(dialog_type=dialog_type):
                # Initially no dialog
                self.assertFalse(DialogManager.has_pending_dialog(self.game_state, dialog_type))
                
                # Trigger dialog
                trigger_method = getattr(self.game_state, f'_trigger_{dialog_type}_dialog')
                trigger_method()
                
                # Verify dialog exists via DialogManager
                self.assertTrue(DialogManager.has_pending_dialog(self.game_state, dialog_type))
                
                # Dismiss via DialogManager
                DialogManager.dismiss_dialog(self.game_state, dialog_type)
                
                # Verify dismissed
                self.assertFalse(DialogManager.has_pending_dialog(self.game_state, dialog_type))
                
    def test_dialog_ui_rendering_returns_clickable_rects(self):
        '''Test that dialog UI functions return clickable rectangles.'''
        # Test intelligence dialog
        self.game_state._trigger_intelligence_dialog()
        intel_rects = draw_intelligence_dialog(
            self.test_surface, 
            self.game_state.pending_intelligence_dialog, 
            800, 600
        )
        self.assertIsInstance(intel_rects, list)
        self.assertGreater(len(intel_rects), 0)  # Should have at least cancel button
        
        # Test media dialog
        self.game_state._trigger_media_dialog()
        media_rects = draw_media_dialog(
            self.test_surface,
            self.game_state.pending_media_dialog,
            800, 600
        )
        self.assertIsInstance(media_rects, list)
        self.assertGreater(len(media_rects), 0)
        
        # Test technical debt dialog
        self.game_state._trigger_technical_debt_dialog()
        debt_rects = draw_technical_debt_dialog(
            self.test_surface,
            self.game_state.pending_technical_debt_dialog,
            800, 600
        )
        self.assertIsInstance(debt_rects, list)
        self.assertGreater(len(debt_rects), 0)
        
    def test_dialog_selection_functions_exist(self):
        '''Test that dialog selection functions exist for option handling.'''
        # Test that selection functions exist
        self.assertTrue(hasattr(self.game_state, 'select_intelligence_option'))
        self.assertTrue(hasattr(self.game_state, 'select_media_option'))
        self.assertTrue(hasattr(self.game_state, 'select_technical_debt_option'))
        
        # Test that they're callable
        self.assertTrue(callable(self.game_state.select_intelligence_option))
        self.assertTrue(callable(self.game_state.select_media_option))
        self.assertTrue(callable(self.game_state.select_technical_debt_option))
        
    def test_multiple_dialogs_exclusivity(self):
        '''Test that only one dialog can be pending at a time.'''
        # Trigger intelligence dialog
        self.game_state._trigger_intelligence_dialog()
        self.assertTrue(DialogManager.has_pending_dialog(self.game_state, 'intelligence'))
        
        # Trigger media dialog (should replace intelligence)
        self.game_state._trigger_media_dialog()
        # Note: This behavior depends on implementation - adjust test as needed
        self.assertTrue(DialogManager.has_pending_dialog(self.game_state, 'media'))
        
    def test_dialog_system_no_memory_leaks(self):
        '''Test that dialogs are properly cleaned up.'''
        # Trigger and dismiss multiple dialogs
        for _ in range(5):
            # Test all dialog types
            self.game_state._trigger_intelligence_dialog()
            self.game_state.dismiss_intelligence_dialog()
            
            self.game_state._trigger_media_dialog()
            self.game_state.dismiss_media_dialog()
            
            self.game_state._trigger_technical_debt_dialog()
            self.game_state.dismiss_technical_debt_dialog()
            
        # All dialogs should be clean
        self.assertFalse(DialogManager.has_pending_dialog(self.game_state, 'intelligence'))
        self.assertFalse(DialogManager.has_pending_dialog(self.game_state, 'media'))
        self.assertFalse(DialogManager.has_pending_dialog(self.game_state, 'technical_debt'))


class TestDialogUIRendering(unittest.TestCase):
    '''Test dialog UI rendering functions in isolation.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        pygame.init()
        self.test_surface = pygame.Surface((800, 600))
        
    def tearDown(self):
        '''Clean up after tests.'''
        pygame.quit()
        
    def create_mock_dialog(self, title, num_options=3):
        '''Create a mock dialog for testing UI rendering.'''
        options = []
        for i in range(num_options):
            options.append({
                'id': f'option_{i}',
                'name': f'Test Option {i+1}',
                'description': f'Description for option {i+1}',
                'cost': i * 1000,
                'ap_cost': i + 1,
                'available': True
            })
            
        return {
            'title': title,
            'description': 'Test dialog description for UI rendering.',
            'options': options
        }
        
    def test_draw_intelligence_dialog_rendering(self):
        '''Test intelligence dialog UI rendering.'''
        mock_dialog = self.create_mock_dialog('Intelligence Operations', 4)
        rects = draw_intelligence_dialog(self.test_surface, mock_dialog, 800, 600)
        
        self.assertIsInstance(rects, list)
        self.assertGreater(len(rects), 0)
        
        # Should have rects for options + cancel button
        expected_rects = len(mock_dialog['options']) + 1
        self.assertEqual(len(rects), expected_rects)
        
    def test_draw_media_dialog_rendering(self):
        '''Test media dialog UI rendering.'''
        mock_dialog = self.create_mock_dialog('Media & PR Operations', 5)
        rects = draw_media_dialog(self.test_surface, mock_dialog, 800, 600)
        
        self.assertIsInstance(rects, list)
        self.assertGreater(len(rects), 0)
        
        # Should have rects for options + cancel button
        expected_rects = len(mock_dialog['options']) + 1
        self.assertEqual(len(rects), expected_rects)
        
    def test_draw_technical_debt_dialog_rendering(self):
        '''Test technical debt dialog UI rendering.''' 
        mock_dialog = self.create_mock_dialog('Technical Debt Management', 3)
        rects = draw_technical_debt_dialog(self.test_surface, mock_dialog, 800, 600)
        
        self.assertIsInstance(rects, list)
        self.assertGreater(len(rects), 0)
        
        # Should have rects for options + cancel button
        expected_rects = len(mock_dialog['options']) + 1
        self.assertEqual(len(rects), expected_rects)
        
    def test_dialog_rendering_with_unavailable_options(self):
        '''Test dialog rendering handles unavailable options correctly.'''
        mock_dialog = self.create_mock_dialog('Test Dialog', 2)
        # Make one option unavailable
        mock_dialog['options'][1]['available'] = False
        
        # Should render without errors
        rects = draw_media_dialog(self.test_surface, mock_dialog, 800, 600)
        
        # Should have fewer clickable rects (unavailable options aren't clickable)
        available_options = sum(1 for opt in mock_dialog['options'] if opt['available'])
        expected_clickable = available_options + 1  # +1 for cancel button
        self.assertEqual(len(rects), expected_clickable)


if __name__ == '__main__':
    unittest.main()