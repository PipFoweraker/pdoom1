"""
Command String Controller - Deterministic Command-Based Game Control

This module provides a simple string-based interface for controlling P(Doom) games
using abbreviated commands. Perfect for sharing strategies, reproducible testing,
and player-friendly automation.

COMMAND STRING FORMAT:
Commands are separated by spaces, using single-letter abbreviations:
- T = End Turn (advance turn)
- H = Hire Staff 
- F = Fundraise
- S = Safety Research
- C = Buy Compute
- R = Research Options (menu)
- G = Grow Community
- I = Intelligence (scout opponents)
- E = Espionage (advanced intelligence)
- U = Upgrade (specify which upgrade)

REPETITION SYNTAX:
Use * followed by a number to repeat commands:
- H*3 = Hire staff 3 times
- T*5 = End turn 5 times
- F*2 S = Fundraise twice, then safety research

EXAMPLE COMMAND STRINGS:
"T H F S T F C S"    = End turn, Hire, Fundraise, Safety research, End turn, Fundraise, Compute, Safety
"H*3 F*2 S T"        = Hire 3 staff, Fundraise twice, Safety research, End turn
"F S C T H I T"      = Fundraise, Safety research, Buy compute, End turn, Hire, Intelligence, End turn

DETERMINISTIC EXECUTION:
With the same seed and command string, execution is 100% deterministic:
- All random events will occur in the same order
- Opponent actions will be identical
- Outcomes will be exactly reproducible
- Perfect for testing and strategy sharing

ASCII-ONLY DESIGN:
All commands use standard ASCII characters for maximum compatibility
and easy sharing via text messages, documentation, and configuration files.
"""

from typing import List, Dict, Any, Optional, Tuple
import json
import re
from dataclasses import dataclass, asdict


@dataclass 
class CommandResult:
    """Result of executing a single command."""
    command: str
    command_letter: str
    success: bool
    message: str
    turn_before: int
    turn_after: int
    state_changes: Dict[str, Any]
    execution_time_ms: float


