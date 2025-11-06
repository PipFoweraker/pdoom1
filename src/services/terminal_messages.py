"""
Enhanced terminal welcome and exit messages for P(Doom).

Provides verbose startup and shutdown messages for alpha/beta testing,
including version info, configuration details, exit reasons, and game state summaries.

This module supports both the Godot engine bridge and the legacy pygame version.
"""

import sys
import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path


def get_ascii_banner() -> str:
    """Get ASCII art banner for game startup."""
    return r"""
    ____  ____                      __
   / __ \/ __ \____  ____  ____ ___/ /
  / /_/ / / / / __ \/ __ \/ __ `__ \/ 
 / ____/ /_/ / /_/ / /_/ / / / / / /  
/_/   /_____/\____/\____/_/ /_/ /_/   
                                      
 Bureaucracy Strategy Game - AI Safety Edition
"""


def get_flavor_texts() -> List[str]:
    """Get list of rotating flavor texts for welcome screen."""
    return [
        "Every turn counts. Every decision matters.",
        "The future is uncertain. Your actions shape it.",
        "P(Doom) is rising. Can you stop it?",
        "In bureaucracy we trust... or do we?",
        "One lab. One mission. Infinite complexity.",
        "Safety first. Always.",
        "The alignment problem awaits...",
        "May your compute be plentiful and your doom be low.",
        "Warning: Actual AI safety research is harder than this.",
        "Remember: This is just a game. The real work is harder.",
    ]


def get_daily_flavor_text() -> str:
    """Get a consistent flavor text for today (changes daily)."""
    texts = get_flavor_texts()
    # Use day of year to pick a consistent text for the day
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    return texts[day_of_year % len(texts)]


def print_welcome_message(
    version: str,
    config: Optional[Dict[str, Any]] = None,
    engine: str = "Godot",
    verbose: bool = False,
    show_banner: bool = True,
    show_flavor: bool = True
) -> None:
    """
    Print enhanced welcome message with version, config, and flavor text.
    
    Args:
        version: Version string (e.g., "v0.10.1")
        config: Optional configuration dictionary with game settings
        engine: Engine name ("Godot" or "Pygame")
        verbose: If True, show detailed configuration information
        show_banner: If True, show ASCII art banner
        show_flavor: If True, show daily flavor text
    """
    print("=" * 80)
    
    if show_banner:
        print(get_ascii_banner())
    else:
        print(f"\nP(Doom): Bureaucracy Strategy Game {version}")
        print()
    
    if show_flavor:
        flavor = get_daily_flavor_text()
        print(f"  {flavor}")
        print()
    
    # Version Information
    print(f"VERSION: {version}")
    print(f"ENGINE: {engine}")
    print(f"STATUS: Alpha/Beta - Testing Phase")
    print(f"PYTHON: {sys.version.split()[0]}")
    
    # Last stable release info (placeholder for now)
    print(f"LAST STABLE: None (pre-release)")
    
    print()
    
    # Configuration Information
    if config:
        print("STARTUP CONFIGURATION:")
        
        # Economy settings
        if 'economy' in config:
            econ = config['economy']
            print(f"  Economic Model: {econ.get('model', 'Bootstrap AI Safety Nonprofit')}")
            print(f"  Starting Funds: ${econ.get('starting_money', 100000):,}")
            print(f"  Weekly Research: ${econ.get('research_cost', 3000):,}")
            
        # Gameplay settings
        if 'gameplay' in config:
            gameplay = config['gameplay']
            print(f"  Action Points: {gameplay.get('action_points_per_turn', 3)} per turn")
            print(f"  Difficulty: {gameplay.get('difficulty', 'STANDARD')}")
        
        # Audio settings
        if 'audio' in config:
            audio = config['audio']
            print(f"  Audio: {'Enabled' if audio.get('sound_enabled', True) else 'Disabled'}")
        
        # UI settings (pygame only)
        if 'ui' in config and engine == "Pygame":
            ui = config['ui']
            print(f"  Window Scale: {ui.get('window_scale', 0.8):.1f}x")
            print(f"  Fullscreen: {'Yes' if ui.get('fullscreen', False) else 'No'}")
        
        # Verbose details
        if verbose:
            print()
            print("DETAILED CONFIGURATION:")
            for section, values in config.items():
                if isinstance(values, dict):
                    print(f"  [{section}]")
                    for key, value in values.items():
                        print(f"    {key}: {value}")
    
    print()
    print("=" * 80)
    print()


