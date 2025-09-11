import sys
import pygame
import random
import json
from src.core.game_state import GameState

from ui import draw_seed_prompt, draw_tooltip, draw_main_menu, draw_overlay, draw_bug_report_form, draw_bug_report_success, draw_end_game_menu, draw_stepwise_tutorial_overlay, draw_first_time_help, draw_pre_game_settings, draw_seed_selection, draw_tutorial_choice, draw_new_player_experience, draw_popup_events, draw_loading_screen, draw_turn_transition_overlay, draw_audio_menu, draw_high_score_screen, draw_start_game_submenu
from ui_new.facade import ui_facade
from src.ui.keybinding_menu import draw_keybinding_menu, draw_keybinding_change_prompt, get_keybinding_menu_click_item


from src.ui.overlay_manager import OverlayManager
from src.services.bug_reporter import BugReporter
from src.services.version import get_display_version
from src.features.onboarding import onboarding
from src.services.config_manager import initialize_config_system, get_current_config, config_manager
from src.services.sound_manager import SoundManager

# Initialize config system on startup
initialize_config_system()
current_config = get_current_config()

# Initialize global sound manager for menu use
global_sound_manager = SoundManager()

# Initialize with config setting if available
# Ensure audio section exists in config
if 'audio' not in current_config:
    current_config['audio'] = {}
if 'sound_enabled' not in current_config['audio']:
    current_config['audio']['sound_enabled'] = True
    
if current_config.get('audio', {}).get('sound_enabled', True):
    global_sound_manager.set_enabled(True)
else:
    global_sound_manager.set_enabled(False)

# --- Adaptive window sizing with loading screen --- #
pygame.init()

# Set up initial screen for loading
info = pygame.display.Info()
window_scale = current_config['ui']['window_scale']
fullscreen_enabled = current_config['ui'].get('fullscreen', False)

if fullscreen_enabled:
    SCREEN_W = info.current_w
    SCREEN_H = info.current_h
    FLAGS = pygame.FULLSCREEN
else:
    SCREEN_W = int(info.current_w * window_scale)
    SCREEN_H = int(info.current_h * window_scale)
    FLAGS = pygame.RESIZABLE

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), FLAGS)
pygame.display.set_caption(f"P(Doom) - Bureaucracy Strategy Prototype {get_display_version()}")
clock = pygame.time.Clock()

# Show loading screen during initialization

# Phase 1: Basic setup
draw_loading_screen(screen, SCREEN_W, SCREEN_H, 0.2, "Initializing systems...")
pygame.display.flip()

# Phase 2: Config and sound
draw_loading_screen(screen, SCREEN_W, SCREEN_H, 0.4, "Loading configuration...")
pygame.display.flip()

# Phase 3: Sound and audio setup
draw_loading_screen(screen, SCREEN_W, SCREEN_H, 0.6, "Setting up audio...")
pygame.display.flip()

# Initialize window manager for UI panels
window_manager = OverlayManager()

# Phase 4: UI components
draw_loading_screen(screen, SCREEN_W, SCREEN_H, 0.8, "Loading UI components...")
pygame.display.flip()

# --- Menu and game state management --- #
# Menu states: 'main_menu', 'custom_seed_prompt', 'config_select', 'pre_game_settings', 'seed_selection', 'tutorial_choice', 'game', 'overlay', 'bug_report', 'bug_report_success', 'end_game_menu', 'tutorial', 'sounds_menu', 'keybinding_menu', 'keybinding_change'

# Panel stack tracking for navigation depth
navigation_stack = []
current_state = 'main_menu'
selected_menu_item = 0  # For keyboard navigation
menu_items = ["New Player Experience", "Launch with Custom Seed", "Settings", "Player Guide", "Exit"]
start_game_submenu_items = ["Basic New Game (Default Global Seed)", "Configure Game / Custom Seed", "Config Settings", "Game Options"]
start_game_submenu_selected_item = 0  # For start game submenu navigation
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

# Tutorial choice state
tutorial_choice_selected_item = 0  # For tutorial choice navigation (0=No, 1=Yes) - Default to No

# New Player Experience state
npe_tutorial_enabled = False    # Tutorial checkbox state
npe_intro_enabled = False       # Intro scenario checkbox state
npe_selected_item = 0           # Currently selected item (0=Tutorial checkbox, 1=Intro checkbox, 2=Start button)

# Pre-game settings state
pre_game_settings = {
    "difficulty": "STANDARD",
    "music_volume": 70,
    "sound_volume": 80,
    "graphics_quality": "STANDARD",
    "safety_level": "STANDARD"
}
selected_settings_item = 0
seed_choice = "weekly"  # "weekly" or "custom"
tutorial_enabled = False  # Default to no tutorial

# Tutorial state
current_tutorial_content = None

# Escape menu system for safe quit
escape_count = 0
escape_timer = 0  # Track time since last escape press
ESCAPE_TIMEOUT = 2000  # 2 seconds in milliseconds
ESCAPE_THRESHOLD = 3  # Number of escapes needed to show quit confirmation
first_time_help_content = None
first_time_help_close_button = None
current_help_mechanic = None  # Track which mechanic is currently showing

# Audio menu state
sounds_menu_selected_item = 0
audio_settings = {
    'master_enabled': True,
    'sfx_volume': 80,  # 0-100
    'individual_sounds': {
        'popup_open': True,
        'popup_close': True, 
        'popup_accept': True,
        'error_beep': True,
        'blob': True,
        'ap_spend': True,
        'money_spend': True
    }
}

# Keybinding menu state
keybinding_menu_selected_item = 0
keybinding_change_action = None  # Action being rebound
keybinding_change_display = None  # Display name for action being rebound
keybinding_all_bindings = []  # List of all keybinding items

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

# Phase 5: Complete initialization
draw_loading_screen(screen, SCREEN_W, SCREEN_H, 1.0, "Ready!")
pygame.display.flip()

# Brief pause to show completion (fast-load optimization: skip if under 100ms total)
import time
loading_start = time.time()
if time.time() - loading_start > 0.1:  # Only pause if loading took time
    pygame.time.wait(500)  # Brief pause to show "Ready!" message


def get_weekly_seed():
    import datetime
    # Example: YYYYWW (year and ISO week number)
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"{now.year}{now.isocalendar()[1]}"

def _handle_debug_console_keypress(key, game_state):
    """Handle debug console keypress using the debug console manager."""
    try:
        from src.ui.debug_console_manager import debug_console_manager
        return debug_console_manager.handle_keypress(key, game_state)
    except ImportError:
        return False

def _handle_debug_console_click(pos, screen_w, screen_h):
    """Handle debug console click using the debug console manager."""
    try:
        from src.ui.debug_console_manager import debug_console_manager
        return debug_console_manager.handle_click(pos, screen_w, screen_h)
    except ImportError:
        return False

def _draw_debug_console(screen, game_state, screen_w, screen_h):
    """Draw debug console using the debug console manager."""
    try:
        from src.ui.debug_console_manager import debug_console_manager
        debug_console_manager.draw(screen, game_state, screen_w, screen_h)
    except ImportError:
        pass

def load_markdown_file(filename):
    """Load and return the contents of a markdown file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Could not load {filename}"

def push_navigation_state(new_state):
    """Push current state to navigation stack and transition to new state."""
    global navigation_stack, current_state
    navigation_stack.append(current_state)
    current_state = new_state

def pop_navigation_state():
    """Pop from navigation stack and return to previous state."""
    global navigation_stack, current_state
    if navigation_stack:
        current_state = navigation_stack.pop()
        return True
    return False

def get_navigation_depth():
    """Get current navigation depth (number of states in stack)."""
    return len(navigation_stack)

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
    hints_enabled = "Enabled" if onboarding.are_hints_enabled() else "Disabled"
    
    # Get hint status
    hint_status = onboarding.get_hint_status()
    seen_hints = [name for name, seen in hint_status.items() if seen]
    unseen_hints = [name for name, seen in hint_status.items() if not seen]
    
    return f"""# Settings

## Tutorial & Help System
- **Tutorial System**: {tutorial_status}
- **Tutorial Completed**: {tutorial_completed}
- **In-Game Hints**: {hints_enabled}
- **In-Game Help**: Press 'H' key anytime to access Player Guide

### Hint Status (Factorio-style)
**Seen Hints ({len(seen_hints)}):** {', '.join(seen_hints) if seen_hints else 'None'}
**Available Hints ({len(unseen_hints)}):** {', '.join(unseen_hints) if unseen_hints else 'All seen'}

**Hint Controls:**
- Press **Ctrl+R** during gameplay to reset all hints
- Hints show once per new action, then auto-dismiss
- Configurable in config files (first_time_help setting)

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
- **Ctrl+D**: Debug UI state (shows blocking conditions)
- **Ctrl+E**: Clear stuck popup events (emergency)
- **Ctrl+R**: Reset all hints to show again

