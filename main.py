import sys
import pygame
from src.services.deterministic_rng import get_rng
import json
from src.core.game_state import GameState
from src.services.game_state_manager import get_game_state_manager

from ui import draw_seed_prompt, draw_bug_report_form, draw_bug_report_success, draw_end_game_menu, draw_first_time_help, draw_pre_game_settings, draw_seed_selection, draw_tutorial_choice, draw_new_player_experience, draw_popup_events, draw_turn_transition_overlay, draw_audio_menu, draw_high_score_screen, draw_ui
from src.ui.menus import draw_main_menu
from src.ui.tutorials import draw_stepwise_tutorial_overlay
from src.ui.menus import draw_start_game_submenu
from src.ui.layout import draw_overlay
from src.ui.components import draw_tooltip, draw_loading_screen
from src.ui.keybinding_menu import draw_keybinding_menu, draw_keybinding_change_prompt, get_keybinding_menu_click_item
from src.ui.enhanced_settings import draw_settings_main_menu
from src.ui.privacy_controls import privacy_controls

from src.ui.overlay_manager import OverlayManager
from src.services.bug_reporter import BugReporter
from src.services.version import get_display_version
from src.features.onboarding import onboarding
from src.services.config_manager import initialize_config_system, get_current_config, config_manager
from src.services.sound_manager import SoundManager
from src.ui.pre_game_settings import pre_game_settings_manager

# Import new input management system
from src.core.input_event_manager import InputEventManager, KeyEventResult
from src.core.dialog_state_manager import DialogStateManager

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

# Check for dev mode
def is_dev_mode_enabled():
    """Check if dev mode is enabled from dev_mode.json"""
    try:
        with open('dev_mode.json', 'r') as f:
            dev_config = json.load(f)
            return dev_config.get('dev_mode_enabled', False)
    except (FileNotFoundError, json.JSONDecodeError):
        return False

def is_verbose_logging_enabled():
    """Check if verbose logging is enabled from dev_mode.json"""
    try:
        with open('dev_mode.json', 'r') as f:
            dev_config = json.load(f)
            return dev_config.get('verbose_logging_enabled', False)
    except (FileNotFoundError, json.JSONDecodeError):
        return False

def log_shutdown(reason="User exit"):
    """Log shutdown information when dev mode is enabled"""
    if is_verbose_logging_enabled():
        print("=" * 80)
        print(f"[SHUTDOWN] P(Doom) {get_display_version()} shutting down")
        print(f"[SHUTDOWN] Reason: {reason}")
        print(f"[SHUTDOWN] Pygame version: {pygame.version.ver}")
        print(f"[SHUTDOWN] Thank you for playing!")
        print("=" * 80)
    elif is_dev_mode_enabled():
        print(f"[DEV] P(Doom) {get_display_version()} shutting down - {reason}")
    else:
        print(f"P(Doom) {get_display_version()} - Thanks for playing!")

# --- Adaptive window sizing with loading screen --- #
pygame.init()

# Enhanced startup information with dev mode support
dev_mode = is_dev_mode_enabled()
verbose_logging = is_verbose_logging_enabled()

print(f"Starting P(Doom): Bureaucracy Strategy Game {get_display_version()}")
print("=" * 80)

if dev_mode:
    print("[DEV MODE] Development mode enabled")
    if verbose_logging:
        print("[VERBOSE] Verbose logging enabled")

print("STARTUP CONFIGURATION:")
print(f"  Version: {get_display_version()}")

if verbose_logging:
    from src.services.version import get_version_info
    version_info = get_version_info() 
    print(f"  Full Version Info: {version_info}")
    print(f"  Python Version: {sys.version}")
    print(f"  Pygame Version: {pygame.version.ver}")

print(f"  Economic Model: Bootstrap AI Safety Nonprofit")
print(f"  Starting Funds: $100k")
print(f"  Staff Maintenance: $600 first, $800 additional/week") 
print(f"  Research Costs: $3k/week (reduced from $40k)")
print(f"  Hiring Costs: $0 (no signing bonuses)")
print(f"  Moore's Law: 2% compute cost reduction/week")
print(f"  Audio: {'Enabled' if current_config['audio']['sound_enabled'] else 'Disabled'}")
print(f"  Window Scale: {current_config['ui']['window_scale']:.1f}x")
print(f"  Fullscreen: {'Yes' if current_config['ui'].get('fullscreen', False) else 'No'}")

if verbose_logging:
    print(f"  Config Directory: {config_manager.CONFIG_DIR}")
    print(f"  Current Config: {config_manager.current_config_name}")
    try:
        available_configs = config_manager.list_available_configs()
        print(f"  Available Configs: {', '.join(available_configs)}")
    except Exception:
        print(f"  Available Configs: [Error loading config list]")

print("=" * 80)

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
# Menu states: 'main_menu', 'custom_seed_prompt', 'config_select', 'pre_game_settings', 'seed_selection', 'tutorial_choice', 'game', 'overlay', 'bug_report', 'bug_report_success', 'end_game_menu', 'tutorial', 'sounds_menu', 'keybinding_menu', 'keybinding_change', 'leaderboard', 'settings_menu', 'privacy_controls'

# Panel stack tracking for navigation depth
navigation_stack = []
current_state = 'main_menu'
game_state = None  # Global game state variable
selected_menu_item = 0  # For keyboard navigation
# Main menu: Primary actions first, then secondary, exit last
menu_items = ["Launch Lab", "Launch with Custom Seed", "Player Guide", "View Leaderboard", "Settings", "Exit"]
# Start game submenu: Quick start first, then configuration options
start_game_submenu_items = ["Basic New Game (Default Global Seed)", "Configure Game / Custom Seed", "Config Settings", "Game Options"]
start_game_submenu_selected_item = 0  # For start game submenu navigation
# End game menu: Primary actions first (continue playing), then meta actions
end_game_menu_items = ["Play Again", "View Full Leaderboard", "Submit Feedback", "Settings", "Main Menu"]
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
    "safety_level": "STANDARD",
    "player_name": "Anonymous",
    "lab_name": ""  # Will be auto-generated if left empty
}
selected_settings_item = 0
seed_choice = "weekly"  # "weekly" or "custom"
tutorial_enabled = False  # Default to no tutorial

