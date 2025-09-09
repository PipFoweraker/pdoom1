#!/usr/bin/env python3
"""
Test script for lab name functionality
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_lab_name_system():
    """Test all components of the lab name system"""
    print("[TEST] Testing Lab Name System...")
    
    # Test 1: Lab Name Manager
    print("\n1. Testing Lab Name Manager...")
    from src.services.lab_name_manager import get_lab_name_manager
    
    manager = get_lab_name_manager()
    assert len(manager._lab_names) > 0, "Should have lab names loaded"
    
    # Test random name generation
    name1 = manager.get_random_lab_name("test1")
    manager.get_random_lab_name("test2")
    name3 = manager.get_random_lab_name("test1")  # Same seed
    
    assert name1 == name3, "Same seed should give same name"
    assert isinstance(name1, str), "Should return string"
    print(f"   ? Deterministic naming: '{name1}' == '{name3}'")
    
    # Test 2: Game State Integration
    print("\n2. Testing Game State Integration...")
    from src.core.game_state import GameState
    
    gs = GameState('integration-test')
    assert hasattr(gs, 'lab_name'), "Game state should have lab_name attribute"
    assert isinstance(gs.lab_name, str), "Lab name should be string"
    assert len(gs.lab_name) > 0, "Lab name should not be empty"
    print(f"   ? Game state lab name: '{gs.lab_name}'")
    
    # Test 3: UI Integration
    print("\n3. Testing UI Integration...")
    from ui import get_default_context_info
    
    context_info = get_default_context_info(gs)
    assert context_info['title'] == gs.lab_name, "UI title should show lab name"
    print(f"   ? UI displays lab name: '{context_info['title']}'")
    
    # Test 4: Leaderboard Integration
    print("\n4. Testing Leaderboard Integration...")
    import json
    
    # Create a finished game
    gs_finished = GameState('leaderboard-test-unique')
    gs_finished.game_over = True
    gs_finished.turn = 10
    gs_finished.save_highscore()
    
    # Check saved data
    with open('local_highscore.json', 'r') as f:
        data = json.load(f)
    
    record = data['leaderboard-test-unique']
    assert record['lab_name'] == gs_finished.lab_name, "Leaderboard should save lab name"
    assert record['score'] == 10, "Leaderboard should save score"
    print(f"   ? Leaderboard entry: {record['lab_name']} - {record['score']} turns")
    
    print("\n[CELEBRATION] All tests passed! Lab name system is working correctly.")
    print(f"\n[LIST] Summary:")
    print(f"   ? Lab names loaded: {len(manager._lab_names)}")
    print(f"   ? Themes available: {len(manager.get_all_themes())}")
    print(f"   ? Deterministic naming: ?")
    print(f"   ? UI integration: ?") 
    print(f"   ? Leaderboard integration: ?")

if __name__ == "__main__":
    test_lab_name_system()
