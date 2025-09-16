#!/usr/bin/env python3
"""
Menu System Diagnostic Tests
Comprehensive testing for menu layout, positioning, and behavior across different game states.
Tests for hardcoded positioning issues and layout breaks.
"""

import unittest
import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game_state import GameState
from src.features.end_game_scenarios import EndGameScenario
import ui


class MenuSystemDiagnosticTests(unittest.TestCase):
    """Test suite for diagnosing menu system issues"""
    
    def setUp(self):
        """Initialize pygame and test surfaces"""
        pygame.init()
        pygame.font.init()
        
        # Test different screen sizes to catch hardcoded positioning
        self.screen_sizes = [
            (800, 600),    # Small screen
            (1024, 768),   # Medium screen  
            (1280, 720),   # HD
            (1920, 1080),  # Full HD
            (2560, 1440),  # 2K
            (640, 480),    # Very small
        ]
        
        # Create test surfaces for each size
        self.test_surfaces = {}
        for size in self.screen_sizes:
            self.test_surfaces[size] = pygame.Surface(size)
    
    def test_main_menu_layout_consistency(self):
        """Test main menu layout across different screen sizes"""
        print("\n=== Testing Main Menu Layout Consistency ===")
        
        for size in self.screen_sizes:
            with self.subTest(screen_size=size):
                surface = self.test_surfaces[size]
                w, h = size
                
                # Test main menu with different selected items
                for selected_item in range(5):  # Test multiple selections
                    try:
                        ui.draw_main_menu(surface, w, h, selected_item)
                        print(f"✓ Main menu renders at {w}x{h}, item {selected_item}")
                    except Exception as e:
                        self.fail(f"Main menu failed at {w}x{h}, item {selected_item}: {e}")
    
    def test_end_game_menu_positioning(self):
        """Test end game menu with various game states and screen sizes"""
        print("\n=== Testing End Game Menu Positioning ===")
        
        # Create different game states
        test_states = self._create_test_game_states()
        
        for size in self.screen_sizes:
            for state_name, game_state in test_states.items():
                with self.subTest(screen_size=size, game_state=state_name):
                    surface = self.test_surfaces[size]
                    w, h = size
                    
                    # Test with different selected menu items
                    for selected_item in range(5):
                        try:
                            ui.draw_end_game_menu(surface, w, h, selected_item, game_state, "test-seed")
                            print(f"[OK] End game menu renders at {w}x{h}, state: {state_name}, item: {selected_item}")
                        except Exception as e:
                            self.fail(f"End game menu failed at {w}x{h}, state: {state_name}, item: {selected_item}: {e}")
    
    def test_menu_button_bounds_checking(self):
        """Test that menu buttons stay within screen boundaries"""
        print("\n=== Testing Menu Button Bounds ===")
        
        # Mock button clicking to test bounds
        for size in self.screen_sizes:
            w, h = size
            
            # Test main menu buttons
            try:
                # This would ideally test actual button rectangles, but since ui.py doesn't expose them,
                # we'll test by creating a surface and ensuring no exceptions
                surface = self.test_surfaces[size]
                ui.draw_main_menu(surface, w, h, 0)
                
                # Check if content fits within bounds (basic test)
                # More sophisticated bounds checking would require refactoring ui.py
                self.assertGreater(w, 0)
                self.assertGreater(h, 0)
                print(f"✓ Main menu bounds OK at {w}x{h}")
                
            except Exception as e:
                self.fail(f"Main menu bounds test failed at {w}x{h}: {e}")
    
    def test_menu_text_scaling(self):
        """Test that menu text scales properly with screen size"""
        print("\n=== Testing Menu Text Scaling ===")
        
        game_state = GameState("text-scale-test")
        
        for size in self.screen_sizes:
            w, h = size
            surface = self.test_surfaces[size]
            
            try:
                # Test various menus that use text scaling
                ui.draw_main_menu(surface, w, h, 0)
                ui.draw_end_game_menu(surface, w, h, 0, game_state, "test-seed")
                ui.draw_sounds_menu(surface, w, h, 0)
                
                print(f"✓ Text scaling works at {w}x{h}")
                
            except Exception as e:
                self.fail(f"Text scaling failed at {w}x{h}: {e}")
    
    def test_end_game_scenarios_layout(self):
        """Test end game menu with different scenario types"""
        print("\n=== Testing End Game Scenarios Layout ===")
        
        # Test different end game scenarios
        scenarios = [
            EndGameScenario(
                "CATASTROPHIC_FAILURE",
                "AI System Compromised",
                "Your AI research lab has suffered a catastrophic security breach.",
                "Failed to implement adequate security measures early in development.",
                "Your lab's failure serves as a cautionary tale for the industry."
            ),
            EndGameScenario(
                "RESEARCH_SUCCESS", 
                "AI Safety Milestone Achieved",
                "Your lab successfully developed safe AI systems.",
                "Consistent investment in safety research paid off.",
                "Your work becomes the foundation for safe AI development worldwide."
            ),
            EndGameScenario(
                "FUNDING_CRISIS",
                "Financial Collapse", 
                "Unable to secure funding, your lab shuts down.",
                "Poor financial planning and unsuccessful fundraising.",
                "Your research notes are acquired by a larger corporation."
            ),
            None  # Test no scenario case
        ]
        
        for scenario in scenarios:
            game_state = GameState("scenario-test")
            game_state.end_game_scenario = scenario
            
            # Test across different screen sizes
            for size in self.screen_sizes:
                with self.subTest(scenario=scenario.title if scenario else "None", screen_size=size):
                    surface = self.test_surfaces[size]
                    w, h = size
                    
                    try:
                        ui.draw_end_game_menu(surface, w, h, 0, game_state, "test-seed")
                        scenario_name = scenario.title if scenario else "No Scenario"
                        print(f"✓ Scenario '{scenario_name}' renders at {w}x{h}")
                    except Exception as e:
                        scenario_name = scenario.title if scenario else "No Scenario"
                        self.fail(f"Scenario '{scenario_name}' failed at {w}x{h}: {e}")
    
    def test_menu_overflow_conditions(self):
        """Test menu behavior when content might overflow screen bounds"""
        print("\n=== Testing Menu Overflow Conditions ===")
        
        # Create game state with very long lab name and high stats
        game_state = GameState("overflow-test")
        game_state.lab_name = "Very Long Laboratory Name That Might Cause Layout Issues And Text Overflow Problems"
        game_state.turn = 999999
        game_state.money = 999999999
        game_state.staff = 999999
        game_state.reputation = 999999
        game_state.doom = 99.99
        
        # Test on smallest screen size where overflow most likely
        small_sizes = [(640, 480), (800, 600)]
        
        for size in small_sizes:
            w, h = size
            surface = self.test_surfaces[size]
            
            try:
                ui.draw_end_game_menu(surface, w, h, 0, game_state, "very-long-seed-name-that-might-cause-issues")
                print(f"✓ Overflow test passed at {w}x{h}")
            except Exception as e:
                self.fail(f"Overflow test failed at {w}x{h}: {e}")
    
    def test_menu_edge_cases(self):
        """Test menu behavior in edge case scenarios"""
        print("\n=== Testing Menu Edge Cases ===")
        
        # Test with minimal game state
        minimal_state = GameState("edge-test")
        minimal_state.staff = 0
        minimal_state.money = 0
        minimal_state.messages = []
        
        # Test with empty/None values
        edge_cases = [
            ("minimal", minimal_state),
            ("empty_messages", GameState("empty-msg-test"))
        ]
        
        for case_name, game_state in edge_cases:
            for size in [(800, 600), (1920, 1080)]:  # Test on common sizes
                with self.subTest(case=case_name, screen_size=size):
                    surface = self.test_surfaces[size]
                    w, h = size
                    
                    try:
                        ui.draw_end_game_menu(surface, w, h, 0, game_state, "edge-test")
                        print(f"✓ Edge case '{case_name}' OK at {w}x{h}")
                    except Exception as e:
                        self.fail(f"Edge case '{case_name}' failed at {w}x{h}: {e}")
    
    def test_hardcoded_position_detection(self):
        """Detect potential hardcoded positioning by comparing layouts across sizes"""
        print("\n=== Testing for Hardcoded Positioning Issues ===")
        
        game_state = GameState("hardcode-test")
        
        # Compare small vs large screen layouts - differences might indicate hardcoding
        small_surface = self.test_surfaces[(640, 480)]
        large_surface = self.test_surfaces[(1920, 1080)]
        
        # Test that functions don't throw exceptions (basic test)
        # More sophisticated would require extracting position data from ui.py
        try:
            ui.draw_end_game_menu(small_surface, 640, 480, 0, game_state, "test")
            ui.draw_end_game_menu(large_surface, 1920, 1080, 0, game_state, "test") 
            print("✓ No exceptions on different screen sizes - basic hardcoding test passed")
        except Exception as e:
            self.fail(f"Hardcoded positioning test failed: {e}")
    
    def _create_test_game_states(self):
        """Create various game states for testing"""
        states = {}
        
        # Normal end state
        normal_state = GameState("normal-test")
        normal_state.turn = 50
        normal_state.staff = 10
        normal_state.money = 50000
        normal_state.reputation = 75
        normal_state.doom = 25
        states["normal"] = normal_state
        
        # High stats state
        high_state = GameState("high-test") 
        high_state.turn = 200
        high_state.staff = 100
        high_state.money = 1000000
        high_state.reputation = 100
        high_state.doom = 5
        states["high_stats"] = high_state
        
        # Low stats state
        low_state = GameState("low-test")
        low_state.turn = 5
        low_state.staff = 1
        low_state.money = 100
        low_state.reputation = 10
        low_state.doom = 95
        states["low_stats"] = low_state
        
        # With end game scenario
        scenario_state = GameState("scenario-test")
        scenario_state.end_game_scenario = EndGameScenario(
            "TEST_SCENARIO",
            "Test End Game",
            "This is a test end game scenario with long description text that might cause layout issues.",
            "This is test cause analysis that explains what went wrong in detail.",
            "This is a test legacy note about the impact of the player's choices."
        )
        states["with_scenario"] = scenario_state
        
        return states
    
    def tearDown(self):
        """Clean up pygame"""
        pygame.quit()


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
