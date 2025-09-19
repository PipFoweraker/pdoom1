#!/usr/bin/env python3
"""
Debug script to test research paper completion and zabinga sound.
"""

import sys
sys.path.append('.')

from src.core.game_state import GameState

def debug_research_paper_completion():
    """Debug research paper completion flow"""
    print("=== DEBUGGING RESEARCH PAPER COMPLETION ===")
    
    # Create game state
    gs = GameState('test-seed')
    
    # Mock the sound manager to track calls
    zabinga_called = []
    original_play_zabinga = gs.sound_manager.play_zabinga_sound
    
    def mock_play_zabinga():
        zabinga_called.append(True)
        print("🎵 ZABINGA SOUND CALLED! 🎵")
        original_play_zabinga()
    
    gs.sound_manager.play_zabinga_sound = mock_play_zabinga
    
    print(f"Initial research progress: {gs.research_progress}")
    print(f"Initial papers published: {gs.papers_published}")
    
    # Set research progress to just below threshold
    gs.research_progress = 99
    print(f"Set research progress to: {gs.research_progress}")
    
    # Add just enough research progress to complete a paper
    print("Adding 1 research progress...")
    gs._add('research_progress', 1)
    print(f"Research progress after adding 1: {gs.research_progress}")
    
    # Check if the condition would be met
    if gs.research_progress >= 100:
        print("✓ Research progress >= 100, should trigger paper completion")
    else:
        print("✗ Research progress < 100, will not trigger paper completion")
    
    print("\nCalling end_turn()...")
    gs.end_turn()
    
    print(f"Final research progress: {gs.research_progress}")
    print(f"Final papers published: {gs.papers_published}")
    print(f"Zabinga called count: {len(zabinga_called)}")
    
    # Check messages for paper publication
    print("\nGame messages:")
    for msg in gs.messages[-10:]:  # Last 10 messages
        print(f"  - {msg}")
        if "paper" in msg.lower():
            print("    ^ FOUND PAPER MESSAGE!")
    
    if len(zabinga_called) > 0:
        print("✓ SUCCESS: Zabinga sound was called!")
    else:
        print("✗ FAILURE: Zabinga sound was NOT called!")
    
    return len(zabinga_called) > 0

if __name__ == "__main__":
    success = debug_research_paper_completion()
    sys.exit(0 if success else 1)