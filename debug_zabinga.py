#!/usr/bin/env python3
"""Debug zabinga sound issue"""

from src.core.game_state import GameState

def test_zabinga_debug():
    print("=== ZABINGA DEBUG TEST ===")
    
    # Create game state
    gs = GameState("test-seed")
    print(f"Initial research progress: {gs.research_progress}")
    print(f"Initial papers published: {gs.papers_published}")
    
    # Add some staff and compute to generate research
    gs.staff = 5
    gs.compute = 100
    print(f"Added staff: {gs.staff}, compute: {gs.compute}")
    
    # Set up research progress just below threshold
    gs.research_progress = 99
    print(f"Set research progress to: {gs.research_progress}")
    
    # Track zabinga calls
    zabinga_calls = []
    original_zabinga = gs.sound_manager.play_zabinga_sound
    
    def debug_zabinga():
        zabinga_calls.append("CALLED")
        print("ZABINGA SOUND CALLED!")
        original_zabinga()
    
    gs.sound_manager.play_zabinga_sound = debug_zabinga
    
    print(f"Sound manager enabled: {gs.sound_manager.enabled}")
    print(f"Sound manager audio available: {gs.sound_manager.audio_available}")
    print(f"Zabinga sound in sounds dict: {'zabinga' in gs.sound_manager.sounds}")
    
    # Add research progress
    print("\nAdding 1 research progress...")
    gs._add('research_progress', 1)
    print(f"Research progress after add: {gs.research_progress}")
    
    # End turn to trigger processing
    print("\nCalling end_turn()...")
    gs.end_turn()
    
    print(f"Research progress after end_turn: {gs.research_progress}")
    print(f"Papers published after end_turn: {gs.papers_published}")
    print(f"Zabinga calls: {len(zabinga_calls)}")
    print(f"Messages: {gs.messages[-5:]}")  # Last 5 messages
    
if __name__ == "__main__":
    test_zabinga_debug()