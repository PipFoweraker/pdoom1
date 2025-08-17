"""
End game menu screen for P(Doom) - Display game over screen with statistics

This module provides the end game menu with final statistics, game outcomes,
and navigation options after a game session ends.
"""

import pygame
from ui import wrap_text


def draw_end_game_menu(screen, w, h, selected_item, game_state, seed):
    """
    Draw the end-of-game menu with game summary and options.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected menu item (for keyboard navigation)
        game_state: GameState object for displaying final stats
        seed: Game seed used for this session
    
    Features:
    - Displays final game statistics
    - Menu options: Relaunch, Main Menu, Settings, Submit Feedback, Submit Bug
    - Keyboard navigation support
    - Consistent styling with main menu
    """
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.05), bold=True)
    subtitle_font = pygame.font.SysFont('Consolas', int(h*0.035))
    stats_font = pygame.font.SysFont('Consolas', int(h*0.025))
    menu_font = pygame.font.SysFont('Consolas', int(h*0.03), bold=True)
    small_font = pygame.font.SysFont('Consolas', int(h*0.02))
    
    # Colors
    title_color = (255, 100, 100)  # Red for "GAME OVER"
    subtitle_color = (255, 220, 220)
    stats_color = (240, 255, 255)
    menu_active_color = (100, 200, 255)
    menu_inactive_color = (180, 180, 180)
    button_bg_active = (70, 130, 180)
    button_bg_inactive = (60, 60, 100)
    
    # Title
    if game_state.end_game_scenario:
        title_text = title_font.render(game_state.end_game_scenario.title, True, title_color)
    else:
        title_text = title_font.render("GAME OVER", True, title_color)
    title_rect = title_text.get_rect(center=(w//2, int(h*0.08)))
    screen.blit(title_text, title_rect)
    
    # Game end scenario description
    if game_state.end_game_scenario:
        # Wrap the description text
        description_lines = wrap_text(game_state.end_game_scenario.description, subtitle_font, w*2//3)
        start_y = int(h*0.13)
        for i, line in enumerate(description_lines[:4]):  # Limit to 4 lines to fit layout
            desc_text = subtitle_font.render(line, True, subtitle_color)
            desc_rect = desc_text.get_rect(center=(w//2, start_y + i * int(h*0.025)))
            screen.blit(desc_text, desc_rect)
    else:
        # Fallback to last message
        end_message = game_state.messages[-1] if game_state.messages else "Game ended"
        subtitle_text = subtitle_font.render(end_message, True, subtitle_color)
        subtitle_rect = subtitle_text.get_rect(center=(w//2, int(h*0.15)))
        screen.blit(subtitle_text, subtitle_rect)
    
    # Game statistics in a box - adjust position to make room for scenario details
    stats_box_y = int(h*0.25) if game_state.end_game_scenario else int(h*0.22)
    stats_box = pygame.Rect(w//6, stats_box_y, w*2//3, int(h*0.22))
    pygame.draw.rect(screen, (40, 40, 70), stats_box, border_radius=12)
    pygame.draw.rect(screen, (130, 190, 255), stats_box, width=3, border_radius=12)
    
    # Statistics content
    stats_lines = [
        f"Survived until Turn: {game_state.turn}",
        f"Final Staff: {game_state.staff}",
        f"Final Money: ${game_state.money}",
        f"Final Reputation: {game_state.reputation}",
        f"Final p(Doom): {game_state.doom}%",
        f"Seed: {seed}",
        f"High Score (turns): {game_state.highscore}"
    ]
    
    stats_start_y = stats_box.y + 15
    line_height = int(h*0.025)
    
    for i, line in enumerate(stats_lines):
        stats_text = stats_font.render(line, True, stats_color)
        screen.blit(stats_text, (stats_box.x + 20, stats_start_y + i * line_height))
    
    # Cause Analysis section (if scenario available)
    if game_state.end_game_scenario and game_state.end_game_scenario.cause_analysis:
        analysis_y = stats_box.y + stats_box.height + 15
        analysis_box = pygame.Rect(w//6, analysis_y, w*2//3, int(h*0.12))
        pygame.draw.rect(screen, (50, 30, 30), analysis_box, border_radius=8)
        pygame.draw.rect(screen, (200, 100, 100), analysis_box, width=2, border_radius=8)
        
        # Analysis title
        analysis_title = small_font.render("What Went Wrong:", True, (255, 200, 200))
        screen.blit(analysis_title, (analysis_box.x + 15, analysis_box.y + 8))
        
        # Analysis text (wrapped)
        analysis_lines = wrap_text(game_state.end_game_scenario.cause_analysis, small_font, analysis_box.width - 30)
        for i, line in enumerate(analysis_lines[:3]):  # Limit to 3 lines
            analysis_text = small_font.render(line, True, (255, 220, 220))
            screen.blit(analysis_text, (analysis_box.x + 15, analysis_box.y + 25 + i * 16))
    
    # Legacy Note section (if scenario available)
    if game_state.end_game_scenario and game_state.end_game_scenario.legacy_note:
        legacy_y_offset = int(h*0.12) + 20 if game_state.end_game_scenario.cause_analysis else 15
        legacy_y = stats_box.y + stats_box.height + legacy_y_offset
        legacy_box = pygame.Rect(w//6, legacy_y, w*2//3, int(h*0.08))
        pygame.draw.rect(screen, (30, 50, 30), legacy_box, border_radius=8)
        pygame.draw.rect(screen, (100, 200, 100), legacy_box, width=2, border_radius=8)
        
        # Legacy title
        legacy_title = small_font.render("Your Legacy:", True, (200, 255, 200))
        screen.blit(legacy_title, (legacy_box.x + 15, legacy_box.y + 8))
        
        # Legacy text (wrapped)
        legacy_lines = wrap_text(game_state.end_game_scenario.legacy_note, small_font, legacy_box.width - 30)
        for i, line in enumerate(legacy_lines[:2]):  # Limit to 2 lines
            legacy_text = small_font.render(line, True, (220, 255, 220))
            screen.blit(legacy_text, (legacy_box.x + 15, legacy_box.y + 25 + i * 16))
    
    # Menu options
    menu_items = ["Relaunch Game", "Main Menu", "Settings", "Submit Feedback", "Submit Bug Request"]
    
    button_width = int(w * 0.35)
    button_height = int(h * 0.06)
    start_y = int(h * 0.55)
    spacing = int(h * 0.08)
    center_x = w // 2
    
    for i, item in enumerate(menu_items):
        # Button rectangle
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Button styling based on selection
        if i == selected_item:
            pygame.draw.rect(screen, button_bg_active, button_rect, border_radius=8)
            pygame.draw.rect(screen, menu_active_color, button_rect, width=3, border_radius=8)
            text_color = (255, 255, 255)
        else:
            pygame.draw.rect(screen, button_bg_inactive, button_rect, border_radius=8)
            pygame.draw.rect(screen, menu_inactive_color, button_rect, width=2, border_radius=8)
            text_color = menu_inactive_color
        
        # Button text
        button_text = menu_font.render(item, True, text_color)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
    
    # Instructions
    instruction_text = small_font.render("Use arrow keys to navigate, Enter to select, Escape for Main Menu", True, (200, 200, 200))
    inst_rect = instruction_text.get_rect(center=(w//2, int(h*0.92)))
    screen.blit(instruction_text, inst_rect)