@dataclass
class CommandStringReport:
    """Complete execution report for a command string."""
    seed: str
    command_string: str
    expanded_commands: List[str]
    total_commands: int
    successful_commands: int
    failed_commands: int
    initial_state: Dict[str, Any]
    final_state: Dict[str, Any]
    final_turn: int
    total_execution_time_ms: float
    command_results: List[CommandResult]
    
    def to_json(self) -> str:
        """Convert report to JSON string."""
        return json.dumps(asdict(self), indent=2, default=str)
    
    def save_to_file(self, filepath: str) -> None:
        """Save report to JSON file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())


class CommandStringParser:
    """Parse command strings into executable action sequences."""
    
    # ASCII-only command mappings
    COMMAND_MAP = {
        'T': 'end_turn',
        'H': 'hire_staff',
        'F': 'fundraise', 
        'S': 'safety_research',
        'C': 'buy_compute',
        'R': 'research_options',
        'G': 'grow_community',
        'I': 'intelligence_gathering',
        'E': 'espionage',
        'U': 'upgrade_purchase',
        'P': 'press_release',
        'N': 'networking',
        'M': 'monitoring_systems',
        'A': 'conduct_audit',
        'L': 'lobbying',
        'D': 'data_analysis',
        'O': 'outreach_program'
    }
    
    def __init__(self):
        """Initialize the command string parser."""
        self.valid_commands = set(self.COMMAND_MAP.keys())
    
    def validate_command_string(self, command_string: str) -> Tuple[bool, str]:
        """
        Validate a command string without executing it.
        
        Args:
            command_string: Command string to validate
            
        Returns:
            (is_valid, message) tuple
        """
        try:
            self.parse_command_string(command_string)
            return True, "Command string is valid"
        except ValueError as e:
            return False, str(e)
    
    def parse_command_string(self, command_string: str) -> List[Tuple[str, int]]:
        """
        Parse command string into (command, repetition_count) tuples.
        
        Args:
            command_string: Space-separated command string
            
        Returns:
            List of (command_letter, count) tuples
            
        Raises:
            ValueError: If command string contains invalid syntax
        """
        if not command_string.strip():
            return []
        
        commands = []
        tokens = command_string.strip().upper().split()
        
        for token in tokens:
            # Handle repetition syntax: H*3 means H repeated 3 times
            if '*' in token:
                parts = token.split('*')
                if len(parts) != 2:
                    raise ValueError(f"Invalid repetition syntax: {token}. Use format 'H*3'")
                
                cmd_letter, count_str = parts
                
                # Validate command letter
                if cmd_letter not in self.valid_commands:
                    raise ValueError(f"Invalid command: {cmd_letter}. Valid: {', '.join(sorted(self.valid_commands))}")
                
                # Validate count
                try:
                    count = int(count_str)
                    if count < 1 or count > 99:  # Reasonable limits
                        raise ValueError(f"Invalid repetition count: {count_str}. Must be 1-99")
                except ValueError:
                    raise ValueError(f"Invalid repetition count: {count_str}. Must be a number")
                
                commands.append((cmd_letter, count))
            else:
                # Single command
                if token not in self.valid_commands:
                    raise ValueError(f"Invalid command: {token}. Valid: {', '.join(sorted(self.valid_commands))}")
                
                commands.append((token, 1))
        
        return commands
    
    def expand_command_string(self, command_string: str) -> List[str]:
        """
        Expand command string with repetitions into individual commands.
        
        Args:
            command_string: Command string to expand
            
        Returns:
            List of individual command letters to execute
        """
        parsed = self.parse_command_string(command_string)
        expanded = []
        
        for cmd_letter, count in parsed:
            for _ in range(count):
                expanded.append(cmd_letter)
        
        return expanded
    
    def get_command_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all available commands."""
        descriptions = {
            'T': 'End Turn - Advance to the next turn',
            'H': 'Hire Staff - Recruit new team members',
            'F': 'Fundraise - Raise money through various channels',
            'S': 'Safety Research - Conduct AI safety research',
            'C': 'Buy Compute - Purchase computational resources',
            'R': 'Research Options - Access research menu',
            'G': 'Grow Community - Expand community outreach',
            'I': 'Intelligence - Gather information on opponents',
            'E': 'Espionage - Advanced intelligence operations',
            'U': 'Upgrade - Purchase available upgrades',
            'P': 'Press Release - Public relations activities',
            'N': 'Networking - Professional networking events',
            'M': 'Monitoring - Monitor systems and threats',
            'A': 'Audit - Conduct internal audits',
            'L': 'Lobbying - Government relations activities',
            'D': 'Data Analysis - Analyze research data',
            'O': 'Outreach - Community outreach programs'
        }
        return descriptions
    
    def generate_example_strings(self) -> List[Tuple[str, str]]:
        """Generate example command strings with descriptions."""
        examples = [
            ("T H F S T F C S", "Basic early game: End turn, hire, fundraise, research, repeat"),
            ("H*3 F*2 S T", "Staff up: Hire 3 staff, fundraise twice, research, end turn"),
            ("F S C T H I T", "Balanced approach: Fundraise, research, compute, hire, intelligence"),
            ("G P N T*5", "PR focus: Community, press, networking, then coast 5 turns"),
            ("H F S U T*3 A M", "Growth phase: Hire, fundraise, research, upgrade, monitor"),
            ("T*10", "Speed run: Just advance 10 turns quickly"),
            ("H*5 F*3 S*2 C U T", "Resource buildup: Mass hiring, fundraising, research, compute"),
            ("I*3 E T H F S", "Intelligence focus: Scout heavily, then standard actions")
        ]
        return examples


