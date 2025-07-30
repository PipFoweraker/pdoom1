import os
import sys
import pygame
import random
import json
from game_state import GameState
from ui import draw_ui, draw_scoreboard, draw_seed_prompt, draw_tooltip

# --- Adaptive window sizing --- #
pygame.init()
info = pygame.display.Info()
SCREEN_W = int(info.current_w * 0.8)
SCREEN_H = int(info.current_h * 0.8)
FLAGS = pygame.RESIZABLE
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), FLAGS)
pygame.display.set_caption("P(Doom) - Bureaucracy Strategy Prototype v3")
clock = pygame.time.Clock()

# --- Seed prompt --- #
seed = None
seed_input = ""
prompting_seed = True

def get_weekly_seed():
    import datetime
    # Example: YYYYWW (year and ISO week number)
    now = datetime.datetime.utcnow()
    return f"{now.year}{now.isocalendar()[1]}"

def main():
    global seed, seed_input, prompting_seed, screen, SCREEN_W, SCREEN_H

    # --- Prompt for seed --- #
    while prompting_seed:
        screen.fill((32, 32, 44))
        draw_seed_prompt(screen, seed_input, get_weekly_seed())
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Use entered seed or weekly default
                    seed = seed_input.strip() if seed_input.strip() else get_weekly_seed()
                    random.seed(seed)
                    prompting_seed = False
                elif event.key == pygame.K_BACKSPACE:
                    seed_input = seed_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.unicode.isprintable():
                    seed_input += event.unicode
    # --- Game setup --- #
    random.seed(seed)
    game_state = GameState(seed)
    scoreboard_active = False
    tooltip_text = None

    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Update screen size and redraw
                SCREEN_W, SCREEN_H = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), FLAGS)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if scoreboard_active:
                    # On scoreboard, click anywhere to restart
                    main()
                    return
                tooltip_text = game_state.handle_click((mx, my), SCREEN_W, SCREEN_H)
            elif event.type == pygame.MOUSEMOTION:
                tooltip_text = game_state.check_hover(event.pos, SCREEN_W, SCREEN_H)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_state.game_over:
                    game_state.end_turn()
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # --- Draw everything --- #
        screen.fill((25, 25, 35))
        if game_state.game_over:
            draw_scoreboard(screen, game_state, SCREEN_W, SCREEN_H, seed)
            scoreboard_active = True
        else:
            draw_ui(screen, game_state, SCREEN_W, SCREEN_H)
            if tooltip_text:
                draw_tooltip(screen, tooltip_text, pygame.mouse.get_pos(), SCREEN_W, SCREEN_H)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()