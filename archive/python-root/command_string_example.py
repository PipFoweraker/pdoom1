# !/usr/bin/env python3
'''
Command String Integration Example

Demonstrates how to use the ASCII-only command string system with
the actual P(Doom) game state for deterministic strategy execution.

Example Usage:
    python command_string_example.py 'H*3 F*2 S T' test-seed-123
    python command_string_example.py 'T*5' random-strategy
    python command_string_example.py 'F S C H I T' early-intelligence
'''

import sys
import os
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from testing.command_string_controller import CommandStringController, CommandStringParser
    from src.core.game_state import GameState
except ImportError:
    print('Could not import required modules. Make sure you're running from the project root.')
    sys.exit(1)


def demonstrate_basic_usage():
    '''Show basic command string usage.'''
    print('Command String System - Basic Usage')
    print('=' * 50)
    
    # Create parser to show available commands
    parser = CommandStringParser()
    
    print('Available Single-Letter Commands:')
    commands = parser.get_command_descriptions()
    for cmd, desc in sorted(commands.items()):
        print(f'  {cmd}: {desc}')
    
    print('\nRepetition Syntax:')
    print('  H*3 = Hire staff 3 times')
    print('  T*5 = End turn 5 times')
    print('  F*2 S*3 = Fundraise twice, then safety research 3 times')
    
    print('\nExample Strategies:')
    examples = parser.generate_example_strings()
    for cmd_str, desc in examples[:5]:  # Show first 5
        print(f'  '{cmd_str}' -> {desc}')


def demonstrate_command_validation():
    '''Show command string validation.'''
    print('\nCommand String Validation')
    print('-' * 30)
    
    parser = CommandStringParser()
    
    test_cases = [
        ('H F S T', 'Valid basic strategy'),
        ('H*3 F*2 T', 'Valid with repetition'),  
        ('X Y Z', 'Invalid commands'),
        ('H*0 F', 'Invalid repetition count'),
        ('', 'Empty string')
    ]
    
    for cmd_str, description in test_cases:
        is_valid, message = parser.validate_command_string(cmd_str)
        status = 'PASS' if is_valid else 'FAIL'
        print(f'  {status} '{cmd_str}' ({description})')
        print(f'      {message}')


def execute_command_string_example(command_string: str, seed: str):
    '''Execute a command string with example game state.'''
    print(f'\nExecuting Command String: '{command_string}'')
    print(f'Seed: {seed}')
    print('-' * 50)
    
    try:
        # Create game state
        print('Creating game state...')
        game_state = GameState(seed)
        
        # Create controller
        controller = CommandStringController(game_state)
        
        # Validate command string first
        is_valid, message = controller.parser.validate_command_string(command_string)
        if not is_valid:
            print(f'ERROR: Invalid command string: {message}')
            return
        
        print(f'Command string is valid: {message}')
        
        # Show expansion
        expanded = controller.parser.expand_command_string(command_string)
        print(f'Expands to {len(expanded)} commands: {' '.join(expanded)}')
        
        # Show initial state
        initial_state = controller._capture_state()
        print(f'\nInitial State (Turn {initial_state['turn']}):')
        print(f'  Money: ${initial_state['money']}')
        print(f'  Staff: {initial_state['staff']}')
        print(f'  Reputation: {initial_state['reputation']}')
        print(f'  Doom: {initial_state['doom']}')
        
        # Execute command string
        print('\nExecuting commands...')
        report = controller.execute_command_string(command_string, seed)
        
        # Show results
        print(f'\nExecution Complete!')
        print(f'Total commands executed: {report.total_commands}')
        print(f'Successful: {report.successful_commands}')
        print(f'Failed: {report.failed_commands}')
        print(f'Execution time: {report.total_execution_time_ms:.1f}ms')
        print(f'Final turn: {report.final_turn}')
        
        # Show final state
        final_state = report.final_state
        print(f'\nFinal State (Turn {final_state['turn']}):')
        print(f'  Money: ${final_state['money']} (?{final_state['money'] - initial_state['money']:+d})')
        print(f'  Staff: {final_state['staff']} (?{final_state['staff'] - initial_state['staff']:+d})')
        print(f'  Reputation: {final_state['reputation']} (?{final_state['reputation'] - initial_state['reputation']:+d})')
        print(f'  Doom: {final_state['doom']} (?{final_state['doom'] - initial_state['doom']:+d})')
        
        # Show command details
        if report.failed_commands > 0:
            print(f'\nFailed Commands:')
            for result in report.command_results:
                if not result.success:
                    print(f'  {result.command_letter} ({result.command}): {result.message}')
        
        # Save report
        report_file = f'command_report_{seed.replace('-', '_')}.json'
        report.save_to_file(report_file)
        print(f'\nDetailed report saved to: {report_file}')
        
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()


def show_strategy_examples():
    '''Show example strategies for different playstyles.'''
    print('\nStrategy Examples')
    print('-' * 30)
    
    strategies = [
        ('Early Economy', 'H*2 F*3 T', 'Build staff and funding foundation'),
        ('Research Focus', 'F S*3 C T H S', 'Prioritize safety research early'),
        ('Balanced Growth', 'H F S C T*2 H F', 'Steady progression across all areas'),
        ('Speed Run', 'T*10', 'Skip to turn 10 quickly'),
        ('Intelligence Heavy', 'I*3 E H F S T', 'Gather opponent information'),
        ('Community Building', 'G*2 P N H F T', 'Focus on reputation and outreach')
    ]
    
    parser = CommandStringParser()
    
    for name, cmd_str, description in strategies:
        print(f'\n{name}: '{cmd_str}'')
        print(f'  Description: {description}')
        
        try:
            expanded = parser.expand_command_string(cmd_str)
            print(f'  Commands: {len(expanded)} actions')
            print(f'  Sequence: {' '.join(expanded)}')
        except ValueError as e:
            print(f'  ERROR: {e}')


def main():
    '''Main entry point.'''
    if len(sys.argv) >= 3:
        # Execute specific command string
        command_string = sys.argv[1]
        seed = sys.argv[2]
        execute_command_string_example(command_string, seed)
    else:
        # Show demonstrations
        demonstrate_basic_usage()
        demonstrate_command_validation()
        show_strategy_examples()
        
        print('\n' + '=' * 50)
        print('To execute a command string:')
        print('  python command_string_example.py \'H*3 F*2 S T\' test-seed')
        print('\nTo test with your own strategies:')
        print('  python command_string_example.py \'Your-Commands-Here\' your-seed')


if __name__ == '__main__':
    main()