class CommandStringController:
    """
    Execute command strings against a game state.
    
    This controller bridges between simple command strings and the complex
    game state, providing deterministic execution for testing and strategy sharing.
    """
    
    def __init__(self, game_state=None):
        """
        Initialize the command string controller.
        
        Args:
            game_state: Game state to control (optional)
        """
        self.game_state = game_state
        self.parser = CommandStringParser()
    
    def set_game_state(self, game_state):
        """Set the game state to control."""
        self.game_state = game_state
    
    def execute_command_string(self, command_string: str, seed: str = None) -> CommandStringReport:
        """
        Execute a complete command string and return detailed report.
        
        Args:
            command_string: Command string to execute
            seed: Optional seed for reproducibility
            
        Returns:
            CommandStringReport with complete execution details
            
        Raises:
            ValueError: If command string is invalid
            RuntimeError: If no game state is available
        """
        if not self.game_state:
            raise RuntimeError("No game state available. Call set_game_state() first.")
        
        # Validate command string
        is_valid, error_msg = self.parser.validate_command_string(command_string)
        if not is_valid:
            raise ValueError(f"Invalid command string: {error_msg}")
        
        # Parse and expand commands
        expanded_commands = self.parser.expand_command_string(command_string)
        
        # Capture initial state
        initial_state = self._capture_state()
        initial_turn = getattr(self.game_state, 'turn_count', 0)
        
        # Execute commands
        import time
        start_time = time.time()
        
        command_results = []
        successful_commands = 0
        failed_commands = 0
        
        for cmd_letter in expanded_commands:
            cmd_start_time = time.time()
            
            try:
                result = self._execute_single_command(cmd_letter)
                result.execution_time_ms = (time.time() - cmd_start_time) * 1000
                command_results.append(result)
                
                if result.success:
                    successful_commands += 1
                else:
                    failed_commands += 1
                    
            except Exception as e:
                # Handle unexpected errors gracefully
                result = CommandResult(
                    command=self.parser.COMMAND_MAP.get(cmd_letter, cmd_letter),
                    command_letter=cmd_letter,
                    success=False,
                    message=f"Unexpected error: {str(e)}",
                    turn_before=getattr(self.game_state, 'turn_count', 0),
                    turn_after=getattr(self.game_state, 'turn_count', 0),
                    state_changes={},
                    execution_time_ms=(time.time() - cmd_start_time) * 1000
                )
                command_results.append(result)
                failed_commands += 1
        
        total_execution_time = (time.time() - start_time) * 1000
        
        # Generate final report
        report = CommandStringReport(
            seed=seed or "unknown",
            command_string=command_string,
            expanded_commands=expanded_commands,
            total_commands=len(expanded_commands),
            successful_commands=successful_commands,
            failed_commands=failed_commands,
            initial_state=initial_state,
            final_state=self._capture_state(),
            final_turn=getattr(self.game_state, 'turn_count', 0),
            total_execution_time_ms=total_execution_time,
            command_results=command_results
        )
        
        return report
    
    def _execute_single_command(self, cmd_letter: str) -> CommandResult:
        """Execute a single command and return result."""
        command_name = self.parser.COMMAND_MAP.get(cmd_letter, cmd_letter)
        turn_before = getattr(self.game_state, 'turn_count', 0)
        state_before = self._capture_state()
        
        # Dispatch to appropriate handler
        success, message = self._dispatch_command(cmd_letter)
        
        turn_after = getattr(self.game_state, 'turn_count', 0)
        state_after = self._capture_state()
        
        # Calculate state changes
        state_changes = self._calculate_state_changes(state_before, state_after)
        
        return CommandResult(
            command=command_name,
            command_letter=cmd_letter,
            success=success,
            message=message,
            turn_before=turn_before,
            turn_after=turn_after,
            state_changes=state_changes,
            execution_time_ms=0.0  # Will be set by caller
        )
    
    def _dispatch_command(self, cmd_letter: str) -> Tuple[bool, str]:
        """
        Dispatch command to appropriate handler.
        
        Args:
            cmd_letter: Single letter command
            
        Returns:
            (success, message) tuple
        """
        try:
            if cmd_letter == 'T':
                return self._end_turn()
            elif cmd_letter == 'H':
                return self._hire_staff()
            elif cmd_letter == 'F':
                return self._fundraise()
            elif cmd_letter == 'S':
                return self._safety_research()
            elif cmd_letter == 'C':
                return self._buy_compute()
            elif cmd_letter == 'R':
                return self._research_options()
            elif cmd_letter == 'G':
                return self._grow_community()
            elif cmd_letter == 'I':
                return self._intelligence_gathering()
            elif cmd_letter == 'E':
                return self._espionage()
            elif cmd_letter == 'U':
                return self._upgrade_purchase()
            elif cmd_letter == 'P':
                return self._press_release()
            elif cmd_letter == 'N':
                return self._networking()
            elif cmd_letter == 'M':
                return self._monitoring_systems()
            elif cmd_letter == 'A':
                return self._conduct_audit()
            elif cmd_letter == 'L':
                return self._lobbying()
            elif cmd_letter == 'D':
                return self._data_analysis()
            elif cmd_letter == 'O':
                return self._outreach_program()
            else:
                return False, f"Unknown command: {cmd_letter}"
        except Exception as e:
            return False, f"Command execution error: {str(e)}"
    
    def _end_turn(self) -> Tuple[bool, str]:
        """Execute end turn command."""
        if hasattr(self.game_state, 'end_turn'):
            try:
                success = self.game_state.end_turn()
                if success:
                    return True, f"Turn advanced to {getattr(self.game_state, 'turn_count', '?')}"
                else:
                    return False, "Failed to advance turn (may be blocked by dialogs)"
            except Exception as e:
                return False, f"End turn failed: {str(e)}"
        else:
            return False, "Game state does not support end_turn"
    
    def _hire_staff(self) -> Tuple[bool, str]:
        """Execute hire staff command."""
        # Find and execute hire staff action
        if hasattr(self.game_state, 'actions'):
            for action in self.game_state.actions:
                action_name = action.get('name', '').lower()
                if 'hire' in action_name and 'staff' in action_name:
                    if action.get('available', False):
                        try:
                            success = self.game_state.execute_action(action)
                            if success:
                                cost = action.get('cost', 0)
                                return True, f"Hired staff for ${cost}"
                            else:
                                return False, "Hire staff action failed"
                        except Exception as e:
                            return False, f"Hire staff error: {str(e)}"
                    else:
                        reason = action.get('unavailable_reason', 'Not available')
                        return False, f"Cannot hire staff: {reason}"
        
        return False, "Hire staff action not found"
    
    def _fundraise(self) -> Tuple[bool, str]:
        """Execute fundraise command."""
        if hasattr(self.game_state, 'actions'):
            for action in self.game_state.actions:
                action_name = action.get('name', '').lower()
                if 'fundrais' in action_name or 'funding' in action_name:
                    if action.get('available', False):
                        try:
                            success = self.game_state.execute_action(action)
                            if success:
                                return True, "Fundraising successful"
                            else:
                                return False, "Fundraising failed"
                        except Exception as e:
                            return False, f"Fundraising error: {str(e)}"
                    else:
                        reason = action.get('unavailable_reason', 'Not available')
                        return False, f"Cannot fundraise: {reason}"
        
        return False, "Fundraising action not found"
    
    def _safety_research(self) -> Tuple[bool, str]:
        """Execute safety research command."""
        if hasattr(self.game_state, 'actions'):
            for action in self.game_state.actions:
                action_name = action.get('name', '').lower()
                if 'safety' in action_name and 'research' in action_name:
                    if action.get('available', False):
                        try:
                            success = self.game_state.execute_action(action)
                            if success:
                                return True, "Safety research completed"
                            else:
                                return False, "Safety research failed"
                        except Exception as e:
                            return False, f"Safety research error: {str(e)}"
                    else:
                        reason = action.get('unavailable_reason', 'Not available')
                        return False, f"Cannot do safety research: {reason}"
        
        return False, "Safety research action not found"
    
    def _buy_compute(self) -> Tuple[bool, str]:
        """Execute buy compute command."""
        if hasattr(self.game_state, 'actions'):
            for action in self.game_state.actions:
                action_name = action.get('name', '').lower()
                if 'compute' in action_name and ('buy' in action_name or 'purchase' in action_name):
                    if action.get('available', False):
                        try:
                            success = self.game_state.execute_action(action)
                            if success:
                                return True, "Compute purchased"
                            else:
                                return False, "Compute purchase failed"
                        except Exception as e:
                            return False, f"Compute purchase error: {str(e)}"
                    else:
                        reason = action.get('unavailable_reason', 'Not available')
                        return False, f"Cannot buy compute: {reason}"
        
        return False, "Buy compute action not found"
    
    # Placeholder implementations for other commands
    def _research_options(self) -> Tuple[bool, str]:
        return False, "Research options not implemented for command strings yet"
    
    def _grow_community(self) -> Tuple[bool, str]:
        return self._find_and_execute_action(['community', 'grow'], "Community growth")
    
    def _intelligence_gathering(self) -> Tuple[bool, str]:
        return self._find_and_execute_action(['scout', 'intelligence'], "Intelligence gathering")
    
    def _espionage(self) -> Tuple[bool, str]:
        return False, "Espionage not implemented yet"
    
    def _upgrade_purchase(self) -> Tuple[bool, str]:
        return False, "Upgrade purchase via command string not implemented yet"
    
    def _press_release(self) -> Tuple[bool, str]:
        return self._find_and_execute_action(['press', 'release'], "Press release")
    
    def _networking(self) -> Tuple[bool, str]:
        return self._find_and_execute_action(['network'], "Networking")
    
    def _monitoring_systems(self) -> Tuple[bool, str]:
        return self._find_and_execute_action(['monitor'], "Monitoring")
    
    def _conduct_audit(self) -> Tuple[bool, str]:
        return self._find_and_execute_action(['audit'], "Audit")
    
    def _lobbying(self) -> Tuple[bool, str]:
        return self._find_and_execute_action(['lobby'], "Lobbying")
    
    def _data_analysis(self) -> Tuple[bool, str]:
        return self._find_and_execute_action(['data', 'analysis'], "Data analysis")
    
    def _outreach_program(self) -> Tuple[bool, str]:
        return self._find_and_execute_action(['outreach'], "Outreach")
    
    def _find_and_execute_action(self, keywords: List[str], action_description: str) -> Tuple[bool, str]:
        """Helper to find and execute actions by keywords."""
        if hasattr(self.game_state, 'actions'):
            for action in self.game_state.actions:
                action_name = action.get('name', '').lower()
                if all(keyword.lower() in action_name for keyword in keywords):
                    if action.get('available', False):
                        try:
                            success = self.game_state.execute_action(action)
                            if success:
                                return True, f"{action_description} successful"
                            else:
                                return False, f"{action_description} failed"
                        except Exception as e:
                            return False, f"{action_description} error: {str(e)}"
                    else:
                        reason = action.get('unavailable_reason', 'Not available')
                        return False, f"Cannot {action_description.lower()}: {reason}"
        
        return False, f"{action_description} action not found"
    
    def _capture_state(self) -> Dict[str, Any]:
        """Capture current game state."""
        if not self.game_state:
            return {}
        
        return {
            'turn': getattr(self.game_state, 'turn_count', 0),
            'money': getattr(self.game_state, 'money', 0),
            'staff': getattr(self.game_state, 'staff', 0),
            'reputation': getattr(self.game_state, 'reputation', 0),
            'doom': getattr(self.game_state, 'doom', 0),
            'compute': getattr(self.game_state, 'compute', 0),
            'action_points': getattr(self.game_state, 'action_points', 0),
            'game_over': getattr(self.game_state, 'game_over', False)
        }
    
    def _calculate_state_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate differences between two states."""
        changes = {}
        
        for key in before.keys():
            if key in after and before[key] != after[key]:
                if isinstance(before[key], (int, float)) and isinstance(after[key], (int, float)):
                    changes[key] = {
                        'before': before[key],
                        'after': after[key],
                        'delta': after[key] - before[key]
                    }
                else:
                    changes[key] = {
                        'before': before[key],
                        'after': after[key]
                    }
        
        return changes


# Example usage and testing functions
def demonstrate_command_strings():
    """Demonstrate command string usage."""
    parser = CommandStringParser()
    
    print("Command String Controller - ASCII-Only Deterministic Game Control")
    print("=" * 70)
    
    print("\nAvailable Commands:")
    commands = parser.get_command_descriptions()
    for cmd, desc in commands.items():
        print(f"  {cmd}: {desc}")
    
    print("\nExample Command Strings:")
    examples = parser.generate_example_strings()
    for cmd_str, description in examples:
        print(f"  {cmd_str}")
        print(f"    -> {description}")
        
        # Show expansion
        try:
            expanded = parser.expand_command_string(cmd_str)
            print(f"    -> Expands to: {' '.join(expanded)}")
        except ValueError as e:
            print(f"    -> ERROR: {e}")
        print()
    
    print("\nValidation Examples:")
    test_cases = [
        "H F S T",           # Valid
        "H*3 F*2 T",         # Valid with repetition
        "X Y Z",             # Invalid commands
        "H*0 F",             # Invalid repetition count
        "H* F",              # Invalid repetition syntax
    ]
    
    for test_case in test_cases:
        is_valid, message = parser.validate_command_string(test_case)
        status = "VALID" if is_valid else "INVALID"
        print(f"  '{test_case}' -> {status}: {message}")


if __name__ == "__main__":
    demonstrate_command_strings()
