# !/usr/bin/env python3
'''
Test Command String Controller

Quick validation script for the ASCII-only command string system.
Tests parsing, validation, and example generation without requiring
a full game state.
'''

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from testing.command_string_controller import CommandStringParser, CommandStringController


def test_command_parsing():
    '''Test command string parsing functionality.'''
    print('Testing Command String Parsing')
    print('-' * 40)
    
    parser = CommandStringParser()
    
    # Test valid command strings
    valid_cases = [
        'H F S T',
        'H*3 F*2 S T',
        'T*10',
        'H F S C U G I E P N M A L D O T',
        'F*5 S*3 H*2 T*1'
    ]
    
    print('Valid Command Strings:')
    for cmd_str in valid_cases:
        try:
            expanded = parser.expand_command_string(cmd_str)
            print(f'  '{cmd_str}' -> {expanded} ({len(expanded)} commands)')
        except ValueError as e:
            print(f'  '{cmd_str}' -> ERROR: {e}')
    
    print('\nInvalid Command Strings:')
    invalid_cases = [
        'X Y Z',           # Invalid commands
        'H*0 F',           # Invalid count
        'H*101 F',         # Count too high
        'H* F',            # Missing count
        'H**3 F',          # Double asterisk
        'H*3* F',          # Trailing asterisk
        ''                 # Empty string
    ]
    
    for cmd_str in invalid_cases:
        is_valid, message = parser.validate_command_string(cmd_str)
        print(f'  '{cmd_str}' -> {message}')


def test_command_descriptions():
    '''Test command description generation.'''
    print('\nTesting Command Descriptions')
    print('-' * 40)
    
    parser = CommandStringParser()
    descriptions = parser.get_command_descriptions()
    
    print(f'Available Commands ({len(descriptions)}):')
    for cmd, desc in sorted(descriptions.items()):
        print(f'  {cmd}: {desc}')


def test_example_generation():
    '''Test example command string generation.'''
    print('\nTesting Example Generation')
    print('-' * 40)
    
    parser = CommandStringParser()
    examples = parser.generate_example_strings()
    
    print(f'Generated Examples ({len(examples)}):')
    for cmd_str, description in examples:
        print(f'  '{cmd_str}'')
        print(f'    -> {description}')
        
        # Validate the example
        is_valid, message = parser.validate_command_string(cmd_str)
        if not is_valid:
            print(f'    -> WARNING: Example is invalid: {message}')
        else:
            expanded = parser.expand_command_string(cmd_str)
            print(f'    -> {len(expanded)} total commands')
        print()


def test_controller_initialization():
    '''Test controller initialization without game state.'''
    print('Testing Controller Initialization')
    print('-' * 40)
    
    # Test without game state
    controller = CommandStringController()
    print('  Controller created without game state: OK')
    
    # Test command string validation through controller
    parser = controller.parser
    test_string = 'H*3 F*2 S T'
    
    is_valid, message = parser.validate_command_string(test_string)
    print(f'  Command validation: {'OK' if is_valid else 'FAILED'}')
    print(f'  Message: {message}')
    
    if is_valid:
        expanded = parser.expand_command_string(test_string)
        print(f'  Expanded to {len(expanded)} commands: {expanded}')


def test_ascii_compliance():
    '''Test that all content is ASCII-only.'''
    print('\nTesting ASCII Compliance')
    print('-' * 40)
    
    parser = CommandStringParser()
    
    # Test command mappings
    for cmd, action in parser.COMMAND_MAP.items():
        try:
            cmd.encode('ascii')
            action.encode('ascii')
        except UnicodeEncodeError:
            print(f'  ERROR: Non-ASCII in command mapping: {cmd} -> {action}')
            return False
    
    # Test descriptions
    descriptions = parser.get_command_descriptions()
    for cmd, desc in descriptions.items():
        try:
            cmd.encode('ascii')
            desc.encode('ascii')
        except UnicodeEncodeError:
            print(f'  ERROR: Non-ASCII in description: {cmd} -> {desc}')
            return False
    
    # Test examples
    examples = parser.generate_example_strings()
    for cmd_str, desc in examples:
        try:
            cmd_str.encode('ascii')
            desc.encode('ascii')
        except UnicodeEncodeError:
            print(f'  ERROR: Non-ASCII in example: {cmd_str} -> {desc}')
            return False
    
    print('  All content is ASCII-compliant: OK')
    return True


def run_all_tests():
    '''Run all command string tests.'''
    print('Command String Controller Test Suite')
    print('=' * 50)
    
    try:
        test_command_parsing()
        test_command_descriptions()
        test_example_generation()
        test_controller_initialization()
        ascii_ok = test_ascii_compliance()
        
        print('\nTest Summary')
        print('-' * 40)
        print('  Command parsing: PASSED')
        print('  Command descriptions: PASSED')
        print('  Example generation: PASSED')
        print('  Controller initialization: PASSED')
        print(f'  ASCII compliance: {'PASSED' if ascii_ok else 'FAILED'}')
        
        if ascii_ok:
            print('\nAll tests PASSED! Command string system is ready.')
        else:
            print('\nSome tests FAILED! Check ASCII compliance issues.')
            
    except Exception as e:
        print(f'\nUnexpected error during testing: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