# Text input for name fields - managed by pre_game_settings_manager

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

# Settings menu state
settings_menu_selected_item = 0
privacy_controls_selected_item = 0

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


def handle_game_keyboard_input(event, game_state, onboarding_manager, 
                             first_time_help_content, current_help_mechanic, 
                             overlay_content, overlay_title, current_state,
                             escape_count, escape_timer, running):
    """
    Handle keyboard input for the main game using the new Input Event Manager.
    
    This replaces the massive keyboard handling section in main() with a clean,
    testable interface using the extracted InputEventManager and DialogStateManager.
    
    Args:
        event: pygame keyboard event
        game_state: Current game state
        onboarding_manager: Tutorial/onboarding system
        first_time_help_content: Current help popup content
        current_help_mechanic: Current help mechanic being shown
        overlay_content: Current overlay content
        overlay_title: Current overlay title  
        current_state: Current game state string
        escape_count: Current escape key count
        escape_timer: Current escape timer
        running: Current running state
        
    Returns:
        Tuple of (updated_values_dict, should_quit, key_consumed)
    """
    # Initialize managers if not already done
    if not hasattr(game_state, '_input_manager'):
        game_state._input_manager = InputEventManager(game_state)
        game_state._dialog_manager = DialogStateManager(game_state)
    
    # Create overlay handlers dictionary for the input manager
    overlay_handlers = {
        'load_markdown_file': load_markdown_file,
        'push_navigation_state': lambda state: None,  # This will be handled by caller
        'overlay_content': overlay_content,
        'overlay_title': overlay_title,
        'current_state': current_state,
        'first_time_help_content': first_time_help_content,
        'first_time_help_close_button': None,
        'current_help_mechanic': current_help_mechanic,
        'onboarding': onboarding_manager
    }
    
    # Handle the keyboard event using the InputEventManager
    result = game_state._input_manager.handle_keydown_event(
        event, first_time_help_content, onboarding_manager, overlay_handlers
    )
    
    # Prepare return values
    updated_values = {}
    should_quit = False
    key_consumed = (result != KeyEventResult.NOT_HANDLED)
    
    # Handle special cases that need to update main loop state
    if result == KeyEventResult.CONSUMED:
        # Update overlay state if help key was pressed
        if event.key == pygame.K_h:
            updated_values['overlay_content'] = overlay_handlers.get('overlay_content')
            updated_values['overlay_title'] = overlay_handlers.get('overlay_title')
            updated_values['push_navigation_state'] = 'overlay'
        
        # Update state if menu key was pressed
        if event.key == pygame.K_m:
            updated_values['current_state'] = overlay_handlers.get('current_state')
        
        # Update help state if help popup was handled
        if first_time_help_content and event.key in [pygame.K_ESCAPE, pygame.K_RETURN]:
            updated_values['first_time_help_content'] = overlay_handlers.get('first_time_help_content')
            updated_values['first_time_help_close_button'] = overlay_handlers.get('first_time_help_close_button')
            updated_values['current_help_mechanic'] = overlay_handlers.get('current_help_mechanic')
        
        # Handle escape menu and quit logic
        if game_state._input_manager.should_show_escape_menu():
            updated_values['current_state'] = 'escape_menu'
        
        if game_state._input_manager.should_quit_game():
            should_quit = True
    
    return updated_values, should_quit, key_consumed

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
    
    # Extract mouse coordinates for sound button handler
    mx, my = mouse_pos
    
    # Use unified menu helper for collision detection
    from src.ui.menu_helpers import get_menu_button_collision
    clicked_item = get_menu_button_collision(mouse_pos, menu_items, w, h)
    
    if clicked_item is not None:
        i = clicked_item
        selected_menu_item = i
        
        # Execute menu action based on selection (updated for new order)
        if i == 0:  # Launch Lab
            current_state = 'start_game_submenu'
        elif i == 1:  # Launch with Custom Seed
            current_state = 'custom_seed_prompt'
            seed_input = ""  # Clear any previous input
        elif i == 2:  # Player Guide
            overlay_content = load_markdown_file('docs/PLAYERGUIDE.md')
            overlay_title = "Player Guide"
            push_navigation_state('overlay')
        elif i == 3:  # View Leaderboard
            # Go directly to leaderboard screen with default seed
            current_state = 'high_score'
            high_score_selected_item = 0  # Reset selection
            # Set a default seed for leaderboard viewing if none exists
            if seed is None:
                seed = get_weekly_seed()  # Use the default weekly seed
        elif i == 4:  # Settings
            current_state = 'settings_menu'
        elif i == 5:  # Exit
            log_shutdown("Main menu exit")
            pygame.quit()
            sys.exit()
    
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
        if selected_menu_item == 0:  # Launch Lab
            current_state = 'start_game_submenu'
        elif selected_menu_item == 1:  # Launch with Custom Seed
            current_state = 'custom_seed_prompt'
            seed_input = ""  # Clear any previous input
        elif selected_menu_item == 2:  # Player Guide
            overlay_content = load_markdown_file('docs/PLAYERGUIDE.md')
            overlay_title = "Player Guide"
            push_navigation_state('overlay')
        elif selected_menu_item == 3:  # View Leaderboard
            # Go directly to leaderboard screen with default seed
            current_state = 'high_score'
            high_score_selected_item = 0  # Reset selection
            # Set a default seed for leaderboard viewing if none exists
            if seed is None:
                seed = get_weekly_seed()  # Use the default weekly seed
        elif selected_menu_item == 4:  # Settings
            current_state = 'settings_menu'
        elif selected_menu_item == 5:  # Exit
            log_shutdown("Menu keyboard exit")
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
                current_state = 'pre_game_settings'  # Go to lab config screen first
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
            current_state = 'pre_game_settings'  # Go to lab config screen first
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
    
    # Check for random lab name button first
    if pre_game_settings_manager.handle_random_lab_name_click(mouse_pos, w, h, pre_game_settings):
        return  # Handled by the manager
    
    # Calculate button positions (must match draw_pre_game_settings layout)
    button_width = int(w * 0.55)
    button_height = int(h * 0.07)
    start_y = int(h * 0.32)
    spacing = int(h * 0.085)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    # Settings items (1 continue button + 2 name fields + 4 settings = 7 total)
    num_items = 7
    
    for i in range(num_items):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            selected_settings_item = i
            
            if i == 0:  # Continue button (now first)
                # If seed is already set (from Basic New Game), skip seed selection
                if seed is not None:
                    current_state = 'tutorial_choice'
                else:
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
    
    # Handle text input mode first
    if pre_game_settings_manager.is_text_input_active():
        if key == pygame.K_RETURN:
            # Exit text input mode
            pre_game_settings_manager.deactivate_text_input()
        elif key == pygame.K_ESCAPE:
            # Cancel text input, revert changes
            pre_game_settings_manager.deactivate_text_input()
        elif key == pygame.K_BACKSPACE:
            # Handle backspace (clear selected text or remove character)
            pre_game_settings_manager.handle_backspace(pre_game_settings)
        # Other text input will be handled by TEXTINPUT event
        return
    
    # Normal navigation mode
    if key == pygame.K_UP:
        selected_settings_item = (selected_settings_item - 1) % 7  # Updated for 2 new name fields
    elif key == pygame.K_DOWN:
        selected_settings_item = (selected_settings_item + 1) % 7  # Updated for 2 new name fields
    elif key == pygame.K_RETURN:
        if selected_settings_item == 0:  # Continue button (first item)
            # Always go to seed selection to allow user choice
            # The seed selection screen can handle pre-set seeds appropriately
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
    pre_game_settings_manager.cycle_setting_value(setting_index, pre_game_settings, reverse)


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
            from src.services.deterministic_rng import init_deterministic_rng
            init_deterministic_rng(seed)
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
        from src.services.deterministic_rng import init_deterministic_rng
        init_deterministic_rng(seed)
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
        from src.services.deterministic_rng import init_deterministic_rng
        init_deterministic_rng(seed)
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
            from src.services.deterministic_rng import init_deterministic_rng
            init_deterministic_rng(seed)
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
            elif i == 5:  # Back to Settings Menu
                current_state = 'settings_menu'
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
        elif sounds_menu_selected_item == 5:  # Back to Settings Menu
            current_state = 'settings_menu'
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
        current_state = 'settings_menu'


