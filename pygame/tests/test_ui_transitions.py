import unittest
import sys
import os

# Add the parent directory to the path so we can import game_state
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game_state import GameState


class TestUITransitions(unittest.TestCase):
    '''Test the UI transition system for smooth visual feedback.'''
    
    def setUp(self):
        '''Set up a fresh GameState for each test.'''
        self.game_state = GameState('test_seed')
    
    def test_ui_transitions_initialized(self):
        '''Test that UI transition system is properly initialized.'''
        self.assertTrue(hasattr(self.game_state, 'ui_transitions'))
        self.assertTrue(hasattr(self.game_state, 'upgrade_transitions'))
        self.assertIsInstance(self.game_state.ui_transitions, list)
        self.assertIsInstance(self.game_state.upgrade_transitions, dict)
        self.assertEqual(len(self.game_state.ui_transitions), 0)
        self.assertEqual(len(self.game_state.upgrade_transitions), 0)
    
    def test_create_upgrade_transition(self):
        '''Test that upgrade transitions are created correctly.'''
        # Set up screen dimensions and rectangles
        w, h = 800, 600
        start_rect = (100, 200, 150, 50)  # Button position
        end_rect = (650, 50, 45, 45)     # Icon position
        upgrade_idx = 0
        
        # Create a transition
        transition = self.game_state._create_upgrade_transition(upgrade_idx, start_rect, end_rect)
        
        # Verify transition was created correctly
        self.assertIsNotNone(transition)
        self.assertEqual(transition['type'], 'upgrade_transition')
        self.assertEqual(transition['upgrade_idx'], upgrade_idx)
        self.assertEqual(transition['start_rect'], start_rect)
        self.assertEqual(transition['end_rect'], end_rect)
        self.assertEqual(transition['progress'], 0.0)
        self.assertEqual(transition['duration'], 45)
        self.assertFalse(transition['completed'])
        self.assertGreater(transition['glow_timer'], 0)
        
        # Verify transition was added to lists
        self.assertIn(transition, self.game_state.ui_transitions)
        self.assertIn(upgrade_idx, self.game_state.upgrade_transitions)
        self.assertEqual(self.game_state.upgrade_transitions[upgrade_idx], transition)
    
    def test_transition_progress_advancement(self):
        '''Test that transitions advance correctly over time.'''
        # Create a transition
        w, h = 800, 600
        start_rect = (100, 200, 150, 50)
        end_rect = (650, 50, 45, 45)
        transition = self.game_state._create_upgrade_transition(0, start_rect, end_rect)
        
        initial_progress = transition['progress']
        initial_trail_count = len(transition['trail_points'])
        
        # Update transitions several times
        for _ in range(5):
            self.game_state._update_ui_transitions()
        
        # Verify progress advanced
        self.assertGreater(transition['progress'], initial_progress)
        self.assertGreater(len(transition['trail_points']), initial_trail_count)
        
        # Update until completion (45 frames for enhanced duration)
        for _ in range(45):
            self.game_state._update_ui_transitions()
        
        # Verify transition completed
        self.assertEqual(transition['progress'], 1.0)
        self.assertTrue(transition['completed'])
    
    def test_transition_interpolation(self):
        '''Test that position interpolation works correctly.'''
        start_rect = (100, 200, 150, 50)
        end_rect = (650, 50, 45, 45)
        
        # Test interpolation at various progress points
        pos_0 = self.game_state._interpolate_position(start_rect, end_rect, 0.0)
        pos_50 = self.game_state._interpolate_position(start_rect, end_rect, 0.5)
        pos_100 = self.game_state._interpolate_position(start_rect, end_rect, 1.0)
        
        # Start position should be center of start rect
        expected_start = (175, 225)  # 100 + 150/2, 200 + 50/2
        self.assertEqual(pos_0[0], expected_start[0])
        self.assertEqual(pos_0[1], expected_start[1])
        
        # End position should be center of end rect
        expected_end = (672, 72)  # 650 + 45/2, 50 + 45/2
        self.assertAlmostEqual(pos_100[0], expected_end[0], delta=1)
        self.assertAlmostEqual(pos_100[1], expected_end[1], delta=1)
        
        # Middle position should be roughly between start and end (accounting for arc)
        self.assertGreater(pos_50[0], pos_0[0])
        self.assertLess(pos_50[0], pos_100[0])
        # Y should be higher than both start and end due to arc
        self.assertLess(pos_50[1], min(pos_0[1], pos_100[1]))
    
    def test_trail_fade_effect(self):
        '''Test that trail points fade correctly.'''
        # Create a transition and advance it
        start_rect = (100, 200, 150, 50)
        end_rect = (650, 50, 45, 45)
        transition = self.game_state._create_upgrade_transition(0, start_rect, end_rect)
        
        # Add some trail points
        for _ in range(10):
            self.game_state._update_ui_transitions()
        
        # Check that trail points exist and have alpha values
        trail_points = transition['trail_points']
        self.assertGreater(len(trail_points), 0)
        
        for point in trail_points:
            self.assertIn('alpha', point)
            self.assertIn('pos', point)
            self.assertIn('age', point)
            self.assertGreaterEqual(point['alpha'], 0)
            self.assertLessEqual(point['alpha'], 255)
        
        # Continue updating and verify older points fade
        trail_points[0]['alpha'] if trail_points else 255
        for _ in range(20):
            self.game_state._update_ui_transitions()
        
        # Points should have faded or been removed
        remaining_points = transition['trail_points']
        if remaining_points:
            # If any points remain, they should be newer/brighter
            for point in remaining_points:
                self.assertLessEqual(point['age'], 20)  # Enhanced trail limit
    
    def test_transition_cleanup(self):
        '''Test that completed transitions are cleaned up properly.'''
        # Create a transition
        start_rect = (100, 200, 150, 50)
        end_rect = (650, 50, 45, 45)
        upgrade_idx = 0
        self.game_state._create_upgrade_transition(upgrade_idx, start_rect, end_rect)
        
        # Verify transition exists
        self.assertEqual(len(self.game_state.ui_transitions), 1)
        self.assertIn(upgrade_idx, self.game_state.upgrade_transitions)
        
        # Complete the transition (need more iterations due to enhanced glow timer of 90)
        for _ in range(150):  # 45 for animation + 90+ for glow + buffer
            self.game_state._update_ui_transitions()
        
        # Verify transition was cleaned up
        self.assertEqual(len(self.game_state.ui_transitions), 0)
        self.assertNotIn(upgrade_idx, self.game_state.upgrade_transitions)
    
    def test_upgrade_icon_rect_calculation(self):
        '''Test that upgrade icon rectangles are calculated correctly.'''
        w, h = 800, 600
        
        # Test for first upgrade (no others purchased)
        icon_rect = self.game_state._get_upgrade_icon_rect(0, w, h)
        self.assertEqual(len(icon_rect), 4)  # x, y, width, height
        
        # Icon should be at top right area
        self.assertGreater(icon_rect[0], w // 2)  # Right side of screen
        self.assertLess(icon_rect[1], h // 4)    # Top area of screen
        
        # Purchase an upgrade and test positioning
        self.game_state.upgrades[0]['purchased'] = True
        icon_rect_2 = self.game_state._get_upgrade_icon_rect(1, w, h)
        
        # Second icon should be to the left of first
        self.assertLess(icon_rect_2[0], icon_rect[0])
    
    def test_multiple_transitions(self):
        '''Test that multiple transitions can run simultaneously.'''
        w, h = 800, 600
        
        # Create multiple transitions
        transition1 = self.game_state._create_upgrade_transition(0, (100, 200, 150, 50), (650, 50, 45, 45))
        transition2 = self.game_state._create_upgrade_transition(1, (100, 300, 150, 50), (600, 50, 45, 45))
        
        # Verify both exist
        self.assertEqual(len(self.game_state.ui_transitions), 2)
        self.assertEqual(len(self.game_state.upgrade_transitions), 2)
        
        # Update and verify both progress
        for _ in range(10):
            self.game_state._update_ui_transitions()
        
        self.assertGreater(transition1['progress'], 0)
        self.assertGreater(transition2['progress'], 0)
        self.assertGreater(len(transition1['trail_points']), 0)
        self.assertGreater(len(transition2['trail_points']), 0)


class TestUITransitionIntegration(unittest.TestCase):
    '''Test integration of UI transitions with upgrade purchase system.'''
    
    def setUp(self):
        '''Set up a fresh GameState for each test.'''
        self.game_state = GameState('test_seed')
    
    def test_transition_triggered_on_upgrade_purchase(self):
        '''Test that purchasing an upgrade creates a transition.'''
        # Set sufficient money and simulate screen size
        self.game_state.money = 1000
        w, h = 800, 600
        
        # Get upgrade button position
        upgrade_rects = self.game_state._get_upgrade_rects(w, h)
        upgrade_rect = upgrade_rects[0]
        upgrade = self.game_state.upgrades[0]
        
        # Verify no transitions initially
        self.assertEqual(len(self.game_state.ui_transitions), 0)
        
        # Simulate clicking on upgrade (from handle_click logic)
        if not upgrade.get('purchased', False) and self.game_state.money >= upgrade['cost']:
            self.game_state._add('money', -upgrade['cost'])
            upgrade['purchased'] = True
            self.game_state.upgrade_effects.add(upgrade['effect_key'])
            self.game_state.messages.append(f'Upgrade purchased: {upgrade['name']}')
            self.game_state.logger.log_upgrade(upgrade['name'], upgrade['cost'], self.game_state.turn)
            
            # Create transition (as in modified handle_click)
            icon_rect = self.game_state._get_upgrade_icon_rect(0, w, h)
            self.game_state._create_upgrade_transition(0, upgrade_rect, icon_rect)
        
        # Verify transition was created
        self.assertEqual(len(self.game_state.ui_transitions), 1)
        transition = self.game_state.ui_transitions[0]
        self.assertEqual(transition['type'], 'upgrade_transition')
        self.assertEqual(transition['upgrade_idx'], 0)
        self.assertTrue(upgrade.get('purchased', False))
    
    def test_extensible_transition_system(self):
        '''Test that the transition system can handle different types of UI elements.'''
        # The system is designed to be extensible for other UI elements
        # Test that we can add different transition types
        
        # Create a mock transition for a different UI element type
        mock_transition = {
            'type': 'action_transition',
            'element_id': 'test_action',
            'progress': 0.0,
            'duration': 20,
            'completed': False,
            'custom_data': {'test': True}
        }
        
        self.game_state.ui_transitions.append(mock_transition)
        
        # Verify the system can handle it without crashing
        self.game_state._update_ui_transitions()
        
        # The upgrade-specific logic shouldn't affect other transition types
        self.assertIn(mock_transition, self.game_state.ui_transitions)
        
        # Only upgrade transitions should be updated by upgrade-specific code
        upgrade_transitions = [t for t in self.game_state.ui_transitions if t['type'] == 'upgrade_transition']
        other_transitions = [t for t in self.game_state.ui_transitions if t['type'] != 'upgrade_transition']
        
        self.assertEqual(len(upgrade_transitions), 0)
        self.assertEqual(len(other_transitions), 1)
        self.assertEqual(other_transitions[0], mock_transition)


if __name__ == '__main__':
    unittest.main()