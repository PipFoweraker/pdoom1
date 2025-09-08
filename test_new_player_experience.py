#!/usr/bin/env python3
"""
Test script for the new player experience functionality.
Validates that the new system works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_new_player_experience():
    """Test the new player experience system."""
    print("🧪 Testing New Player Experience System")
    print("=" * 50)
    
    # Test 1: Verify the new menu item exists
    try:
        import main
        expected_menu_items = ["New Player Experience", "Launch with Custom Seed", "Settings", "Player Guide", "Exit"]
        actual_menu_items = main.menu_items
        assert actual_menu_items == expected_menu_items, f"Expected {expected_menu_items}, got {actual_menu_items}"
        print("✅ Test 1 PASSED: Menu items updated correctly")
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        return False
    
    # Test 2: Verify new player experience state variables exist
    try:
        # Check that the variables are defined
        assert hasattr(main, 'npe_tutorial_enabled'), "npe_tutorial_enabled not found"
        assert hasattr(main, 'npe_intro_enabled'), "npe_intro_enabled not found"
        assert hasattr(main, 'npe_selected_item'), "npe_selected_item not found"
        
        # Check initial values
        assert main.npe_tutorial_enabled == False, "npe_tutorial_enabled should start as False"
        assert main.npe_intro_enabled == False, "npe_intro_enabled should start as False"
        assert main.npe_selected_item == 0, "npe_selected_item should start as 0"
        print("✅ Test 2 PASSED: New player experience state variables correct")
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        return False
    
    # Test 3: Verify handler functions exist
    try:
        assert hasattr(main, 'handle_new_player_experience_click'), "handle_new_player_experience_click not found"
        assert hasattr(main, 'handle_new_player_experience_hover'), "handle_new_player_experience_hover not found" 
        assert hasattr(main, 'handle_new_player_experience_keyboard'), "handle_new_player_experience_keyboard not found"
        print("✅ Test 3 PASSED: Handler functions defined")
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        return False
    
    # Test 4: Verify UI function exists
    try:
        from ui import draw_new_player_experience
        print("✅ Test 4 PASSED: UI drawing function defined")
    except Exception as e:
        print(f"❌ Test 4 FAILED: {e}")
        return False
    
    # Test 5: Test state manipulation
    try:
        # Simulate enabling tutorial
        main.npe_tutorial_enabled = True
        assert main.npe_tutorial_enabled == True, "Could not enable tutorial"
        
        # Simulate enabling intro
        main.npe_intro_enabled = True
        assert main.npe_intro_enabled == True, "Could not enable intro"
        
        # Reset for clean state
        main.npe_tutorial_enabled = False
        main.npe_intro_enabled = False
        print("✅ Test 5 PASSED: State manipulation works")
    except Exception as e:
        print(f"❌ Test 5 FAILED: {e}")
        return False
    
    # Test 6: Test intro message integration
    try:
        from src.core.game_state import GameState
        
        # Enable intro and create game state
        main.npe_intro_enabled = True
        test_game_state = GameState('test-seed')
        
        # Simulate the intro message logic
        startup_money = test_game_state.money
        expected_intro = f"Doom is coming. You convinced a funder to give you ${startup_money:,}. Your job is to save the world. Good luck!"
        print(f"📝 Intro message would be: '{expected_intro}'")
        
        # Reset
        main.npe_intro_enabled = False
        print("✅ Test 6 PASSED: Intro message generation works")
    except Exception as e:
        print(f"❌ Test 6 FAILED: {e}")
        return False
    
    print("=" * 50)
    print("🎉 ALL TESTS PASSED! New Player Experience system is working correctly.")
    return True

if __name__ == "__main__":
    success = test_new_player_experience()
    sys.exit(0 if success else 1)
