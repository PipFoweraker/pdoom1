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
    
    print(f"=== Integration Test: Pygame Adapter + Pure Logic ===")
    print(f"Initial state:")
    print(f"  Turn: {logic.state.turn}")
    print(f"  Money: ${logic.state.money:,.0f}")
    print(f"  Safety: {logic.state.safety}")
    print(f"  Total employees: {logic.state.get_total_employees()}")
    
    # Test 1: Execute hiring action
    print(f"\n--- Test 1: Hiring Action ---")
    print(f"Executing: hire_safety_researcher")
    result = logic.execute_action('hire_safety_researcher')
    
    assert result.success, "Action should succeed"
    assert logic.state.money == 50000, "Should cost $50k"
    assert logic.state.safety == 2, "Should gain 2 safety"
    assert logic.state.employees['safety_researchers'] == 1, "Should have 1 safety researcher"
    
    print(f"After action:")
    print(f"  Money: ${logic.state.money:,.0f}")
    print(f"  Safety: {logic.state.safety}")
    print(f"  Safety researchers: {logic.state.employees['safety_researchers']}")
    
    # Test 2: Turn processing
    print(f"\n--- Test 2: Turn Processing ---")
    print(f"Processing turn end...")
    result = logic.process_turn_end()
    
    assert result.success, "Turn should process"
    assert logic.state.turn == 1, "Turn should increment"
    
    print(f"After turn:")
    print(f"  Turn: {logic.state.turn}")
    print(f"  Compute: {logic.state.compute}")
    print(f"  Money: ${logic.state.money:,.0f} (after maintenance)")
    
    # Test 3: Resource purchase
    print(f"\n--- Test 3: Resource Actions ---")
    result = logic.execute_action('purchase_compute')
    assert result.success, "Purchase should succeed"
    print(f"  Purchase compute: {logic.state.compute}")
    
    # Test 4: Research with requirements
    print(f"\n--- Test 4: Research Actions ---")
    result = logic.execute_action('research_safety')
    assert result.success, "Research should succeed with staff"
    print(f"  Safety research (with staff): Succeeded")
    print(f"  Safety after research: {logic.state.safety}")
    
    # Test a research action that should fail (no capabilities researchers)
    result = logic.execute_action('research_capabilities')
    assert not result.success, "Should fail without capabilities researchers"
    print(f"  Capabilities research (no staff): Failed as expected")
    
    # Test 5: Engine interface functionality
    print(f"\n--- Test 5: Engine Interface ---")
    available_actions = logic.get_available_actions()
    print(f"  Available actions: {len(available_actions)}")
    print(f"  Can afford hire_capabilities_researcher: {logic.can_afford_action('hire_capabilities_researcher')}")
    
    # Test 6: State serialization (important for save/load)
    print(f"\n--- Test 6: State Serialization ---")
    state_dict = logic.state.to_dict()
    assert isinstance(state_dict, dict), "State should serialize to dict"
    reconstructed_state = logic.state.__class__.from_dict(state_dict)
    assert reconstructed_state.turn == logic.state.turn, "State should deserialize correctly"
    print(f"  State serialization: Working")
    
    print(f"\n=== [OK] Integration test passed! ===")
    print(f"Final state:")
    print(f"  Turn: {logic.state.turn}")
    print(f"  Money: ${logic.state.money:,.0f}")
    print(f"  Safety: {logic.state.safety}")
    print(f"  Compute: {logic.state.compute}")
    print(f"  Employees: {logic.state.get_total_employees()}")
    
    pygame.quit()

if __name__ == '__main__':
    test_integration()