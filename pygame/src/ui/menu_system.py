'''
Menu System Module

Handles all menu rendering functions for P(Doom) UI system.
Extracted from monolithic ui.py for better maintainability.

Functions:
- draw_main_menu: Renders the main menu with navigation
- draw_start_game_submenu: Renders game launch options submenu
- draw_sounds_menu: Renders sound configuration menu
- draw_config_menu: Renders configuration selection menu
- MenuConfig: Configuration class for consolidated menu system
- draw_consolidated_menu: Unified menu renderer with consistent styling
'''

import pygame
from typing import Any, Optional, List
from src.features.visual_feedback import visual_feedback, ButtonState, FeedbackStyle, draw_low_poly_button
from src.services.keyboard_shortcuts import get_main_menu_shortcuts, get_in_game_shortcuts, format_shortcut_list


class MenuConfig:
    '''Configuration class for consolidated menu system.'''
    def __init__(self, 
                 title: str,
                 items: List[str],
                 instructions: Optional[List[str]] = None,
                 subtitle: Optional[str] = None,
                 current_item: Optional[str] = None,
                 show_shortcuts: bool = False,
                 button_style: str = 'normal'):
        self.title = title
        self.items = items
        self.instructions = instructions or ['Use arrow keys or mouse to navigate', 'Press Enter or click to select', 'Press Escape to go back']
        self.subtitle = subtitle
        self.current_item = current_item  # For highlighting current selection (e.g., config menus)
        self.show_shortcuts = show_shortcuts  # Show keyboard shortcuts on sides
        self.button_style = button_style  # 'normal', 'with_descriptions', 'toggle'


def draw_consolidated_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, 
                         config: MenuConfig, descriptions: Optional[List[str]] = None,
                         item_states: Optional[List[str]] = None) -> None:
    '''
    Consolidated menu renderer that handles all menu types with consistent styling.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout  
        selected_item: index of currently selected menu item
        config: MenuConfig object with menu settings
        descriptions: optional list of descriptions for each item (for submenu style)
        item_states: optional list of state indicators for toggle items (e.g., 'ON'/'OFF')
    '''
    # Standard menu fonts - consistent across all menus
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.035))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.025))
    inst_font = pygame.font.SysFont('Consolas', int(h*0.02))
    
    # Clear background
    screen.fill((50, 50, 50))
    
    # Title rendering
    title_surf = title_font.render(config.title, True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.15)
    screen.blit(title_surf, (title_x, title_y))
    
    # Subtitle if provided
    if config.subtitle:
        subtitle_surf = desc_font.render(config.subtitle, True, (200, 200, 200))
        subtitle_x = w // 2 - subtitle_surf.get_width() // 2
        subtitle_y = title_y + title_surf.get_height() + 10
        screen.blit(subtitle_surf, (subtitle_x, subtitle_y))
    
    # Button layout calculations
    button_width = int(w * 0.4)
    button_height = int(h * 0.08)
    start_y = int(h * 0.35) if not config.subtitle else int(h * 0.3)
    spacing = int(h * 0.1) if not descriptions else int(h * 0.08)
    center_x = w // 2
    
    # Render menu items
    for i, item in enumerate(config.items):
        # Calculate button position
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.FOCUSED
        elif config.current_item and item == config.current_item:
            button_state = ButtonState.HOVER  # Highlight current selection
        else:
            button_state = ButtonState.NORMAL
        
        # Append state indicator for toggle items
        display_text = item
        if item_states and i < len(item_states):
            display_text = f'{item}: {item_states[i]}'
        
        # Draw button using appropriate style
        if config.button_style == 'with_descriptions' and descriptions:
            draw_low_poly_button(screen, button_rect, display_text, button_state)
            # Draw description below button
            if i < len(descriptions):
                desc_surf = desc_font.render(descriptions[i], True, (150, 150, 150))
                desc_x = center_x - desc_surf.get_width() // 2
                desc_y = button_y + button_height + 5
                screen.blit(desc_surf, (desc_x, desc_y))
        else:
            visual_feedback.draw_button(screen, button_rect, display_text, button_state, FeedbackStyle.MENU_ITEM)
    
    # Instructions at bottom
    inst_y = int(h * 0.85)
    for i, instruction in enumerate(config.instructions):
        inst_surf = inst_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y + i * int(h * 0.03)))
    
    # Show keyboard shortcuts if enabled (main menu only)
    if config.show_shortcuts:
        shortcut_font = pygame.font.SysFont('Consolas', int(h*0.018))
        
        # Left side - Main Menu shortcuts
        left_shortcuts = get_main_menu_shortcuts()
        left_formatted = format_shortcut_list(left_shortcuts)
        
        left_title_surf = shortcut_font.render('Menu Controls:', True, (160, 160, 160))
        left_x = int(w * 0.05)
        left_y = int(h * 0.25)
        screen.blit(left_title_surf, (left_x, left_y))
        
        for i, shortcut_text in enumerate(left_formatted):
            shortcut_surf = shortcut_font.render(shortcut_text, True, (140, 140, 140))
            screen.blit(shortcut_surf, (left_x, left_y + 30 + i * 25))
        
        # Right side - In-Game shortcuts preview  
        right_shortcuts = get_in_game_shortcuts()[:4]
        right_formatted = format_shortcut_list(right_shortcuts)
        
        right_title_surf = shortcut_font.render('In-Game Controls:', True, (160, 160, 160))
        right_x = int(w * 0.75)
        right_y = int(h * 0.25)
        screen.blit(right_title_surf, (right_x, right_y))
        
        for i, shortcut_text in enumerate(right_formatted):
            shortcut_surf = shortcut_font.render(shortcut_text, True, (140, 140, 140))
            screen.blit(shortcut_surf, (right_x, right_y + 30 + i * 25))


