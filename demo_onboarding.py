#!/usr/bin/env python3
"""
Demonstration script for the P(Doom) onboarding system.

This script shows how the onboarding system works without needing to run the full game.
It demonstrates the tutorial progression and first-time help features.
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from onboarding import OnboardingSystem

def demonstrate_onboarding():
    """Demonstrate the onboarding system functionality."""
    print("=== P(Doom) Onboarding System Demo ===\n")
    
    # Create a fresh onboarding system (simulating new player)
    print("Creating new player onboarding system...")
    onboarding = OnboardingSystem()
    
    print(f"New player status:")
    print(f"  - Is first time: {onboarding.is_first_time}")
    print(f"  - Tutorial enabled: {onboarding.tutorial_enabled}")
    print(f"  - Should show tutorial: {onboarding.should_show_tutorial()}")
    print()
    
    # Start tutorial
    print("Starting tutorial...")
    onboarding.start_tutorial()
    print(f"  - Tutorial overlay active: {onboarding.show_tutorial_overlay}")
    print(f"  - Current step: {onboarding.current_tutorial_step}")
    print()
    
    # Demonstrate tutorial content
    print("Tutorial content for welcome step:")
    welcome_content = onboarding.get_tutorial_content('welcome')
    print(f"  Title: {welcome_content['title']}")
    print(f"  Content (first 100 chars): {welcome_content['content'][:100]}...")
    print(f"  Next step: {welcome_content['next_step']}")
    print()
    
    # Progress through tutorial steps
    print("Progressing through tutorial steps...")
    tutorial_sequence = ['welcome', 'resources', 'actions', 'action_points', 'end_turn', 'events', 'upgrades']
    
    for step in tutorial_sequence:
        print(f"  Completing step: {step}")
        onboarding.advance_tutorial_step(step)
        if onboarding.current_tutorial_step:
            print(f"    Next step: {onboarding.current_tutorial_step}")
        else:
            print("    Tutorial completed!")
            break
    
    print(f"  - Tutorial overlay active: {onboarding.show_tutorial_overlay}")
    print(f"  - Is first time: {onboarding.is_first_time}")
    print(f"  - Completed steps: {list(onboarding.completed_steps)}")
    print()
    
    # Demonstrate first-time help
    print("First-time help system:")
    mechanics = ['first_staff_hire', 'first_upgrade_purchase', 'action_points_exhausted', 'high_doom_warning']
    
    for mechanic in mechanics:
        if onboarding.should_show_mechanic_help(mechanic):
            help_content = onboarding.get_mechanic_help(mechanic)
            if help_content:
                print(f"  {mechanic}:")
                print(f"    Title: {help_content['title']}")
                print(f"    Content: {help_content['content'][:80]}...")
                # Mark as seen
                onboarding.mark_mechanic_seen(mechanic)
                print(f"    Now seen: {not onboarding.should_show_mechanic_help(mechanic)}")
        print()
    
    # Demonstrate tooltip system
    print("Tooltip system:")
    onboarding.add_tooltip("This is a high priority tooltip", priority=3)
    onboarding.add_tooltip("This is a low priority tooltip", priority=1)
    onboarding.add_tooltip("This is a medium priority tooltip", priority=2)
    
    print("  Added 3 tooltips with different priorities")
    print("  Getting tooltips in priority order:")
    while True:
        tooltip = onboarding.get_next_tooltip()
        if tooltip:
            print(f"    - {tooltip}")
        else:
            break
    
    print()
    
    # Test tutorial reset
    print("Testing tutorial reset...")
    onboarding.reset_tutorial()
    print(f"  - Is first time: {onboarding.is_first_time}")
    print(f"  - Tutorial dismissed: {onboarding.tutorial_dismissed}")
    print(f"  - Should show tutorial: {onboarding.should_show_tutorial()}")
    print(f"  - Completed steps: {len(onboarding.completed_steps)}")
    print(f"  - Seen mechanics: {len(onboarding.seen_mechanics)}")
    
    print("\n=== Demo Complete ===")
    print("The onboarding system is ready for new players!")
    print("Key features:")
    print("- Interactive tutorial with step progression")
    print("- Context-sensitive first-time help")
    print("- Persistent progress tracking")
    print("- Tooltip management system")
    print("- Tutorial reset capability")


if __name__ == "__main__":
    demonstrate_onboarding()