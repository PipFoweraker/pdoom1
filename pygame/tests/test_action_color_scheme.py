# !/usr/bin/env python3
'''
Test suite for P(Doom) action color-coding system.

Tests the comprehensive color scheme functionality implemented across both
Traditional UI (tutorial mode) and Compact UI (non-tutorial mode).

This ensures consistent visual categorization of actions by type:
- Core Actions (blue-grey): Community, Staff management
- Economic Actions (green): Fundraising, Compute purchasing  
- Research Actions (blue): Research activities, Safety work
- Intelligence Actions (purple): Intelligence operations
- Media Actions (orange): Media & PR activities
- Technical Actions (teal): Infrastructure, Technical debt
- Special Actions (red): Search, Safety audits
'''

import unittest
from src.ui.compact_ui import get_action_color_scheme
from src.core.game_state import GameState


class TestActionColorScheme(unittest.TestCase):
    '''Test the action color scheme function and categorization logic.'''

    def setUp(self):
        '''Set up test fixtures.'''
        self.game_state = GameState('test-color-scheme')
        
    def test_color_scheme_structure(self):
        '''Test that color schemes have the correct structure.'''
        test_actions = [
            'Grow Community', 'Fundraising Options', 'Research Options',
            'Intelligence', 'Media & PR', 'Technical Debt', 'Safety Audit',
            'Unknown Action'
        ]
        
        for action in test_actions:
            with self.subTest(action=action):
                colors = get_action_color_scheme(action)
                
                # Verify required keys exist
                self.assertIn('normal', colors, f'Missing 'normal' color for {action}')
                self.assertIn('hover', colors, f'Missing 'hover' color for {action}')
                self.assertIn('border', colors, f'Missing 'border' color for {action}')
                
                # Verify color format (RGB tuples)
                for color_type, color_value in colors.items():
                    self.assertIsInstance(color_value, tuple, f'{action} {color_type} not a tuple')
                    self.assertEqual(len(color_value), 3, f'{action} {color_type} not RGB tuple')
                    
                    for component in color_value:
                        self.assertIsInstance(component, int, f'{action} {color_type} component not int')
                        self.assertGreaterEqual(component, 0, f'{action} {color_type} component < 0')
                        self.assertLessEqual(component, 255, f'{action} {color_type} component > 255')
    
    def test_hover_brightness_progression(self):
        '''Test that hover colors are lighter than normal colors.'''
        test_actions = ['Grow Community', 'Fundraising Options', 'Research Options']
        
        for action in test_actions:
            with self.subTest(action=action):
                colors = get_action_color_scheme(action)
                normal_brightness = sum(colors['normal'])
                hover_brightness = sum(colors['hover'])
                
                self.assertGreaterEqual(
                    hover_brightness, normal_brightness,
                    f'{action} hover ({hover_brightness}) not lighter than normal ({normal_brightness})'
                )
    
    def test_core_action_categorization(self):
        '''Test that core actions get blue-grey colors.'''
        core_actions = ['Grow Community', 'Hire Staff', 'Hire Manager']
        expected_normal = (70, 90, 120)
        expected_hover = (90, 110, 140)
        
        for action in core_actions:
            with self.subTest(action=action):
                colors = get_action_color_scheme(action)
                self.assertEqual(colors['normal'], expected_normal)
                self.assertEqual(colors['hover'], expected_hover)
    
    def test_economic_action_categorization(self):
        '''Test that economic actions get green colors.'''
        economic_actions = ['Fundraising Options', 'Buy Compute', 'Advanced Funding']
        expected_normal = (60, 100, 70)
        expected_hover = (80, 120, 90)
        
        for action in economic_actions:
            with self.subTest(action=action):
                colors = get_action_color_scheme(action)
                self.assertEqual(colors['normal'], expected_normal)
                self.assertEqual(colors['hover'], expected_hover)
    
    def test_research_action_categorization(self):
        '''Test that research actions get blue colors.'''
        research_actions = ['Research Options', 'Safety Research', 'Team Building']
        expected_normal = (60, 80, 120)
        expected_hover = (80, 100, 140)
        
        for action in research_actions:
            with self.subTest(action=action):
                colors = get_action_color_scheme(action)
                self.assertEqual(colors['normal'], expected_normal)
                self.assertEqual(colors['hover'], expected_hover)
    
    def test_special_action_categorization(self):
        '''Test that special actions get appropriate unique colors.'''
        test_cases = [
            ('Intelligence', (90, 70, 120)),    # Purple
            ('Media & PR', (120, 80, 50)),      # Orange  
            ('Technical Debt', (50, 100, 100)), # Teal
            ('Safety Audit', (100, 60, 60))     # Red
        ]
        
        for action, expected_normal in test_cases:
            with self.subTest(action=action):
                colors = get_action_color_scheme(action)
                self.assertEqual(colors['normal'], expected_normal)
    
    def test_default_fallback(self):
        '''Test that unknown actions get default colors.'''
        unknown_actions = ['Unknown Action', 'Random Thing', '']
        expected_normal = (70, 70, 90)
        expected_hover = (90, 90, 110)
        
        for action in unknown_actions:
            with self.subTest(action=action):
                colors = get_action_color_scheme(action)
                self.assertEqual(colors['normal'], expected_normal)
                self.assertEqual(colors['hover'], expected_hover)


