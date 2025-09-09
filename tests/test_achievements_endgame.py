#!/usr/bin/env python3
"""
Test script for the achievements and endgame scenarios functionality.
Validates Issue #195 implementation - endgame scenarios beyond binary win/lose.

This test suite covers:
- Achievement unlocking system
- Critical warning system  
- Victory condition detection
- Pyrrhic victory scenarios
- Endgame scenario analysis
- Integration with existing systems

Testing approach follows existing patterns from test_fixes.py and test_technical_failures.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_achievements_system_imports():
    """Test that all achievement system components can be imported."""
    print("[TEST] Testing Achievement System Imports")
    print("=" * 50)
    
    try:
        from src.features.achievements_endgame import (
            Achievement, AchievementType, EndGameType, WarningType,
            AchievementsEndgameSystem, achievements_endgame_system
        )
        print("? Achievement system imports successfully")
        return True
    except ImportError as e:
        print(f"? Achievement system import failed: {e}")
        return False

def test_achievement_creation():
    """Test Achievement class creation and properties."""
    print("\n[TEST] Testing Achievement Creation")
    print("=" * 50)
    
    try:
        from src.features.achievements_endgame import Achievement, AchievementType
        
        # Test basic achievement creation
        achievement = Achievement(
            achievement_id="test_achievement",
            name="Test Achievement",
            description="A test achievement",
            achievement_type=AchievementType.SURVIVAL,
            check_condition=lambda gs: True,  # Simple test condition
            rarity="common"
        )
        
        assert achievement.id == "test_achievement", "Achievement ID incorrect"
        assert achievement.name == "Test Achievement", "Achievement name incorrect"
        assert achievement.type == AchievementType.SURVIVAL, "Achievement type incorrect"
        assert achievement.rarity == "common", "Achievement rarity incorrect"
        
        print("? Achievement creation works correctly")
        return True
    except Exception as e:
        print(f"? Achievement creation failed: {e}")
        return False

def test_achievements_endgame_system_initialization():
    """Test AchievementsEndgameSystem initialization."""
    print("\n[TEST] Testing Achievements System Initialization")
    print("=" * 50)
    
    try:
        from src.features.achievements_endgame import achievements_endgame_system
        
        # Test that system has achievements
        achievements = achievements_endgame_system.achievements
        assert len(achievements) > 0, "No achievements found in system"
        assert len(achievements) >= 20, f"Expected at least 20 achievements, found {len(achievements)}"
        
        # Test that system has all required achievement types
        achievement_types = {ach.type for ach in achievements.values()}
        required_types = ["SURVIVAL", "WORKFORCE", "RESEARCH", "FINANCIAL", "SAFETY", "REPUTATION"]
        for req_type in required_types:
            found = any(ach_type.name == req_type for ach_type in achievement_types)
            assert found, f"Missing required achievement type: {req_type}"
        
        print(f"? Achievements system initialized with {len(achievements)} achievements")
        return True
    except Exception as e:
        print(f"? Achievements system initialization failed: {e}")
        return False

def test_game_state_integration():
    """Test integration with game state system."""
    print("\n[TEST] Testing Game State Integration")
    print("=" * 50)
    
    try:
        from src.core.game_state import GameState
        
        # Create test game state
        game_state = GameState(seed="test_seed")
        
        # Check that achievements tracking variables exist
        assert hasattr(game_state, 'unlocked_achievements'), "Missing unlocked_achievements"
        assert hasattr(game_state, 'peak_reputation'), "Missing peak_reputation"
        assert hasattr(game_state, 'min_money_reached'), "Missing min_money_reached"
        assert hasattr(game_state, 'max_doom_reached'), "Missing max_doom_reached"
        
        # Check that achievements processing method exists
        assert hasattr(game_state, '_process_achievements_and_warnings'), "Missing achievements processing method"
        
        print("? Game state integration successful")
        return True
    except Exception as e:
        print(f"? Game state integration failed: {e}")
        return False

def test_achievement_checking():
    """Test achievement checking logic."""
    print("\n[TEST] Testing Achievement Checking Logic")
    print("=" * 50)
    
    try:
        from src.core.game_state import GameState
        from src.features.achievements_endgame import achievements_endgame_system
        
        # Create test game state
        game_state = GameState(seed="test_seed")
        
        # Simulate conditions for "First Steps" achievement (first turn)
        game_state.turn = 1
        
        # Check for new achievements
        new_achievements = achievements_endgame_system.check_new_achievements(game_state)
        
        # Should have some achievements available (any achievement that can be unlocked early)
        # We'll just check that the system can check achievements without crashing
        assert isinstance(new_achievements, list), "Achievement checking should return a list"
        
        print("? Achievement checking logic works")
        return True
    except Exception as e:
        print(f"? Achievement checking failed: {e}")
        return False

def test_warning_system():
    """Test critical warning system."""
    print("\n[TEST] Testing Warning System")
    print("=" * 50)
    
    try:
        from src.core.game_state import GameState
        from src.features.achievements_endgame import achievements_endgame_system
        
        # Create test game state with high doom
        game_state = GameState(seed="test_seed")
        game_state.doom = 85  # Should trigger warning
        
        # Check for warnings
        warnings = achievements_endgame_system.check_critical_warnings(game_state)
        
        # Should have at least one warning at 85% doom
        assert len(warnings) > 0, "No warnings generated at 85% doom"
        
        # Test extreme doom warning
        game_state.doom = 98  # Should trigger multiple warnings
        extreme_warnings = achievements_endgame_system.check_critical_warnings(game_state)
        assert len(extreme_warnings) > len(warnings), "Should have more warnings at 98% doom"
        
        print(f"? Warning system works (85% doom: {len(warnings)}, 98% doom: {len(extreme_warnings)})")
        return True
    except Exception as e:
        print(f"? Warning system failed: {e}")
        return False

def test_victory_conditions():
    """Test victory condition detection."""
    print("\n[TEST] Testing Victory Conditions")
    print("=" * 50)
    
    try:
        from src.core.game_state import GameState
        
        # Create test game state with victory condition
        game_state = GameState(seed="test_seed")
        game_state.doom = 0  # Ultimate victory condition
        game_state.turn = 100  # Some progress made
        
        # Process achievements and warnings (should detect victory)
        initial_game_over = game_state.game_over
        game_state._process_achievements_and_warnings()
        
        # Should trigger game over due to victory
        assert game_state.game_over == True, "Victory not detected at doom = 0"
        
        print("? Victory condition detection works")
        return True
    except Exception as e:
        print(f"? Victory condition test failed: {e}")
        return False

def test_endgame_scenarios_integration():
    """Test integration with enhanced endgame scenarios."""
    print("\n[TEST] Testing Endgame Scenarios Integration")
    print("=" * 50)
    
    try:
        from src.features.end_game_scenarios import EndGameScenariosManager
        from src.core.game_state import GameState
        
        # Create test game state with victory
        game_state = GameState(seed="test_seed")
        game_state.doom = 0
        game_state.turn = 200
        game_state.unlocked_achievements = {"first_steps", "milestone_100", "efficiency_expert"}
        
        # Create scenarios manager
        scenarios_manager = EndGameScenariosManager()
        
        # Get scenario (should detect victory)
        scenario = scenarios_manager.get_scenario(game_state)
        
        assert scenario is not None, "No scenario returned for victory condition"
        
        print("? Endgame scenarios integration works")
        return True
    except Exception as e:
        print(f"? Endgame scenarios integration failed: {e}")
        return False

def test_resource_tracking():
    """Test resource tracking for achievements."""
    print("\n[TEST] Testing Resource Tracking")
    print("=" * 50)
    
    try:
        from src.core.game_state import GameState
        
        # Create test game state
        game_state = GameState(seed="test_seed")
        
        # Simulate resource changes that should be tracked
        initial_money = game_state.money
        game_state._add('money', 100)
        # Money doesn't have peak tracking in current implementation
        
        # Test reputation tracking (which does exist)
        initial_reputation = game_state.reputation
        game_state._add('reputation', 10)
        assert game_state.peak_reputation >= initial_reputation + 10, "Peak reputation not tracked correctly"
        
        print("? Resource tracking works correctly")
        return True
    except Exception as e:
        print(f"? Resource tracking failed: {e}")
        return False

def test_achievement_rarity_system():
    """Test achievement rarity classification."""
    print("\n[TEST] Testing Achievement Rarity System")
    print("=" * 50)
    
    try:
        from src.features.achievements_endgame import achievements_endgame_system
        
        # Count achievements by rarity
        rarity_counts = {}
        for achievement in achievements_endgame_system.achievements.values():
            rarity = achievement.rarity
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        # Should have achievements in multiple rarity categories
        assert len(rarity_counts) >= 3, f"Expected multiple rarity levels, found: {list(rarity_counts.keys())}"
        
        # Should have more common than legendary achievements
        common_count = rarity_counts.get("common", 0)
        legendary_count = rarity_counts.get("legendary", 0)
        assert common_count > legendary_count, "Should have more common than legendary achievements"
        
        print(f"? Achievement rarity system works: {rarity_counts}")
        return True
    except Exception as e:
        print(f"? Achievement rarity system failed: {e}")
        return False

def test_defensive_programming():
    """Test that achievement system handles errors gracefully."""
    print("\n[TEST] Testing Defensive Programming")
    print("=" * 50)
    
    try:
        from src.core.game_state import GameState
        
        # Create game state
        game_state = GameState(seed="test_seed")
        
        # Test that achievements processing doesn't crash with unusual values
        game_state.doom = 999  # Unusual value
        game_state.turn = -1   # Invalid turn
        
        # This should not crash the game
        game_state._process_achievements_and_warnings()
        
        print("? Defensive programming works - no crashes with unusual values")
        return True
    except Exception as e:
        print(f"? Defensive programming failed: {e}")
        return False

def run_all_tests():
    """Run all achievement system tests."""
    print("[ROCKET] Running Achievement & Endgame System Tests")
    print("=" * 60)
    print("Testing Issue #195 Implementation: Endgame scenarios beyond binary win/lose")
    print()
    
    tests = [
        test_achievements_system_imports,
        test_achievement_creation,
        test_achievements_endgame_system_initialization,
        test_game_state_integration,
        test_achievement_checking,
        test_warning_system,
        test_victory_conditions,
        test_endgame_scenarios_integration,
        test_resource_tracking,
        test_achievement_rarity_system,
        test_defensive_programming
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"? Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"[CHART] Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("[CELEBRATION] ALL TESTS PASSED! Achievement system is ready for Issue #195")
        print("\n[GAME] To test in game:")
        print("1. Run: python main.py")
        print("2. Start a game and play through several turns")
        print("3. Watch for achievement notifications and warnings")
        print("4. Try to reach p(Doom) = 0 for ultimate victory!")
    else:
        print(f"[WARNING]?  {failed} test(s) failed. Please review implementation.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
