"""
High score screen for P(Doom) - Display leaderboards and score submission

This module provides the high score screen that displays both local and remote
leaderboards with player score submission functionality.
"""

import pygame
from visual_feedback import visual_feedback, ButtonState, draw_low_poly_button


def draw_high_score_screen(screen, w, h, game_state, seed, submit_callback=None):
    """
    Draw the high score screen with leaderboards and submission options.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        game_state: current game state with final scores
        seed: game seed used for this run
        submit_callback: optional callback for leaderboard submission
    """
    # Clear background
    screen.fill((20, 30, 40))  # Dark blue background for high scores
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    header_font = pygame.font.SysFont('Consolas', int(h*0.04), bold=True)
    font = pygame.font.SysFont('Consolas', int(h*0.025))
    small_font = pygame.font.SysFont('Consolas', int(h*0.02))
    
    # Title
    title_text = title_font.render("P(Doom) High Scores", True, (255, 255, 255))
    title_x = w // 2 - title_text.get_width() // 2
    screen.blit(title_text, (title_x, int(h * 0.05)))
    
    # Player's final score section
    score_y = int(h * 0.15)
    final_header = header_font.render("Your Final Score", True, (255, 220, 100))
    screen.blit(final_header, (int(w * 0.05), score_y))
    
    # Score details box
    score_box = pygame.Rect(int(w * 0.05), score_y + int(h * 0.05), int(w * 0.9), int(h * 0.25))
    pygame.draw.rect(screen, (40, 40, 70), score_box, border_radius=12)
    pygame.draw.rect(screen, (130, 190, 255), score_box, width=3, border_radius=12)
    
    # Score details
    details_x = score_box.x + int(w * 0.02)
    details_y = score_box.y + int(h * 0.02)
    line_height = int(h * 0.03)
    
    score_lines = [
        f"Turns Survived: {game_state.turn}",
        f"Final Staff: {game_state.staff}",
        f"Final Money: ${game_state.money:,}",
        f"Final Reputation: {game_state.reputation}",
        f"Final p(Doom): {game_state.doom:.1f}%",
        f"Seed: {seed}",
        f"High Score: {getattr(game_state, 'highscore', game_state.turn)}"
    ]
    
    for i, line in enumerate(score_lines):
        color = (240, 255, 255)
        if i == len(score_lines) - 1:  # Highlight high score
            color = (255, 220, 100)
        text = font.render(line, True, color)
        screen.blit(text, (details_x, details_y + i * line_height))
    
    # Leaderboard section (placeholder for now)
    leaderboard_y = score_y + int(h * 0.32)
    leaderboard_header = header_font.render("Local High Scores", True, (255, 220, 100))
    screen.blit(leaderboard_header, (int(w * 0.05), leaderboard_y))
    
    # Simple leaderboard placeholder
    leaderboard_box = pygame.Rect(int(w * 0.05), leaderboard_y + int(h * 0.05), int(w * 0.9), int(h * 0.25))
    pygame.draw.rect(screen, (30, 30, 50), leaderboard_box, border_radius=12)
    pygame.draw.rect(screen, (100, 150, 200), leaderboard_box, width=2, border_radius=12)
    
    # Placeholder leaderboard entries
    entries_x = leaderboard_box.x + int(w * 0.02)
    entries_y = leaderboard_box.y + int(h * 0.02)
    
    placeholder_entries = [
        "1. Anonymous - 42 turns",
        "2. Anonymous - 35 turns", 
        "3. Anonymous - 28 turns",
        "4. Anonymous - 23 turns",
        "5. Anonymous - 19 turns"
    ]
    
    for i, entry in enumerate(placeholder_entries):
        entry_text = font.render(entry, True, (200, 220, 240))
        screen.blit(entry_text, (entries_x, entries_y + i * line_height))
    
    # Control instructions
    instructions_y = int(h * 0.85)
    instructions = [
        "Press SPACE to return to main menu",
        "Press ESC to exit game"
    ]
    
    for i, instruction in enumerate(instructions):
        instruction_text = small_font.render(instruction, True, (180, 180, 180))
        instruction_x = w // 2 - instruction_text.get_width() // 2
        screen.blit(instruction_text, (instruction_x, instructions_y + i * int(h * 0.03)))