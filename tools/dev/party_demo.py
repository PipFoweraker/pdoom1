# !/usr/bin/env python3
"""
Quick Game Over Demo for Party
===============================

Forces a game over state to immediately see the spectacular 
enhanced game over screen with leaderboard integration.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.game_state import GameState
from src.scores.enhanced_leaderboard import EnhancedLeaderboardManager
import pygame

def create_demo_session():
    """Create an impressive demo game session for the party."""
    print("[DEMO] Creating impressive game session...")
    
    # Create enhanced demo session
    gs = GameState('party-demo-2025')
    gs.lab_name = 'Quantum AI Labs'  # Cool name for party
    gs.player_name = 'PartyHost'
    
    # Set impressive stats
    gs.turn = 28  # Good survival time
    gs.money = 82000  # Decent money management
    gs.staff = 5  # Strong team
    gs.reputation = 195  # High reputation
    gs.doom = 42  # Reasonable risk level
    
    print(f"Demo Lab: {gs.lab_name}")
    print(f"Survived: {gs.turn} turns")
    print(f"Final Stats: ${gs.money:,}, {gs.staff} staff, {gs.reputation} rep, {gs.doom}% doom")
    
    # Record to leaderboard for comparison
    manager = EnhancedLeaderboardManager()
    manager.start_game_session(gs)
    success, rank, session = manager.end_game_session(gs)
    print(f"Leaderboard Rank: #{rank}")
    
    return gs

def force_game_over_screen():
    """Launch the game with a forced game over to see the enhanced screen."""
    print("[DEMO] Launching enhanced game over screen...")
    
    # Initialize pygame
    pygame.init()
    
    # Create demo session
    gs = create_demo_session()
    
    # Force game over state
    gs.game_over = True
    gs.end_game_scenario = None  # Use basic game over for clean demo
    
    # Set up display
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("P(Doom) - Enhanced Game Over Demo")
    
    # Import and run the enhanced game over screen
    from ui import render_game_over_screen
    
    clock = pygame.time.Clock()
    selected_item = 0
    running = True
    
    print("[SUCCESS] Enhanced game over screen loaded!")
    print("Look for:")
    print("- 'NEW HIGH SCORE!' celebration (if you're #1)")
    print("- Lab name prominently displayed")
    print("- Mini leaderboard with your rank highlighted")
    print("- Professional statistics presentation")
    print("- Green styling for new records!")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    selected_item = max(0, selected_item - 1)
                elif event.key == pygame.K_DOWN:
                    selected_item = min(4, selected_item + 1)
                elif event.key == pygame.K_RETURN:
                    print(f"Selected: {['View Full Leaderboard', 'Play Again', 'Main Menu', 'Settings', 'Submit Feedback'][selected_item]}")
                    if selected_item == 0:  # View Full Leaderboard
                        print("This would open the full leaderboard screen!")
                    elif selected_item == 1:  # Play Again
                        running = False
        
        screen.fill((20, 25, 40))  # Dark background
        render_game_over_screen(screen, gs, gs.seed, selected_item)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("[DEMO COMPLETE] Ready for party presentation!")

if __name__ == "__main__":
    force_game_over_screen()
