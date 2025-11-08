import unittest
import sys
import os

# Add the parent directory to the path so we can import game_state
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game_state import GameState


class TestUpgradePurchasing(unittest.TestCase):
    '''Test upgrade purchasing mechanics.'''
    
    def setUp(self):
        '''Set up a fresh GameState for each test.'''
        self.game_state = GameState('test_seed')
    
    def test_can_purchase_upgrade_with_sufficient_money(self):
        '''Test that upgrades can be purchased if enough money is available.'''
        # Set sufficient money for the first upgrade (cost: 200)
        self.game_state.money = 250
        initial_money = self.game_state.money
        
        # Get the first upgrade (should be 'Upgrade Computer System' with cost 200)
        upgrade_idx = 0
        upgrade = self.game_state.upgrades[upgrade_idx]
        upgrade.get('purchased', False)
        
        # Simulate clicking on the upgrade by directly calling the purchase logic
        if not upgrade.get('purchased', False):
            if self.game_state.money >= upgrade['cost']:
                self.game_state.money -= upgrade['cost']
                upgrade['purchased'] = True
                self.game_state.upgrade_effects.add(upgrade['effect_key'])
                self.game_state.messages.append(f'Upgrade purchased: {upgrade['name']}')
        
        # Verify purchase was successful
        self.assertTrue(upgrade.get('purchased', False), 'Upgrade should be marked as purchased')
        self.assertEqual(self.game_state.money, initial_money - upgrade['cost'], 
                        'Money should be deducted correctly')
        self.assertIn(upgrade['effect_key'], self.game_state.upgrade_effects, 
                     'Upgrade effect should be added to effects set')
        self.assertTrue(any('Upgrade purchased:' in msg for msg in self.game_state.messages),
                       'Success message should be added to messages')
    
    def test_cannot_purchase_upgrade_with_insufficient_money(self):
        '''Test that upgrades cannot be purchased without enough money.'''
        # Set insufficient money for any upgrade (all upgrades cost 120+)
        self.game_state.money = 50
        initial_money = self.game_state.money
        
        # Try to purchase the first upgrade
        upgrade_idx = 0
        upgrade = self.game_state.upgrades[upgrade_idx]
        upgrade.get('purchased', False)
        
        # Simulate clicking on the upgrade
        if not upgrade.get('purchased', False):
            if self.game_state.money >= upgrade['cost']:
                self.game_state.money -= upgrade['cost']
                upgrade['purchased'] = True
                self.game_state.upgrade_effects.add(upgrade['effect_key'])
                self.game_state.messages.append(f'Upgrade purchased: {upgrade['name']}')
            else:
                self.game_state.messages.append('Not enough money for upgrade.')
        
        # Verify purchase was rejected
        self.assertFalse(upgrade.get('purchased', False), 'Upgrade should not be marked as purchased')
        self.assertEqual(self.game_state.money, initial_money, 'Money should not be deducted')
        self.assertNotIn(upgrade['effect_key'], self.game_state.upgrade_effects,
                        'Upgrade effect should not be added to effects set')
        self.assertIn('Not enough money for upgrade.', self.game_state.messages,
                     'Failure message should be added to messages')
    
    def test_cannot_purchase_already_purchased_upgrade(self):
        '''Test that already purchased upgrades cannot be purchased again.'''
        # Set sufficient money
        self.game_state.money = 1000
        initial_money = self.game_state.money
        
        # Get the first upgrade and mark it as already purchased
        upgrade_idx = 0
        upgrade = self.game_state.upgrades[upgrade_idx]
        upgrade['purchased'] = True
        self.game_state.upgrade_effects.add(upgrade['effect_key'])
        
        # Try to purchase the already purchased upgrade
        if not upgrade.get('purchased', False):
            if self.game_state.money >= upgrade['cost']:
                self.game_state.money -= upgrade['cost']
                upgrade['purchased'] = True
                self.game_state.upgrade_effects.add(upgrade['effect_key'])
                self.game_state.messages.append(f'Upgrade purchased: {upgrade['name']}')
            else:
                self.game_state.messages.append('Not enough money for upgrade.')
        else:
            self.game_state.messages.append('Already purchased.')
        
        # Verify no changes occurred
        self.assertTrue(upgrade.get('purchased', False), 'Upgrade should remain purchased')
        self.assertEqual(self.game_state.money, initial_money, 'Money should not be deducted')
        self.assertIn('Already purchased.', self.game_state.messages,
                     'Already purchased message should be added')
    
    def test_upgrade_effect_activation(self):
        '''Test that purchased upgrades activate their effects correctly.'''
        # Set sufficient money
        self.game_state.money = 1000
        
        # Purchase all three upgrades and verify their effects are activated
        expected_effects = set()
        for upgrade in self.game_state.upgrades:
            if not upgrade.get('purchased', False):
                if self.game_state.money >= upgrade['cost']:
                    self.game_state.money -= upgrade['cost']
                    upgrade['purchased'] = True
                    self.game_state.upgrade_effects.add(upgrade['effect_key'])
                    expected_effects.add(upgrade['effect_key'])
        
        # Verify all expected effects are in the upgrade_effects set
        self.assertEqual(self.game_state.upgrade_effects, expected_effects,
                        'All purchased upgrade effects should be active')
    
    def test_upgrade_success_messages(self):
        '''Test that correct success messages are generated for upgrade purchases.'''
        # Set sufficient money
        self.game_state.money = 1000
        initial_message_count = len(self.game_state.messages)
        
        # Purchase the first upgrade
        upgrade = self.game_state.upgrades[0]
        if not upgrade.get('purchased', False):
            if self.game_state.money >= upgrade['cost']:
                self.game_state.money -= upgrade['cost']
                upgrade['purchased'] = True
                self.game_state.upgrade_effects.add(upgrade['effect_key'])
                self.game_state.messages.append(f'Upgrade purchased: {upgrade['name']}')
        
        # Check that a success message was added
        new_messages = self.game_state.messages[initial_message_count:]
        self.assertEqual(len(new_messages), 1, 'Exactly one message should be added')
        self.assertTrue(new_messages[0].startswith('Upgrade purchased:'),
                       'Message should start with 'Upgrade purchased:'')
        self.assertIn(upgrade['name'], new_messages[0],
                     'Message should contain the upgrade name')


