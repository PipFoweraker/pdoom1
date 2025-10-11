"""Test pure logic works with pygame adapter"""
import pygame
import sys
import os

# Add shared to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.core.game_logic import GameLogic
from adapters.pygame_engine import create_pygame_engine_from_existing

def test_integration():
    """Verify pure logic + pygame adapter works"""
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Create engine adapter
    engine = create_pygame_engine_from_existing(screen)
    
    # Create pure game logic
    logic = GameLogic(engine, seed="integration-test")
    
    print(f"Initial state:")
    print(f"  Turn: {logic.state.turn}")
    print(f"  Money: ${logic.state.money:,.0f}")
    print(f"  Safety: {logic.state.safety}")
    
    # Execute action
    print("\nExecuting: hire_safety_researcher")
    result = logic.execute_action('hire_safety_researcher')
    
    assert result.success, "Action should succeed"
    assert logic.state.money == 50000, "Should cost $50k"
    assert logic.state.safety == 2, "Should gain 2 safety"
    
    print(f"After action:")
    print(f"  Money: ${logic.state.money:,.0f}")
    print(f"  Safety: {logic.state.safety}")
    
    # Process turn
    print("\nProcessing turn end...")
    result = logic.process_turn_end()
    
    assert result.success, "Turn should process"
    assert logic.state.turn == 1, "Turn should increment"
    
    print(f"After turn:")
    print(f"  Turn: {logic.state.turn}")
    print(f"  Compute: {logic.state.compute}")
    
    print("\n[OK] Integration test passed!")
    pygame.quit()

if __name__ == '__main__':
    test_integration()