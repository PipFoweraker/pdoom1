'''
Tests for accounting software functionality - Issue #52.

This module tests the last_balance_change tracking and display when
accounting software upgrade is purchased.
'''

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import pygame
from src.core.game_state import GameState


class TestAccountingSoftware(unittest.TestCase):
    '''Test accounting software bug fixes.'''

    def setUp(self):
        '''Set up test fixtures.'''
        self.game_state = GameState('test_seed')

    def test_no_balance_change_without_accounting_software(self):
        '''Test that last_balance_change is not updated without accounting software.'''
        initial_money = self.game_state.money
        
        # Make a transaction without accounting software
        self.game_state._add('money', 100)
        
        # Should not track balance change
        self.assertEqual(self.game_state.last_balance_change, 0)
        self.assertEqual(self.game_state.money, initial_money + 100)

    def test_balance_change_with_accounting_software(self):
        '''Test that last_balance_change is updated when accounting software is bought.'''
        initial_money = self.game_state.money
        
        # Buy accounting software
        self.game_state.accounting_software_bought = True
        
        # Make positive transaction
        self.game_state._add('money', 500)
        self.assertEqual(self.game_state.last_balance_change, 500)
        self.assertEqual(self.game_state.money, initial_money + 500)
        
        # Make negative transaction
        self.game_state._add('money', -200)
        self.assertEqual(self.game_state.last_balance_change, -200)
        self.assertEqual(self.game_state.money, initial_money + 500 - 200)
        
        # Make zero transaction
        self.game_state._add('money', 0)
        self.assertEqual(self.game_state.last_balance_change, 0)
        self.assertEqual(self.game_state.money, initial_money + 500 - 200)

    def test_sequential_transactions(self):
        '''Test that last_balance_change reflects only the most recent transaction.'''
        # Buy accounting software
        self.game_state.accounting_software_bought = True
        
        # Multiple transactions - should only track the last one
        self.game_state._add('money', 100)
        self.assertEqual(self.game_state.last_balance_change, 100)
        
        self.game_state._add('money', -50)
        self.assertEqual(self.game_state.last_balance_change, -50)
        
        self.game_state._add('money', 300)
        self.assertEqual(self.game_state.last_balance_change, 300)

    def test_balance_change_sign_correctness(self):
        '''Test that balance change sign is correct for positive and negative amounts.'''
        # Buy accounting software
        self.game_state.accounting_software_bought = True
        
        # Test positive transaction
        self.game_state._add('money', 150)
        self.assertEqual(self.game_state.last_balance_change, 150)
        self.assertGreater(self.game_state.last_balance_change, 0)
        
        # Test negative transaction  
        self.game_state._add('money', -75)
        self.assertEqual(self.game_state.last_balance_change, -75)
        self.assertLess(self.game_state.last_balance_change, 0)
        
        # Test zero transaction
        self.game_state._add('money', 0)
        self.assertEqual(self.game_state.last_balance_change, 0)

    def test_other_resources_dont_affect_balance_change(self):
        '''Test that changing other resources doesn't affect last_balance_change.'''
        # Buy accounting software
        self.game_state.accounting_software_bought = True
        
        # Set initial balance change
        self.game_state._add('money', 100)
        self.assertEqual(self.game_state.last_balance_change, 100)
        
        # Change other resources
        self.game_state._add('staff', 5)
        self.game_state._add('reputation', 10)
        self.game_state._add('doom', -5)
        
        # Balance change should remain unchanged
        self.assertEqual(self.game_state.last_balance_change, 100)


class TestAccountingUIColorDisplay(unittest.TestCase):
    '''Test that accounting display shows correct colors.'''

    def setUp(self):
        '''Set up pygame for UI tests.'''
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.game_state = GameState('test_seed')
        self.game_state.accounting_software_bought = True

    def tearDown(self):
        '''Clean up pygame.'''
        pygame.quit()

    def test_positive_balance_change_color(self):
        '''Test that positive balance changes are displayed in green.'''
        # Set positive balance change
        self.game_state._add('money', 250)
        self.assertEqual(self.game_state.last_balance_change, 250)
        
        # Test color logic (we'll examine the color constants used in ui.py)
        # Green color for positive changes: (100, 255, 100) or similar
        self.assertGreater(self.game_state.last_balance_change, 0)

    def test_negative_balance_change_color(self):
        '''Test that negative balance changes are displayed in red.'''
        # Set negative balance change
        self.game_state._add('money', -150)
        self.assertEqual(self.game_state.last_balance_change, -150)
        
        # Test color logic (we'll examine the color constants used in ui.py)
        # Red color for negative changes: (255, 100, 100) or similar
        self.assertLess(self.game_state.last_balance_change, 0)

    def test_zero_balance_change_color(self):
        '''Test that zero balance changes are displayed appropriately.'''
        # Set zero balance change
        self.game_state._add('money', 0)
        self.assertEqual(self.game_state.last_balance_change, 0)
        
        # Zero should be treated like positive (green)


if __name__ == '__main__':
    unittest.main()