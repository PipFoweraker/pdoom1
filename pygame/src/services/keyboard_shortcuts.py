'''
Centralized keyboard shortcuts definitions for P(Doom) game.
This module provides consistent keyboard shortcut information across the UI.
'''

# Main Menu Keyboard Shortcuts
MAIN_MENU_SHORTCUTS = [
    ('??', 'Navigate menu'),
    ('Enter', 'Select option'),
    ('Esc', 'Exit game'),
    ('Mouse', 'Click to select'),
]

# In-Game Keyboard Shortcuts  
IN_GAME_SHORTCUTS = [
    ('1-9', 'Execute actions'),
    ('Space', 'End turn'),
    ('H', 'Help guide'),
    ('Esc', 'Quit to menu'),
    ('??', 'Scroll event log'),
]

# Additional shortcuts for context
ADDITIONAL_SHORTCUTS = [
    ('Mouse', 'Hover for tooltips'),
    ('Click', 'Final score menu'),
]

def get_main_menu_shortcuts():
    '''Get keyboard shortcuts for the main menu screen.'''
    return MAIN_MENU_SHORTCUTS

def get_in_game_shortcuts():
    '''Get keyboard shortcuts for the in-game screen.''' 
    return IN_GAME_SHORTCUTS

def get_all_shortcuts():
    '''Get all keyboard shortcuts organized by context.'''
    return {
        'main_menu': MAIN_MENU_SHORTCUTS,
        'in_game': IN_GAME_SHORTCUTS,
        'additional': ADDITIONAL_SHORTCUTS
    }

def format_shortcut_list(shortcuts, max_width=None):
    '''
    Format a list of shortcuts for display.
    
    Args:
        shortcuts: List of (key, description) tuples
        max_width: Optional maximum width for text wrapping
        
    Returns:
        List of formatted strings ready for rendering
    '''
    formatted = []
    for key, desc in shortcuts:
        formatted.append(f'{key:>6}: {desc}')
    return formatted