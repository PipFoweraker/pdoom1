import os
import sys
import pygame
import random
import json
from game_state import GameState
from ui import draw_ui, draw_scoreboard, draw_seed_prompt, draw_tooltip, draw_main_menu, draw_overlay, draw_bug_report_form, draw_bug_report_success
from bug_reporter import BugReporter
from version import get_display_version

# --- Adaptive window sizing --- #
pygame.init()
info = pygame.display.Info()
SCREEN_W = int(info.current_w * 0.8)
SCREEN_H = int(info.current_h * 0.8)
FLAGS = pygame.RESIZABLE
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), FLAGS)
pygame.display.set_caption(f"P(Doom) - Bureaucracy Strategy Prototype {get_display_version()}")
clock = pygame.time.Clock()

# --- Menu and game state management --- #
# Menu states: 'main_menu', 'custom_seed_prompt', 'game', 'overlay', 'bug_report', 'bug_report_success'
current_state = 'main_menu'
selected_menu_item = 0  # For keyboard navigation
menu_items = ["Launch with Weekly Seed", "Launch with Custom Seed", "Options", "Player Guide", "README", "Report Bug"]
seed = None
seed_input = ""
overlay_content = None
overlay_title = None
overlay_scroll = 0

# Bug report form state
bug_report_data = {
    "type_index": 0,
    "title": "",
    "description": "",
    "steps": "",
    "expected": "",
    "actual": "",
    "attribution": False,
    "name": "",
    "contact": ""
}
bug_report_selected_field = 0
bug_report_editing_field = False
bug_report_success_message = ""


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
            elif i == 5:  # Report Bug
                current_state = 'bug_report'
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
        elif selected_menu_item == 2:  # Settings 
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
        elif selected_menu_item == 5:  # Report Bug
            current_state = 'bug_report'

def handle_bug_report_click(mouse_pos, w, h):
    """Handle mouse clicks in the bug report form."""
    global current_state, bug_report_data, bug_report_selected_field, bug_report_success_message
    
    # For now, just implement button handling - form field clicking can be added later
    mx, my = mouse_pos
    
    # Button positions (matching the UI layout)
    button_y = 80 + 9 * 45 + 20  # Based on UI layout calculation
    button_width = 150
    button_height = 40
    button_spacing = 20
    
    total_button_width = 3 * button_width + 2 * button_spacing
    start_x = (w - total_button_width) // 2
    
    # Check which button was clicked
    buttons = [
        {"text": "Save Locally", "action": "save_local"},
        {"text": "Submit to GitHub", "action": "submit_github"},
        {"text": "Cancel", "action": "cancel"}
    ]
    
    for i, button in enumerate(buttons):
        button_x = start_x + i * (button_width + button_spacing)
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            if button["action"] == "cancel":
                current_state = 'main_menu'
            elif button["action"] == "save_local":
                save_bug_report_locally()
            elif button["action"] == "submit_github":
                submit_bug_report_to_github()
            break

def handle_bug_report_keyboard(key):
    """Handle keyboard input in the bug report form."""
    global bug_report_selected_field, bug_report_editing_field, bug_report_data, current_state
    
    # Number of fields (excluding name field when attribution is off)
    total_fields = 8 if bug_report_data.get("attribution", False) else 7
    
    if key == pygame.K_ESCAPE:
        current_state = 'main_menu'
    elif key == pygame.K_UP:
        bug_report_selected_field = (bug_report_selected_field - 1) % total_fields
    elif key == pygame.K_DOWN or key == pygame.K_TAB:
        bug_report_selected_field = (bug_report_selected_field + 1) % total_fields
    elif key == pygame.K_RETURN:
        # Handle field-specific actions
        if bug_report_selected_field == 0:  # Type dropdown
            type_options = ["bug", "feature_request", "feedback"]
            current_index = bug_report_data.get("type_index", 0)
            bug_report_data["type_index"] = (current_index + 1) % len(type_options)
        elif bug_report_selected_field == 6:  # Attribution checkbox
            bug_report_data["attribution"] = not bug_report_data.get("attribution", False)
            if not bug_report_data["attribution"]:
                bug_report_data["name"] = ""  # Clear name if attribution disabled
        else:
            # Toggle editing mode for text fields
            bug_report_editing_field = not bug_report_editing_field
    elif bug_report_editing_field and bug_report_selected_field in [1, 2, 3, 4, 5, 7, 8]:
        # Handle text input for text fields
        field_keys = ["", "title", "description", "steps", "expected", "actual", "", "name", "contact"]
        field_key = field_keys[bug_report_selected_field]
        
        if field_key:
            if key == pygame.K_BACKSPACE:
                bug_report_data[field_key] = bug_report_data.get(field_key, "")[:-1]
            elif key == pygame.K_RETURN:
                bug_report_editing_field = False
            elif hasattr(pygame.event.Event, 'unicode'):  # Handle text input
                # This is a simplified approach - in a real implementation,
                # you'd want to handle unicode input properly
                if key < 256 and chr(key).isprintable():
                    bug_report_data[field_key] = bug_report_data.get(field_key, "") + chr(key)

