import os
import sys
import pygame
import random
import json
from game_state import GameState
from ui import draw_ui, draw_scoreboard, draw_seed_prompt, draw_tooltip, draw_main_menu, draw_overlay

# --- Adaptive window sizing --- #
pygame.init()
info = pygame.display.Info()
SCREEN_W = int(info.current_w * 0.8)
SCREEN_H = int(info.current_h * 0.8)
FLAGS = pygame.RESIZABLE
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), FLAGS)
pygame.display.set_caption("P(Doom) - Bureaucracy Strategy Prototype v3")
clock = pygame.time.Clock()

# --- Menu and game state management --- #
# Menu states: 'main_menu', 'custom_seed_prompt', 'game', 'overlay'
current_state = 'main_menu'
selected_menu_item = 0  # For keyboard navigation
menu_items = ["Launch with Weekly Seed", "Launch with Custom Seed", "Settings", "Player Guide", "README"]
seed = None
seed_input = ""
overlay_content = None
overlay_title = None
overlay_scroll = 0

def create_settings_content():
    """Create content for the settings menu"""
    return """# Settings

## Sound
Sound effects are enabled by default and can be toggled using the mute button in the bottom-right corner during gameplay.

## Controls
- **Mute Button**: Click the sound icon in the bottom-right corner to toggle all sound effects
- **Employee Blobs**: Watch animated employee blobs in the lower middle area
- **Compute Resources**: Purchase compute using the "Buy Compute" action ($100 per 10 flops)
- **Research Progress**: Productive employees (with compute) contribute to research papers

## Gameplay Features
- **Weekly Ticks**: Each turn represents one week
- **Employee Productivity**: Employees with compute show glowing halos and contribute to research
- **Research Papers**: Published when research progress reaches 100, boosting reputation
- **Starting Funding**: $100,000 to support expanded operations

## Visual Indicators
- **Glowing Halos**: Productive employees with compute access
- **Blob Animation**: New employees animate in from the side
- **Resource Display**: Compute, research progress, and papers published shown in top bar

Press Escape to return to the main menu."""

def get_weekly_seed():
    import datetime
    # Example: YYYYWW (year and ISO week number)
    now = datetime.datetime.utcnow()
    return f"{now.year}{now.isocalendar()[1]}"

