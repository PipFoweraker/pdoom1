#!/usr/bin/env python3
"""
Debug script to check turn processing path.
"""

import sys
sys.path.append('.')

from src.core.game_state import GameState

def debug_turn_processing():
    """Debug turn processing path"""
    print("=== DEBUGGING TURN PROCESSING PATH ===")
    
    # Create game state
    gs = GameState('test-seed')
    
    print(f"Has turn_manager: {hasattr(gs, 'turn_manager')}")
    print(f"turn_processing: {gs.turn_processing}")
    print(f"turn: {gs.turn}")
    
    # Set up research for paper completion
    gs.research_progress = 100  # Set directly to trigger condition
    print(f"Research progress: {gs.research_progress}")
    
    # Check if we would take the turn_manager path
    if hasattr(gs, 'turn_manager'):
        print("Will use turn_manager.process_turn()")
    else:
        print("Will use legacy turn processing")
        print(f"turn_processing before: {gs.turn_processing}")
    
    # Call end_turn and see what path we take
    result = gs.end_turn()
    
    print(f"end_turn() returned: {result}")
    print(f"turn_processing after: {gs.turn_processing}")
    print(f"Research progress after: {gs.research_progress}")
    print(f"Papers published after: {gs.papers_published}")

if __name__ == "__main__":
    debug_turn_processing()