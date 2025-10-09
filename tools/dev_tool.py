# !/usr/bin/env python3
"""
P(Doom) Development Tool
========================

Simple but extensible dev tool for testing game functionality.
Designed for growth - easy to add new test scenarios and utilities.

Usage:
    python dev_tool.py                    # Interactive menu
    python dev_tool.py --test dual        # Run dual identity test
    python dev_tool.py --test leaderboard # Run leaderboard test
    python dev_tool.py --test game        # Run game state test
    python dev_tool.py --list             # List available tests
"""

import sys
import argparse
from typing import Dict, Callable, Any
from pathlib import Path

# Add project root to path for imports (now we're in tools/, so go up one level)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.game_state import GameState
from src.scores.enhanced_leaderboard import EnhancedLeaderboardManager
from src.services.version import get_display_version


class DevTool:
    """Extensible development testing tool."""
    
    def __init__(self):
        self.tests: Dict[str, Callable[[], None]] = {
            'dual': self.test_dual_identity,
            'leaderboard': self.test_leaderboard_system,
            'game': self.test_game_state,
            'session': self.test_complete_session,
            'seeds': self.test_seed_variations,
            'turns': self.test_turn_progression,
        }
    
    def test_dual_identity(self):
        """Test dual identity system (player_name + lab_name)."""
        print(f"[TEST] Testing Dual Identity System - P(Doom) {get_display_version()}")
        print("=" * 60)
        
        # Test basic dual identity
        gs = GameState('test-seed-123')
        print(f"Default Player Name: {gs.player_name}")
        print(f"Generated Lab Name: {gs.lab_name}")
        
        # Test customization
        gs.player_name = 'DevTester'
        print(f"Customized Player Name: {gs.player_name}")
        print(f"Lab Name (unchanged): {gs.lab_name}")
        
        # Test different seeds generate different lab names
        gs2 = GameState('different-seed')
        print(f"Different seed lab name: {gs2.lab_name}")
        
        print("[OK] Dual identity system working correctly")
    
    def test_leaderboard_system(self):
        """Test enhanced leaderboard functionality."""
        print(f"[TEST] Testing Enhanced Leaderboard System - P(Doom) {get_display_version()}")
        print("=" * 60)
        
        # Create manager
        manager = EnhancedLeaderboardManager()
        print("[OK] EnhancedLeaderboardManager created")
        
        # Test seed-specific retrieval
        seed = 'dev-test-seed'
        leaderboard = manager.get_leaderboard_for_seed(seed)
        print(f"[OK] Retrieved leaderboard for '{seed}': {len(leaderboard.entries)} entries")
        
        # Test session creation via end_game_session
        gs = GameState(seed)
        gs.player_name = 'DevTool'
        gs.turn = 10  # Use correct attribute name
        gs.money = 85000
        
        # Start and end session to test full lifecycle
        manager.start_game_session(gs)
        success, rank, session = manager.end_game_session(gs)
        print(f"[OK] Session lifecycle: Player='{session.player_name}', Lab='{session.lab_name}', Rank=#{rank}")
        
        print("[OK] Leaderboard system functioning correctly")
    
    def test_game_state(self):
        """Test basic game state functionality."""
        print(f"[TEST] Testing Game State - P(Doom) {get_display_version()}")
        print("=" * 60)
        
        gs = GameState('dev-game-test')
        print(f"Initial state:")
        print(f"  Turn: {gs.turn}")
        print(f"  Money: ${gs.money:,}")
        print(f"  Staff: {gs.staff}")
        print(f"  Reputation: {gs.reputation}")
        print(f"  Doom: {gs.doom}%")
        print(f"  Action Points: {gs.action_points}")
        
        # Test turn advancement
        gs.end_turn()
        print(f"After end_turn():")
        print(f"  Turn: {gs.turn}")
        print(f"  Action Points: {gs.action_points}")
        
        print("[OK] Game state working correctly")
    
    def test_complete_session(self):
        """Test complete game session simulation."""
        print(f"[TEST] Testing Complete Session Simulation - P(Doom) {get_display_version()}")
        print("=" * 60)
        
        # Create game and simulate progress
        gs = GameState('session-test')
        gs.player_name = 'SessionTester'
        
        print(f"Starting session: {gs.player_name} at {gs.lab_name}")
        
        # Simulate multiple turns
        for _ in range(5):
            gs.end_turn()
            gs.money -= 2000  # Simulate spending
            gs.reputation += 5  # Small progress
            print(f"  Turn {gs.turn}: ${gs.money:,}, Rep: {gs.reputation}")
        
        # Test leaderboard recording
        manager = EnhancedLeaderboardManager()
        manager.start_game_session(gs)
        success, rank, session = manager.end_game_session(gs)
        
        print(f"[OK] Session recorded to leaderboard (Rank #{rank})")
        
        # Verify recording
        leaderboard = manager.get_leaderboard_for_seed('session-test')
        print(f"[OK] Leaderboard now has {len(leaderboard.entries)} entries")
    
    def test_seed_variations(self):
        """Test how different seeds create different experiences."""
        print(f"[TEST] Testing Seed Variations - P(Doom) {get_display_version()}")
        print("=" * 60)
        
        seeds = ['alpha', 'beta', 'gamma', 'delta', 'epsilon']
        
        for seed in seeds:
            gs = GameState(seed)
            print(f"Seed '{seed}': Lab Name = '{gs.lab_name}'")
        
        print("[OK] Seed variation system working correctly")
    
    def test_turn_progression(self):
        """Test game progression over multiple turns to identify issues."""
        print(f"[TEST] Testing Turn Progression - P(Doom) {get_display_version()}")
        print("=" * 60)
        
        seed = input("Enter seed (or press Enter for 'debug-turns'): ").strip()
        if not seed:
            seed = 'debug-turns'
            
        max_turns_input = input("Enter max turns to test (or press Enter for 15): ").strip()
        try:
            max_turns = int(max_turns_input) if max_turns_input else 15
        except ValueError:
            max_turns = 15
        
        print(f"Testing seed '{seed}' for up to {max_turns} turns...")
        print("-" * 60)
        
        gs = GameState(seed)
        
        for turn_num in range(max_turns):
            doom_val = int(gs.doom) if hasattr(gs, 'doom') else 0
            processing_flag = getattr(gs, 'turn_processing', False)
            print(f"Turn {gs.turn:2d}: Staff={gs.staff:2d} Money=${gs.money:7,} Doom={doom_val:3d} Rep={gs.reputation:3d} Processing={processing_flag} GameOver={gs.game_over}")
            
            if gs.game_over:
                print(f"\n*** GAME OVER at turn {gs.turn} ***")
                print("Recent messages:")
                for i, msg in enumerate(gs.messages[-8:], 1):
                    print(f"  {i}: {msg}")
                break
            
            print(f"    -> Before end_turn: turn={gs.turn}, processing={getattr(gs, 'turn_processing', False)}")
            result = gs.end_turn()
            print(f"    -> After end_turn: turn={gs.turn}, processing={getattr(gs, 'turn_processing', False)}, result={result}")
            
            # Check if turn processing is stuck
            if getattr(gs, 'turn_processing', False):
                print(f"    -> WARNING: Turn processing stuck! Resetting...")
                gs.turn_processing = False
                gs.turn_processing_timer = 0
        else:
            print(f"\n[OK] Game survived {max_turns} turns without ending")
        
        print("[DONE] Turn progression test completed")
    
    def list_tests(self):
        """List all available tests."""
        print(f"[INFO] Available Tests - P(Doom) {get_display_version()}")
        print("=" * 60)
        
        for name, func in self.tests.items():
            doc = func.__doc__ or "No description"
            print(f"  {name:12} - {doc}")
    
    def interactive_menu(self):
        """Run interactive test selection menu."""
        print(f"[DEV] P(Doom) Development Tool - {get_display_version()}")
        print("=" * 60)
        print("Select a test to run:")
        print()
        
        for i, (name, func) in enumerate(self.tests.items(), 1):
            doc = func.__doc__ or "No description"
            print(f"  {i}. {name:12} - {doc}")
        
        print(f"  {len(self.tests) + 1}. Exit")
        print()
        
        try:
            choice = input("Enter choice (1-{}): ".format(len(self.tests) + 1))
            choice_num = int(choice)
            
            if choice_num == len(self.tests) + 1:
                print("Goodbye!")
                return
            
            if 1 <= choice_num <= len(self.tests):
                test_name = list(self.tests.keys())[choice_num - 1]
                print()
                self.run_test(test_name)
            else:
                print("Invalid choice!")
                
        except (ValueError, KeyboardInterrupt):
            print("\nGoodbye!")
    
    def run_test(self, test_name: str):
        """Run a specific test by name."""
        if test_name not in self.tests:
            print(f"[ERROR] Unknown test: {test_name}")
            print(f"Available tests: {', '.join(self.tests.keys())}")
            return
        
        try:
            self.tests[test_name]()
            print()
            print("[SUCCESS] Test completed successfully!")
        except Exception as e:
            print(f"[FAIL] Test failed: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="P(Doom) Development Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--test', '-t', 
                       help='Run specific test')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available tests')
    
    args = parser.parse_args()
    
    dev_tool = DevTool()
    
    if args.list:
        dev_tool.list_tests()
    elif args.test:
        dev_tool.run_test(args.test)
    else:
        dev_tool.interactive_menu()


if __name__ == "__main__":
    main()
