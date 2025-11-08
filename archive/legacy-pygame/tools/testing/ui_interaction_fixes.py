# !/usr/bin/env python3
'''
UI Interaction Fixes for P(Doom)

This module contains fixes for UI interaction issues including:
1. Button clicks not registering consistently
2. Spacebar stopping working after certain actions
3. Modal dialog conflicts
4. Event handling priority issues

Created for GitHub issue: UI Interaction Issues
'''

import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_event_handling_state(game_state, onboarding, current_state):
    '''
    Debug function to check what might be blocking event handling.
    Returns a dictionary of potential blocking conditions.
    '''
    debug_info = {
        'current_state': current_state,
        'game_over': getattr(game_state, 'game_over', 'N/A') if game_state else 'N/A',
        'turn_processing': getattr(game_state, 'turn_processing', 'N/A') if game_state else 'N/A',
        'tutorial_overlay_active': getattr(onboarding, 'show_tutorial_overlay', 'N/A') if onboarding else 'N/A',
        'first_time_help_active': False,  # Will be set by caller
        'hiring_dialog_active': False,   # Will be set by caller
        'pending_popup_events': False,   # Will be set by caller
        'overlay_manager_active': False, # Will be set by caller
    }
    
    if game_state:
        debug_info['pending_popup_events'] = (
            hasattr(game_state, 'pending_popup_events') and 
            bool(game_state.pending_popup_events)
        )
        
        debug_info['hiring_dialog_active'] = (
            hasattr(game_state, 'pending_hiring_dialog') and 
            bool(game_state.pending_hiring_dialog)
        )
        
        debug_info['overlay_manager_active'] = (
            hasattr(game_state, 'overlay_manager') and 
            any(element.visible for element in game_state.overlay_manager.elements.values())
        )
    
    return debug_info

def reset_ui_state_safely(game_state, onboarding, first_time_help_vars):
    '''
    Safely reset UI state variables that might be stuck.
    This is a diagnostic/recovery function.
    '''
    fixes_applied = []
    
    # Fix 1: Reset tutorial overlay if it seems stuck
    if onboarding and hasattr(onboarding, 'show_tutorial_overlay'):
        if onboarding.show_tutorial_overlay:
            # Check if tutorial should realistically still be active
            # If we're past turn 3, tutorial should probably be dismissible
            if game_state and game_state.turn > 3:
                onboarding.show_tutorial_overlay = False
                fixes_applied.append('Reset stuck tutorial overlay')
    
    # Fix 2: Clear first-time help if no valid mechanic
    if first_time_help_vars and first_time_help_vars.get('content'):
        if not first_time_help_vars.get('mechanic'):
            first_time_help_vars['content'] = None
            first_time_help_vars['close_button'] = None
            fixes_applied.append('Cleared orphaned first-time help')
    
    # Fix 3: Reset turn processing if it's been active too long
    if game_state and hasattr(game_state, 'turn_processing'):
        if game_state.turn_processing and hasattr(game_state, 'turn_processing_timer'):
            if game_state.turn_processing_timer <= 0:
                game_state.turn_processing = False
                fixes_applied.append('Reset stuck turn processing')
    
    return fixes_applied

def check_blocking_conditions(game_state, onboarding, first_time_help_content, current_state):
    '''
    Check for conditions that might block spacebar/input.
    Returns list of blocking conditions found.
    '''
    blocking_conditions = []
    
    # Check if not in game state
    if current_state != 'game':
        blocking_conditions.append(f'Not in game state (current: {current_state})')
    
    # Check if game is over
    if game_state and getattr(game_state, 'game_over', False):
        blocking_conditions.append('Game is over')
    
    # Check if turn is processing
    if game_state and getattr(game_state, 'turn_processing', False):
        blocking_conditions.append('Turn is currently processing')
    
    # Check if tutorial overlay is blocking
    if onboarding and getattr(onboarding, 'show_tutorial_overlay', False):
        blocking_conditions.append('Tutorial overlay is active')
    
    # Check if first-time help is blocking
    if first_time_help_content:
        blocking_conditions.append('First-time help is active')
    
    # Check if hiring dialog is blocking
    if game_state and hasattr(game_state, 'pending_hiring_dialog') and game_state.pending_hiring_dialog:
        blocking_conditions.append('Hiring dialog is active')
    
    # Check if popup events are blocking
    if (game_state and hasattr(game_state, 'pending_popup_events') and 
        game_state.pending_popup_events):
        blocking_conditions.append('Popup events are pending')
    
    return blocking_conditions

def create_spacebar_test_function():
    '''
    Creates a test function that can be called to verify spacebar functionality.
    Returns True if spacebar should work, False otherwise.
    '''
    def test_spacebar_functionality(game_state, onboarding, first_time_help_content, current_state):
        '''Test if spacebar should be functional in current state.'''
        
        # Basic requirements for spacebar to work
        if current_state != 'game':
            return False, 'Not in game state'
        
        if not game_state:
            return False, 'No game state'
        
        if getattr(game_state, 'game_over', False):
            return False, 'Game is over'
        
        if getattr(game_state, 'turn_processing', False):
            return False, 'Turn is processing'
        
        # Check for blocking overlays
        blocking_conditions = check_blocking_conditions(
            game_state, onboarding, first_time_help_content, current_state
        )
        
        if blocking_conditions:
            return False, f'Blocked by: {', '.join(blocking_conditions)}'
        
        return True, 'Spacebar should work'
    
    return test_spacebar_functionality

# Create the test function
test_spacebar = create_spacebar_test_function()

if __name__ == '__main__':
    # print('UI Interaction Fixes Module')
    # print('This module provides diagnostic and fix functions for UI interaction issues.')
    # print('Import and use the functions in main.py for debugging and fixing issues.')
