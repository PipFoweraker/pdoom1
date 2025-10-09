import unittest
from src.core.game_state import GameState


class TestActivityLogTooltip(unittest.TestCase):
    '''Test activity log tooltip functionality'''
    
    def setUp(self):
        '''Set up a GameState for testing'''
        self.game_state = GameState('test_seed')
        # RNG is now initialized by GameState constructor
        
    def test_tooltip_shows_purchase_prompt_when_upgrade_not_purchased(self):
        '''Test that hovering over activity log shows purchase prompt when upgrade not purchased'''
        # Ensure compact display upgrade is not purchased
        self.assertNotIn('compact_activity_display', self.game_state.upgrade_effects)
        
        # Simulate mouse hovering over activity log area
        w, h = 800, 600
        activity_log_rect = self.game_state._get_activity_log_rect(w, h)
        log_center_x = activity_log_rect[0] + activity_log_rect[2] // 2
        log_center_y = activity_log_rect[1] + activity_log_rect[3] // 2
        
        tooltip = self.game_state.check_hover((log_center_x, log_center_y), w, h)
        self.assertEqual(tooltip, 'You may purchase the ability to minimise this for $150!')
        
    def test_tooltip_shows_minimize_info_when_upgrade_purchased(self):
        '''Test that hovering over activity log shows minimize info when upgrade is purchased'''
        # Purchase the compact activity display upgrade
        self.game_state.money = 200
        for upgrade in self.game_state.upgrades:
            if upgrade['name'] == 'Compact Activity Display':
                upgrade['purchased'] = True
                self.game_state.upgrade_effects.add(upgrade['effect_key'])
                break
        
        self.game_state.scrollable_event_log_enabled = True
        
        # Simulate mouse hovering over activity log area
        w, h = 800, 600
        activity_log_rect = self.game_state._get_activity_log_rect(w, h)
        log_center_x = activity_log_rect[0] + activity_log_rect[2] // 2
        log_center_y = activity_log_rect[1] + activity_log_rect[3] // 2
        
        tooltip = self.game_state.check_hover((log_center_x, log_center_y), w, h)
        self.assertEqual(tooltip, 'Activity Log - Click minimize button to reduce screen space')
        
    def test_tooltip_shows_expand_info_when_minimized(self):
        '''Test that hovering over minimized activity log shows expand info'''
        # Purchase the compact activity display upgrade and minimize
        self.game_state.money = 200
        for upgrade in self.game_state.upgrades:
            if upgrade['name'] == 'Compact Activity Display':
                upgrade['purchased'] = True
                self.game_state.upgrade_effects.add(upgrade['effect_key'])
                break
        
        self.game_state.scrollable_event_log_enabled = True
        self.game_state.activity_log_minimized = True
        
        # Simulate mouse hovering over minimized activity log area
        w, h = 800, 600
        activity_log_rect = self.game_state._get_activity_log_rect(w, h)
        log_center_x = activity_log_rect[0] + activity_log_rect[2] // 2
        log_center_y = activity_log_rect[1] + activity_log_rect[3] // 2
        
        tooltip = self.game_state.check_hover((log_center_x, log_center_y), w, h)
        self.assertEqual(tooltip, 'Activity Log (minimized) - Click expand button to show full log')


class TestActivityLogDrag(unittest.TestCase):
    '''Test activity log drag/move functionality'''
    
    def setUp(self):
        '''Set up a GameState for testing'''
        self.game_state = GameState('test_seed')
        # RNG is now initialized by GameState constructor
        
    def test_activity_log_drag_initialization(self):
        '''Test that drag-related attributes are properly initialized'''
        self.assertFalse(self.game_state.activity_log_being_dragged)
        self.assertEqual(self.game_state.activity_log_drag_offset, (0, 0))
        self.assertEqual(self.game_state.activity_log_position, (0, 0))
        
    def test_activity_log_position_methods(self):
        '''Test position calculation methods'''
        w, h = 800, 600
        
        # Test base position
        base_pos = self.game_state._get_activity_log_base_position(w, h)
        self.assertEqual(base_pos, (int(w*0.04), int(h*0.74)))
        
        # Test current position with no offset
        current_pos = self.game_state._get_activity_log_current_position(w, h)
        self.assertEqual(current_pos, base_pos)
        
        # Test current position with offset
        self.game_state.activity_log_position = (50, -20)
        current_pos = self.game_state._get_activity_log_current_position(w, h)
        expected = (base_pos[0] + 50, base_pos[1] - 20)
        self.assertEqual(current_pos, expected)
        
    def test_drag_start_on_activity_log_click(self):
        '''Test that clicking on activity log starts drag operation'''
        w, h = 800, 600
        
        # Get activity log area and click in the center
        activity_log_rect = self.game_state._get_activity_log_rect(w, h)
        log_center_x = activity_log_rect[0] + activity_log_rect[2] // 2
        log_center_y = activity_log_rect[1] + activity_log_rect[3] // 2
        
        # Simulate click
        self.game_state.handle_click((log_center_x, log_center_y), w, h)
        
        # Should start dragging
        self.assertTrue(self.game_state.activity_log_being_dragged)
        self.assertNotEqual(self.game_state.activity_log_drag_offset, (0, 0))
        
    def test_drag_motion_updates_position(self):
        '''Test that mouse motion updates activity log position during drag'''
        w, h = 800, 600
        
        # Start dragging
        self.game_state.activity_log_being_dragged = True
        self.game_state.activity_log_drag_offset = (10, 10)
        initial_position = self.game_state.activity_log_position
        
        # Simulate mouse motion
        new_mouse_pos = (100, 200)
        self.game_state.handle_mouse_motion(new_mouse_pos, w, h)
        
        # Position should have changed
        self.assertNotEqual(self.game_state.activity_log_position, initial_position)
        
    def test_drag_release_stops_dragging(self):
        '''Test that mouse release stops drag operation'''
        w, h = 800, 600
        
        # Start dragging
        self.game_state.activity_log_being_dragged = True
        self.game_state.activity_log_drag_offset = (10, 10)
        
        # Simulate mouse release
        result = self.game_state.handle_mouse_release((100, 200), w, h)
        
        # Should stop dragging
        self.assertFalse(self.game_state.activity_log_being_dragged)
        self.assertEqual(self.game_state.activity_log_drag_offset, (0, 0))
        self.assertTrue(result)  # Should return True indicating drag was completed
        
    def test_drag_constrains_position_to_screen(self):
        '''Test that dragging constrains activity log position to screen bounds'''
        w, h = 800, 600
        
        # Start dragging
        self.game_state.activity_log_being_dragged = True
        self.game_state.activity_log_drag_offset = (0, 0)
        
        # Try to drag to extreme positions
        extreme_positions = [
            (-1000, -1000),  # Way off screen top-left
            (2000, 2000),    # Way off screen bottom-right
            (-500, 300),     # Off left edge
            (1500, 300),     # Off right edge
        ]
        
        for extreme_pos in extreme_positions:
            self.game_state.handle_mouse_motion(extreme_pos, w, h)
            
            # Position should be constrained
            current_pos = self.game_state._get_activity_log_current_position(w, h)
            
            # Should be within screen bounds (allowing some margin for the log size)
            self.assertGreaterEqual(current_pos[0], 0)
            self.assertGreaterEqual(current_pos[1], 0)
            self.assertLessEqual(current_pos[0], w - int(w * 0.44))  # Account for log width
            self.assertLessEqual(current_pos[1], h - int(h * 0.22))  # Account for log height
            

if __name__ == '__main__':
    unittest.main()