def draw_main_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, sound_manager: Optional[Any] = None) -> None:
    '''
    Draw the main menu with vertically stacked, center-oriented buttons.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected menu item (for keyboard navigation)
        sound_manager: optional SoundManager instance for sound toggle button
    
    Features:
    - Grey background as specified in requirements
    - Centered title and subtitle
    - 5 vertically stacked buttons with distinct visual states:
      * Normal: dark blue with light border
      * Selected: bright blue with white border (keyboard navigation)
      * Inactive: grey (Options button is placeholder)
    - Responsive sizing based on screen dimensions
    - Clear usage instructions at bottom
    - Sound toggle button in bottom right (if sound_manager provided)
    '''
    # Fonts for menu - scale based on screen size
    title_font = pygame.font.SysFont('Consolas', int(h*0.08), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.035))
    
    # Title at top
    title_surf = title_font.render('P(Doom)', True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.15)
    screen.blit(title_surf, (title_x, title_y))
    
    # Subtitle
    subtitle_font = pygame.font.SysFont('Consolas', int(h*0.025))
    subtitle_surf = subtitle_font.render('Bureaucracy Strategy Prototype', True, (200, 200, 200))
    subtitle_x = w // 2 - subtitle_surf.get_width() // 2
    subtitle_y = title_y + title_surf.get_height() + 10
    screen.blit(subtitle_surf, (subtitle_x, subtitle_y))
    
    # Menu items
    menu_items = [
        'Launch Lab',
        'Launch with Custom Seed', 
        'Settings',
        'Player Guide',
        'View Leaderboard',
        'Exit'
    ]
    
    # Button layout
    button_width = int(w * 0.4)
    button_height = int(h * 0.08)
    start_y = int(h * 0.35)
    spacing = int(h * 0.1)
    center_x = w // 2
    
    for i, item in enumerate(menu_items):
        # Calculate button position
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state for visual feedback
        if i == selected_item:
            button_state = ButtonState.FOCUSED  # Use focused state for keyboard navigation
        else:
            button_state = ButtonState.NORMAL
        
        # Use visual feedback system for consistent styling
        visual_feedback.draw_button(
            screen, button_rect, item, button_state, FeedbackStyle.MENU_ITEM
        )
    
    # Instructions at bottom  
    instruction_font = pygame.font.SysFont('Consolas', int(h*0.02))
    instructions = [
        'Use mouse or arrow keys to navigate',
        'Press Enter or click to select', 
        'Press Escape to quit'
    ]
    
    # Add DEV MODE specific instructions if enabled
    try:
        from src.services.dev_mode import is_dev_mode_enabled
        if is_dev_mode_enabled():
            instructions.append('F10 to toggle DEV MODE')
    except ImportError:
        pass
    
    for i, instruction in enumerate(instructions):
        inst_surf = instruction_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        inst_y = int(h * 0.85) + i * int(h * 0.03)
        screen.blit(inst_surf, (inst_x, inst_y))
    
    # Draw keyboard shortcuts on the sides
    shortcut_font = pygame.font.SysFont('Consolas', int(h*0.018))
    
    # Left side - Main Menu shortcuts
    left_shortcuts = get_main_menu_shortcuts()
    left_formatted = format_shortcut_list(left_shortcuts)
    
    left_title_surf = shortcut_font.render('Menu Controls:', True, (160, 160, 160))
    left_x = int(w * 0.05)
    left_y = int(h * 0.25)
    screen.blit(left_title_surf, (left_x, left_y))
    
    for i, shortcut_text in enumerate(left_formatted):
        shortcut_surf = shortcut_font.render(shortcut_text, True, (140, 140, 140))
        screen.blit(shortcut_surf, (left_x, left_y + 30 + i * 25))
    
    # Right side - In-Game shortcuts preview
    right_shortcuts = get_in_game_shortcuts()[:4]  # Show first 4 to fit space
    right_formatted = format_shortcut_list(right_shortcuts)
    
    right_title_surf = shortcut_font.render('In-Game Controls:', True, (160, 160, 160))
    right_x = int(w * 0.75)
    right_y = int(h * 0.25)
    screen.blit(right_title_surf, (right_x, right_y))
    
    for i, shortcut_text in enumerate(right_formatted):
        shortcut_surf = shortcut_font.render(shortcut_text, True, (140, 140, 140))
        screen.blit(shortcut_surf, (right_x, right_y + 30 + i * 25))
    
    # Draw sound toggle button if sound manager is available (Issue #89)
    if sound_manager:
        # Import here to avoid circular dependency
        from ui import draw_mute_button_standalone
        draw_mute_button_standalone(screen, sound_manager, w, h)
    
    # Draw DEV MODE indicator (top-left) and version (bottom-right)
    # Import here to avoid circular dependency
    from ui import draw_dev_mode_indicator, draw_version_footer
    draw_dev_mode_indicator(screen, w, h)
    draw_version_footer(screen, w, h)