def load_markdown_file(filename):
    """Load and return the contents of a markdown file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Could not load {filename}"

def handle_menu_click(mouse_pos, w, h):
    """
    Handle mouse clicks on main menu items.
    
    Args:
        mouse_pos: Tuple of (x, y) mouse coordinates
        w, h: Screen width and height for button positioning
    
    Updates global state based on which menu item was clicked:
    - Weekly Seed: Immediately starts game with current weekly seed
    - Custom Seed: Transitions to seed input prompt
    - Options: Currently inactive (greyed out)
    - Player Guide: Shows PLAYERGUIDE.md in scrollable overlay
    - README: Shows README.md in scrollable overlay
    """
    global current_state, selected_menu_item, seed, overlay_content, overlay_title
    
    # Calculate menu button positions (must match draw_main_menu layout)
    button_width = int(w * 0.4)
    button_height = int(h * 0.08)
    start_y = int(h * 0.35)
    spacing = int(h * 0.1)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    # Check each menu button for collision
    for i, item in enumerate(menu_items):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            selected_menu_item = i
            
            # Execute menu action based on selection
            if i == 0:  # Launch with Weekly Seed
                seed = get_weekly_seed()
                random.seed(seed)
                current_state = 'game'
            elif i == 1:  # Launch with Custom Seed
                current_state = 'custom_seed_prompt'
            elif i == 2:  # Options/Settings
                overlay_content = create_settings_content()
                overlay_title = "Settings"
                current_state = 'overlay'
            elif i == 3:  # Player Guide
                overlay_content = load_markdown_file('PLAYERGUIDE.md')
                overlay_title = "Player Guide"
                current_state = 'overlay'
            elif i == 4:  # README
                overlay_content = load_markdown_file('README.md')
                overlay_title = "README"
                current_state = 'overlay'
            break

def handle_menu_keyboard(key):
    """
    Handle keyboard navigation in main menu.
    
    Args:
        key: pygame key constant from keydown event
    
    Supports:
    - Up/Down arrows: Navigate between menu items
    - Enter: Activate currently selected menu item
    
    Same functionality as handle_menu_click but for keyboard users.
    """
    global selected_menu_item, current_state, seed, overlay_content, overlay_title
    
    if key == pygame.K_UP:
        # Move selection up, wrapping to bottom
        selected_menu_item = (selected_menu_item - 1) % len(menu_items)
    elif key == pygame.K_DOWN:
        # Move selection down, wrapping to top  
        selected_menu_item = (selected_menu_item + 1) % len(menu_items)
    elif key == pygame.K_RETURN:
        # Activate selected menu item (same logic as mouse click)
        if selected_menu_item == 0:  # Launch with Weekly Seed
            seed = get_weekly_seed()
            random.seed(seed)
            current_state = 'game'
        elif selected_menu_item == 1:  # Launch with Custom Seed
            current_state = 'custom_seed_prompt'
            elif i == 2:  # Options/Settings
                overlay_content = create_settings_content()
                overlay_title = "Settings"
                current_state = 'overlay'
        elif selected_menu_item == 3:  # Player Guide
            overlay_content = load_markdown_file('PLAYERGUIDE.md')
            overlay_title = "Player Guide"
            current_state = 'overlay'
        elif selected_menu_item == 4:  # README
            overlay_content = load_markdown_file('README.md')
            overlay_title = "README"
            current_state = 'overlay'

def main():
    """
    Main game loop with state management for menu system.
    
    States:
    - 'main_menu': Shows main menu with navigation options
    - 'custom_seed_prompt': Text input for custom game seed
    - 'overlay': Scrollable display for README/Player Guide
    - 'game': Active gameplay (existing game logic)
    
    The state machine allows smooth transitions between menu, documentation,
    and gameplay while preserving the original game experience.
    """
    global seed, seed_input, current_state, screen, SCREEN_W, SCREEN_H, selected_menu_item, overlay_scroll
    
    # Initialize game state as None - will be created when game starts
    game_state = None
    scoreboard_active = False
    tooltip_text = None

    running = True
    try:
        while running:
            clock.tick(30)  # 30 FPS for smooth menu navigation
            
            # --- Event handling based on current state --- #
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.VIDEORESIZE:
                    # Update screen size and redraw (responsive design)
                    SCREEN_W, SCREEN_H = event.w, event.h
                    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), FLAGS)
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    
                    # Handle mouse wheel for scrollable event log
                    if current_state == 'game' and game_state and game_state.scrollable_event_log_enabled:
                        if event.button == 4:  # Mouse wheel up
                            game_state.event_log_scroll_offset = max(0, game_state.event_log_scroll_offset - 3)
                        elif event.button == 5:  # Mouse wheel down
                            max_scroll = max(0, len(game_state.event_log_history) + len(game_state.messages) - 7)
                            game_state.event_log_scroll_offset = min(max_scroll, game_state.event_log_scroll_offset + 3)
                    
                    # Handle mouse clicks based on current state
                    if current_state == 'main_menu':
                        handle_menu_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'overlay':
                        # Click anywhere to return to main menu from overlay
                        current_state = 'main_menu'
                        overlay_scroll = 0
                    elif current_state == 'custom_seed_prompt':
                        # Future: could add click-to-focus for text input
                        pass
                    elif current_state == 'game':
                        # Existing game mouse handling
                        if scoreboard_active:
                            # On scoreboard, click anywhere to restart
                            main()
                            return
                        tooltip_text = game_state.handle_click((mx, my), SCREEN_W, SCREEN_H)
                        
                elif event.type == pygame.MOUSEMOTION:
                    # Mouse hover effects only active during gameplay
                    if current_state == 'game' and game_state:
                        tooltip_text = game_state.check_hover(event.pos, SCREEN_W, SCREEN_H)
                        
                elif event.type == pygame.KEYDOWN:
                    # Keyboard handling varies by state
                    if current_state == 'main_menu':
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        else:
                            handle_menu_keyboard(event.key)
                            
                    elif current_state == 'overlay':
                        # Overlay navigation: scroll with arrows, escape to return
                        if event.key == pygame.K_ESCAPE:
                            current_state = 'main_menu'
                            overlay_scroll = 0
                        elif event.key == pygame.K_UP:
                            overlay_scroll = max(0, overlay_scroll - 20)
                        elif event.key == pygame.K_DOWN:
                            overlay_scroll += 20
                            
                    elif current_state == 'custom_seed_prompt':
                        # Text input for custom seed (preserving original logic)
                        if event.key == pygame.K_RETURN:
                            # Use entered seed or weekly default
                            seed = seed_input.strip() if seed_input.strip() else get_weekly_seed()
                            random.seed(seed)
                            current_state = 'game'
                        elif event.key == pygame.K_BACKSPACE:
                            seed_input = seed_input[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            current_state = 'main_menu'
                            seed_input = ""
                        elif event.unicode.isprintable():
                            seed_input += event.unicode
                            
                    elif current_state == 'game':
                        # Arrow key scrolling for scrollable event log
                        if game_state and game_state.scrollable_event_log_enabled:
                            if event.key == pygame.K_UP:
                                game_state.event_log_scroll_offset = max(0, game_state.event_log_scroll_offset - 1)
                            elif event.key == pygame.K_DOWN:
                                max_scroll = max(0, len(game_state.event_log_history) + len(game_state.messages) - 7)
                                game_state.event_log_scroll_offset = min(max_scroll, game_state.event_log_scroll_offset + 1)
                        
                        # Existing game keyboard handling
                        if event.key == pygame.K_SPACE and game_state and not game_state.game_over:
                            game_state.end_turn()
                        elif event.key == pygame.K_ESCAPE:
                            running = False

            # --- Game state initialization --- #
            # Create game state when entering game for first time
            if current_state == 'game' and game_state is None:
                game_state = GameState(seed)
                scoreboard_active = False

            # --- Rendering based on current state --- #
            if current_state == 'main_menu':
                # Grey background as specified in requirements
                screen.fill((128, 128, 128))
                draw_main_menu(screen, SCREEN_W, SCREEN_H, selected_menu_item)
                
            elif current_state == 'custom_seed_prompt':
                # Preserve original seed prompt appearance
                screen.fill((32, 32, 44))
                draw_seed_prompt(screen, seed_input, get_weekly_seed())
                
            elif current_state == 'overlay':
                # Dark background for documentation overlay
                screen.fill((40, 40, 50))
                draw_overlay(screen, overlay_title, overlay_content, overlay_scroll, SCREEN_W, SCREEN_H)
                
            elif current_state == 'game':
                # Preserve original game appearance and logic
                screen.fill((25, 25, 35))
                if game_state.game_over:
                    draw_scoreboard(screen, game_state, SCREEN_W, SCREEN_H, seed)
                    scoreboard_active = True
                else:
                    draw_ui(screen, game_state, SCREEN_W, SCREEN_H)
                    if tooltip_text:
                        draw_tooltip(screen, tooltip_text, pygame.mouse.get_pos(), SCREEN_W, SCREEN_H)
                        
            pygame.display.flip()
    except Exception as e:
        # If an exception occurs during gameplay, try to save the game log
        if game_state and hasattr(game_state, 'logger') and not game_state.game_over:
            try:
                final_resources = {
                    'money': game_state.money,
                    'staff': game_state.staff,
                    'reputation': game_state.reputation,
                    'doom': game_state.doom
                }
                game_state.logger.log_game_end(f"Game crashed: {str(e)}", game_state.turn, final_resources)
                log_path = game_state.logger.write_log_file()
                print(f"Game crashed, but log saved to: {log_path}")
            except Exception:
                print("Game crashed and could not save log")
        raise  # Re-raise the exception
    finally:
        # Ensure we try to write log on any exit if game was in progress
        if game_state and hasattr(game_state, 'logger') and not game_state.game_over:
            try:
                final_resources = {
                    'money': game_state.money,
                    'staff': game_state.staff,
                    'reputation': game_state.reputation,
                    'doom': game_state.doom
                }
                game_state.logger.log_game_end("Game quit by user", game_state.turn, final_resources)
                log_path = game_state.logger.write_log_file()
                print(f"Game log saved to: {log_path}")
            except Exception:
                pass
        pygame.quit()

if __name__ == "__main__":
    main()