def handle_settings_menu_click(mouse_pos, w, h):
    """Handle mouse clicks on main settings menu."""
    global current_state, settings_menu_selected_item
    
    # Menu item layout (matching draw_settings_main_menu)
    button_width = int(w * 0.65)
    button_height = int(h * 0.07)
    start_y = int(h * 0.25)
    spacing = int(h * 0.08)
    center_x = w // 2
    
    mx, my = mouse_pos
    
    # Settings menu items (matching enhanced_settings.py)
    settings_categories = [
        "Audio Settings",
        "Game Configuration", 
        "Gameplay Settings",
        "Accessibility",
        "Keybindings",
        "Privacy Controls",  # Our new option
        "Back to Main Menu"
    ]
    
    for i, _ in enumerate(settings_categories):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            settings_menu_selected_item = i
            
            # Execute selected menu action
            if i == 0:  # Audio Settings
                current_state = 'sounds_menu'
                sounds_menu_selected_item = 0
            elif i == 1:  # Game Configuration
                # TODO: Implement game config menu
                pass
            elif i == 2:  # Gameplay Settings
                # TODO: Implement gameplay settings
                pass
            elif i == 3:  # Accessibility
                # TODO: Implement accessibility settings
                pass
            elif i == 4:  # Keybindings
                current_state = 'keybinding_menu'
                keybinding_menu_selected_item = 0
            elif i == 5:  # Privacy Controls
                current_state = 'privacy_controls'
                privacy_controls.reset()
            elif i == 6:  # Back to Main Menu
                current_state = 'main_menu'
            break


def handle_settings_menu_keyboard(key):
    """Handle keyboard navigation for main settings menu."""
    global current_state, settings_menu_selected_item
    
    menu_items_count = 7  # Number of menu items
    
    if key == pygame.K_UP:
        settings_menu_selected_item = (settings_menu_selected_item - 1) % menu_items_count
    elif key == pygame.K_DOWN:
        settings_menu_selected_item = (settings_menu_selected_item + 1) % menu_items_count
    elif key == pygame.K_RETURN or key == pygame.K_SPACE:
        # Execute selected menu action
        if settings_menu_selected_item == 0:  # Audio Settings
            current_state = 'sounds_menu'
            sounds_menu_selected_item = 0
        elif settings_menu_selected_item == 1:  # Game Configuration
            # TODO: Implement game config menu
            pass
        elif settings_menu_selected_item == 2:  # Gameplay Settings
            # TODO: Implement gameplay settings
            pass
        elif settings_menu_selected_item == 3:  # Accessibility
            # TODO: Implement accessibility settings
            pass
        elif settings_menu_selected_item == 4:  # Keybindings
            current_state = 'keybinding_menu'
            keybinding_menu_selected_item = 0
        elif settings_menu_selected_item == 5:  # Privacy Controls
            current_state = 'privacy_controls'
            privacy_controls.reset()
        elif settings_menu_selected_item == 6:  # Back to Main Menu
            current_state = 'main_menu'
    elif key == pygame.K_ESCAPE:
        current_state = 'main_menu'


def handle_privacy_controls_click(mouse_pos, w, h):
    """Handle mouse clicks on privacy controls menu."""
    global current_state
    
    # Delegate to privacy controls component
    action = privacy_controls.handle_mouse_click(mouse_pos, w, h)
    
    if action == "back":
        current_state = 'settings_menu'
    elif action == "level_changed":
        # Optionally show a confirmation message
        pass
    elif action == "data_deleted":
        # Optionally show a success message
        pass


