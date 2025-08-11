#!/usr/bin/env python3
"""
Full feature test for Batch 2 features
"""

from game_state import GameState
from actions import ACTIONS  
from events import EVENTS
import random

def run_game_simulation():
    print('=== FULL FEATURE TEST ===')
    random.seed(42)
    gs = GameState('test_seed')
    
    # Simulate several turns of gameplay
    for turn in range(1, 12):
        gs.turn = turn
        print(f'\n--- TURN {turn} ---')
        
        # Check events this turn
        triggered_events = []
        for event in EVENTS:
            if event['trigger'](gs):
                triggered_events.append(event['name'])
                
        if triggered_events:
            print(f'Events triggered: {triggered_events}')
            
        # Simulate some resource accumulation
        if turn % 3 == 0:
            gs._add('reputation', 5)
            gs._add('money', 100)
            
        if turn == 6:
            print('Unlocking intelligence network...')
            gs.scouting_unlocked = True
            
        if turn == 8:
            print('Testing opponent scouting...')
            gs._scout_opponents()
            
        if turn == 10:
            print('Testing expense request...')
            gs._trigger_expense_request()
            
        # Show current state
        print(f'Resources: Money=${gs.money}, Staff={gs.staff}, Rep={gs.reputation}, Compute={gs.compute}')
        print(f'Opponents discovered: {sum(1 for opp in gs.opponents if opp.discovered)}')
        
    print('\n=== SIMULATION COMPLETE ===')

if __name__ == "__main__":
    run_game_simulation()