def draw_start_game_submenu(screen: pygame.Surface, w: int, h: int, selected_item: int) -> None:
    '''Draw the start game submenu with different game launch options.'''
    # Clear background
    screen.fill((50, 50, 50))
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.03))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.022))
    
    # Title
    title_surf = title_font.render('Start Game', True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.15)
    screen.blit(title_surf, (title_x, title_y))
    
    # Subtitle
    subtitle_text = 'Choose your starting configuration:'
    subtitle_surf = desc_font.render(subtitle_text, True, (200, 200, 200))
    subtitle_x = w // 2 - subtitle_surf.get_width() // 2
    subtitle_y = title_y + title_surf.get_height() + 10
    screen.blit(subtitle_surf, (subtitle_x, subtitle_y))
    
    # Menu items with descriptions
    items_with_desc = [
        ('Basic New Game (Default Global Seed)', 'Quick start with weekly seed - zero configuration'),
        ('Configure Game / Custom Seed', 'Choose your own seed for reproducible games'), 
        ('Config Settings', 'Modify game difficulty and starting resources'),
        ('Game Options', 'Audio, display, and accessibility settings')
    ]
    
    # Button layout
    button_width = int(w * 0.5)
    button_height = int(h * 0.08)
    start_y = int(h * 0.3)
    spacing = int(h * 0.1)
    center_x = w // 2
    
    for i, (item, description) in enumerate(items_with_desc):
        # Calculate button position
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.FOCUSED
        else:
            button_state = ButtonState.NORMAL
        
        # Draw button
        draw_low_poly_button(screen, button_rect, item, button_state)
        
        # Draw description below button
        desc_surf = desc_font.render(description, True, (150, 150, 150))
        desc_x = center_x - desc_surf.get_width() // 2
        desc_y = button_y + button_height + 5
        screen.blit(desc_surf, (desc_x, desc_y))
    
    # Instructions
    inst_font = pygame.font.SysFont('Consolas', int(h*0.02))
    instructions = [
        'Use arrow keys or mouse to navigate',
        'Press Enter or click to select ? Press Escape to go back'
    ]
    
    inst_y = int(h * 0.85)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 5