def handle_privacy_controls_keyboard(key):
    """Handle keyboard navigation for privacy controls menu."""
    global current_state
    
    # Delegate to privacy controls component
    action = privacy_controls.handle_key_press(key)
    
    if action == "back":
        current_state = 'settings_menu'
    elif action == "level_changed":
        # Optionally show a confirmation message
        pass
    elif action == "data_deleted":
        # Optionally show a success message
        pass


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
        current_state = 'settings_menu'  # Go back to settings menu


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
            
            # Execute menu action based on selection (updated for new order)
            if i == 0:  # Play Again - PRIMARY ACTION for continuing play
                # Use Game State Manager for clean restart (End Game State Reset Bug fix)
                game_state_manager = get_game_state_manager()
                game_state = game_state_manager.restart_game_with_same_seed()
                current_state = 'game'
            elif i == 1:  # View Full Leaderboard
                current_state = 'high_score'
                high_score_selected_item = 0  # Reset high score selection
            elif i == 2:  # Submit Feedback (simplified menu)
                # Reset and pre-fill feedback form
                reset_bug_report_form()
                bug_report_data["type_index"] = 2  # Feedback
                current_state = 'bug_report'
            elif i == 3:  # Settings
                overlay_content = create_settings_content()
                overlay_title = "Settings"
                push_navigation_state('overlay')
            elif i == 4:  # Main Menu
                _flush_game_state()  # Clear game state to prevent end game loop
                current_state = 'main_menu'
                selected_menu_item = 0
            break

def handle_end_game_menu_keyboard(key):
    """Handle keyboard navigation for end-game menu with both horizontal and vertical support."""
    global end_game_selected_item, current_state, selected_menu_item, overlay_content, overlay_title
    
    # Support both vertical (UP/DOWN) and horizontal (LEFT/RIGHT) navigation
    # This handles both horizontal and vertical button layouts
    if key == pygame.K_UP or key == pygame.K_LEFT:
        end_game_selected_item = (end_game_selected_item - 1) % len(end_game_menu_items)
    elif key == pygame.K_DOWN or key == pygame.K_RIGHT:
        end_game_selected_item = (end_game_selected_item + 1) % len(end_game_menu_items)
    elif key == pygame.K_RETURN or key == pygame.K_SPACE:
        # Execute selected menu action (updated for new order)
        if end_game_selected_item == 0:  # Play Again - PRIMARY ACTION
            current_state = 'game'
        elif end_game_selected_item == 1:  # View Full Leaderboard
            current_state = 'high_score'
        elif end_game_selected_item == 2:  # Submit Feedback
            reset_bug_report_form()
            bug_report_data["type_index"] = 2  # Feedback
            current_state = 'bug_report'
        elif end_game_selected_item == 3:  # Settings
            overlay_content = create_settings_content()
            overlay_title = "Settings"
            push_navigation_state('overlay')
        elif end_game_selected_item == 4:  # Main Menu
            _flush_game_state()  # Clear game state to prevent end game loop
            current_state = 'main_menu'
            selected_menu_item = 0
    elif key == pygame.K_ESCAPE:
        # Return to main menu
        _flush_game_state()  # Clear game state to prevent end game loop
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
    """Handle mouse clicks on high score screen with interactive menu."""
    global current_state, selected_menu_item, high_score_selected_item, high_score_submit_to_leaderboard, game_state
    
    # Menu items count for button layout (text is dynamic: "Play Again" or "Launch New Game")
    MENU_ITEM_COUNT = 5  # Total number of buttons
    
    # Button layout matching the UI
    button_width = int(w * 0.4)
    button_height = int(h * 0.06)
    start_y = int(h * 0.52)
    
    mx, my = mouse_pos
    
    # Check each menu button
    for i in range(MENU_ITEM_COUNT):
        y = start_y + i * int(button_height + h * 0.02)
        x = w // 2 - button_width // 2
        button_rect = pygame.Rect(x, y, button_width, button_height)
        
        if button_rect.collidepoint(mx, my):
            high_score_selected_item = i  # Update selection
            # Execute the selected action
            _execute_high_score_menu_action(i)
            return

def handle_high_score_keyboard(key):
    """Handle keyboard navigation for high score screen with interactive menu."""
    global current_state, selected_menu_item, high_score_selected_item, high_score_submit_to_leaderboard, game_state
    
    # Menu items count for navigation (text is dynamic: "Play Again" or "Launch New Game")
    MENU_ITEM_COUNT = 5  # Total number of buttons
    
    if key == pygame.K_UP:
        high_score_selected_item = (high_score_selected_item - 1) % MENU_ITEM_COUNT
    elif key == pygame.K_DOWN:
        high_score_selected_item = (high_score_selected_item + 1) % MENU_ITEM_COUNT
    elif key == pygame.K_RETURN or key == pygame.K_SPACE:
        _execute_high_score_menu_action(high_score_selected_item)
    elif key == pygame.K_ESCAPE:
        # Quick exit to main menu
        _flush_game_state()
        current_state = 'main_menu'
        selected_menu_item = 0

