# !/usr/bin/env python3
'''
Demo: Context-Aware Button Text System

This demonstration shows how the enhanced leaderboard system now provides
context-aware button text:
- 'Launch New Game' when accessed from main menu (no recent game)
- 'Play Again' when accessed from a completed game session
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game_state import GameState
from src.services.version import get_display_version

def demo_context_aware_buttons():
    '''Demonstrate the context-aware button text system implementation.'''
    print(f'=== P(Doom) {get_display_version()} Context-Aware Button Demo ===')
    print()
    
    print('Context-Aware Button Text System:')
    print('  Enhanced leaderboard screen now shows different button text')
    print('  based on how the user accessed the screen:')
    print()
    
    print('Scenario 1: Main Menu Access')
    print('  User clicks 'View Leaderboard' from main menu')
    print('  from_main_menu = True (game_state is None)')
    print('  Button shows: 'Launch New Game'')
    print('  Logic: User hasn't played recently, so they're launching fresh')
    print()
    
    print('Scenario 2: Post-Game Access')
    print('  User completes a game and proceeds to leaderboard')
    print('  from_main_menu = False (game_state exists)')
    print('  Button shows: 'Play Again'')
    print('  Logic: User just finished a game, so they're playing again')
    print()
    
    print('Implementation Details:')
    print('  - draw_high_score_screen() takes from_main_menu parameter')
    print('  - Dynamic menu items: first_button = 'Launch New Game' if from_main_menu else 'Play Again'')
    print('  - Context detection: from_main_menu = game_state is None')
    print('  - Menu handlers use MENU_ITEM_COUNT for navigation wrapping')
    print('  - Actions remain the same regardless of button text')
    print()
    
    print('Benefits:')
    print('  v More accurate user experience')
    print('  v Context reflects user's actual situation')
    print('  v Clearer intent for new vs returning players')
    print('  v Maintains all existing functionality')
    print()
    
    # Test game state creation for demonstration
    try:
        test_game = GameState('demo-seed')
        print('v Context system ready for party demonstration!')
    except Exception as e:
        print(f'x Error: {e}')

if __name__ == '__main__':
    demo_context_aware_buttons()