class TestGameActionsColorIntegration(unittest.TestCase):
    '''Test color system integration with actual game actions.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.game_state = GameState('test-game-integration')
        
    def test_all_game_actions_have_colors(self):
        '''Test that all game actions return valid color schemes.'''
        actions = self.game_state.gameplay_actions
        self.assertGreater(len(actions), 0, 'No actions available for testing')
        
        for i, action in enumerate(actions):
            action_name = action.get('name', f'Action {i}')
            with self.subTest(action=action_name):
                colors = get_action_color_scheme(action_name)
                
                # Verify structure
                self.assertIn('normal', colors)
                self.assertIn('hover', colors) 
                self.assertIn('border', colors)
                
                # Verify all colors are valid RGB tuples
                for color_key, color_value in colors.items():
                    self.assertIsInstance(color_value, tuple)
                    self.assertEqual(len(color_value), 3)
                    self.assertTrue(all(isinstance(c, int) and 0 <= c <= 255 for c in color_value))
    
    def test_color_distribution(self):
        '''Test that actions are distributed across different color categories.'''
        actions = self.game_state.gameplay_actions
        color_categories = set()
        
        for action in actions:
            action_name = action.get('name', '')
            colors = get_action_color_scheme(action_name)
            
            # Categorize by dominant color component
            r, g, b = colors['normal']
            if g > r and g > b:
                color_categories.add('green')
            elif b > r and b > g:
                color_categories.add('blue')  
            elif r > 100:
                color_categories.add('orange')
            elif g > 90 and b > 90:
                color_categories.add('teal')
            elif r > g and r > b:
                color_categories.add('red')
            else:
                color_categories.add('purple')
        
        # Should have at least 3 different color categories
        self.assertGreaterEqual(len(color_categories), 3, 
                               f'Actions should span multiple color categories, found: {color_categories}')


class TestVisualFeedbackIntegration(unittest.TestCase):
    '''Test that our color system integrates properly with the visual feedback system.'''
    
    def test_visual_feedback_color_mapping(self):
        '''Test that color schemes can be converted to visual feedback format.'''
        from src.features.visual_feedback import ButtonState
        
        test_action = 'Grow Community'
        colors = get_action_color_scheme(test_action)
        
        # Test all button states
        states_to_test = [ButtonState.NORMAL, ButtonState.HOVER, ButtonState.PRESSED]
        
        for state in states_to_test:
            with self.subTest(state=state):
                # Create custom color mapping like in ui.py
                if state == ButtonState.NORMAL:
                    custom_colors = {
                        'bg': colors['normal'],
                        'border': colors['border'],
                        'text': (255, 255, 255),
                        'shadow': tuple(max(0, c - 30) for c in colors['normal']),
                        'glow': colors['border']
                    }
                elif state == ButtonState.HOVER:
                    custom_colors = {
                        'bg': colors['hover'],
                        'border': colors['border'],
                        'text': (255, 255, 255),
                        'shadow': tuple(max(0, c - 30) for c in colors['hover']),
                        'glow': colors['border']
                    }
                elif state == ButtonState.PRESSED:
                    pressed_bg = tuple(max(0, c - 20) for c in colors['normal'])
                    custom_colors = {
                        'bg': pressed_bg,
                        'border': colors['border'],
                        'text': (255, 255, 255),
                        'shadow': tuple(max(0, c - 30) for c in pressed_bg),
                        'glow': colors['border']
                    }
                
                # Verify all required keys are present
                required_keys = ['bg', 'border', 'text', 'shadow', 'glow']
                for key in required_keys:
                    self.assertIn(key, custom_colors, f'Missing {key} for {state}')
                    self.assertIsInstance(custom_colors[key], tuple)
                    self.assertEqual(len(custom_colors[key]), 3)
    
    def test_shadow_color_generation(self):
        '''Test that shadow colors are properly darkened.'''
        test_actions = ['Grow Community', 'Fundraising Options', 'Intelligence']
        
        for action in test_actions:
            with self.subTest(action=action):
                colors = get_action_color_scheme(action)
                shadow = tuple(max(0, c - 30) for c in colors['normal'])
                
                # Shadow should be darker than normal
                normal_brightness = sum(colors['normal'])
                shadow_brightness = sum(shadow)
                self.assertLess(shadow_brightness, normal_brightness, 
                              f'Shadow not darker than normal for {action}')
                
                # Shadow components should be non-negative
                self.assertTrue(all(c >= 0 for c in shadow), 
                              f'Shadow has negative components for {action}')


class TestUIModesColorConsistency(unittest.TestCase):
    '''Test that color systems work consistently across UI modes.'''
    
    def setUp(self):
        '''Set up test fixtures for both UI modes.'''
        self.traditional_gs = GameState('test-traditional')
        self.traditional_gs.tutorial_enabled = True
        
        self.compact_gs = GameState('test-compact') 
        self.compact_gs.tutorial_enabled = False
    
    def test_color_consistency_across_modes(self):
        '''Test that the same actions get the same colors in both UI modes.'''
        actions_traditional = self.traditional_gs.gameplay_actions
        actions_compact = self.compact_gs.gameplay_actions
        
        # Should have same actions available
        self.assertEqual(len(actions_traditional), len(actions_compact))
        
        for i in range(min(len(actions_traditional), len(actions_compact))):
            traditional_name = actions_traditional[i].get('name', '')
            compact_name = actions_compact[i].get('name', '')
            
            # Same action should have same colors regardless of UI mode
            if traditional_name == compact_name:
                traditional_colors = get_action_color_scheme(traditional_name)
                compact_colors = get_action_color_scheme(compact_name)
                
                self.assertEqual(traditional_colors, compact_colors,
                               f'Color mismatch for {traditional_name} between UI modes')


if __name__ == '__main__':
    unittest.main()