def _execute_high_score_menu_action(action_index):
    """Execute the selected menu action from the high score screen."""
    global current_state, selected_menu_item, high_score_selected_item, game_state
    
    # Note: Menu items are dynamic - first item is "Play Again" or "Launch New Game" based on context
    # Actions remain the same regardless of button text
    
    if action_index == 0:  # Play Again / Launch New Game - go to seed selection (pre-game)
        _flush_game_state()
        current_state = 'seed_selection'
        selected_menu_item = 0
    elif action_index == 1:  # Main Menu
        _flush_game_state()
        current_state = 'main_menu'
        selected_menu_item = 0
    elif action_index == 2:  # Settings
        current_state = 'sounds_menu'  # Could be settings menu if available
        selected_menu_item = 0
    elif action_index == 3:  # Submit Feedback
        current_state = 'bug_report'
        selected_menu_item = 0
    elif action_index == 4:  # View Full Leaderboard (same screen, different focus)
        # Stay on the same screen but maybe scroll to leaderboard section
        pass

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
    global end_game_selected_item, high_score_submit_to_leaderboard, game_state
    global first_time_help_content, first_time_help_close_button, current_help_mechanic
    # UI overlay variables need global declaration to prevent UnboundLocalError when referenced before assignment
    global first_time_help_content, first_time_help_close_button, current_tutorial_content, current_help_mechanic
    global overlay_content, overlay_title
    # Hiring dialog rects need to persist between frames for click detection
    global cached_hiring_dialog_rects
    # Fundraising dialog rects need to persist between frames for click detection 
    global cached_fundraising_dialog_rects
    # Research dialog rects need to persist between frames for click detection
    global cached_research_dialog_rects  
    # Keybinding menu variables
    global keybinding_all_bindings
    # Escape handling variables
    global escape_count, escape_timer
    
    # Game state is initialized globally
    tooltip_text = None
    # Initialize cached hiring dialog rects
    cached_hiring_dialog_rects = None
    # Initialize cached fundraising dialog rects
    cached_fundraising_dialog_rects = None
    # Initialize cached research dialog rects
    cached_research_dialog_rects = None
    # Initialize cached intelligence dialog rects
    cached_intelligence_dialog_rects = None
    # Initialize cached media dialog rects
    cached_media_dialog_rects = None
    # Initialize cached technical debt dialog rects
    cached_technical_debt_dialog_rects = None

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
                    elif current_state == 'overlay':
                        # Handle mouse wheel scrolling for overlay content
                        if event.y > 0:  # Mouse wheel up - scroll up
                            overlay_scroll = max(0, overlay_scroll - 30)
                        elif event.y < 0:  # Mouse wheel down - scroll down
                            overlay_scroll += 30
                    elif current_state in ['main_menu', 'start_game_submenu', 'end_game_menu', 'sounds_menu', 'settings_menu']:
                        # Unified mouse wheel menu navigation
                        if event.y > 0:  # Mouse wheel up - move selection up
                            if current_state == 'main_menu':
                                selected_menu_item = (selected_menu_item - 1) % len(menu_items)
                            elif current_state == 'start_game_submenu':
                                selected_menu_item = (selected_menu_item - 1) % len(start_game_submenu_items)
                            elif current_state == 'end_game_menu':
                                selected_menu_item = (selected_menu_item - 1) % len(end_game_menu_items)
                            elif current_state == 'sounds_menu':
                                selected_menu_item = (selected_menu_item - 1) % 6  # Audio menu has 6 items
                            elif current_state == 'settings_menu':
                                selected_menu_item = (selected_menu_item - 1) % 7  # Settings menu has 7 items
                        elif event.y < 0:  # Mouse wheel down - move selection down
                            if current_state == 'main_menu':
                                selected_menu_item = (selected_menu_item + 1) % len(menu_items)
                            elif current_state == 'start_game_submenu':
                                selected_menu_item = (selected_menu_item + 1) % len(start_game_submenu_items)
                            elif current_state == 'end_game_menu':
                                selected_menu_item = (selected_menu_item + 1) % len(end_game_menu_items)
                            elif current_state == 'sounds_menu':
                                selected_menu_item = (selected_menu_item + 1) % 6  # Audio menu has 6 items
                            elif current_state == 'settings_menu':
                                selected_menu_item = (selected_menu_item + 1) % 7  # Settings menu has 7 items
                    # Always continue - don't let unhandled wheel events cause issues
                    continue
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Skip mouse wheel button events (buttons 4 and 5) to prevent wheel clicks
                    if event.button in [4, 5]:  # Mouse wheel up/down as button events
                        continue
                    
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
                    elif current_state == 'settings_menu':
                        handle_settings_menu_click((mx, my), SCREEN_W, SCREEN_H)
                    elif current_state == 'privacy_controls':
                        handle_privacy_controls_click((mx, my), SCREEN_W, SCREEN_H)
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
                            # Check for intelligence dialog clicks
                            elif game_state and game_state.pending_intelligence_dialog and cached_intelligence_dialog_rects is not None:
                                intelligence_handled = False
                                for rect_info in cached_intelligence_dialog_rects:
                                    if rect_info['rect'].collidepoint(mx, my):
                                        if rect_info['type'] == 'intelligence_option':
                                            # Player selected an intelligence option
                                            game_state.select_intelligence_option(rect_info['option_id'])
                                            intelligence_handled = True
                                            break
                                        elif rect_info['type'] == 'cancel':
                                            # Player cancelled the intelligence dialog
                                            game_state.dismiss_intelligence_dialog()
                                            intelligence_handled = True
                                            break
                                
                                if intelligence_handled:
                                    pass  # Intelligence dialog handled the click
                                else:
                                    # When intelligence dialog is open, check if click is inside dialog area
                                    dialog_width = int(SCREEN_W * 0.7)
                                    dialog_height = int(SCREEN_H * 0.6)
                                    dialog_x = (SCREEN_W - dialog_width) // 2
                                    dialog_y = (SCREEN_H - dialog_height) // 2
                                    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
                                    
                                    if dialog_rect.collidepoint(mx, my):
                                        # Click is inside dialog area but not on a button - do nothing (modal behavior)
                                        pass
                                    else:
                                        # Click is outside dialog area - dismiss the dialog
                                        game_state.dismiss_intelligence_dialog()
                                        if hasattr(game_state, 'sound_manager'):
                                            game_state.sound_manager.play_sound('popup_close')
                            # Check for media dialog clicks
                            elif game_state and game_state.pending_media_dialog and cached_media_dialog_rects is not None:
                                media_handled = False
                                for rect_info in cached_media_dialog_rects:
                                    if rect_info['rect'].collidepoint(mx, my):
                                        if rect_info['type'] == 'media_option':
                                            # Player selected a media option
                                            game_state.select_media_option(rect_info['option_id'])
                                            media_handled = True
                                            break
                                        elif rect_info['type'] == 'cancel':
                                            # Player cancelled the media dialog
                                            game_state.dismiss_media_dialog()
                                            media_handled = True
                                            break
                                
                                if media_handled:
                                    pass  # Media dialog handled the click
                                else:
                                    # When media dialog is open, check if click is inside dialog area
                                    dialog_width = int(SCREEN_W * 0.7)
                                    dialog_height = int(SCREEN_H * 0.6)
                                    dialog_x = (SCREEN_W - dialog_width) // 2
                                    dialog_y = (SCREEN_H - dialog_height) // 2
                                    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
                                    
                                    if dialog_rect.collidepoint(mx, my):
                                        # Click is inside dialog area but not on a button - do nothing (modal behavior)
                                        pass
                                    else:
                                        # Click is outside dialog area - dismiss the dialog
                                        game_state.dismiss_media_dialog()
                                        if hasattr(game_state, 'sound_manager'):
                                            game_state.sound_manager.play_sound('popup_close')
                            # Check for technical debt dialog clicks
                            elif game_state and game_state.pending_technical_debt_dialog and cached_technical_debt_dialog_rects is not None:
                                technical_debt_handled = False
                                for rect_info in cached_technical_debt_dialog_rects:
                                    if rect_info['rect'].collidepoint(mx, my):
                                        if rect_info['type'] == 'technical_debt_option':
                                            # Player selected a technical debt option
                                            game_state.select_technical_debt_option(rect_info['option_id'])
                                            technical_debt_handled = True
                                            break
                                        elif rect_info['type'] == 'cancel':
                                            # Player cancelled the technical debt dialog
                                            game_state.dismiss_technical_debt_dialog()
                                            technical_debt_handled = True
                                            break
                                
                                if technical_debt_handled:
                                    pass  # Technical debt dialog handled the click
                                else:
                                    # When technical debt dialog is open, check if click is inside dialog area
                                    dialog_width = int(SCREEN_W * 0.7)
                                    dialog_height = int(SCREEN_H * 0.6)
                                    dialog_x = (SCREEN_W - dialog_width) // 2
                                    dialog_y = (SCREEN_H - dialog_height) // 2
                                    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
                                    
                                    if dialog_rect.collidepoint(mx, my):
                                        # Click is inside dialog area but not on a button - do nothing (modal behavior)
                                        pass
                                    else:
                                        # Click is outside dialog area - dismiss the dialog
                                        game_state.dismiss_technical_debt_dialog()
                                        if hasattr(game_state, 'sound_manager'):
                                            game_state.sound_manager.play_sound('popup_close')
                            # Check for fundraising dialog clicks
                            elif game_state and game_state.pending_fundraising_dialog and cached_fundraising_dialog_rects is not None:
                                fundraising_handled = False
                                for rect_info in cached_fundraising_dialog_rects:
                                    if rect_info['rect'].collidepoint(mx, my):
                                        if rect_info['type'] == 'funding_option':
                                            # Player selected a funding option
                                            game_state.select_fundraising_option(rect_info['option_id'])
                                            fundraising_handled = True
                                            break
                                        elif rect_info['type'] == 'cancel':
                                            # Player cancelled the fundraising dialog
                                            game_state.dismiss_fundraising_dialog()
                                            fundraising_handled = True
                                            break
                                
                                if fundraising_handled:
                                    pass  # Fundraising dialog handled the click
                                else:
                                    # When fundraising dialog is open, check if click is inside dialog area
                                    # Calculate dialog rect (same as in ui.py draw_fundraising_dialog)
                                    dialog_width = int(SCREEN_W * 0.85)
                                    dialog_height = int(SCREEN_H * 0.9)
                                    dialog_x = (SCREEN_W - dialog_width) // 2
                                    dialog_y = (SCREEN_H - dialog_height) // 2
                                    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
                                    
                                    if dialog_rect.collidepoint(mx, my):
                                        # Click is inside dialog area but not on a button - do nothing (modal behavior)
                                        pass
                                    else:
                                        # Click is outside dialog area - dismiss the dialog
                                        game_state.dismiss_fundraising_dialog()
                                        if hasattr(game_state, 'sound_manager'):
                                            game_state.sound_manager.play_sound('popup_close')
                            # Check for research dialog clicks
                            elif game_state and game_state.pending_research_dialog and cached_research_dialog_rects is not None:
                                research_handled = False
                                for rect_info in cached_research_dialog_rects:
                                    if rect_info['rect'].collidepoint(mx, my):
                                        if rect_info['type'] == 'research_option':
                                            # Player selected a research option
                                            game_state.select_research_option(rect_info['option_id'])
                                            research_handled = True
                                            break
                                        elif rect_info['type'] == 'cancel':
                                            # Player cancelled the research dialog
                                            game_state.dismiss_research_dialog()
                                            research_handled = True
                                            break
                                
                                if research_handled:
                                    pass  # Research dialog handled the click
                                else:
                                    # When research dialog is open, check if click is inside dialog area
                                    # Calculate dialog rect (same as in ui.py draw_research_dialog)
                                    dialog_width = int(SCREEN_W * 0.85)
                                    dialog_height = int(SCREEN_H * 0.9)
                                    dialog_x = (SCREEN_W - dialog_width) // 2
                                    dialog_y = (SCREEN_H - dialog_height) // 2
                                    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
                                    
                                    if dialog_rect.collidepoint(mx, my):
                                        # Click is inside dialog area but not on a button - do nothing (modal behavior)
                                        pass
                                    else:
                                        # Click is outside dialog area - dismiss the dialog
                                        game_state.dismiss_research_dialog()
                                        if hasattr(game_state, 'sound_manager'):
                                            game_state.sound_manager.play_sound('popup_close')
                            # Check for dashboard element clicks - Research Quality Selection Submenu Bug fix
                            elif (game_state and hasattr(game_state, '_dashboard_clickable_rects') and 
                                  game_state._dashboard_clickable_rects):
                                dashboard_handled = False
                                for rect_info in game_state._dashboard_clickable_rects:
                                    if rect_info['rect'].collidepoint(mx, my):
                                        if rect_info['type'] == 'research_quality_select':
                                            # Player selected a research quality option
                                            from src.services.dashboard_manager import get_dashboard_manager
                                            dashboard_manager = get_dashboard_manager()
                                            success = dashboard_manager.handle_research_quality_selection(
                                                rect_info['quality'], game_state
                                            )
                                            if success and hasattr(game_state, 'sound_manager'):
                                                game_state.sound_manager.play_sound('button_click')
                                            dashboard_handled = True
                                            break
                                
                                if not dashboard_handled:
                                    # Dashboard elements didn't handle the click, continue with other handlers
                                    pass
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
                        
                elif event.type == pygame.TEXTINPUT:
                    # Handle text input for name fields in pre_game_settings
                    if current_state == 'pre_game_settings' and pre_game_settings_manager.is_text_input_active():
                        pre_game_settings_manager.handle_text_input(event.text, pre_game_settings)
                        
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
                        
                        # Handle dashboard hover effects - Research Quality Selection Submenu Bug fix
                        from src.services.dashboard_manager import get_dashboard_manager
                        dashboard_manager = get_dashboard_manager()
                        dashboard_manager.handle_mouse_hover(event.pos, game_state, SCREEN_W, SCREEN_H)
                
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
                    
                    # Global DEV MODE toggle (F10) - available in all states
                    if event.key == pygame.K_F10:
                        try:
                            from src.services.dev_mode import toggle_dev_mode
                            new_state = toggle_dev_mode()
                            status_msg = "DEV MODE ON" if new_state else "DEV MODE OFF"
                            
                            # If we're in game, show message there. Otherwise, we'll just toggle silently.
                            if current_state == 'game' and game_state:
                                game_state.add_message(f"System: {status_msg} (F10)")
                                if hasattr(game_state, 'sound_manager'):
                                    game_state.sound_manager.play_sound('ui_accept')
                        except ImportError:
                            pass  # Silently fail if dev_mode module not available
                    
                    # Keyboard handling varies by state
                    elif current_state == 'main_menu':
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
                    elif current_state == 'settings_menu':
                        handle_settings_menu_keyboard(event.key)
                    elif current_state == 'privacy_controls':
                        handle_privacy_controls_keyboard(event.key)
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
                        # NEW: Use extracted InputEventManager for clean keyboard handling
                        updated_values, should_quit, key_event_consumed = handle_game_keyboard_input(
                            event, game_state, onboarding, first_time_help_content, 
                            current_help_mechanic, overlay_content, overlay_title, 
                            current_state, escape_count, escape_timer, running
                        )
                        
                        # Apply any state updates from the input handler
                        for key, value in updated_values.items():
                            if key == 'overlay_content':
                                overlay_content = value
                            elif key == 'overlay_title':
                                overlay_title = value
                            elif key == 'push_navigation_state':
                                push_navigation_state(value)
                            elif key == 'current_state':
                                current_state = value
                            elif key == 'first_time_help_content':
                                first_time_help_content = value
                            elif key == 'first_time_help_close_button':
                                first_time_help_close_button = value
                            elif key == 'current_help_mechanic':
                                current_help_mechanic = value
                        
                        # Handle quit request from input handler
                        if should_quit:
                            running = False


            # --- Game state initialization --- #
            # Create game state when entering game for first time
            if current_state == 'game' and game_state is None:
                # Use Game State Manager for clean game initialization
                game_state_manager = get_game_state_manager()
                game_state = game_state_manager.create_fresh_game_state(seed)
                
                # Apply custom names from pre_game_settings
                if pre_game_settings.get("player_name") and pre_game_settings["player_name"] != "Anonymous":
                    game_state.player_name = pre_game_settings["player_name"]
                
                if pre_game_settings.get("lab_name") and pre_game_settings["lab_name"]:
                    game_state.lab_name = pre_game_settings["lab_name"]
                
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
                # Enhanced Debug key (D) - comprehensive blocking condition check
                current_keys = pygame.key.get_pressed()
                if current_keys[pygame.K_d] and current_keys[pygame.K_LCTRL]:  # Ctrl+D for debug
                    # Check all possible blocking conditions
                    blocking_checks = [
                        ("help", first_time_help_content),
                        ("tutorial", onboarding.show_tutorial_overlay),
                        ("hiring", game_state.pending_hiring_dialog),
                        ("funding", game_state.pending_fundraising_dialog),
                        ("research", game_state.pending_research_dialog),
                        ("intelligence", game_state.pending_intelligence_dialog),
                        ("media", game_state.pending_media_dialog),
                        ("tech_debt", game_state.pending_technical_debt_dialog),
                        ("infrastructure", game_state.pending_infrastructure_dialog),
                        ("adv_funding", game_state.pending_advanced_funding_dialog),
                        ("operations", game_state.pending_operations_dialog)
                    ]
                    
                    # Add popup events check
                    popup_events_active = (hasattr(game_state, 'pending_popup_events') and 
                                          game_state.pending_popup_events)
                    if popup_events_active:
                        blocking_checks.append(("popup_events", True))
                    
                    # Find active blocking conditions
                    blocking = [name for name, condition in blocking_checks if condition]
                    spacebar_works = not blocking
                    
                    # Create comprehensive debug message
                    debug_msg = f"DEBUG: Spacebar {'WORKS' if spacebar_works else 'BLOCKED'}"
                    if blocking:
                        debug_msg += f" | Blocking: {', '.join(blocking)}"
                    
                    # Add helpful hint about emergency reset
                    if blocking:
                        debug_msg += " | Use Ctrl+E to emergency reset"
                    
                    game_state.add_message(debug_msg)
                
                # Automatic cleanup for turn processing that's been stuck too long
                if hasattr(game_state, 'turn_manager') and game_state.turn_manager.is_processing_stuck():
                    game_state.turn_manager.reset_processing()
                    game_state.add_message("System: Reset stuck turn processing")
                
                # Automatic cleanup for tutorial overlay that's been active too long without interaction
                if (onboarding.show_tutorial_overlay and 
                    game_state.turn > 10):  # If we're past turn 10, tutorial should definitely be dismissible
                    onboarding.show_tutorial_overlay = False
                    game_state.add_message("System: Auto-dismissed stuck tutorial overlay")
                
                # ENHANCED Emergency recovery system (Ctrl+E) - clears ALL blocking UI states
                current_keys = pygame.key.get_pressed()
                if current_keys[pygame.K_e] and current_keys[pygame.K_LCTRL]:  # Ctrl+E emergency reset
                    emergency_cleared = []
                    
                    # Clear popup events
                    if (hasattr(game_state, 'pending_popup_events') and game_state.pending_popup_events):
                        game_state.pending_popup_events.clear()
                        emergency_cleared.append("popup events")
                    
                    # Clear deferred popup events
                    if (hasattr(game_state, 'deferred_events') and 
                        hasattr(game_state.deferred_events, 'pending_popup_events') and
                        game_state.deferred_events.pending_popup_events):
                        game_state.deferred_events.pending_popup_events.clear()
                        emergency_cleared.append("deferred events")
                    
                    # Clear all dialog states that can block spacebar
                    dialog_states = [
                        ('hiring_dialog', 'pending_hiring_dialog'),
                        ('fundraising_dialog', 'pending_fundraising_dialog'),
                        ('research_dialog', 'pending_research_dialog'),
                        ('intelligence_dialog', 'pending_intelligence_dialog'),
                        ('media_dialog', 'pending_media_dialog'),
                        ('technical_debt_dialog', 'pending_technical_debt_dialog'),
                        ('infrastructure_dialog', 'pending_infrastructure_dialog'),
                        ('advanced_funding_dialog', 'pending_advanced_funding_dialog'),
                        ('operations_dialog', 'pending_operations_dialog')
                    ]
                    
                    for dialog_name, attr_name in dialog_states:
                        if hasattr(game_state, attr_name) and getattr(game_state, attr_name) is not None:
                            setattr(game_state, attr_name, None)
                            emergency_cleared.append(dialog_name)
                    
                    # Clear global help content that can block spacebar
                    if first_time_help_content:
                        first_time_help_content = None
                        first_time_help_close_button = None
                        current_help_mechanic = None
                        emergency_cleared.append("help overlay")
                    
                    # Clear tutorial overlay
                    if onboarding.show_tutorial_overlay:
                        onboarding.dismiss_tutorial()
                        emergency_cleared.append("tutorial overlay")
                    
                    # Provide feedback about what was cleared
                    if emergency_cleared:
                        cleared_list = ", ".join(emergency_cleared)
                        game_state.add_message(f"EMERGENCY RESET: Cleared {cleared_list} (Ctrl+E)")
                        if hasattr(game_state, 'sound_manager'):
                            game_state.sound_manager.play_sound('ui_accept')
                    else:
                        game_state.add_message("EMERGENCY RESET: No stuck UI states found (Ctrl+E)")
                        if hasattr(game_state, 'sound_manager'):
                            game_state.sound_manager.play_sound('ui_click')
                
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
                # Check for various first-time mechanics (but not first_staff_hire or first_upgrade_purchase - those are context-sensitive)
                for mechanic in ['high_doom_warning']:
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
                
            elif current_state == 'settings_menu':
                # Main settings menu
                screen.fill((40, 45, 55))
                draw_settings_main_menu(screen, SCREEN_W, SCREEN_H, settings_menu_selected_item)
                
            elif current_state == 'privacy_controls':
                # Privacy controls menu
                screen.fill((40, 45, 55))
                privacy_controls.draw(screen, SCREEN_W, SCREEN_H)
                
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
                # High score screen with interactive menu (lab config styling)
                screen.fill((64, 64, 64))  # Grey background matching config menu
                # Determine context: from_main_menu = True if no game_state (accessed from main menu)
                from_main_menu = game_state is None
                draw_high_score_screen(screen, SCREEN_W, SCREEN_H, game_state, seed, high_score_submit_to_leaderboard, high_score_selected_item, from_main_menu)

            elif current_state == 'escape_menu':
                # Draw the game in background (dimmed)
                screen.fill((25, 25, 35))
                if game_state:
                    draw_ui(screen, game_state, SCREEN_W, SCREEN_H)
                    
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
                        if hasattr(game_state, 'turn_manager'):
                            game_state.turn_manager.update_processing_timer()  # Handle turn transition timing
                        else:
                            game_state.update_turn_processing()  # Fallback to old method
                        game_state.overlay_manager.update_animations()
                    
                    draw_ui(screen, game_state, SCREEN_W, SCREEN_H)
                    
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
                    
                    # Only show tooltips if enabled in configuration (default: off for cleaner UI)
                    if tooltip_text:
                        from src.services.ui_config import should_show_tooltips
                        if should_show_tooltips(game_state):
                            draw_tooltip(screen, tooltip_text, pygame.mouse.get_pos(), SCREEN_W, SCREEN_H)
                    
                    # Draw hiring dialog if active
                    if game_state and game_state.pending_hiring_dialog:
                        from src.ui.dialogs import draw_hiring_dialog
                        cached_hiring_dialog_rects = draw_hiring_dialog(screen, game_state.pending_hiring_dialog, SCREEN_W, SCREEN_H)
                    else:
                        # Clear cached rects when dialog is not active
                        cached_hiring_dialog_rects = None
                    
                    # Draw intelligence dialog if active
                    if game_state and game_state.pending_intelligence_dialog:
                        from src.ui.dialogs import draw_intelligence_dialog
                        cached_intelligence_dialog_rects = draw_intelligence_dialog(screen, game_state.pending_intelligence_dialog, SCREEN_W, SCREEN_H)
                    else:
                        # Clear cached rects when dialog is not active
                        cached_intelligence_dialog_rects = None
                    
                    # Draw fundraising dialog if active
                    if game_state and game_state.pending_fundraising_dialog:
                        from src.ui.dialogs import draw_fundraising_dialog
                        cached_fundraising_dialog_rects = draw_fundraising_dialog(screen, game_state.pending_fundraising_dialog, SCREEN_W, SCREEN_H)
                    else:
                        # Clear cached rects when dialog is not active
                        cached_fundraising_dialog_rects = None
                    
                    # Draw research dialog if active
                    if game_state and game_state.pending_research_dialog:
                        from src.ui.dialogs import draw_research_dialog
                        cached_research_dialog_rects = draw_research_dialog(screen, game_state.pending_research_dialog, SCREEN_W, SCREEN_H)
                    else:
                        # Clear cached rects when dialog is not active
                        cached_research_dialog_rects = None
                    
                    # Draw media dialog if active
                    if game_state and game_state.pending_media_dialog:
                        from src.ui.dialogs import draw_media_dialog
                        cached_media_dialog_rects = draw_media_dialog(screen, game_state.pending_media_dialog, SCREEN_W, SCREEN_H)
                    else:
                        # Clear cached rects when dialog is not active
                        cached_media_dialog_rects = None
                    
                    # Draw technical debt dialog if active
                    if game_state and game_state.pending_technical_debt_dialog:
                        from src.ui.dialogs import draw_technical_debt_dialog
                        cached_technical_debt_dialog_rects = draw_technical_debt_dialog(screen, game_state.pending_technical_debt_dialog, SCREEN_W, SCREEN_H)
                    else:
                        # Clear cached rects when dialog is not active
                        cached_technical_debt_dialog_rects = None
                    

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
                    if game_state and hasattr(game_state, 'turn_manager') and game_state.turn_manager.is_processing():
                        draw_turn_transition_overlay(screen, SCREEN_W, SCREEN_H, game_state.turn_manager.processing_timer, game_state.turn_manager.processing_duration)
                    elif game_state and game_state.turn_processing:  # Fallback to old system
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
        
        # Final shutdown logging
        log_shutdown()
        pygame.quit()

if __name__ == "__main__":
    main()