*Note: Settings are currently informational. Configuration options will be added in future updates.*"""

def handle_menu_click(mouse_pos, w, h):
    """
    Handle mouse clicks on main menu items.
    
    Args:
        mouse_pos: Tuple of (x, y) mouse coordinates
        w, h: Screen width and height for button positioning
    
    Updates global state based on which menu item was clicked:
    - New Player Experience: Tutorial and intro selection screen
    - Launch with Custom Seed: Transitions to seed input prompt
    - Settings: Settings menu (audio, keybindings, etc.)
    - Player Guide: Shows docs/PLAYERGUIDE.md in scrollable overlay
    - Exit: Closes the game
    """
    global current_state, selected_menu_item, overlay_content, overlay_title, seed
    
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
            if i == 0:  # Start Game
                current_state = 'start_game_submenu'
            elif i == 1:  # New Player Experience
                seed = get_weekly_seed()
                current_state = 'new_player_experience'
            elif i == 2:  # Launch with Custom Seed
                current_state = 'custom_seed_prompt'
                seed_input = ""  # Clear any previous input
            elif i == 3:  # Settings
                current_state = 'sounds_menu'
            elif i == 4:  # Player Guide
                overlay_content = load_markdown_file('docs/PLAYERGUIDE.md')
                overlay_title = "Player Guide"
                push_navigation_state('overlay')
            elif i == 5:  # Exit
                pygame.quit()
                sys.exit()
            break
    
    # Check for sound button click (bottom right corner)
    button_size = int(min(w, h) * 0.06)
    button_x = w - button_size - 20
    button_y = h - button_size - 20
    sound_button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
    
    if sound_button_rect.collidepoint(mx, my):
        global_sound_manager.toggle()
        # Update config to persist the sound setting
        if 'audio' not in current_config:
            current_config['audio'] = {}
        current_config['audio']['sound_enabled'] = global_sound_manager.is_enabled()
        config_manager.save_config(config_manager.get_current_config_name(), current_config)

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
    global selected_menu_item, current_state, overlay_content, overlay_title, seed, seed_input
    
    if key == pygame.K_UP:
        # Move selection up, wrapping to bottom
        selected_menu_item = (selected_menu_item - 1) % len(menu_items)
    elif key == pygame.K_DOWN:
        # Move selection down, wrapping to top  
        selected_menu_item = (selected_menu_item + 1) % len(menu_items)
    elif key == pygame.K_RETURN:
        # Activate selected menu item (same logic as mouse click)
        if selected_menu_item == 0:  # Start Game
            current_state = 'start_game_submenu'
        elif selected_menu_item == 1:  # New Player Experience
            seed = get_weekly_seed()
            current_state = 'new_player_experience'
        elif selected_menu_item == 2:  # Launch with Custom Seed
            current_state = 'custom_seed_prompt'
            seed_input = ""  # Clear any previous input
        elif selected_menu_item == 3:  # Settings
            current_state = 'sounds_menu'
        elif selected_menu_item == 4:  # Player Guide
            overlay_content = load_markdown_file('docs/PLAYERGUIDE.md')
            overlay_title = "Player Guide"
            push_navigation_state('overlay')
        elif selected_menu_item == 5:  # Exit
            pygame.quit()
            sys.exit()

def handle_start_game_submenu_click(mouse_pos, w, h):
    """Handle mouse clicks on start game submenu."""
    global current_state, start_game_submenu_selected_item, seed, seed_input, config_selected_item, sounds_menu_selected_item
    
    # Calculate button positions (match the standard menu layout)
    button_width = int(w * 0.5)
    button_height = int(h * 0.08)
    start_y = int(h * 0.3)
    spacing = int(h * 0.1)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    # Check each submenu button
    for i, item in enumerate(start_game_submenu_items):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            start_game_submenu_selected_item = i
            
            if i == 0:  # Basic New Game (Default Global Seed)
                seed = get_weekly_seed()
                current_state = 'game'
            elif i == 1:  # Configure Game / Custom Seed
                current_state = 'seed_selection'
                seed_input = ""
            elif i == 2:  # Config Settings
                current_state = 'config_select'
                config_selected_item = 0
            elif i == 3:  # Game Options
                current_state = 'sounds_menu'
                sounds_menu_selected_item = 0
            break

def handle_start_game_submenu_keyboard(key):
    """Handle keyboard navigation in start game submenu."""
    global start_game_submenu_selected_item, current_state, seed, seed_input, config_selected_item, sounds_menu_selected_item
    
    if key == pygame.K_UP:
        start_game_submenu_selected_item = (start_game_submenu_selected_item - 1) % len(start_game_submenu_items)
    elif key == pygame.K_DOWN:
        start_game_submenu_selected_item = (start_game_submenu_selected_item + 1) % len(start_game_submenu_items)
    elif key == pygame.K_RETURN:
        if start_game_submenu_selected_item == 0:  # Basic New Game
            seed = get_weekly_seed()
            current_state = 'game'
        elif start_game_submenu_selected_item == 1:  # Configure Game / Custom Seed
            current_state = 'seed_selection'
            seed_input = ""
        elif start_game_submenu_selected_item == 2:  # Config Settings
            current_state = 'config_select'
            config_selected_item = 0
        elif start_game_submenu_selected_item == 3:  # Game Options
            current_state = 'sounds_menu'
            sounds_menu_selected_item = 0
    elif key == pygame.K_ESCAPE:
        current_state = 'main_menu'

def handle_config_keyboard(key):
    """
    Handle keyboard navigation in config selection menu.
    
    Args:
        key: pygame key constant from keydown event
    """
    global config_selected_item, current_state, current_config
    
    all_items = available_configs + ["< Back to Main Menu"]
    
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
                # print(f"Switched to configuration: {selected_config}")
        # Return to main menu (both for config selection and back button)
        current_state = 'main_menu'
    elif key == pygame.K_ESCAPE:
        if not pop_navigation_state():
            current_state = 'main_menu'


def handle_pre_game_settings_click(mouse_pos, w, h):
    """Handle mouse clicks on pre-game settings screen."""
    global current_state, selected_settings_item, pre_game_settings
    
    # Calculate button positions (must match draw_pre_game_settings layout)
    button_width = int(w * 0.55)
    button_height = int(h * 0.07)
    start_y = int(h * 0.32)
    spacing = int(h * 0.085)
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
            
            if i == 0:  # Continue button (now first)
                current_state = 'seed_selection'
            else:
                # Cycle through setting values when clicked
                cycle_setting_value(i)
            break
    
    # Check for sound button click (bottom right corner)
    button_size = int(min(w, h) * 0.06)
    button_x = w - button_size - 20
    button_y = h - button_size - 20
    sound_button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
    
    if sound_button_rect.collidepoint(mx, my):
        global_sound_manager.toggle()
        # Update config to persist the sound setting
        if 'audio' not in current_config:
            current_config['audio'] = {}
        current_config['audio']['sound_enabled'] = global_sound_manager.is_enabled()
        config_manager.save_config(config_manager.get_current_config_name(), current_config)


def handle_pre_game_settings_keyboard(key):
    """Handle keyboard navigation for pre-game settings screen."""
    global selected_settings_item, current_state, pre_game_settings
    
    if key == pygame.K_UP:
        selected_settings_item = (selected_settings_item - 1) % 5
    elif key == pygame.K_DOWN:
        selected_settings_item = (selected_settings_item + 1) % 5
    elif key == pygame.K_RETURN:
        if selected_settings_item == 0:  # Continue button (now first)
            current_state = 'seed_selection'
        else:
            # Cycle through setting values
            cycle_setting_value(selected_settings_item)
    elif key == pygame.K_LEFT:
        # Allow left arrow to also cycle settings
        if selected_settings_item > 0:  # Not the Continue button
            cycle_setting_value(selected_settings_item, reverse=True)
    elif key == pygame.K_RIGHT:
        # Allow right arrow to cycle settings forward
        if selected_settings_item > 0:  # Not the Continue button
            cycle_setting_value(selected_settings_item)
    elif key == pygame.K_ESCAPE:
        if not pop_navigation_state():
            current_state = 'main_menu'


def cycle_setting_value(setting_index, reverse=False):
    """Cycle through available values for a setting."""
    global pre_game_settings
    
    if setting_index == 1:  # Research Intensity (Difficulty) - now at index 1
        options = ["EASY", "STANDARD", "HARD"]
        current = pre_game_settings["difficulty"]
        current_idx = options.index(current) if current in options else 1
        new_idx = (current_idx + (-1 if reverse else 1)) % len(options)
        pre_game_settings["difficulty"] = options[new_idx]
        
    elif setting_index == 2:  # Audio Alerts Volume (Sound Volume) - now at index 2
        options = [30, 50, 70, 80, 90, 100]
        current = pre_game_settings["sound_volume"]
        try:
            current_idx = options.index(current)
        except ValueError:
            current_idx = 3  # Default to 80
        new_idx = (current_idx + (-1 if reverse else 1)) % len(options)
        pre_game_settings["sound_volume"] = options[new_idx]
        
    elif setting_index == 3:  # Visual Enhancement (Graphics Quality) - now at index 3
        options = ["LOW", "STANDARD", "HIGH"]
        current = pre_game_settings["graphics_quality"]
        current_idx = options.index(current) if current in options else 1
        new_idx = (current_idx + (-1 if reverse else 1)) % len(options)
        pre_game_settings["graphics_quality"] = options[new_idx]
        
    elif setting_index == 4:  # Safety Protocol Level - now at index 4
        options = ["MINIMAL", "STANDARD", "ENHANCED", "MAXIMUM"]
        current = pre_game_settings["safety_level"]
        current_idx = options.index(current) if current in options else 1
        new_idx = (current_idx + (-1 if reverse else 1)) % len(options)
        pre_game_settings["safety_level"] = options[new_idx]


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
    
    # Check for sound button click (bottom right corner)
    button_size = int(min(w, h) * 0.06)
    button_x = w - button_size - 20
    button_y = h - button_size - 20
    sound_button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
    
    if sound_button_rect.collidepoint(mx, my):
        global_sound_manager.toggle()
        # Update config to persist the sound setting
        if 'audio' not in current_config:
            current_config['audio'] = {}
        current_config['audio']['sound_enabled'] = global_sound_manager.is_enabled()
        config_manager.save_config(config_manager.get_current_config_name(), current_config)


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
    global current_state, tutorial_enabled, tutorial_choice_selected_item
    
    # Calculate button positions (must match draw_tutorial_choice layout)
    button_width = int(w * 0.4)
    button_height = int(h * 0.08)
    start_y = int(h * 0.4)
    spacing = int(h * 0.12)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    for i in range(2):  # No tutorial, Yes tutorial (reordered)
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            tutorial_choice_selected_item = i  # Update selection for visual feedback
            if i == 0:  # No - Regular Mode (now first)
                tutorial_enabled = False
                onboarding.dismiss_tutorial()
            elif i == 1:  # Yes - Enable Tutorial (now second)
                tutorial_enabled = True
                onboarding.start_stepwise_tutorial()  # Start the new stepwise tutorial
            
            # Set the seed and start the game
            random.seed(seed)
            current_state = 'game'
            break


def handle_tutorial_choice_hover(mouse_pos, w, h):
    """Handle mouse hover for tutorial choice screen to update selection."""
    global tutorial_choice_selected_item
    
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
            tutorial_choice_selected_item = i
            break


def handle_tutorial_choice_keyboard(key):
    """Handle keyboard navigation for tutorial choice screen."""
    global current_state, tutorial_enabled, tutorial_choice_selected_item
    
    if key == pygame.K_UP:
        tutorial_choice_selected_item = (tutorial_choice_selected_item - 1) % 2
    elif key == pygame.K_DOWN:
        tutorial_choice_selected_item = (tutorial_choice_selected_item + 1) % 2
    elif key == pygame.K_LEFT:
        tutorial_choice_selected_item = (tutorial_choice_selected_item - 1) % 2
    elif key == pygame.K_RIGHT:
        tutorial_choice_selected_item = (tutorial_choice_selected_item + 1) % 2
    elif key == pygame.K_RETURN or key == pygame.K_SPACE:
        # Use currently selected item
        if tutorial_choice_selected_item == 0:  # No - Regular Mode (now first)
            tutorial_enabled = False
            onboarding.dismiss_tutorial()
        else:  # Yes - Enable Tutorial (now second)
            tutorial_enabled = True
            onboarding.start_stepwise_tutorial()
        
        # Set the seed and start the game
        random.seed(seed)
        current_state = 'game'
    elif key == pygame.K_ESCAPE:
        current_state = 'seed_selection'


def handle_new_player_experience_click(mouse_pos, w, h):
    """Handle mouse clicks on new player experience screen."""
    global current_state, tutorial_enabled, npe_tutorial_enabled, npe_intro_enabled, npe_selected_item
    
    # Layout constants (must match draw_new_player_experience)
    center_x = w // 2
    checkbox_size = int(h * 0.04)
    start_y = int(h * 0.35)
    spacing = int(h * 0.08)
    button_width = int(w * 0.3)
    button_height = int(h * 0.06)
    button_y = int(h * 0.65)
    
    mx, my = mouse_pos
    
    # Check checkbox clicks
    for i in range(2):  # Tutorial checkbox, Intro checkbox
        checkbox_x = center_x - checkbox_size // 2 - int(w * 0.15)
        checkbox_y = start_y + i * spacing
        checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size)
        
        if checkbox_rect.collidepoint(mx, my):
            npe_selected_item = i
            if i == 0:  # Tutorial checkbox
                npe_tutorial_enabled = not npe_tutorial_enabled
            elif i == 1:  # Intro checkbox
                npe_intro_enabled = not npe_intro_enabled
            return
    
    # Check start button click
    button_x = center_x - button_width // 2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    if button_rect.collidepoint(mx, my):
        npe_selected_item = 2
        # Apply settings and start game
        tutorial_enabled = npe_tutorial_enabled
        if tutorial_enabled:
            onboarding.start_stepwise_tutorial()
        else:
            onboarding.dismiss_tutorial()
        
        # Set up intro scenario if enabled
        if npe_intro_enabled:
            # This will be handled in game initialization
            pass
        
        # Set the seed and start the game
        random.seed(seed)
        current_state = 'game'


def handle_new_player_experience_hover(mouse_pos, w, h):
    """Handle mouse hover for new player experience screen."""
    global npe_selected_item
    
    # Layout constants (must match draw_new_player_experience)
    center_x = w // 2
    checkbox_size = int(h * 0.04)
    start_y = int(h * 0.35)
    spacing = int(h * 0.08)
    button_width = int(w * 0.3)
    button_height = int(h * 0.06)
    button_y = int(h * 0.65)
    
    mx, my = mouse_pos
    
    # Check checkbox hover
    for i in range(2):  # Tutorial checkbox, Intro checkbox
        checkbox_x = center_x - checkbox_size // 2 - int(w * 0.15)
        checkbox_y = start_y + i * spacing
        checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size)
        
        if checkbox_rect.collidepoint(mx, my):
            npe_selected_item = i
            return
    
    # Check start button hover
    button_x = center_x - button_width // 2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    if button_rect.collidepoint(mx, my):
        npe_selected_item = 2


def handle_new_player_experience_keyboard(key):
    """Handle keyboard navigation for new player experience screen."""
    global current_state, tutorial_enabled, npe_tutorial_enabled, npe_intro_enabled, npe_selected_item
    
    if key == pygame.K_UP:
        npe_selected_item = (npe_selected_item - 1) % 3
    elif key == pygame.K_DOWN:
        npe_selected_item = (npe_selected_item + 1) % 3
    elif key == pygame.K_RETURN or key == pygame.K_SPACE:
        if npe_selected_item == 0:  # Tutorial checkbox
            npe_tutorial_enabled = not npe_tutorial_enabled
        elif npe_selected_item == 1:  # Intro checkbox
            npe_intro_enabled = not npe_intro_enabled
        elif npe_selected_item == 2:  # Start button
            # Apply settings and start game
            tutorial_enabled = npe_tutorial_enabled
            if tutorial_enabled:
                onboarding.start_stepwise_tutorial()
            else:
                onboarding.dismiss_tutorial()
            
            # Set up intro scenario if enabled
            if npe_intro_enabled:
                # This will be handled in game initialization
                pass
            
            # Set the seed and start the game
            random.seed(seed)
            current_state = 'game'
    elif key == pygame.K_ESCAPE:
        current_state = 'main_menu'


def handle_audio_menu_click(mouse_pos, w, h):
    """Handle mouse clicks on audio settings menu."""
    global current_state, sounds_menu_selected_item, audio_settings, global_sound_manager
    
    # Menu item layout (matching draw_audio_menu)
    button_width = int(w * 0.6)
    button_height = int(h * 0.06)
    start_y = int(h * 0.25)
    spacing = int(h * 0.08)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    # Audio menu items
    menu_items = [
        "Master Sound Toggle",
        "SFX Volume",
        "Sound Effects Settings", 
        "Keybinding Configuration",
        "Test Sound",
        "< Back to Main Menu"
    ]
    
    for i in range(len(menu_items)):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            sounds_menu_selected_item = i
            
            if i == 0:  # Master Sound Toggle
                audio_settings['master_enabled'] = not audio_settings['master_enabled']
                global_sound_manager.set_enabled(audio_settings['master_enabled'])
                # Update config persistence
                current_config['audio']['sound_enabled'] = audio_settings['master_enabled']
                config_manager.save_config(config_manager.get_current_config_name(), current_config)
            elif i == 1:  # SFX Volume
                # Cycle through volume levels
                volumes = [0, 25, 50, 75, 100]
                current_idx = volumes.index(audio_settings['sfx_volume']) if audio_settings['sfx_volume'] in volumes else 3
                audio_settings['sfx_volume'] = volumes[(current_idx + 1) % len(volumes)]
            elif i == 2:  # Sound Effects Settings
                # Toggle to sound effects submenu (for now just cycle individual sounds)
                sound_keys = list(audio_settings['individual_sounds'].keys())
                # Simple toggle of first sound for demonstration
                if sound_keys:
                    first_sound = sound_keys[0]
                    audio_settings['individual_sounds'][first_sound] = not audio_settings['individual_sounds'][first_sound]
                    global_sound_manager.sound_toggles[first_sound] = audio_settings['individual_sounds'][first_sound]
            elif i == 3:  # Keybinding Configuration
                current_state = 'keybinding_menu'
            elif i == 4:  # Test Sound
                if global_sound_manager and audio_settings['master_enabled']:
                    global_sound_manager.play_sound('popup_accept')
            elif i == 5:  # Back to Main Menu
                current_state = 'main_menu'
            break


def handle_audio_menu_keyboard(key):
    """Handle keyboard navigation for audio settings menu."""
    global current_state, sounds_menu_selected_item, audio_settings, global_sound_manager
    
    menu_items_count = 6  # Number of menu items (updated for keybinding option)
    
    if key == pygame.K_UP:
        sounds_menu_selected_item = (sounds_menu_selected_item - 1) % menu_items_count
    elif key == pygame.K_DOWN:
        sounds_menu_selected_item = (sounds_menu_selected_item + 1) % menu_items_count
    elif key == pygame.K_RETURN or key == pygame.K_SPACE:
        # Execute selected menu action
        if sounds_menu_selected_item == 0:  # Master Sound Toggle
            audio_settings['master_enabled'] = not audio_settings['master_enabled']
            global_sound_manager.set_enabled(audio_settings['master_enabled'])
            # Update config persistence
            current_config['audio']['sound_enabled'] = audio_settings['master_enabled']
            config_manager.save_config(config_manager.get_current_config_name(), current_config)
        elif sounds_menu_selected_item == 1:  # SFX Volume
            # Cycle through volume levels
            volumes = [0, 25, 50, 75, 100]
            current_idx = volumes.index(audio_settings['sfx_volume']) if audio_settings['sfx_volume'] in volumes else 3
            audio_settings['sfx_volume'] = volumes[(current_idx + 1) % len(volumes)]
        elif sounds_menu_selected_item == 2:  # Sound Effects Settings
            # Toggle individual sound settings
            sound_keys = list(audio_settings['individual_sounds'].keys())
            if sound_keys:
                first_sound = sound_keys[0]
                audio_settings['individual_sounds'][first_sound] = not audio_settings['individual_sounds'][first_sound]
                global_sound_manager.sound_toggles[first_sound] = audio_settings['individual_sounds'][first_sound]
        elif sounds_menu_selected_item == 3:  # Keybinding Configuration
            current_state = 'keybinding_menu'
        elif sounds_menu_selected_item == 4:  # Test Sound
            if global_sound_manager and audio_settings['master_enabled']:
                global_sound_manager.play_sound('popup_accept')
        elif sounds_menu_selected_item == 5:  # Back to Main Menu
            current_state = 'main_menu'
    elif key == pygame.K_LEFT:
        # Allow left arrow for settings adjustment
        if sounds_menu_selected_item == 1:  # SFX Volume
            volumes = [0, 25, 50, 75, 100]
            current_idx = volumes.index(audio_settings['sfx_volume']) if audio_settings['sfx_volume'] in volumes else 3
            audio_settings['sfx_volume'] = volumes[(current_idx - 1) % len(volumes)]
    elif key == pygame.K_RIGHT:
        # Allow right arrow for settings adjustment
        if sounds_menu_selected_item == 1:  # SFX Volume
            volumes = [0, 25, 50, 75, 100]
            current_idx = volumes.index(audio_settings['sfx_volume']) if audio_settings['sfx_volume'] in volumes else 3
            audio_settings['sfx_volume'] = volumes[(current_idx + 1) % len(volumes)]
    elif key == pygame.K_ESCAPE:
        current_state = 'main_menu'


def handle_keybinding_menu_keyboard(key):
    """Handle keyboard navigation in the keybinding configuration menu."""
    global keybinding_menu_selected_item, current_state
    
    total_items = 18  # 9 actions + 3 game controls + 4 nav controls + 2 special items
    
    if key == pygame.K_UP:
        keybinding_menu_selected_item = (keybinding_menu_selected_item - 1) % total_items
    elif key == pygame.K_DOWN:
        keybinding_menu_selected_item = (keybinding_menu_selected_item + 1) % total_items
    elif key == pygame.K_RETURN or key == pygame.K_SPACE:
        handle_keybinding_menu_select()
    elif key == pygame.K_ESCAPE:
        current_state = 'sounds_menu'  # Go back to audio menu


def handle_keybinding_menu_select():
    """Handle selection of a keybinding menu item."""
    global current_state, keybinding_change_action, keybinding_change_display
    from src.services.keybinding_manager import keybinding_manager
    
    # Map selected item to action
    if keybinding_menu_selected_item < 9:
        # Action keybindings (0-8)
        action_num = keybinding_menu_selected_item + 1
        keybinding_change_action = f"action_{action_num}"
        keybinding_change_display = f"Action {action_num}"
        current_state = 'keybinding_change'
    elif keybinding_menu_selected_item < 12:
        # Game control keybindings (9-11)
        game_actions = ["end_turn", "help_guide", "quit_to_menu"]
        game_displays = ["End Turn", "Help Guide", "Quit to Menu"]
        idx = keybinding_menu_selected_item - 9
        keybinding_change_action = game_actions[idx]
        keybinding_change_display = game_displays[idx]
        current_state = 'keybinding_change'
    elif keybinding_menu_selected_item < 16:
        # Navigation keybindings (12-15)
        nav_actions = ["menu_up", "menu_down", "menu_select", "menu_back"]
        nav_displays = ["Menu Up", "Menu Down", "Menu Select", "Menu Back"]
        idx = keybinding_menu_selected_item - 12
        keybinding_change_action = nav_actions[idx]
        keybinding_change_display = nav_displays[idx]
        current_state = 'keybinding_change'
    elif keybinding_menu_selected_item == 16:
        # Reset to defaults
        keybinding_manager.reset_to_defaults()
        keybinding_manager.save_keybindings()
    elif keybinding_menu_selected_item == 17:
        # Back to menu
        current_state = 'sounds_menu'


def handle_keybinding_change_keyboard(key):
    """Handle keyboard input when changing a keybinding."""
    global current_state, keybinding_change_action
    from src.services.keybinding_manager import keybinding_manager
    
    if key == pygame.K_ESCAPE:
        # Cancel keybinding change
        current_state = 'keybinding_menu'
        keybinding_change_action = None
    else:
        # Try to set the new keybinding
        if keybinding_manager.set_keybinding(keybinding_change_action, key):
            # Save the new keybinding and return to menu
            keybinding_manager.save_keybindings()
            current_state = 'keybinding_menu'
            keybinding_change_action = None


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
                push_navigation_state('overlay')
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
        elif end_game_selected_item == 1:  # Relaunch Game
            current_state = 'game'
        elif end_game_selected_item == 2:  # Main Menu
            current_state = 'main_menu'
            selected_menu_item = 0
        elif end_game_selected_item == 3:  # Settings
            overlay_content = create_settings_content()
            overlay_title = "Settings"
            push_navigation_state('overlay')
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


# Escape menu state
escape_menu_selected_item = 0
escape_menu_items = ["Resume Game", "Main Menu", "Quit Game"]

def handle_escape_menu_click(mouse_pos, w, h):
    """Handle mouse clicks on escape menu."""
    global escape_menu_selected_item, current_state, selected_menu_item, running
    
    mx, my = mouse_pos
    
    # Calculate menu dimensions
    menu_width = 400
    menu_height = 300
    menu_x = (w - menu_width) // 2
    menu_y = (h - menu_height) // 2
    
    # Button dimensions
    button_height = 50
    button_spacing = 20
    start_y = menu_y + 100
    
    for i, item in enumerate(escape_menu_items):
        button_y = start_y + i * (button_height + button_spacing)
        button_rect = pygame.Rect(menu_x + 50, button_y, menu_width - 100, button_height)
        
        if button_rect.collidepoint(mx, my):
            escape_menu_selected_item = i
            handle_escape_menu_select()
            break

def handle_escape_menu_keyboard(key):
    """Handle keyboard navigation for escape menu."""
    global escape_menu_selected_item, current_state, selected_menu_item, running
    
    if key == pygame.K_UP:
        escape_menu_selected_item = (escape_menu_selected_item - 1) % len(escape_menu_items)
    elif key == pygame.K_DOWN:
        escape_menu_selected_item = (escape_menu_selected_item + 1) % len(escape_menu_items)
    elif key == pygame.K_RETURN or key == pygame.K_SPACE:
        handle_escape_menu_select()
    elif key == pygame.K_ESCAPE:
        # Go back to game
        current_state = 'game'

def handle_escape_menu_select():
    """Handle escape menu selection."""
    global current_state, selected_menu_item, running, escape_count
    
    if escape_menu_selected_item == 0:  # Resume Game
        current_state = 'game'
        escape_count = 0  # Reset escape counter
    elif escape_menu_selected_item == 1:  # Main Menu
        current_state = 'main_menu'
        selected_menu_item = 0
        escape_count = 0
    elif escape_menu_selected_item == 2:  # Quit Game
        running = False


def draw_escape_menu(screen, w, h):
    """Draw the escape menu overlay."""
    # Menu dimensions
    menu_width = 400
    menu_height = 300
    menu_x = (w - menu_width) // 2
    menu_y = (h - menu_height) // 2
    
    # Draw menu background
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    pygame.draw.rect(screen, (40, 40, 50), menu_rect)
    pygame.draw.rect(screen, (80, 80, 90), menu_rect, 3)
    
    # Draw title
    font = pygame.font.SysFont('Consolas', 24, bold=True)
    title_text = font.render("ESCAPE MENU", True, (255, 255, 255))
    title_rect = title_text.get_rect(centerx=menu_x + menu_width // 2, y=menu_y + 20)
    screen.blit(title_text, title_rect)
    
    # Draw subtitle
    subtitle_font = pygame.font.SysFont('Consolas', 14)
    subtitle_text = subtitle_font.render("Use UP/DOWN arrows and ENTER to select", True, (180, 180, 180))
    subtitle_rect = subtitle_text.get_rect(centerx=menu_x + menu_width // 2, y=menu_y + 50)
    screen.blit(subtitle_text, subtitle_rect)
    
    # Draw menu items
    button_font = pygame.font.SysFont('Consolas', 18, bold=True)
    button_height = 50
    button_spacing = 20
    start_y = menu_y + 100
    
    for i, item in enumerate(escape_menu_items):
        button_y = start_y + i * (button_height + button_spacing)
        button_rect = pygame.Rect(menu_x + 50, button_y, menu_width - 100, button_height)
        
        # Button color based on selection
        if i == escape_menu_selected_item:
            button_color = (70, 130, 180)  # Steel blue for selected
            text_color = (255, 255, 255)
        else:
            button_color = (60, 60, 70)
            text_color = (200, 200, 200)
        
        # Draw button
        pygame.draw.rect(screen, button_color, button_rect)
        pygame.draw.rect(screen, (120, 120, 130), button_rect, 2)
        
        # Draw button text
        text = button_font.render(item, True, text_color)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)


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
                    # print(f"Game log flushed to: {log_path}")
                    pass
                game_state._final_logged = True
            except Exception as e:
                # print(f"Error during game state flush: {e}")
                pass
        
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
    global end_game_selected_item, high_score_submit_to_leaderboard
    # UI overlay variables need global declaration to prevent UnboundLocalError when referenced before assignment
    global first_time_help_content, first_time_help_close_button, current_tutorial_content, current_help_mechanic
    global overlay_content, overlay_title
    # Hiring dialog rects need to persist between frames for click detection
    global cached_hiring_dialog_rects
    # Keybinding menu variables
    global keybinding_all_bindings
    # Escape handling variables
    global escape_count, escape_timer
    
    # Initialize game state as None - will be created when game starts
    game_state = None
    tooltip_text = None
    # Initialize cached hiring dialog rects
    cached_hiring_dialog_rects = None

    running = True
    try:
        while running:
            clock.tick(30)  # 30 FPS for smooth menu navigation
            
            # Initialize variables used in event handling
            back_button_rect = None
            
            # --- Event handling based on current state --- #
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.VIDEORESIZE:
                    # Update screen size and redraw (responsive design)
                    SCREEN_W, SCREEN_H = event.w, event.h
                    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), FLAGS)
                
                elif event.type == pygame.MOUSEWHEEL:
                    # Modern pygame mouse wheel handling (prevents crashes)
                    if (current_state == 'game' and game_state and 
                        game_state.scrollable_event_log_enabled):
                        # Handle mouse wheel scrolling for event log
                        if event.y > 0:  # Mouse wheel up
                            game_state.event_log_scroll_offset = max(0, game_state.event_log_scroll_offset - 3)
                        elif event.y < 0:  # Mouse wheel down
                            max_scroll = max(0, len(game_state.event_log_history) + len(game_state.messages) - 7)
                            game_state.event_log_scroll_offset = min(max_scroll, game_state.event_log_scroll_offset + 3)
                    # Always continue - don't let unhandled wheel events cause issues
                    continue
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    
                    # Handle overlay manager events first (highest priority)
                    if current_state == 'game' and game_state:
                        handled_element = game_state.overlay_manager.handle_mouse_event(event, SCREEN_W, SCREEN_H)
                        if handled_element:
                            # Overlay manager handled the event
                            continue
                    
                    # Handle mouse clicks based on current state
                    if current_state == 'main_menu':
                        handle_menu_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'start_game_submenu':
                        handle_start_game_submenu_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'pre_game_settings':
                        handle_pre_game_settings_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'seed_selection':
                        handle_seed_selection_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'tutorial_choice':
                        handle_tutorial_choice_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'new_player_experience':
                        handle_new_player_experience_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'sounds_menu':
                        handle_audio_menu_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'keybinding_menu':
                        # Handle keybinding menu clicks
                        clicked_item = get_keybinding_menu_click_item((mx, my), SCREEN_W, SCREEN_H, len(keybinding_all_bindings))
                        if clicked_item >= 0:
                            keybinding_menu_selected_item = clicked_item
                            # Trigger action for this item
                            handle_keybinding_menu_select()
                    elif current_state == 'overlay':
                        # Check for Back button click first
                        if back_button_rect and back_button_rect.collidepoint(mx, my):
                            if not pop_navigation_state():
                                current_state = 'main_menu'
                            overlay_scroll = 0
                        else:
                            # Click anywhere else to return via navigation stack
                            if not pop_navigation_state():
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

                    elif current_state == 'escape_menu':
                        # Handle escape menu clicks
                        handle_escape_menu_click((mx, my), SCREEN_W, SCREEN_H)

                    elif current_state == 'game':
                        # Stepwise tutorial button handling (takes precedence)
                        if onboarding.show_tutorial_overlay:
                            tutorial_data = onboarding.get_current_stepwise_tutorial_data()
                            if tutorial_data:
                                tutorial_buttons = draw_stepwise_tutorial_overlay(screen, tutorial_data, SCREEN_W, SCREEN_H)
                                
                                # Check button clicks
                                if 'next' in tutorial_buttons and tutorial_buttons['next'].collidepoint(mx, my):
                                    # Next button clicked
                                    onboarding.advance_stepwise_tutorial()
                                elif 'back' in tutorial_buttons and tutorial_buttons['back'].collidepoint(mx, my):
                                    # Back button clicked
                                    onboarding.go_back_stepwise_tutorial()
                                elif 'skip' in tutorial_buttons and tutorial_buttons['skip'].collidepoint(mx, my):
                                    # Skip button clicked
                                    onboarding.dismiss_tutorial()
                        
                        # Window manager handling (for draggable windows)
                        elif window_manager.handle_mouse_event(event, SCREEN_W, SCREEN_H):
                            # Check for minimize button clicks
                            from ui import draw_window_with_header
                            for element_id in window_manager.elements:
                                element = window_manager.elements[element_id]
                                if element.visible:
                                    # Get minimize button rect
                                    header_rect, minimize_rect = draw_window_with_header(
                                        pygame.Surface((1, 1)), element.rect, element.title, 
                                        element.content, element.state.value == 'minimized'
                                    )
                                    if minimize_rect.collidepoint(mx, my):
                                        window_manager.toggle_minimize(element_id)
                                        break
                            # Window manager handled the event, skip other processing
                        
                        # First-time help close button
                        elif first_time_help_content and first_time_help_close_button:
                            # Check if the close button was clicked
                            if first_time_help_close_button.collidepoint(mx, my):
                                # Mark mechanic as seen so it won't reappear
                                if current_help_mechanic:
                                    onboarding.mark_mechanic_seen(current_help_mechanic)
                                # Play popup close sound
                                if game_state and hasattr(game_state, 'sound_manager'):
                                    game_state.sound_manager.play_sound('popup_close')
                                first_time_help_content = None
                                first_time_help_close_button = None
                                current_help_mechanic = None
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
                            # Check for hiring dialog clicks first
                            if game_state and game_state.pending_hiring_dialog and cached_hiring_dialog_rects is not None:
                                hiring_handled = False
                                for rect_info in cached_hiring_dialog_rects:
                                    if rect_info['rect'].collidepoint(mx, my):
                                        if rect_info['type'] == 'employee_option':
                                            # Player selected an employee subtype
                                            game_state.select_employee_subtype(rect_info['subtype_id'])
                                            hiring_handled = True
                                            break
                                        elif rect_info['type'] == 'researcher_option':
                                            # Player selected a researcher from the pool
                                            game_state.select_researcher_from_pool(rect_info['researcher_index'])
                                            hiring_handled = True
                                            break
                                        elif rect_info['type'] == 'back_to_subtypes':
                                            # Player wants to go back to employee subtype selection
                                            game_state.pending_hiring_dialog["mode"] = None
                                            hiring_handled = True
                                            break
                                        elif rect_info['type'] == 'cancel':
                                            # Player cancelled the hiring dialog
                                            game_state.dismiss_hiring_dialog()
                                            hiring_handled = True
                                            break
                                
                                if hiring_handled:
                                    pass  # Hiring dialog handled the click
                                else:
                                    # When hiring dialog is open, check if click is inside dialog area
                                    # Calculate dialog rect (same as in ui.py draw_hiring_dialog)
                                    dialog_width = int(SCREEN_W * 0.8)
                                    dialog_height = int(SCREEN_H * 0.85)
                                    dialog_x = (SCREEN_W - dialog_width) // 2
                                    dialog_y = (SCREEN_H - dialog_height) // 2
                                    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
                                    
                                    if dialog_rect.collidepoint(mx, my):
                                        # Click is inside dialog area but not on a button - do nothing (modal behavior)
                                        pass
                                    else:
                                        # Click is outside dialog area - dismiss the dialog
                                        game_state.dismiss_hiring_dialog()
                                        if hasattr(game_state, 'sound_manager'):
                                            game_state.sound_manager.play_sound('popup_close')
                            # Check for popup button clicks first
                            elif handle_popup_button_click((mx, my), game_state, SCREEN_W, SCREEN_H):
                                # Popup button was clicked, no need for further processing
                                pass
                            # Check for debug console clicks
                            elif _handle_debug_console_click((mx, my), SCREEN_W, SCREEN_H):
                                # Debug console handled the click
                                pass
                            else:
                                # Regular game mouse handling
                                result = game_state.handle_click((mx, my), SCREEN_W, SCREEN_H)
                                if result == 'play_sound':
                                    game_state.sound_manager.play_ap_spend_sound()
                                tooltip_text = result
                        
                elif event.type == pygame.MOUSEMOTION:
                    # Handle window manager motion events first (for dragging)
                    if current_state == 'game' and window_manager.handle_mouse_event(event, SCREEN_W, SCREEN_H):
                        # Window manager handled the event (dragging), skip other processing
                        continue
                    
                    # Handle overlay manager hover events
                    if current_state == 'game' and game_state:
                        handled_element = game_state.overlay_manager.handle_mouse_event(event, SCREEN_W, SCREEN_H)
                        if handled_element:
                            # Overlay manager handled the event
                            continue
                    
                    # Handle activity log dragging
                    if current_state == 'game' and game_state:
                        game_state.handle_mouse_motion(event.pos, SCREEN_W, SCREEN_H)
                    
                    # Mouse hover effects for tutorial choice screen
                    elif current_state == 'tutorial_choice':
                        handle_tutorial_choice_hover(event.pos, SCREEN_W, SCREEN_H)
                    
                    # Mouse hover effects for new player experience screen
                    elif current_state == 'new_player_experience':
                        handle_new_player_experience_hover(event.pos, SCREEN_W, SCREEN_H)
                    
                    # Mouse hover effects only active during gameplay
                    if current_state == 'game' and game_state:
                        tooltip_text = game_state.check_hover(event.pos, SCREEN_W, SCREEN_H)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Handle window manager button release (for ending drag operations)
                    if current_state == 'game':
                        window_manager.handle_mouse_event(event, SCREEN_W, SCREEN_H)
                    
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
                    
                    elif current_state == 'start_game_submenu':
                        handle_start_game_submenu_keyboard(event.key)
                    
                    elif current_state == 'config_select':
                        handle_config_keyboard(event.key)
                            
                    elif current_state == 'pre_game_settings':
                        handle_pre_game_settings_keyboard(event.key)
                    elif current_state == 'seed_selection':
                        handle_seed_selection_keyboard(event.key)
                    elif current_state == 'tutorial_choice':
                        handle_tutorial_choice_keyboard(event.key)
                    elif current_state == 'new_player_experience':
                        handle_new_player_experience_keyboard(event.key)
                    elif current_state == 'sounds_menu':
                        handle_audio_menu_keyboard(event.key)
                    elif current_state == 'keybinding_menu':
                        handle_keybinding_menu_keyboard(event.key)
                    elif current_state == 'keybinding_change':
                        handle_keybinding_change_keyboard(event.key)
                    elif current_state == 'overlay':
                        # Overlay navigation: scroll with arrows, escape to return
                        if event.key == pygame.K_ESCAPE:
                            if not pop_navigation_state():
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

                    elif current_state == 'escape_menu':
                        # Handle escape menu keyboard navigation
                        handle_escape_menu_keyboard(event.key)

                            
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

                        # Help key (H) - always available regardless of overlay state
                        if event.key == pygame.K_h:
                            overlay_content = load_markdown_file('docs/PLAYERGUIDE.md')
                            overlay_title = "Player Guide"
                            push_navigation_state('overlay')
                        
                        # Stepwise tutorial keyboard handling (takes precedence when tutorial is active)
                        elif onboarding.show_tutorial_overlay:
                            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                                # Advance tutorial step
                                onboarding.advance_stepwise_tutorial()
                            elif event.key == pygame.K_BACKSPACE:
                                # Go back in tutorial
                                onboarding.go_back_stepwise_tutorial()
                            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_s:
                                # Skip tutorial (ESC or S key)
                                onboarding.dismiss_tutorial()
                        
                        # Help key (H) - redundant check removed since it's handled above
                        
                        # Close first-time help
                        elif event.key == pygame.K_ESCAPE and first_time_help_content:
                            # Mark mechanic as seen so it won't reappear
                            if current_help_mechanic:
                                onboarding.mark_mechanic_seen(current_help_mechanic)
                            # Play popup close sound
                            if game_state and hasattr(game_state, 'sound_manager'):
                                game_state.sound_manager.play_sound('popup_close')
                            first_time_help_content = None
                            first_time_help_close_button = None
                            current_help_mechanic = None
                        
                        # Close hiring dialog with multiple keys (Left Arrow, Backspace, or ESC)
                        elif (event.key in [pygame.K_LEFT, pygame.K_BACKSPACE, pygame.K_ESCAPE] and 
                              game_state and game_state.pending_hiring_dialog):
                            game_state.dismiss_hiring_dialog()
                            # Play popup close sound
                            if hasattr(game_state, 'sound_manager'):
                                game_state.sound_manager.play_sound('popup_close')
                        
                        # Dedicated menu key - 'M' to access main menu/pause
                        elif event.key == pygame.K_m and current_state == 'game' and game_state:
                            # Toggle escape menu (pause/main menu access)
                            current_state = 'escape_menu'
                        
                        # Screenshot functionality with [ key
                        elif event.key == pygame.K_LEFTBRACKET:
                            import datetime
                            import os
                            # Create screenshots directory if it doesn't exist
                            screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
                            os.makedirs(screenshots_dir, exist_ok=True)
                            # Generate timestamp for filename
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            screenshot_path = os.path.join(screenshots_dir, f'pdoom_screenshot_{timestamp}.png')
                            # Save the current screen
                            pygame.image.save(screen, screenshot_path)
                            # print(f"Screenshot saved: {screenshot_path}")
                            # Play UI sound if available
                            if game_state and hasattr(game_state, 'sound_manager'):
                                game_state.sound_manager.play_sound('ui_accept')
                        
                        # Debug console toggle
                        elif _handle_debug_console_keypress(event.key, game_state):
                            pass  # Debug console manager handled it
                        
                        elif event.key == pygame.K_RETURN and first_time_help_content:
                            # Mark mechanic as seen so it won't reappear
                            if current_help_mechanic:
                                onboarding.mark_mechanic_seen(current_help_mechanic)
                            # Play popup accept sound
                            if game_state and hasattr(game_state, 'sound_manager'):
                                game_state.sound_manager.play_sound('popup_accept')
                            first_time_help_content = None
                            first_time_help_close_button = None
                            current_help_mechanic = None
                        
                        # Arrow key scrolling for scrollable event log
                        elif game_state and game_state.scrollable_event_log_enabled:
                            if event.key == pygame.K_UP:
                                game_state.event_log_scroll_offset = max(0, game_state.event_log_scroll_offset - 1)
                            elif event.key == pygame.K_DOWN:
                                max_scroll = max(0, len(game_state.event_log_history) + len(game_state.messages) - 7)
                                game_state.event_log_scroll_offset = min(max_scroll, game_state.event_log_scroll_offset + 1)
                        
                        # Safe escape handling - ALWAYS ACTIVE (not blocked by tutorial)
                        elif event.key == pygame.K_ESCAPE:
                            # Safe escape menu system
                            current_time = pygame.time.get_ticks()
                            
                            # Reset escape count if too much time has passed
                            if current_time - escape_timer > ESCAPE_TIMEOUT:
                                escape_count = 0
                            
                            escape_count += 1
                            escape_timer = current_time
                            
                            if escape_count >= ESCAPE_THRESHOLD:
                                # Show quit confirmation after multiple escapes
                                current_state = 'escape_menu'
                                escape_count = 0  # Reset counter
                            else:
                                # First few escapes - show pause/menu hint
                                if hasattr(game_state, 'messages'):
                                    remaining = ESCAPE_THRESHOLD - escape_count
                                    if remaining == 1:
                                        game_state.add_message(f"Press ESCAPE {remaining} more time to access quit menu, or press ENTER to confirm quit")
                                    else:
                                        game_state.add_message(f"Press ESCAPE {remaining} more times to access quit menu")
                                
                                # Play UI sound
                                if game_state and hasattr(game_state, 'sound_manager'):
                                    game_state.sound_manager.play_sound('ui_click')
                        
                        # Handle ENTER to confirm quit when multiple escapes were pressed
                        elif event.key == pygame.K_RETURN and escape_count >= ESCAPE_THRESHOLD - 1:
                            running = False
                        
                        # CRITICAL FIX: End turn handling - HIGHEST PRIORITY for game flow
                        # Check for end turn first to prevent overlay/modal interference
                        elif event.key == pygame.K_SPACE and game_state and not game_state.game_over:
                            # Import keybinding manager for customizable controls
                            from src.services.keybinding_manager import keybinding_manager
                            
                            # Get configured end turn key
                            end_turn_key = keybinding_manager.get_key_for_action("end_turn")
                            
                            # Check if this is the end turn key (space bar is default)
                            if event.key == end_turn_key:
                                # Only block end turn for true modal states
                                blocking_conditions = [
                                    first_time_help_content,  # Help overlay is blocking
                                    game_state.pending_hiring_dialog,  # Hiring dialog is modal
                                    onboarding.show_tutorial_overlay  # Tutorial is active
                                ]
                                
                                if any(blocking_conditions):
                                    # Provide clear feedback about why end turn is blocked
                                    if first_time_help_content:
                                        game_state.add_message("Close the help popup first (ESC or click X)")
                                    elif game_state.pending_hiring_dialog:
                                        game_state.add_message("Close the hiring dialog first (ESC or click outside)")
                                    elif onboarding.show_tutorial_overlay:
                                        game_state.add_message("Complete or skip the tutorial step first")
                                    
                                    if hasattr(game_state, 'sound_manager'):
                                        game_state.sound_manager.play_sound('error_beep')
                                
                                # Check for popup events - allow end turn but give feedback
                                elif (hasattr(game_state, 'pending_popup_events') and game_state.pending_popup_events):
                                    game_state.add_message("Please resolve the pending events before ending turn")
                                    if hasattr(game_state, 'sound_manager'):
                                        game_state.sound_manager.play_sound('error_beep')
                                else:
                                    # Try to end turn - this should work now
                                    if not game_state.end_turn():
                                        # Turn was rejected (already processing or other reason)
                                        pass  # Error feedback already provided by end_turn method
                        
                        # Handle ENTER as alternative end turn key when space is configured
                        elif event.key == pygame.K_RETURN and game_state and not game_state.game_over:
                            from src.services.keybinding_manager import keybinding_manager
                            end_turn_key = keybinding_manager.get_key_for_action("end_turn")
                            
                            # Allow Enter as alternative to space bar for end turn
                            if end_turn_key == pygame.K_SPACE:
                                # Same logic as space bar handling above
                                blocking_conditions = [
                                    first_time_help_content,
                                    game_state.pending_hiring_dialog,
                                    onboarding.show_tutorial_overlay
                                ]
                                
                                if any(blocking_conditions):
                                    if first_time_help_content:
                                        game_state.add_message("Close the help popup first (ESC or click X)")
                                    elif game_state.pending_hiring_dialog:
                                        game_state.add_message("Close the hiring dialog first (ESC or click outside)")
                                    elif onboarding.show_tutorial_overlay:
                                        game_state.add_message("Complete or skip the tutorial step first")
                                    
                                    if hasattr(game_state, 'sound_manager'):
                                        game_state.sound_manager.play_sound('error_beep')
                                
                                elif (hasattr(game_state, 'pending_popup_events') and game_state.pending_popup_events):
                                    game_state.add_message("Please resolve the pending events before ending turn")
                                    if hasattr(game_state, 'sound_manager'):
                                        game_state.sound_manager.play_sound('error_beep')
                                else:
                                    if not game_state.end_turn():
                                        pass
                        
                        # Regular game keyboard handling (only if tutorial is not active)
                        elif not onboarding.show_tutorial_overlay:
                            # Import keybinding manager for customizable controls
                            from src.services.keybinding_manager import keybinding_manager
                            
                            # New 3-column layout keybindings
                            if game_state and not game_state.game_over:
                                # Check if using 3-column layout
                                from src.services.config_manager import get_current_config
                                config = get_current_config()
                                if config.get('enable_three_column_layout', False):
                                    # Import 3-column layout manager
                                    from ui_new.screens.game import three_column_layout
                                    
                                    # Convert pygame key to string
                                    key_name = pygame.key.name(event.key)
                                    
                                    # Handle keypress through layout system
                                    bound_action = three_column_layout.handle_keypress(key_name)
                                    if bound_action:
                                        action_idx = bound_action['original_index']
                                        # Check if this would be an undo operation before calling
                                        was_undo = action_idx in game_state.selected_actions
                                        
                                        # Try to select/deselect the action
                                        game_state.select_action(action_idx, was_undo=was_undo)
                                        continue  # Skip original keybinding system
                            
                            # Action shortcuts using customizable keybindings (fallback)
                            if game_state and not game_state.game_over:
                                # Check if this key is bound to an action
                                for action_index in range(min(9, len(game_state.actions))):
                                    action_key = keybinding_manager.get_action_number_key(action_index)
                                    if action_key and event.key == action_key:
                                        # Check if this would be an undo operation before calling
                                        was_undo = action_index in game_state.selected_actions
                                        
                                        # Try to execute the action using keyboard shortcut
                                        success = game_state.execute_action_by_keyboard(action_index)
                                        if success and not was_undo:
                                            # Play AP spend sound for successful new selections (not undos)
                                            game_state.sound_manager.play_ap_spend_sound()
                                        break
                            
                            # 'H' key for help (Player Guide)
                            elif event.key == pygame.K_h:
                                overlay_content = load_markdown_file('docs/PLAYERGUIDE.md')
                                overlay_title = "Player Guide"
                                overlay_scroll = 0
                                push_navigation_state('overlay')
                            
                            # 'C' key for clearing stuck popup events (UI interaction fix)
                            elif event.key == pygame.K_c and game_state:
                                if game_state.clear_stuck_popup_events():
                                    game_state.add_message("Emergency UI cleanup: Stuck events cleared")
                                else:
                                    game_state.add_message("No stuck popup events found")
                            
                            # 'W' key for window management demo (debug feature)
                            elif event.key == pygame.K_w and current_config.get('advanced', {}).get('enable_demo_window', False):
                                from src.ui.overlay_manager import UIElement, ZLayer
                                
                                # Create a demo window if it doesn't exist
                                demo_window_id = "demo_window"
                                if demo_window_id not in window_manager.elements:
                                    demo_rect = pygame.Rect(200, 150, 300, 200)
                                    demo_element = UIElement(
                                        id=demo_window_id,
                                        layer=ZLayer.DIALOGS,
                                        rect=demo_rect,
                                        title="Demo Window",
                                        content="This is a draggable window!\n\nYou can:\n- Click and drag the header\n- Click minimize button\n- Press W again to close",
                                        draggable=True
                                    )
                                    # Set header area for dragging (top 30 pixels)
                                    demo_element.header_rect = pygame.Rect(demo_rect.x, demo_rect.y, demo_rect.width, 30)
                                    window_manager.register_element(demo_element)
                                else:
                                    # Remove existing window
                                    window_manager.unregister_element(demo_window_id)

            # --- Game state initialization --- #
            # Create game state when entering game for first time
            if current_state == 'game' and game_state is None:
                game_state = GameState(seed)
                
                # Sync sound state from global sound manager to game state
                game_state.sound_manager.set_enabled(global_sound_manager.is_enabled())
                
                # Add intro scenario message if enabled
                if npe_intro_enabled:
                    startup_money = game_state.money  # Get the actual starting money from config
                    intro_message = f"Doom is coming. You convinced a funder to give you ${startup_money:,}. Your job is to save the world. Good luck!"
                    game_state.messages.append(intro_message)
                
                # Check if tutorial should be shown for new players
                if onboarding.should_show_tutorial() and not game_state.onboarding_started:
                    onboarding.start_tutorial()
                    game_state.onboarding_started = True

            # --- UI State Cleanup and Debugging --- #
            # CRITICAL FIX: Automatic cleanup for stuck UI states
            if current_state == 'game' and game_state:
                # Debug key (D) - check for blocking conditions when pressed
                current_keys = pygame.key.get_pressed()
                if current_keys[pygame.K_d] and current_keys[pygame.K_LCTRL]:  # Ctrl+D for debug
                    from ui_interaction_fixes import check_blocking_conditions, test_spacebar
                    blocking = check_blocking_conditions(game_state, onboarding, first_time_help_content, current_state)
                    spacebar_works, reason = test_spacebar(game_state, onboarding, first_time_help_content, current_state)
                    debug_msg = f"DEBUG: Spacebar {'WORKS' if spacebar_works else 'BLOCKED'} - {reason}"
                    if blocking:
                        debug_msg += f" | Blocking: {', '.join(blocking)}"
                    game_state.add_message(debug_msg)
                
                # Automatic cleanup for turn processing that's been stuck too long
                if (hasattr(game_state, 'turn_processing') and game_state.turn_processing and 
                    hasattr(game_state, 'turn_processing_timer') and game_state.turn_processing_timer <= -30):  # 1 second at 30fps
                    game_state.turn_processing = False
                    game_state.turn_processing_timer = 0
                    game_state.add_message("System: Reset stuck turn processing")
                
                # Automatic cleanup for tutorial overlay that's been active too long without interaction
                if (onboarding.show_tutorial_overlay and 
                    game_state.turn > 10):  # If we're past turn 10, tutorial should definitely be dismissible
                    onboarding.show_tutorial_overlay = False
                    game_state.add_message("System: Auto-dismissed stuck tutorial overlay")
                
                # Automatic cleanup for stuck popup events (if they've been pending for too long)
                if (hasattr(game_state, 'pending_popup_events') and game_state.pending_popup_events and
                    game_state.turn > 3):  # If we're past turn 3 and still have popup events, they might be stuck
                    # Allow players to dismiss stuck popup events with Ctrl+E
                    current_keys = pygame.key.get_pressed()
                    if current_keys[pygame.K_e] and current_keys[pygame.K_LCTRL]:  # Ctrl+E to clear stuck popups
                        game_state.pending_popup_events.clear()
                        game_state.add_message("System: Cleared stuck popup events (Ctrl+E)")
                
                # Add recovery for deferred events system too
                if (hasattr(game_state, 'deferred_events') and 
                    hasattr(game_state.deferred_events, 'pending_popup_events') and
                    game_state.deferred_events.pending_popup_events and
                    game_state.turn > 3):
                    current_keys = pygame.key.get_pressed()
                    if current_keys[pygame.K_e] and current_keys[pygame.K_LCTRL]:  # Ctrl+E to clear stuck popups
                        game_state.deferred_events.pending_popup_events.clear()
                        game_state.add_message("System: Cleared stuck deferred popup events (Ctrl+E)")
                
                # Factorio-style hint reset with Ctrl+R
                current_keys = pygame.key.get_pressed()
                if current_keys[pygame.K_r] and current_keys[pygame.K_LCTRL]:  # Ctrl+R to reset hints
                    onboarding.reset_all_hints()
                    game_state.add_message("System: All hints reset! They will show again for new actions (Ctrl+R)")

            # --- First-time help checking --- #
            # Check for pending first-time help triggered by specific actions
            if (current_state == 'game' and game_state and 
                not first_time_help_content and 
                not onboarding.show_tutorial_overlay and
                game_state._pending_first_time_help):
                help_content = onboarding.get_mechanic_help(game_state._pending_first_time_help)
                if help_content and isinstance(help_content, dict) and 'title' in help_content and 'content' in help_content:
                    first_time_help_content = help_content
                    current_help_mechanic = game_state._pending_first_time_help
                    game_state._pending_first_time_help = None  # Clear the pending help
                    # Play popup open sound
                    if game_state and hasattr(game_state, 'sound_manager'):
                        game_state.sound_manager.play_sound('popup_open')
            
            # Check for first-time mechanics and show contextual help (only if tutorial is not active)
            if (current_state == 'game' and game_state and 
                not first_time_help_content and 
                not onboarding.show_tutorial_overlay):
                # Check for various first-time mechanics (but not first_staff_hire - that's context-sensitive)
                for mechanic in ['first_upgrade_purchase', 'high_doom_warning']:
                    if onboarding.should_show_hint(mechanic):
                        help_content = onboarding.get_mechanic_help(mechanic)
                        if help_content and isinstance(help_content, dict) and 'title' in help_content and 'content' in help_content:
                            first_time_help_content = help_content
                            current_help_mechanic = mechanic  # Track which mechanic is showing
                            # Play popup open sound
                            if game_state and hasattr(game_state, 'sound_manager'):
                                game_state.sound_manager.play_sound('popup_open')
                            break
                
                # Special case: action_points_exhausted should only show when actually exhausted
                if (not first_time_help_content and 
                    onboarding.should_show_hint('action_points_exhausted') and 
                    game_state.action_points == 0):
                    help_content = onboarding.get_mechanic_help('action_points_exhausted')
                    if help_content and isinstance(help_content, dict) and 'title' in help_content and 'content' in help_content:
                        first_time_help_content = help_content
                        current_help_mechanic = 'action_points_exhausted'  # Track which mechanic is showing
                        # Play popup open sound
                        if game_state and hasattr(game_state, 'sound_manager'):
                            game_state.sound_manager.play_sound('popup_open')


            # --- Rendering based on current state --- #
            back_button_rect = None  # Initialize for click handling
            
            if current_state == 'main_menu':
                # Grey background as specified in requirements
                screen.fill((128, 128, 128))
                draw_main_menu(screen, SCREEN_W, SCREEN_H, selected_menu_item, global_sound_manager)
            
            elif current_state == 'start_game_submenu':
                # Start game submenu
                draw_start_game_submenu(screen, SCREEN_W, SCREEN_H, start_game_submenu_selected_item)
            
            elif current_state == 'config_select':
                # Config selection menu
                screen.fill((64, 64, 64))
                from ui import draw_config_menu
                draw_config_menu(screen, SCREEN_W, SCREEN_H, config_selected_item, 
                               available_configs, config_manager.get_current_config_name())
            
            elif current_state == 'pre_game_settings':
                # Pre-game settings screen
                screen.fill((50, 50, 50))
                draw_pre_game_settings(screen, SCREEN_W, SCREEN_H, pre_game_settings, selected_settings_item, global_sound_manager)
            
            elif current_state == 'seed_selection':
                # Seed selection screen
                screen.fill((50, 50, 50))
                draw_seed_selection(screen, SCREEN_W, SCREEN_H, 0, seed_input, global_sound_manager)  # Selected item handling can be improved
            
            elif current_state == 'tutorial_choice':
                # Tutorial choice screen
                screen.fill((50, 50, 50))
                draw_tutorial_choice(screen, SCREEN_W, SCREEN_H, tutorial_choice_selected_item)
            
            elif current_state == 'new_player_experience':
                # New player experience screen
                screen.fill((50, 50, 50))
                draw_new_player_experience(screen, SCREEN_W, SCREEN_H, npe_selected_item, npe_tutorial_enabled, npe_intro_enabled)
            
            elif current_state == 'sounds_menu':
                # Audio settings menu
                screen.fill((40, 45, 55))
                draw_audio_menu(screen, SCREEN_W, SCREEN_H, sounds_menu_selected_item, audio_settings, global_sound_manager)
                
            elif current_state == 'keybinding_menu':
                # Keybinding configuration menu
                screen.fill((20, 25, 35))
                keybinding_all_bindings = draw_keybinding_menu(screen, SCREEN_W, SCREEN_H, keybinding_menu_selected_item)
                
            elif current_state == 'keybinding_change':
                # Keybinding change prompt
                screen.fill((20, 25, 35))
                keybinding_all_bindings = draw_keybinding_menu(screen, SCREEN_W, SCREEN_H, keybinding_menu_selected_item)
                draw_keybinding_change_prompt(screen, SCREEN_W, SCREEN_H, keybinding_change_display, keybinding_change_action)
                
            elif current_state == 'custom_seed_prompt':
                # Preserve original seed prompt appearance
                screen.fill((32, 32, 44))
                draw_seed_prompt(screen, seed_input, get_weekly_seed())
                
            elif current_state == 'overlay':
                # Dark background for documentation overlay
                screen.fill((40, 40, 50))
                back_button_rect = draw_overlay(screen, overlay_title, overlay_content, overlay_scroll, SCREEN_W, SCREEN_H, get_navigation_depth())
                
            elif current_state == 'bug_report':
                # Bug report form
                draw_bug_report_form(screen, bug_report_data, bug_report_selected_field, SCREEN_W, SCREEN_H)
                
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

            elif current_state == 'escape_menu':
                # Draw the game in background (dimmed)
                screen.fill((25, 25, 35))
                if game_state:
                    ui_facade.render_game(screen, game_state, SCREEN_W, SCREEN_H)
                    
                # Draw dark overlay
                overlay = pygame.Surface((SCREEN_W, SCREEN_H))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(128)
                screen.blit(overlay, (0, 0))
                
                # Draw escape menu
                draw_escape_menu(screen, SCREEN_W, SCREEN_H)

                
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
                        game_state.update_turn_processing()  # Handle turn transition timing
                        game_state.overlay_manager.update_animations()
                    
                    ui_facade.render_game(screen, game_state, SCREEN_W, SCREEN_H)
                    
                    # Render overlay manager elements
                    if game_state:
                        game_state.overlay_manager.render_elements(screen)
                    
                    # Render window manager elements
                    for layer in window_manager.z_order:
                        for element_id in window_manager.z_order[layer]:
                            element = window_manager.elements[element_id]
                            if element.visible:
                                from ui import draw_window_with_header
                                header_rect, minimize_rect = draw_window_with_header(
                                    screen, element.rect, element.title, element.content, 
                                    element.state.value == 'minimized'
                                )
                                # Update header rect for dragging
                                element.header_rect = header_rect
                    
                    if tooltip_text:
                        draw_tooltip(screen, tooltip_text, pygame.mouse.get_pos(), SCREEN_W, SCREEN_H)
                    
                    # Draw hiring dialog if active
                    if game_state and game_state.pending_hiring_dialog:
                        from ui import draw_hiring_dialog
                        cached_hiring_dialog_rects = draw_hiring_dialog(screen, game_state.pending_hiring_dialog, SCREEN_W, SCREEN_H)
                    else:
                        # Clear cached rects when dialog is not active
                        cached_hiring_dialog_rects = None
                    

                    # Draw stepwise tutorial overlay if active
                    if onboarding.show_tutorial_overlay:
                        tutorial_data = onboarding.get_current_stepwise_tutorial_data()
                        if tutorial_data:
                            draw_stepwise_tutorial_overlay(screen, tutorial_data, SCREEN_W, SCREEN_H)
                    
                    # Draw first-time help if available (but not when other dialogs are active)
                    if (first_time_help_content and isinstance(first_time_help_content, dict) and
                        not (game_state and game_state.pending_hiring_dialog)):
                        mouse_pos = pygame.mouse.get_pos()
                        first_time_help_close_button = draw_first_time_help(screen, first_time_help_content, SCREEN_W, SCREEN_H, mouse_pos)
                        # If drawing failed (returned None), clear the help content to prevent repeated attempts
                        if first_time_help_close_button is None:
                            first_time_help_content = None
                    
                    # Draw turn transition overlay if processing
                    if game_state and game_state.turn_processing:
                        draw_turn_transition_overlay(screen, SCREEN_W, SCREEN_H, game_state.turn_processing_timer, game_state.turn_processing_duration)

                        
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
                game_state.logger.write_log_file()
                # print(f"Game crashed, but log saved to: {log_path}")
            except Exception:
                # print("Game crashed and could not save log")
                pass
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
                game_state.logger.write_log_file()
                # print(f"Game log saved to: {log_path}")
            except Exception:
                pass
        pygame.quit()

if __name__ == "__main__":
    main()