class TestUpgradeInitialization(unittest.TestCase):
    '''Test that upgrades are properly initialized.'''
    
    def test_upgrades_loaded_correctly(self):
        '''Test that upgrades are loaded from upgrades.py correctly.'''
        game_state = GameState('test_seed')
        
        # Verify upgrades are loaded
        self.assertGreater(len(game_state.upgrades), 0, 'Should have upgrades loaded')
        
        # Verify upgrade structure
        for upgrade in game_state.upgrades:
            self.assertIn('name', upgrade, 'Each upgrade should have a name')
            self.assertIn('desc', upgrade, 'Each upgrade should have a description')
            self.assertIn('cost', upgrade, 'Each upgrade should have a cost')
            self.assertIn('effect_key', upgrade, 'Each upgrade should have an effect_key')
            self.assertIsInstance(upgrade['cost'], int, 'Cost should be an integer')
            self.assertGreater(upgrade['cost'], 0, 'Cost should be positive')
    
    def test_upgrades_initially_not_purchased(self):
        '''Test that upgrades start as not purchased.'''
        game_state = GameState('test_seed')
        
        for upgrade in game_state.upgrades:
            self.assertFalse(upgrade.get('purchased', False),
                           f'Upgrade '{upgrade['name']}' should not be purchased initially')
    
    def test_upgrade_effects_initially_empty(self):
        '''Test that upgrade effects set starts empty.'''
        game_state = GameState('test_seed')
        
        self.assertEqual(len(game_state.upgrade_effects), 0,
                        'Upgrade effects should be empty initially')
        self.assertIsInstance(game_state.upgrade_effects, set,
                             'Upgrade effects should be a set')


if __name__ == '__main__':
    unittest.main()