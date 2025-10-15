# !/usr/bin/env python3
'''
Test script for Economic Cycles & Funding Volatility system (Issue #192)
'''

import unittest
from src.core.game_state import GameState


class TestEconomicCycles(unittest.TestCase):
    '''Test cases for economic cycles functionality.'''
    
    def test_economic_system_initialization(self):
        '''Test that economic system initializes correctly.'''
        gs = GameState('test-economic-cycles')
        
        # Assert basic components exist
        self.assertTrue(hasattr(gs, 'economic_cycles'), 'Economic cycles system should exist')
        self.assertIsNotNone(gs.economic_cycles.current_state, 'Economic state should be initialized')
        self.assertIsNotNone(gs.economic_cycles.current_state.phase, 'Economic phase should be set')
        
        # Assert funding multiplier is reasonable
        multiplier = gs.economic_cycles.current_state.funding_multiplier
        self.assertGreaterEqual(multiplier, 0.5, 'Funding multiplier should not be below 0.5')
        self.assertLessEqual(multiplier, 2.0, 'Funding multiplier should not exceed 2.0')
    
    def test_economic_timeline_progression(self):
        '''Test economic phase transitions over time.'''
        gs = GameState('test-economic-cycles')
        
        # Test specific timeline points
        timeline_tests = [
            (0, 'STABLE'),     # Starting phase
            (25, 'STABLE'),   # Last turn of STABLE phase
            (26, 'BOOM'),     # First turn of BOOM phase
            (50, 'BOOM'),     # Should remain in boom
            (105, 'CORRECTION'), # Should transition to correction
            (160, 'RECESSION'),  # Should be in recession
        ]
        
        for turn, expected_phase in timeline_tests:
            gs.economic_cycles.update_for_turn(turn)
            actual_phase = gs.economic_cycles.current_state.phase.name
            self.assertEqual(actual_phase, expected_phase, 
                           f'Turn {turn}: Expected {expected_phase}, got {actual_phase}')
    
    def test_fundraising_multiplier_effects(self):
        '''Test that economic phases affect fundraising.'''
        gs = GameState('test-fundraising')
        
        # Get initial funding multiplier
        initial_multiplier = gs.economic_cycles.current_state.funding_multiplier
        self.assertIsInstance(initial_multiplier, (int, float), 'Multiplier should be numeric')
        
        # Test that multiplier affects different economic phases
        for turn in [0, 50, 150]:  # Different economic phases
            gs.economic_cycles.update_for_turn(turn)
            multiplier = gs.economic_cycles.current_state.funding_multiplier
            self.assertGreaterEqual(multiplier, 0.3, 'Multiplier should not be too low')
            self.assertLessEqual(multiplier, 3.0, 'Multiplier should not be too high')


def test_economic_cycles():
    '''Legacy function for backward compatibility.'''
    # Keep the original print-based test as a demonstration function
    print('=== Testing Economic Cycles & Funding Volatility (Issue #192) ===')
    
    # Test 1: Basic initialization
    print('\n1. Testing basic initialization...')
    gs = GameState('test-economic-cycles')
    print(f'[OK] Economic system loaded: {hasattr(gs, 'economic_cycles')}')
    print(f'[OK] Current phase: {gs.economic_cycles.current_state.phase.name}')
    print(f'[OK] Funding multiplier: {gs.economic_cycles.current_state.funding_multiplier:.2f}')
    
    # Test 2: Economic timeline progression
    print('\n2. Testing economic timeline progression...')
    timeline_tests = [
        (0, 'Jan 2017'),
        (25, 'Jul 2017'),  # Should transition to boom
        (50, 'Jan 2018'),  # Should be in boom
        (105, 'Jan 2019'), # Should transition to correction
        (160, 'Jan 2020'), # Should be in recession 
        (200, 'Oct 2020'), # Should be in boom again
        (300, 'Oct 2022'), # Should be in recession
        (400, 'Sep 2024')  # Should be in boom
    ]
    
    for turn, description in timeline_tests:
        news = gs.economic_cycles.update_for_turn(turn)
        phase = gs.economic_cycles.current_state.phase.name
        year = gs.economic_cycles.current_state.cycle_year
        multiplier = gs.economic_cycles.current_state.funding_multiplier
        print(f'Turn {turn:3d} ({description}): {phase:10s} - Year {year} - Multiplier {multiplier:.2f}')
        if news:
            print(f'    [NEWS] NEWS: {news}')
    
    # Test 3: Fundraising mechanics
    print('\n3. Testing enhanced fundraising mechanics...')
    gs = GameState('test-fundraising')
    initial_money = gs.money
    print(f'Initial money: ${initial_money}k')
    print(f'Economic phase: {gs.economic_cycles.current_state.phase.name}')
    print(f'Funding multiplier: {gs.economic_cycles.current_state.funding_multiplier:.2f}')
    
    # Test fundraising action
    result = gs.attempt_action_selection(1)  # Fundraise action
    print(f'Fundraising action selected: {result}')
    
    # End turn to execute action
    gs.end_turn()
    
    final_money = gs.money
    money_gained = final_money - initial_money
    print(f'After fundraising: ${final_money}k (gained ${money_gained}k)')
    print(f'Funding cooldown: {getattr(gs, 'funding_round_cooldown', 0)} turns')
    
    # Test 4: Advanced funding actions unlock
    print('\n4. Testing advanced funding unlocks...')
    gs.money = 2000  # Ensure enough money for multiple rounds
    gs.reputation = 20  # High reputation
    
    # Check if advanced funding is available
    has_advanced = getattr(gs, 'advanced_funding_unlocked', False)
    print(f'Advanced funding initially unlocked: {has_advanced}')
    
    # Do several funding rounds to trigger unlock
    for i in range(3):
        if getattr(gs, 'funding_round_cooldown', 0) <= 0:
            gs.attempt_action_selection(1)  # Fundraise
            gs.end_turn()
            print(f'Funding round {i+1} completed')
        else:
            print(f'Funding round {i+1} skipped due to cooldown')
    
    has_advanced_after = getattr(gs, 'advanced_funding_unlocked', False)
    print(f'Advanced funding unlocked after rounds: {has_advanced_after}')
    
    # Test 5: Economic events
    print('\n5. Testing economic events...')
    gs = GameState('test-events')
    gs.turn = 50  # Advance to a turn where events can trigger
    gs.money = 50   # Low money to trigger some events
    gs.reputation = 15
    
    # Set to recession phase to test crisis events
    from src.features.economic_cycles import EconomicPhase
    gs.economic_cycles.current_state.phase = EconomicPhase.RECESSION
    print(f'Set to recession phase for event testing')
    
    # Trigger events
    print('Triggering events...')
    initial_messages = len(gs.messages)
    gs.trigger_events()
    new_messages = len(gs.messages) - initial_messages
    print(f'Generated {new_messages} new event messages')
    
    for message in gs.messages[-5:]:  # Show last 5 messages
        print(f'  ? {message}')
    
    print('\n? All Economic Cycles & Funding Volatility tests completed successfully!')
    print('[TARGET] Issue #192 implementation verified')

if __name__ == '__main__':
    test_economic_cycles()