def save_bug_report_locally():
    """Save the bug report to local storage."""
    global bug_report_success_message, current_state
    
    try:
        reporter = BugReporter()
        
        # Convert form data to bug report
        type_options = ["bug", "feature_request", "feedback"]
        report_type = type_options[bug_report_data.get("type_index", 0)]
        
        report = reporter.create_bug_report(
            report_type=report_type,
            title=bug_report_data.get("title", ""),
            description=bug_report_data.get("description", ""),
            steps_to_reproduce=bug_report_data.get("steps", ""),
            expected_behavior=bug_report_data.get("expected", ""),
            actual_behavior=bug_report_data.get("actual", ""),
            include_attribution=bug_report_data.get("attribution", False),
            attribution_name=bug_report_data.get("name", ""),
            contact_info=bug_report_data.get("contact", "")
        )
        
        filepath = reporter.save_report_locally(report)
        bug_report_success_message = f"Bug report saved successfully!\n\nSaved to: {filepath}\n\nThank you for helping improve P(Doom)!"
        current_state = 'bug_report_success'
        
        # Reset form
        reset_bug_report_form()
        
    except Exception as e:
        bug_report_success_message = f"Error saving bug report:\n{str(e)}\n\nPlease try again or contact the developers directly."
        current_state = 'bug_report_success'

def submit_bug_report_to_github():
    """Submit the bug report to GitHub (placeholder for future implementation)."""
    global bug_report_success_message, current_state
    
    # For now, this will just format the report for GitHub and save it locally
    # In a future implementation, this could integrate with GitHub API
    
    try:
        reporter = BugReporter()
        
        # Convert form data to bug report
        type_options = ["bug", "feature_request", "feedback"]
        report_type = type_options[bug_report_data.get("type_index", 0)]
        
        report = reporter.create_bug_report(
            report_type=report_type,
            title=bug_report_data.get("title", ""),
            description=bug_report_data.get("description", ""),
            steps_to_reproduce=bug_report_data.get("steps", ""),
            expected_behavior=bug_report_data.get("expected", ""),
            actual_behavior=bug_report_data.get("actual", ""),
            include_attribution=bug_report_data.get("attribution", False),
            attribution_name=bug_report_data.get("name", ""),
            contact_info=bug_report_data.get("contact", "")
        )
        
        # Format for GitHub
        github_format = reporter.format_for_github(report)
        
        # Save locally with GitHub formatting
        filepath = reporter.save_report_locally(report)
        
        bug_report_success_message = f"Bug report prepared for GitHub!\n\nTitle: {github_format['title']}\n\nTo submit to GitHub:\n1. Go to the P(Doom) repository issues page\n2. Click 'New Issue'\n3. Copy the content from: {filepath}\n\nThank you for contributing!"
        current_state = 'bug_report_success'
        
        # Reset form
        reset_bug_report_form()
        
    except Exception as e:
        bug_report_success_message = f"Error preparing GitHub report:\n{str(e)}\n\nPlease try saving locally instead."
        current_state = 'bug_report_success'

def reset_bug_report_form():
    """Reset the bug report form to default values."""
    global bug_report_data, bug_report_selected_field, bug_report_editing_field
    
    bug_report_data = {
        "type_index": 0,
        "title": "",
        "description": "",
        "steps": "",
        "expected": "",
        "actual": "",
        "attribution": False,
        "name": "",
        "contact": ""
    }
    bug_report_selected_field = 0
    bug_report_editing_field = False

def main():
    """
    Main game loop with state management for menu system.
    
    States:
    - 'main_menu': Shows main menu with navigation options
    - 'custom_seed_prompt': Text input for custom game seed
    - 'overlay': Scrollable display for README/Player Guide
    - 'bug_report': Bug reporting form interface
    - 'bug_report_success': Success message after bug report submission
    - 'game': Active gameplay (existing game logic)
    
    The state machine allows smooth transitions between menu, documentation,
    bug reporting, and gameplay while preserving the original game experience.
    """
    global seed, seed_input, current_state, screen, SCREEN_W, SCREEN_H, selected_menu_item, overlay_scroll
    global bug_report_data, bug_report_selected_field, bug_report_editing_field, bug_report_success_message
    
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
                    elif current_state == 'bug_report':
                        # Handle bug report form clicks
                        handle_bug_report_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'bug_report_success':
                        # Click anywhere to return to main menu
                        current_state = 'main_menu'
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
                            
                    elif current_state == 'bug_report':
                        # Bug report form keyboard handling
                        handle_bug_report_keyboard(event.key)
                        
                    elif current_state == 'bug_report_success':
                        # Any key returns to main menu
                        current_state = 'main_menu'
                            
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
                
            elif current_state == 'bug_report':
                # Bug report form
                buttons = draw_bug_report_form(screen, bug_report_data, bug_report_selected_field, SCREEN_W, SCREEN_H)
                
            elif current_state == 'bug_report_success':
                # Bug report success message
                draw_bug_report_success(screen, bug_report_success_message, SCREEN_W, SCREEN_H)
                
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
