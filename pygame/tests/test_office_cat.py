'''
Test the office cat feature - enhanced dev engagement system
'''
import unittest
from src.core.game_state import GameState


class TestOfficeCat(unittest.TestCase):
    def setUp(self):
        '''Set up test game state'''
        self.gs = GameState('test-cat-seed')
    
    def test_office_cat_initialization(self):
        '''Test that office cat system initializes correctly'''
        # Cat should not be adopted initially
        self.assertFalse(self.gs.office_cat_adopted)
        self.assertEqual(self.gs.office_cat_total_pets, 0)
        self.assertEqual(self.gs.office_cat_total_food_cost, 0)
    
    def test_cat_adoption_event(self):
        '''Test that cat adoption event works correctly'''
        # Manually trigger the adoption event
        self.gs._trigger_stray_cat_adoption()
        
        # Verify cat is now adopted
        self.assertTrue(self.gs.office_cat_adopted)
        self.assertTrue(self.gs.office_cats_adopted)  # Legacy compatibility
        
        # Check that setup costs were applied
        self.assertLess(self.gs.money, 100000)  # Flea treatment cost applied (started with $100k)
        self.assertGreater(self.gs.reputation, 0)  # Reputation boost applied
        
        # Check messages were added
        self.assertGreater(len(self.gs.messages), 0)
        cat_messages = [msg for msg in self.gs.messages if 'cat' in msg.lower() or '[CAT]' in msg]
        self.assertGreater(len(cat_messages), 0)
    
    def test_cat_petting_mechanics(self):
        '''Test that cat petting works correctly'''
        # Adopt the cat first
        self.gs._trigger_stray_cat_adoption()
        
        # Clear messages from adoption
        self.gs.messages = []
        
        # Test petting the cat (simulate mouse click near cat position)
        cat_x, cat_y = self.gs.office_cat_position
        result = self.gs.pet_office_cat((cat_x, cat_y))
        
        # Verify petting worked
        self.assertTrue(result)
        self.assertEqual(self.gs.office_cat_total_pets, 1)
        self.assertEqual(self.gs.office_cat_last_petted, self.gs.turn)
        self.assertGreater(self.gs.office_cat_love_emoji_timer, 0)
    
    def test_cat_upkeep_costs(self):
        '''Test that cat upkeep costs are applied correctly'''
        # Adopt the cat first
        self.gs._trigger_stray_cat_adoption()
        
        # Note starting money
        money_before = self.gs.money
        
        # Advance to next turn to trigger upkeep
        self.gs.end_turn()
        
        # Verify upkeep costs were applied
        self.assertLess(self.gs.money, money_before)
        self.assertGreater(self.gs.office_cat_total_food_cost, 0)
        
        # Check upkeep message was added
        upkeep_messages = [msg for msg in self.gs.messages if 'Cat upkeep' in msg]
        self.assertGreater(len(upkeep_messages), 0)
    
    def test_cat_doom_stages(self):
        '''Test that cat doom stages work correctly'''
        # Adopt the cat first
        self.gs._trigger_stray_cat_adoption()
        
        # Test different doom levels
        self.gs.doom = 0
        self.assertEqual(self.gs.get_cat_doom_stage(), 0)  # Happy cat
        
        self.gs.doom = 20
        self.assertEqual(self.gs.get_cat_doom_stage(), 1)  # Concerned cat
        
        self.gs.doom = 50
        self.assertEqual(self.gs.get_cat_doom_stage(), 2)  # Alert cat
        
        self.gs.doom = 70
        self.assertEqual(self.gs.get_cat_doom_stage(), 3)  # Ominous cat
        
        self.gs.doom = 90
        self.assertEqual(self.gs.get_cat_doom_stage(), 4)  # Doom cat
    
    def test_cat_position_updates(self):
        '''Test that cat position updates work correctly'''
        # Adopt the cat first
        self.gs._trigger_stray_cat_adoption()
        
        # Update cat position with screen dimensions
        screen_w, screen_h = 800, 600
        self.gs.office_cat_position
        
        self.gs.update_cat_position(screen_w, screen_h)
        
        # Position should be updated (cat moves towards target)
        final_pos = self.gs.office_cat_position
        # Position should be valid coordinates
        self.assertIsInstance(final_pos[0], int)
        self.assertIsInstance(final_pos[1], int)


if __name__ == '__main__':
    unittest.main()