def print_exit_message(
    version: str,
    exit_reason: str = "User exit",
    game_state: Optional[Dict[str, Any]] = None,
    log_path: Optional[str] = None,
    last_actions: Optional[List[str]] = None,
    crash_info: Optional[str] = None,
    verbose: bool = False
) -> None:
    """
    Print enhanced exit message with game state summary and debugging info.
    
    Args:
        version: Version string (e.g., "v0.10.1")
        exit_reason: Reason for exit (e.g., "User exit", "Game over", "Crash")
        game_state: Optional final game state dictionary
        log_path: Optional path to game log file
        last_actions: Optional list of last N player actions
        crash_info: Optional crash/error information
        verbose: If True, show detailed exit information
    """
    print()
    print("=" * 80)
    print(f"SHUTDOWN - P(Doom) {version}")
    print("=" * 80)
    
    # Exit reason
    print(f"EXIT REASON: {exit_reason}")
    print(f"TIMESTAMP: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Game state summary (if available)
    if game_state:
        print()
        print("FINAL GAME STATE:")
        print(f"  Turn: {game_state.get('turn', 'N/A')}")
        print(f"  Money: ${game_state.get('money', 0):,}")
        print(f"  Compute: {game_state.get('compute', 0):,}")
        print(f"  Safety: {game_state.get('safety', 0)}")
        print(f"  Capabilities: {game_state.get('capabilities', 0)}")
        
        if 'employees' in game_state:
            emp = game_state['employees']
            print(f"  Total Staff: {emp.get('total', 0)}")
            if verbose:
                print(f"    Safety Researchers: {emp.get('safety', 0)}")
                print(f"    Capabilities Researchers: {emp.get('capabilities', 0)}")
                print(f"    Compute Researchers: {emp.get('compute', 0)}")
        
        # Victory/defeat status
        if game_state.get('game_over'):
            if game_state.get('victory'):
                print(f"  RESULT: VICTORY!")
            else:
                print(f"  RESULT: Game Over")
    
    # Last actions (for debugging crashes)
    if last_actions:
        print()
        print(f"LAST {len(last_actions)} ACTIONS:")
        for i, action in enumerate(last_actions, 1):
            print(f"  {i}. {action}")
    
    # Crash information
    if crash_info:
        print()
        print("CRASH INFORMATION:")
        print(f"  {crash_info}")
    
    # Log file location
    if log_path:
        print()
        print(f"GAME LOG: {log_path}")
        print("  (Use this log file for bug reports)")
    
    print()
    print("=" * 80)
    print("Thank you for testing P(Doom)!")
    print("Report bugs: https://github.com/PipFoweraker/pdoom1/issues")
    print("=" * 80)
    print()


def format_action_history(actions: List[Dict[str, Any]], limit: int = 10) -> List[str]:
    """
    Format action history for display in exit messages.
    
    Args:
        actions: List of action dictionaries with 'name', 'turn', etc.
        limit: Maximum number of actions to include
        
    Returns:
        List of formatted action strings
    """
    formatted = []
    recent_actions = actions[-limit:] if len(actions) > limit else actions
    
    for action in recent_actions:
        if isinstance(action, dict):
            turn = action.get('turn', '?')
            name = action.get('name', action.get('action', 'Unknown'))
            result = action.get('result', '')
            
            if result:
                formatted.append(f"Turn {turn}: {name} - {result}")
            else:
                formatted.append(f"Turn {turn}: {name}")
        else:
            # Handle string actions
            formatted.append(str(action))
    
    return formatted


def create_startup_config_dict(pygame_config: Optional[Any] = None) -> Dict[str, Any]:
    """
    Create a standardized config dictionary for startup messages.
    
    Args:
        pygame_config: Optional pygame config manager
        
    Returns:
        Dictionary with standardized config structure
    """
    config = {
        'economy': {
            'model': 'Bootstrap AI Safety Nonprofit',
            'starting_money': 100000,
            'research_cost': 3000,
            'staff_maintenance_first': 600,
            'staff_maintenance_additional': 800,
            'hiring_bonus': 0,
        },
        'gameplay': {
            'action_points_per_turn': 3,
            'difficulty': 'STANDARD',
        },
        'audio': {
            'sound_enabled': True,
        },
    }
    
    # If pygame config is provided, extract actual values
    if pygame_config:
        try:
            if hasattr(pygame_config, 'get'):
                # Direct dictionary access
                if 'audio' in pygame_config:
                    config['audio']['sound_enabled'] = pygame_config['audio'].get('sound_enabled', True)
                if 'ui' in pygame_config:
                    config['ui'] = {
                        'window_scale': pygame_config['ui'].get('window_scale', 0.8),
                        'fullscreen': pygame_config['ui'].get('fullscreen', False),
                    }
        except Exception:
            pass  # Use defaults if extraction fails
    
    return config


class ExitReasonTracker:
    """Track exit reasons throughout the game lifecycle."""
    
    def __init__(self):
        self.exit_reason = "Unknown exit"
        self.is_crash = False
        self.is_graceful = True
        self.game_state = None
        self.last_actions = []
        self.log_path = None
    
    def set_user_exit(self, location: str = "unknown"):
        """User exited normally."""
        self.exit_reason = f"User exit from {location}"
        self.is_graceful = True
        self.is_crash = False
    
    def set_game_over(self, victory: bool = False):
        """Game ended naturally."""
        if victory:
            self.exit_reason = "Victory - Game won!"
        else:
            self.exit_reason = "Game over - Defeat"
        self.is_graceful = True
        self.is_crash = False
    
    def set_crash(self, error_message: str):
        """Game crashed with error."""
        self.exit_reason = f"Crash: {error_message}"
        self.is_crash = True
        self.is_graceful = False
    
    def set_graceful_crash(self, reason: str):
        """Handled error that exits gracefully."""
        self.exit_reason = f"Graceful exit: {reason}"
        self.is_crash = False
        self.is_graceful = True
    
    def update_game_state(self, state: Dict[str, Any]):
        """Update tracked game state."""
        self.game_state = state
    
    def add_action(self, action: str):
        """Add an action to history (keeps last 10)."""
        self.last_actions.append(action)
        if len(self.last_actions) > 10:
            self.last_actions.pop(0)
    
    def set_log_path(self, path: str):
        """Set path to game log file."""
        self.log_path = path
    
    def print_exit(self, version: str, verbose: bool = False):
        """Print exit message with tracked information."""
        print_exit_message(
            version=version,
            exit_reason=self.exit_reason,
            game_state=self.game_state,
            log_path=self.log_path,
            last_actions=self.last_actions if (self.is_crash or len(self.last_actions) > 0) else None,
            crash_info=self.exit_reason if self.is_crash else None,
            verbose=verbose
        )


# Global exit tracker instance
_exit_tracker = ExitReasonTracker()


def get_exit_tracker() -> ExitReasonTracker:
    """Get the global exit reason tracker."""
    return _exit_tracker
