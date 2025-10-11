"""
godot/demo_shared_logic.py

Demonstrates shared game logic working WITHOUT Godot/Pygame.
Pure Python demo showing the migration works.
"""

import sys
from pathlib import Path

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from core.game_logic import GameLogic
from core.engine_interface import MockEngine

def main():
    print("=" * 60)
    print("P(Doom) Shared Logic Demo")
    print("Runs WITHOUT pygame or Godot - pure game logic")
    print("=" * 60)
    
    # Create mock engine
    engine = MockEngine()
    
    # Create game logic with shared code
    logic = GameLogic(engine, seed="demo-seed")
    
    print(f"\n[INIT] Game initialized")
    print(f"  Seed: demo-seed")
    print(f"  Turn: {logic.state.turn}")
    print(f"  Money: ${logic.state.money:,.0f}")
    print(f"  Compute: {logic.state.compute}")
    print(f"  Safety: {logic.state.safety}")
    
    # Demonstrate actions
    print(f"\n[TURN 1] Execute actions...")
    
    print(f"\n  Action: hire_safety_researcher")
    result = logic.execute_action('hire_safety_researcher')
    print(f"    Success: {result.success}")
    print(f"    Money: ${logic.state.money:,.0f}")
    print(f"    Safety: {logic.state.safety}")
    
    print(f"\n  Action: purchase_compute")
    result = logic.execute_action('purchase_compute')
    print(f"    Success: {result.success}")
    print(f"    Compute: {logic.state.compute}")
    
    # Process turn
    print(f"\n[END TURN] Processing...")
    result = logic.process_turn_end()
    print(f"    Turn: {logic.state.turn}")
    print(f"    Compute: {logic.state.compute} (consumed 5)")
    
    # Check events
    print(f"\n[TURN 2] Checking events...")
    events = logic.check_events()
    print(f"    Events triggered: {len(events)}")
    
    # Simulate to turn 10
    print(f"\n[SIMULATE] Fast-forward to turn 10...")
    while logic.state.turn < 10:
        logic.process_turn_end()
    
    # Drain money to trigger crisis
    logic.state.money = 30000
    print(f"    Money: ${logic.state.money:,.0f}")
    
    events = logic.check_events()
    print(f"\n[EVENTS] Triggered: {len(events)} events")
    for event in events:
        print(f"    - {event['name']}: {event['description']}")
        print(f"      Options: {[opt.text for opt in event['options']]}")
    
    # Handle event
    if events:
        print(f"\n[CHOICE] Selecting emergency fundraise...")
        result = logic.handle_event_choice('funding_crisis', 'emergency_fundraise')
        print(f"    Success: {result.success}")
        print(f"    Money: ${logic.state.money:,.0f}")
    
    # Show final state
    print(f"\n[FINAL STATE]")
    print(f"  Turn: {logic.state.turn}")
    print(f"  Money: ${logic.state.money:,.0f}")
    print(f"  Compute: {logic.state.compute}")
    print(f"  Safety: {logic.state.safety}")
    print(f"  Employees: {logic.state.get_total_employees()}")
    
    # Show engine recorded actions
    print(f"\n[ENGINE LOGS]")
    print(f"  Messages: {len(engine.messages)}")
    print(f"  Sounds played: {len(engine.sounds_played)}")
    print(f"  Last 3 messages:")
    for msg, category in engine.messages[-3:]:
        print(f"    [{category.value}] {msg}")
    
    print(f"\n{'=' * 60}")
    print("Demo complete! Shared logic works independently.")
    print("=" * 60)

if __name__ == "__main__":
    main()
