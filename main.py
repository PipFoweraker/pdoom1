import os
import sys
import pygame
import random
import json
from game_state import GameState

from ui import draw_ui, draw_scoreboard, draw_seed_prompt, draw_tooltip, draw_main_menu, draw_overlay, draw_bug_report_form, draw_bug_report_success, draw_end_game_menu, draw_tutorial_overlay, draw_first_time_help, draw_pre_game_settings, draw_seed_selection, draw_tutorial_choice, draw_popup_events


from bug_reporter import BugReporter
from version import get_display_version
from onboarding import onboarding
from config_manager import initialize_config_system, get_current_config, config_manager
from event_system import EventAction

# Initialize config system on startup
initialize_config_system()
current_config = get_current_config()

# --- Adaptive window sizing --- #
pygame.init()
info = pygame.display.Info()
window_scale = current_config['ui']['window_scale']
SCREEN_W = int(info.current_w * window_scale)
SCREEN_H = int(info.current_h * window_scale)
FLAGS = pygame.RESIZABLE
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), FLAGS)
pygame.display.set_caption(f"P(Doom) - Bureaucracy Strategy Prototype {get_display_version()}")
clock = pygame.time.Clock()

# --- Menu and game state management --- #
# Menu states: 'main_menu', 'custom_seed_prompt', 'config_select', 'pre_game_settings', 'seed_selection', 'tutorial_choice', 'game', 'overlay', 'bug_report', 'bug_report_success', 'end_game_menu', 'tutorial'

current_state = 'main_menu'
selected_menu_item = 0  # For keyboard navigation
menu_items = ["Launch with Weekly Seed", "Launch with Custom Seed", "Configuration", "Options", "Player Guide", "README", "Report Bug"]
end_game_menu_items = ["View High Scores", "Relaunch Game", "Main Menu", "Settings", "Submit Feedback", "Submit Bug Request"]
end_game_selected_item = 0  # For end-game menu navigation
high_score_selected_item = 0  # For high-score screen navigation
high_score_submit_to_leaderboard = False  # Leaderboard submission toggle
seed = None
seed_input = ""
overlay_content = None
overlay_title = None
overlay_scroll = 0

# Config selection state
config_selected_item = 0
available_configs = []

# Pre-game settings state
pre_game_settings = {
    "difficulty": "DUMMY",
    "music_volume": 123,
    "sound_volume": 123,
    "graphics_quality": "DUMMY"
}
selected_settings_item = 0
seed_choice = "weekly"  # "weekly" or "custom"
tutorial_enabled = True

# Tutorial state
current_tutorial_content = None
first_time_help_content = None
first_time_help_close_button = None

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
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"{now.year}{now.isocalendar()[1]}"

def load_markdown_file(filename):
    """Load and return the contents of a markdown file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Could not load {filename}"

def get_tutorial_settings():
    """Get current tutorial settings from file."""
    try:
        with open("tutorial_settings.json", "r") as f:
            data = json.load(f)
        return {
            "tutorial_enabled": data.get("tutorial_enabled", True),
            "first_game_launch": data.get("first_game_launch", True)
        }
    except Exception:
        return {"tutorial_enabled": True, "first_game_launch": True}

def create_settings_content(game_state=None):
    """Create settings content for the settings overlay"""

    tutorial_status = "Enabled" if onboarding.tutorial_enabled else "Disabled"
    tutorial_completed = "Yes" if not onboarding.is_first_time else "No"
    
    return f"""# Settings

## Tutorial & Help System
- **Tutorial System**: {tutorial_status}
- **Tutorial Completed**: {tutorial_completed}
- **In-Game Help**: Press 'H' key anytime to access Player Guide
- **First-Time Tips**: Automatic contextual help for new mechanics

To reset tutorial: Delete `onboarding_progress.json` file and restart game


## Game Settings
- **Display Mode**: Windowed (resizable)
- **Resolution**: Adaptive (80% of screen size)
- **FPS**: 30 FPS (optimized for menu navigation)