def draw_sounds_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, game_state: Optional[Any] = None) -> None:
    '''
    Draw the sounds options menu with toggles for individual sound effects.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected menu item (for keyboard navigation)
        game_state: game state object to access sound manager (can be None for standalone testing)
    
    Features:
    - Master sound on/off toggle
    - Individual sound effect toggles (money spend, AP spend, blob, error beep)
    - Back button to return to main menu
    - Responsive sizing and keyboard navigation
    '''
    # Fonts for menu - scale based on screen size
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.03))
    
    # Title at top
    title_surf = title_font.render('Sound Options', True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.15)
    screen.blit(title_surf, (title_x, title_y))
    
    # Get sound manager if available
    sound_manager = None
    if game_state and hasattr(game_state, 'sound_manager'):
        sound_manager = game_state.sound_manager
    
    # Menu items with their current states
    master_enabled = sound_manager.is_enabled() if sound_manager else True
    
    menu_items = [
        f'Master Sound: {'ON' if master_enabled else 'OFF'}',
        f'Money Spend Sound: {'ON' if (sound_manager and sound_manager.is_sound_enabled('money_spend')) else 'OFF'}',
        f'Action Points Sound: {'ON' if (sound_manager and sound_manager.is_sound_enabled('ap_spend')) else 'OFF'}',
        f'Employee Hire Sound: {'ON' if (sound_manager and sound_manager.is_sound_enabled('blob')) else 'OFF'}',
        f'Error Beep Sound: {'ON' if (sound_manager and sound_manager.is_sound_enabled('error_beep')) else 'OFF'}',
        'Back to Main Menu'
    ]
    
    # Button layout
    button_width = int(w * 0.5)
    button_height = int(h * 0.06)
    start_y = int(h * 0.3)
    spacing = int(h * 0.08)
    center_x = w // 2
    
    for i, item in enumerate(menu_items):
        # Calculate button position
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state for visual feedback
        if i == selected_item:
            button_state = ButtonState.FOCUSED  # Use focused state for keyboard navigation
        else:
            button_state = ButtonState.NORMAL
        
        # Use visual feedback system for consistent styling
        visual_feedback.draw_button(
            screen, button_rect, item, button_state, FeedbackStyle.MENU_ITEM
        )
    
    # Instructions at bottom
    instruction_font = pygame.font.SysFont('Consolas', int(h*0.02))
    instructions = [
        'Use arrow keys to navigate, Enter to toggle',
        'Press Escape or select Back to return to Main Menu'
    ]
    
    for i, instruction in enumerate(instructions):
        inst_surf = instruction_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        inst_y = int(h * 0.85) + i * 25
        screen.blit(inst_surf, (inst_x, inst_y))


def draw_config_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, configs: List[str], current_config_name: str) -> None:
    '''
    Draw the configuration selection menu showing available game configurations.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected menu item
        configs: list of available configuration names
        current_config_name: name of currently selected configuration
    '''
    # Fonts for menu - scale based on screen size
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.03))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.02))
    
    # Title at top
    title_surf = title_font.render('Configuration Selection', True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.12)
    screen.blit(title_surf, (title_x, title_y))
    
    # Subtitle showing current config
    subtitle_text = f'Current: {current_config_name}'
    subtitle_surf = desc_font.render(subtitle_text, True, (200, 200, 200))
    subtitle_x = w // 2 - subtitle_surf.get_width() // 2
    subtitle_y = title_y + title_surf.get_height() + 10
    screen.blit(subtitle_surf, (subtitle_x, subtitle_y))
    
    # Menu items - configs plus back option
    menu_items = configs + ['Back to Main Menu']
    
    # Button layout
    button_width = int(w * 0.5)
    button_height = int(h * 0.06)
    start_y = int(h * 0.25)
    spacing = int(h * 0.07)
    center_x = w // 2
    
    for i, item in enumerate(menu_items):
        # Calculate button position
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.FOCUSED
        elif i < len(configs) and item == current_config_name:
            button_state = ButtonState.ACTIVE  # Highlight current config
        else:
            button_state = ButtonState.NORMAL
        
        # Format config name for display
        display_text = item.replace('.json', '').replace('_', ' ').title()
        
        # Use visual feedback system for consistent styling
        visual_feedback.draw_button(
            screen, button_rect, display_text, button_state, FeedbackStyle.MENU_ITEM
        )
    
    # Instructions at bottom
    instruction_font = pygame.font.SysFont('Consolas', int(h*0.018))
    instructions = [
        'Select a configuration to change game difficulty and starting resources',
        'Use arrow keys to navigate, Enter to select',
        'Press Escape or select Back to return to Main Menu'
    ]
    
    inst_y = int(h * 0.8)
    for instruction in instructions:
        inst_surf = instruction_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 5
