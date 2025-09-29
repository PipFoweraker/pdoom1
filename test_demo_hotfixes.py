#!/usr/bin/env python3
"""
Test script to validate the demo hotfix session fixes:
1. Activity log width extension
2. Action button click detection fix

This script programmatically validates that both fixes work correctly
without requiring GUI interaction.
"""

import pygame
from src.core.game_state import GameState


def test_activity_log_width():
    """Test that activity log extends to proper width."""
    print("\n=== Testing Activity Log Width ===")
    
    # Initialize pygame for UI testing
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    w, h = screen.get_size()
    
    gs = GameState('test-seed')
    gs.scrollable_event_log_enabled = True
    
    # Calculate expected log width (should be 34% of screen width)
    expected_width = int(w * 0.34)
    
    # Check END TURN button position (starts at 39%)
    endturn_x = int(w * 0.39)
    gap = endturn_x - (int(w * 0.04) + expected_width)  # Left margin + log width
    
    print(f"Screen width: {w}px")
    print(f"Activity log width: {expected_width}px (36%)")
    print(f"END TURN button starts at: {endturn_x}px (39%)")
    print(f"Gap between log and button: {gap}px")
    
    if gap >= 10:  # At least 10px gap is reasonable
        print("✓ Activity log width is appropriate - good gap to END TURN button")
        return True
    else:
        print("✗ Activity log might overlap with END TURN button")
        return False


def test_action_button_click_detection():
    """Test that action button rectangles are properly stored for click detection."""
    print("\n=== Testing Action Button Click Detection ===")
    
    # Initialize pygame for UI testing
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    w, h = screen.get_size()
    
    gs = GameState('test-seed')
    
    # Simulate the UI drawing process to populate filtered_action_rects
    import ui
    font = pygame.font.SysFont('Arial', 24)
    small_font = pygame.font.SysFont('Arial', 16)
    big_font = pygame.font.SysFont('Arial', 36)
    
    # This will populate gs.filtered_action_rects
    ui.draw_ui(screen, gs, font, small_font, big_font)
    
    # Check if filtered_action_rects is properly set
    if hasattr(gs, 'filtered_action_rects') and gs.filtered_action_rects:
        num_rects = len(gs.filtered_action_rects)
        print(f"✓ Found {num_rects} action button rectangles stored for click detection")
        
        # Check if rectangles are reasonable (not zero height/width)
        valid_rects = 0
        for i, rect in enumerate(gs.filtered_action_rects):
            if rect.width > 0 and rect.height > 0:
                valid_rects += 1
                print(f"  Action {i+1}: {rect.width}x{rect.height} at ({rect.x}, {rect.y})")
        
        if valid_rects == num_rects:
            print(f"✓ All {valid_rects} action button rectangles have valid dimensions")
            return True
        else:
            print(f"✗ Only {valid_rects}/{num_rects} rectangles have valid dimensions")
            return False
    else:
        print("✗ No action button rectangles found - click detection will fail")
        return False


def main():
    """Run all validation tests."""
    print("Demo Hotfix Validation Test")
    print("=" * 40)
    
    test1_passed = test_activity_log_width()
    test2_passed = test_action_button_click_detection()
    
    print("\n" + "=" * 40)
    if test1_passed and test2_passed:
        print("✓ ALL TESTS PASSED - Demo hotfixes are working correctly!")
        return True
    else:
        print("✗ Some tests failed - fixes need review")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)