## Audio Settings
- **Sound Effects**: Enabled
- **Background Music**: Disabled by default

## Gameplay Settings
- **Action Points**: 3 per turn (standard)
- **Scrollable Event Log**: Enabled (use mouse wheel or arrow keys)
- **Weekly Seed**: Auto-generated based on current week

## Accessibility
- **Keyboard Navigation**: Full menu navigation with arrow keys and Enter
- **Mouse Support**: Complete mouse interaction
- **Color Scheme**: High contrast blue/grey theme
- **Text Scaling**: Responsive font sizing based on screen resolution

## Data & Privacy
- **Local Highscores**: Stored in local_highscore.json
- **Game Logs**: Saved locally for debugging (logs/ directory)
- **Bug Reports**: Local storage with optional GitHub submission
- **Attribution**: Optional for bug reports and feedback

## Controls
- **Space**: End turn (during gameplay)
- **Arrow Keys**: Navigate menus, scroll event log
- **Enter**: Confirm selection
- **Escape**: Return to previous menu or quit

*Note: Settings are currently informational. Configuration options will be added in future updates.*"""

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
                current_state = 'pre_game_settings'
            elif i == 1:  # Launch with Custom Seed
                current_state = 'pre_game_settings'
            elif i == 2:  # Options/Settings
                current_state = 'sounds_menu'
                sounds_menu_selected_item = 0
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
    global selected_menu_item, current_state, seed, overlay_content, overlay_title, available_configs, config_selected_item
    
    if key == pygame.K_UP:
        # Move selection up, wrapping to bottom
        selected_menu_item = (selected_menu_item - 1) % len(menu_items)
    elif key == pygame.K_DOWN:
        # Move selection down, wrapping to top  
        selected_menu_item = (selected_menu_item + 1) % len(menu_items)
    elif key == pygame.K_RETURN:
        # Activate selected menu item (same logic as mouse click)
        if selected_menu_item == 0:  # Launch with Weekly Seed
            current_state = 'pre_game_settings'
        elif selected_menu_item == 1:  # Launch with Custom Seed
            current_state = 'pre_game_settings'
        elif selected_menu_item == 2:  # Configuration
            available_configs = config_manager.list_available_configs()
            config_selected_item = 0
            current_state = 'config_select'
        elif selected_menu_item == 3:  # Options
            overlay_content = create_settings_content()
            overlay_title = "Settings"
            current_state = 'overlay'
        elif selected_menu_item == 4:  # Player Guide
            overlay_content = load_markdown_file('PLAYERGUIDE.md')
            overlay_title = "Player Guide"
            current_state = 'overlay'
        elif selected_menu_item == 5:  # README
            overlay_content = load_markdown_file('README.md')
            overlay_title = "README"
            current_state = 'overlay'
        elif selected_menu_item == 6:  # Report Bug
            current_state = 'bug_report'

def handle_config_keyboard(key):
    """
    Handle keyboard navigation in config selection menu.
    
    Args:
        key: pygame key constant from keydown event
    """
    global config_selected_item, current_state, current_config
    
    all_items = available_configs + ["← Back to Main Menu"]
    
    if key == pygame.K_UP:
        config_selected_item = (config_selected_item - 1) % len(all_items)
    elif key == pygame.K_DOWN:
        config_selected_item = (config_selected_item + 1) % len(all_items)
    elif key == pygame.K_RETURN:
        if config_selected_item < len(available_configs):
            # Switch to selected config
            selected_config = available_configs[config_selected_item]
            if config_manager.switch_config(selected_config):
                current_config = get_current_config()  # Reload config
                print(f"Switched to configuration: {selected_config}")
        # Return to main menu (both for config selection and back button)
        current_state = 'main_menu'
    elif key == pygame.K_ESCAPE:
        current_state = 'main_menu'


def handle_pre_game_settings_click(mouse_pos, w, h):
    """Handle mouse clicks on pre-game settings screen."""
    global current_state, selected_settings_item, pre_game_settings
    
    # Calculate button positions (must match draw_pre_game_settings layout)
    button_width = int(w * 0.5)
    button_height = int(h * 0.08)
    start_y = int(h * 0.35)
    spacing = int(h * 0.1)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    # Settings items (4 settings + 1 continue button)
    num_items = 5
    
    for i in range(num_items):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            selected_settings_item = i
            
            if i == 4:  # Continue button
                current_state = 'seed_selection'
            # For now, other settings don't do anything when clicked
            # In a full implementation, they would cycle through values
            break


def handle_pre_game_settings_keyboard(key):
    """Handle keyboard navigation for pre-game settings screen."""
    global selected_settings_item, current_state
    
    if key == pygame.K_UP:
        selected_settings_item = (selected_settings_item - 1) % 5
    elif key == pygame.K_DOWN:
        selected_settings_item = (selected_settings_item + 1) % 5
    elif key == pygame.K_RETURN:
        if selected_settings_item == 4:  # Continue button
            current_state = 'seed_selection'
    elif key == pygame.K_ESCAPE:
        current_state = 'main_menu'


def handle_seed_selection_click(mouse_pos, w, h):
    """Handle mouse clicks on seed selection screen."""
    global current_state, seed_choice, seed
    
    # Calculate button positions (must match draw_seed_selection layout)
    button_width = int(w * 0.4)
    button_height = int(h * 0.08)
    start_y = int(h * 0.35)
    spacing = int(h * 0.12)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    for i in range(2):  # Weekly seed, Custom seed
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            if i == 0:  # Weekly seed
                seed_choice = "weekly"
                seed = get_weekly_seed()
                current_state = 'tutorial_choice'
            elif i == 1:  # Custom seed
                seed_choice = "custom"
                current_state = 'custom_seed_prompt'
            break


def handle_seed_selection_keyboard(key):
    """Handle keyboard navigation for seed selection screen."""
    global current_state, seed_choice, seed
    
    if key == pygame.K_UP or key == pygame.K_DOWN:
        # Toggle between weekly and custom
        pass  # Visual selection can be added later
    elif key == pygame.K_RETURN:
        # Default to weekly seed for now
        seed_choice = "weekly"
        seed = get_weekly_seed()
        current_state = 'tutorial_choice'
    elif key == pygame.K_ESCAPE:
        current_state = 'pre_game_settings'


def handle_tutorial_choice_click(mouse_pos, w, h):
    """Handle mouse clicks on tutorial choice screen."""
    global current_state, tutorial_enabled
    
    # Calculate button positions (must match draw_tutorial_choice layout)
    button_width = int(w * 0.4)
    button_height = int(h * 0.08)
    start_y = int(h * 0.4)
    spacing = int(h * 0.12)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    for i in range(2):  # Yes tutorial, No tutorial
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            if i == 0:  # Yes - Enable Tutorial
                tutorial_enabled = True
            elif i == 1:  # No - Regular Mode
                tutorial_enabled = False
            
            # Set the seed and start the game
            random.seed(seed)
            current_state = 'game'
            break


def handle_tutorial_choice_keyboard(key):
    """Handle keyboard navigation for tutorial choice screen."""
    global current_state, tutorial_enabled
    
    if key == pygame.K_UP or key == pygame.K_DOWN:
        # Toggle between yes and no
        pass  # Visual selection can be added later
    elif key == pygame.K_RETURN:
        # Default to tutorial enabled
        tutorial_enabled = True
        random.seed(seed)
        current_state = 'game'
    elif key == pygame.K_ESCAPE:
        current_state = 'seed_selection'


>>>>>>> 97fa02a53e483fa193b9137cda590d1ca50b361e
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

def handle_end_game_menu_click(mouse_pos, w, h):
    """Handle mouse clicks on end-game menu items."""
    global current_state, selected_menu_item, seed, overlay_content, overlay_title, end_game_selected_item
    
    # Calculate menu button positions (similar to main menu layout)
    button_width = int(w * 0.35)
    button_height = int(h * 0.06)
    start_y = int(h * 0.55)
    spacing = int(h * 0.08)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    # Check each menu button for collision
    for i, item in enumerate(end_game_menu_items):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            end_game_selected_item = i
            
            # Execute menu action based on selection
            if i == 0:  # View High Scores
                current_state = 'high_score'
                high_score_selected_item = 0  # Reset high score selection
            elif i == 1:  # Relaunch Game
                current_state = 'game'
                # Keep the same seed for relaunch
            elif i == 2:  # Main Menu
                current_state = 'main_menu'
                selected_menu_item = 0
            elif i == 3:  # Settings
                overlay_content = create_settings_content()
                overlay_title = "Settings"
                current_state = 'overlay'
            elif i == 4:  # Submit Feedback
                # Reset and pre-fill feedback form
                reset_bug_report_form()
                bug_report_data["type_index"] = 2  # Feedback
                current_state = 'bug_report'
            elif i == 5:  # Submit Bug Request
                # Reset and pre-fill bug report form
                reset_bug_report_form()
                bug_report_data["type_index"] = 0  # Bug
                current_state = 'bug_report'
            break

def handle_end_game_menu_keyboard(key):
    """Handle keyboard navigation for end-game menu."""
    global end_game_selected_item, current_state, selected_menu_item, overlay_content, overlay_title
    
    if key == pygame.K_UP:
        end_game_selected_item = (end_game_selected_item - 1) % len(end_game_menu_items)
    elif key == pygame.K_DOWN:
        end_game_selected_item = (end_game_selected_item + 1) % len(end_game_menu_items)
    elif key == pygame.K_RETURN or key == pygame.K_SPACE:
        # Execute selected menu action
        if end_game_selected_item == 0:  # View High Scores
            current_state = 'high_score'
            high_score_selected_item = 0
        elif end_game_selected_item == 1:  # Relaunch Game
            current_state = 'game'
        elif end_game_selected_item == 2:  # Main Menu
            current_state = 'main_menu'
            selected_menu_item = 0
        elif end_game_selected_item == 3:  # Settings
            overlay_content = create_settings_content()
            overlay_title = "Settings"
            current_state = 'overlay'
        elif end_game_selected_item == 4:  # Submit Feedback
            # Reset and pre-fill feedback form
            reset_bug_report_form()
            bug_report_data["type_index"] = 2  # Feedback
            current_state = 'bug_report'
        elif end_game_selected_item == 5:  # Submit Bug Request
            # Reset and pre-fill bug report form
            reset_bug_report_form()
            bug_report_data["type_index"] = 0  # Bug
            current_state = 'bug_report'
    elif key == pygame.K_ESCAPE:
        # Return to main menu
        current_state = 'main_menu'
        selected_menu_item = 0


def handle_popup_button_click(mouse_pos, game_state, screen_w, screen_h):
    """
    Handle mouse clicks on popup event buttons.
    
    Returns True if a popup button was clicked, False otherwise.
    """
    if not hasattr(game_state, 'pending_popup_events') or not game_state.pending_popup_events:
        return False
    
    # Get button rectangles from draw_popup_events
    # We need fonts for this, so let's create them temporarily
    font = pygame.font.SysFont('Consolas', 16)
    big_font = pygame.font.SysFont('Consolas', 20, bold=True)
    
    # Create a temporary surface to get button rectangles
    temp_surface = pygame.Surface((screen_w, screen_h))
    button_rects = draw_popup_events(temp_surface, game_state, screen_w, screen_h, font, big_font)
    
    mx, my = mouse_pos
    
    # Check each button for collision
    for button_rect, action, event in button_rects:
        if button_rect.collidepoint(mx, my):
            # Handle the action
            game_state.handle_popup_event_action(event, action)
            return True
    
    return False

def handle_high_score_click(mouse_pos, w, h):
    """Handle mouse clicks on high score screen."""
    global current_state, selected_menu_item, high_score_submit_to_leaderboard, game_state
    
    # Button layout (similar to other menus)
    button_width = int(w * 0.3)
    button_height = int(h * 0.06)
    button_y = int(h * 0.85)
    
    mx, my = mouse_pos
    
    # Continue button (centered)
    continue_x = w // 2 - button_width // 2
    continue_rect = pygame.Rect(continue_x, button_y, button_width, button_height)
    
    if continue_rect.collidepoint(mx, my):
        # Flush game state and return to main menu
        _flush_game_state()
        current_state = 'main_menu'
        selected_menu_item = 0
        return
    
    # Leaderboard toggle checkbox (left side)
    checkbox_size = int(h * 0.03)
    checkbox_x = int(w * 0.1)
    checkbox_y = int(h * 0.75)
    checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size)
    
    if checkbox_rect.collidepoint(mx, my):
        high_score_submit_to_leaderboard = not high_score_submit_to_leaderboard
        return

def handle_high_score_keyboard(key):
    """Handle keyboard navigation for high score screen."""
    global current_state, selected_menu_item, high_score_submit_to_leaderboard, game_state
    
    if key == pygame.K_SPACE or key == pygame.K_RETURN:
        # Continue to main menu (default action)
        _flush_game_state()
        current_state = 'main_menu'
        selected_menu_item = 0
    elif key == pygame.K_l:
        # Toggle leaderboard submission
        high_score_submit_to_leaderboard = not high_score_submit_to_leaderboard
    elif key == pygame.K_ESCAPE:
        # Quick escape to main menu
        _flush_game_state()
        current_state = 'main_menu'
        selected_menu_item = 0

def _flush_game_state():
    """Flush/reset the game state for a new game sequence, with logging."""
    global game_state
    
    if game_state:
        # Log final game state if not already logged
        if hasattr(game_state, 'logger') and not hasattr(game_state, '_final_logged'):
            try:
                final_resources = {
                    'money': game_state.money,
                    'staff': game_state.staff,
                    'reputation': game_state.reputation,
                    'doom': game_state.doom
                }
                game_state.logger.log_game_end("Player returned to main menu", game_state.turn, final_resources)
                log_path = game_state.logger.write_log_file()
                if log_path:
                    print(f"Game log flushed to: {log_path}")
                game_state._final_logged = True
            except Exception as e:
                print(f"Error during game state flush: {e}")
        
        # Reset game state for next game
        game_state = None
    
    # Reset any global state variables
    global high_score_submit_to_leaderboard
    high_score_submit_to_leaderboard = False

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
    # UI overlay variables need global declaration to prevent UnboundLocalError when referenced before assignment
    global first_time_help_content, first_time_help_close_button, current_tutorial_content
    global overlay_content, overlay_title
    
    # Initialize game state as None - will be created when game starts
    game_state = None
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
                    
                    # Handle overlay manager events first (highest priority)
                    if current_state == 'game' and game_state:
                        handled_element = game_state.overlay_manager.handle_mouse_event(event, SCREEN_W, SCREEN_H)
                        if handled_element:
                            # Overlay manager handled the event
                            continue
                    
                    # Handle mouse clicks based on current state
                    if current_state == 'main_menu':
                        handle_menu_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'pre_game_settings':
                        handle_pre_game_settings_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'seed_selection':
                        handle_seed_selection_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'tutorial_choice':
                        handle_tutorial_choice_click((mx, my), SCREEN_W, SCREEN_H)
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
                    elif current_state == 'end_game_menu':
                        # Handle end-game menu clicks
                        handle_end_game_menu_click((mx, my), SCREEN_W, SCREEN_H)

                    elif current_state == 'high_score':
                        # Handle high score screen clicks
                        handle_high_score_click((mx, my), SCREEN_W, SCREEN_H)

                    elif current_state == 'game':
                        # Tutorial button handling (takes precedence)
                        if onboarding.show_tutorial_overlay and current_tutorial_content:
                            if current_tutorial_content['next_button'].collidepoint(mx, my):
                                # Next button clicked
                                onboarding.advance_tutorial_step(onboarding.current_tutorial_step)
                            elif current_tutorial_content['skip_button'].collidepoint(mx, my):
                                # Skip button clicked
                                onboarding.dismiss_tutorial()
                            elif current_tutorial_content['help_button'].collidepoint(mx, my):
                                # Help button clicked
                                overlay_content = load_markdown_file('PLAYERGUIDE.md')
                                overlay_title = "Player Guide"
                                current_state = 'overlay'
                        # First-time help close button
                        elif first_time_help_content and first_time_help_close_button:
                            # Check if the close button was clicked
                            if first_time_help_close_button.collidepoint(mx, my):
                                first_time_help_content = None
                                first_time_help_close_button = None
                            else:
                                # Check for popup button clicks first when help is shown
                                if handle_popup_button_click((mx, my), game_state, SCREEN_W, SCREEN_H):
                                    # Popup button was clicked, no need for further processing
                                    pass
                                else:
                                    # Allow normal game interactions when help is shown
                                    result = game_state.handle_click((mx, my), SCREEN_W, SCREEN_H)
                                    if result == 'play_sound':
                                        game_state.sound_manager.play_ap_spend_sound()
                                    tooltip_text = result
                        # Check if tutorial overlay is active
                        elif game_state and game_state.pending_tutorial_message:
                            # Handle tutorial overlay clicks - any click dismisses the tutorial
                            game_state.dismiss_tutorial_message()
                        else:
                            # Check for popup button clicks first
                            if handle_popup_button_click((mx, my), game_state, SCREEN_W, SCREEN_H):
                                # Popup button was clicked, no need for further processing
                                pass
                            else:
                                # Regular game mouse handling
                                result = game_state.handle_click((mx, my), SCREEN_W, SCREEN_H)
                                if result == 'play_sound':
                                    game_state.sound_manager.play_ap_spend_sound()
                                tooltip_text = result
                        
                elif event.type == pygame.MOUSEMOTION:
                    # Handle overlay manager hover events first
                    if current_state == 'game' and game_state:
                        handled_element = game_state.overlay_manager.handle_mouse_event(event, SCREEN_W, SCREEN_H)
                        if handled_element:
                            # Overlay manager handled the event
                            continue
                    
                    # Handle activity log dragging
                    if current_state == 'game' and game_state:
                        game_state.handle_mouse_motion(event.pos, SCREEN_W, SCREEN_H)
                    
                    # Mouse hover effects only active during gameplay
                    if current_state == 'game' and game_state:
                        tooltip_text = game_state.check_hover(event.pos, SCREEN_W, SCREEN_H)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Handle mouse button release (for ending drag operations)
                    if current_state == 'game' and game_state:
                        game_state.handle_mouse_release(event.pos, SCREEN_W, SCREEN_H)
                        
                elif event.type == pygame.KEYDOWN:
                    # Handle overlay manager keyboard events first (for accessibility)
                    if current_state == 'game' and game_state:
                        handled = game_state.overlay_manager.handle_keyboard_event(event)
                        if handled:
                            # Overlay manager handled the event
                            continue
                    
                    # Keyboard handling varies by state
                    if current_state == 'main_menu':
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        else:
                            handle_menu_keyboard(event.key)
                    
                    elif current_state == 'config_select':
                        handle_config_keyboard(event.key)
                            
                    elif current_state == 'pre_game_settings':
                        handle_pre_game_settings_keyboard(event.key)
                    elif current_state == 'seed_selection':
                        handle_seed_selection_keyboard(event.key)
                    elif current_state == 'tutorial_choice':
                        handle_tutorial_choice_keyboard(event.key)
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
                        
                    elif current_state == 'end_game_menu':
                        # Handle end-game menu keyboard navigation
                        handle_end_game_menu_keyboard(event.key)
                        
                    elif current_state == 'high_score':
                        # Handle high score screen keyboard navigation
                        handle_high_score_keyboard(event.key)

                            
                    elif current_state == 'custom_seed_prompt':
                        # Text input for custom seed (preserving original logic)
                        if event.key == pygame.K_RETURN:
                            # Use entered seed or weekly default
                            seed = seed_input.strip() if seed_input.strip() else get_weekly_seed()
                            current_state = 'tutorial_choice'
                        elif event.key == pygame.K_BACKSPACE:
                            seed_input = seed_input[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            current_state = 'seed_selection'
                            seed_input = ""
                        elif event.unicode.isprintable():
                            seed_input += event.unicode
                            
                    elif current_state == 'game':

                        # Tutorial keyboard handling (takes precedence when tutorial is active)
                        if onboarding.show_tutorial_overlay:
                            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                                # Advance tutorial step
                                onboarding.advance_tutorial_step(onboarding.current_tutorial_step)
                            elif event.key == pygame.K_ESCAPE:
                                # Skip tutorial
                                onboarding.dismiss_tutorial()
                            elif event.key == pygame.K_h:
                                # Show help overlay
                                overlay_content = load_markdown_file('PLAYERGUIDE.md')
                                overlay_title = "Player Guide"
                                current_state = 'overlay'
                        
                        # Help key (H) - always available
                        elif event.key == pygame.K_h:
                            overlay_content = load_markdown_file('PLAYERGUIDE.md')
                            overlay_title = "Player Guide"
                            current_state = 'overlay'
                        
                        # Close first-time help
                        elif event.key == pygame.K_ESCAPE and first_time_help_content:
                            first_time_help_content = None
                            first_time_help_close_button = None
                        
                        # Arrow key scrolling for scrollable event log
                        elif game_state and game_state.scrollable_event_log_enabled:
                            if event.key == pygame.K_UP:
                                game_state.event_log_scroll_offset = max(0, game_state.event_log_scroll_offset - 1)
                            elif event.key == pygame.K_DOWN:
                                max_scroll = max(0, len(game_state.event_log_history) + len(game_state.messages) - 7)
                                game_state.event_log_scroll_offset = min(max_scroll, game_state.event_log_scroll_offset + 1)
                        
                        # Regular game keyboard handling (only if tutorial is not active)
                        elif not onboarding.show_tutorial_overlay:
                            if event.key == pygame.K_SPACE and game_state and not game_state.game_over:
                                game_state.end_turn()
                            elif event.key == pygame.K_ESCAPE:
                                running = False
                            
                            # Action shortcuts (1-9 keys for available actions)
                            elif event.key >= pygame.K_1 and event.key <= pygame.K_9 and game_state and not game_state.game_over:
                                action_index = event.key - pygame.K_1  # Convert K_1 to 0, K_2 to 1, etc.
                                if action_index < len(game_state.actions):
                                    # Check if this would be an undo operation before calling
                                    was_undo = action_index in game_state.selected_actions
                                    
                                    # Try to execute the action using keyboard shortcut
                                    success = game_state.execute_action_by_keyboard(action_index)
                                    if success and not was_undo:
                                        # Play AP spend sound for successful new selections (not undos)
                                        game_state.sound_manager.play_ap_spend_sound()
                            
                            # 'H' key for help (Player Guide)
                            elif event.key == pygame.K_h:
                                overlay_content = load_markdown_file('PLAYERGUIDE.md')
                                overlay_title = "Player Guide"
                                overlay_scroll = 0
                                current_state = 'overlay'

            # --- Game state initialization --- #
            # Create game state when entering game for first time
            if current_state == 'game' and game_state is None:
                game_state = GameState(seed)
                

                # Check if tutorial should be shown for new players
                if onboarding.should_show_tutorial() and not game_state.onboarding_started:
                    onboarding.start_tutorial()
                    game_state.onboarding_started = True

            # --- First-time help checking --- #
            # Check for first-time mechanics and show contextual help (only if tutorial is not active)
            if (current_state == 'game' and game_state and 
                not first_time_help_content and 
                not onboarding.show_tutorial_overlay):
                # Check for various first-time mechanics
                for mechanic in ['first_staff_hire', 'first_upgrade_purchase', 'action_points_exhausted', 'high_doom_warning']:
                    if onboarding.should_show_mechanic_help(mechanic):
                        help_content = onboarding.get_mechanic_help(mechanic)
                        if help_content and isinstance(help_content, dict) and 'title' in help_content and 'content' in help_content:
                            first_time_help_content = help_content
                            break


            # --- Rendering based on current state --- #
            if current_state == 'main_menu':
                # Grey background as specified in requirements
                screen.fill((128, 128, 128))
                draw_main_menu(screen, SCREEN_W, SCREEN_H, selected_menu_item)
            
            elif current_state == 'config_select':
                # Config selection menu
                screen.fill((64, 64, 64))
                from ui import draw_config_menu
                draw_config_menu(screen, SCREEN_W, SCREEN_H, config_selected_item, 
                               available_configs, config_manager.get_current_config_name())
            
            elif current_state == 'pre_game_settings':
                # Pre-game settings screen
                screen.fill((50, 50, 50))
                draw_pre_game_settings(screen, SCREEN_W, SCREEN_H, pre_game_settings, selected_settings_item)
            
            elif current_state == 'seed_selection':
                # Seed selection screen
                screen.fill((50, 50, 50))
                draw_seed_selection(screen, SCREEN_W, SCREEN_H, 0, seed_input)  # Selected item handling can be improved
            
            elif current_state == 'tutorial_choice':
                # Tutorial choice screen
                screen.fill((50, 50, 50))
                draw_tutorial_choice(screen, SCREEN_W, SCREEN_H, 0)  # Selected item handling can be improved
>>>>>>> 97fa02a53e483fa193b9137cda590d1ca50b361e
                
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
                
            elif current_state == 'end_game_menu':
                # End-game menu with statistics and options
                screen.fill((25, 25, 35))  # Same dark background as game
                draw_end_game_menu(screen, SCREEN_W, SCREEN_H, end_game_selected_item, game_state, seed)
                
            elif current_state == 'high_score':
                # High score screen with AI safety researchers and player score
                screen.fill((20, 30, 40))  # Dark blue background for high scores
                draw_high_score_screen(screen, SCREEN_W, SCREEN_H, game_state, seed, high_score_submit_to_leaderboard)

                
            elif current_state == 'game':
                # Preserve original game appearance and logic
                screen.fill((25, 25, 35))
                if game_state.game_over:
                    current_state = 'end_game_menu'
                    end_game_selected_item = 0  # Reset selection
                else:
                    # Update systems every frame for smooth animation
                    if game_state:
                        game_state._update_ui_transitions()
                        game_state.overlay_manager.update_animations()
                    
                    draw_ui(screen, game_state, SCREEN_W, SCREEN_H)
                    
                    # Render overlay manager elements
                    if game_state:
                        game_state.overlay_manager.render_elements(screen)
                    
                    if tooltip_text:
                        draw_tooltip(screen, tooltip_text, pygame.mouse.get_pos(), SCREEN_W, SCREEN_H)
                    

                    # Draw tutorial overlay if active
                    if onboarding.show_tutorial_overlay and onboarding.current_tutorial_step:
                        tutorial_content = onboarding.get_tutorial_content(onboarding.current_tutorial_step)
                        current_tutorial_content = draw_tutorial_overlay(screen, tutorial_content, SCREEN_W, SCREEN_H)
                    
                    # Draw first-time help if available
                    if first_time_help_content and isinstance(first_time_help_content, dict):
                        first_time_help_close_button = draw_first_time_help(screen, first_time_help_content, SCREEN_W, SCREEN_H)
                        # If drawing failed (returned None), clear the help content to prevent repeated attempts
                        if first_time_help_close_button is None:
                            first_time_help_content = None

                        
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
