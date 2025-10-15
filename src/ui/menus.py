'''
Menu screen rendering for the P(Doom) game interface.

This module contains all the menu-related drawing functions including
main menu, settings menus, and configuration screens.
'''

from typing import Union, Optional, Dict, Any

import pygame
from src.features.visual_feedback import visual_feedback, ButtonState, FeedbackStyle, draw_low_poly_button
from src.services.keyboard_shortcuts import get_main_menu_shortcuts, get_in_game_shortcuts, format_shortcut_list


def get_research_intensity_display(difficulty: str) -> str:
    '''Convert difficulty setting to bureaucratic terminology.'''
    mapping = {
        'EASY': 'CONSERVATIVE',
        'STANDARD': 'REGULATORY',
        'HARD': 'AGGRESSIVE',
        'DUMMY': 'REGULATORY'
    }
    return mapping.get(difficulty, 'REGULATORY')


def get_volume_display(volume: Union[str, int]) -> str:
    '''Convert volume to descriptive levels.'''
    if isinstance(volume, str) or volume == 123:  # Handle dummy value
        volume = 80
    if volume >= 90:
        return 'MAXIMUM'
    elif volume >= 70:
        return 'HIGH'
    elif volume >= 50:
        return 'MODERATE'
    elif volume >= 30:
        return 'LOW'
    else:
        return 'MINIMAL'


def get_graphics_display(quality: str) -> str:
    '''Convert graphics quality to bureaucratic terms.'''
    mapping = {
        'LOW': 'EFFICIENT', 
        'STANDARD': 'COMPLIANT',
        'HIGH': 'ENHANCED',
        'DUMMY': 'COMPLIANT'
    }
    return mapping.get(quality, 'COMPLIANT')


def get_safety_display(safety_level: str) -> str:
    '''Safety protocol levels for the bureaucratic theme.'''
    mapping = {
        'MINIMAL': 'MINIMAL',
        'STANDARD': 'STANDARD', 
        'ENHANCED': 'ENHANCED',
        'MAXIMUM': 'MAXIMUM',
        'DUMMY': 'STANDARD'
    }
    return mapping.get(safety_level, 'STANDARD')


def draw_enhanced_continue_button(screen: pygame.Surface, rect: pygame.Rect, text: str, button_state: ButtonState) -> None:
    '''Draw the continue button with special highlighting.'''
    # Enhanced colors for the continue button
    if button_state == ButtonState.FOCUSED:
        bg_color = (60, 120, 80)
        border_color = (100, 200, 120)
        text_color = (255, 255, 255)
    else:
        bg_color = (40, 80, 60)
        border_color = (80, 160, 100)
        text_color = (220, 255, 220)
    
    # Draw button background with rounded corners
    pygame.draw.rect(screen, bg_color, rect, border_radius=8)
    pygame.draw.rect(screen, border_color, rect, width=3, border_radius=8)
    
    # Draw text centered
    font = pygame.font.SysFont('Consolas', int(rect.height * 0.35), bold=True)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)


def draw_bureaucratic_setting_button(screen: pygame.Surface, rect: pygame.Rect, text: str, button_state: ButtonState, setting_name: str) -> None:
    '''Draw setting buttons with bureaucratic styling.'''
    # Color scheme based on button state
    if button_state == ButtonState.FOCUSED:
        bg_color = (50, 70, 90)
        border_color = (120, 160, 200)
        text_color = (255, 255, 255)
        accent_color = (200, 220, 255)
    else:
        bg_color = (35, 50, 65)
        border_color = (80, 100, 120)
        text_color = (200, 220, 240)
        accent_color = (150, 170, 190)
    
    # Draw button background
    pygame.draw.rect(screen, bg_color, rect, border_radius=6)
    pygame.draw.rect(screen, border_color, rect, width=2, border_radius=6)
    
    # Add small icon/indicator for the setting type
    icon_x = rect.x + 15
    icon_y = rect.centery
    if 'Research' in setting_name:
        pygame.draw.circle(screen, accent_color, (icon_x, icon_y), 4)
    elif 'Audio' in setting_name:
        pygame.draw.polygon(screen, accent_color, [(icon_x-3, icon_y-3), (icon_x+3, icon_y), (icon_x-3, icon_y+3)])
    elif 'Visual' in setting_name:
        pygame.draw.rect(screen, accent_color, (icon_x-3, icon_y-3, 6, 6))
    elif 'Safety' in setting_name:
        pygame.draw.polygon(screen, accent_color, [(icon_x, icon_y-4), (icon_x-3, icon_y+2), (icon_x+3, icon_y+2)])
    
    # Draw text with proper spacing
    font = pygame.font.SysFont('Consolas', int(rect.height * 0.32))
    text_surf = font.render(text, True, text_color)
    text_x = rect.x + 35  # Account for icon space
    text_y = rect.centery - text_surf.get_height() // 2
    screen.blit(text_surf, (text_x, text_y))


def draw_mute_button_standalone(screen: pygame.Surface, sound_manager: Any, w: int, h: int) -> pygame.Rect:
    '''
    Draw a standalone mute button for menus.
    
    Args:
        screen: pygame surface to draw on
        sound_manager: sound manager instance
        w, h: screen dimensions
    '''
    button_size = int(min(w, h) * 0.04)
    margin = 20
    button_x = w - button_size - margin
    button_y = h - button_size - margin
    
    button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
    
    # Button background
    pygame.draw.circle(screen, (70, 70, 70), 
                      (button_x + button_size//2, button_y + button_size//2), 
                      button_size//2)
    pygame.draw.circle(screen, (255, 255, 255), 
                      (button_x + button_size//2, button_y + button_size//2), 
                      button_size//2, 2)
    
    # Mute/unmute icon
    if sound_manager and sound_manager.is_enabled():
        # Speaker icon
        pygame.draw.polygon(screen, (255, 255, 255), [
            (button_x + button_size//4, button_y + button_size//3),
            (button_x + button_size//2, button_y + button_size//3),
            (button_x + 3*button_size//4, button_y + button_size//6),
            (button_x + 3*button_size//4, button_y + 5*button_size//6),
            (button_x + button_size//2, button_y + 2*button_size//3),
            (button_x + button_size//4, button_y + 2*button_size//3)
        ])
    else:
        # Muted speaker with X
        pygame.draw.polygon(screen, (255, 100, 100), [
            (button_x + button_size//4, button_y + button_size//3),
            (button_x + button_size//2, button_y + button_size//3),
            (button_x + 3*button_size//4, button_y + button_size//6),
            (button_x + 3*button_size//4, button_y + 5*button_size//6),
            (button_x + button_size//2, button_y + 2*button_size//3),
            (button_x + button_size//4, button_y + 2*button_size//3)
        ])
        # X mark
        pygame.draw.line(screen, (255, 100, 100), 
                        (button_x + 2, button_y + 2),
                        (button_x + button_size - 2, button_y + button_size - 2), 3)
        pygame.draw.line(screen, (255, 100, 100),
                        (button_x + button_size - 2, button_y + 2),
                        (button_x + 2, button_y + button_size - 2), 3)
    
    return button_rect


def draw_version_footer(screen: pygame.Surface, w: int, h: int, font: Optional[pygame.font.Font] = None) -> None:
    '''
    Draw version information in bottom right corner.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen dimensions
        font: optional font to use
    '''
    from src.services.version import get_display_version
    
    if font is None:
        font = pygame.font.SysFont('Consolas', int(h*0.02))
    
    version_text = get_display_version()
    version_surf = font.render(version_text, True, (120, 120, 120))
    
    # Position in bottom right with margin
    margin = 10
    version_x = w - version_surf.get_width() - margin
    version_y = h - version_surf.get_height() - margin
    
    screen.blit(version_surf, (version_x, version_y))


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
        draw_mute_button_standalone(screen, sound_manager, w, h)
    
    # Draw version in bottom right corner
    draw_version_footer(screen, w, h)


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


def draw_config_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, configs: list[str], current_config_name: str) -> None:
    '''
    Draw the configuration selection menu.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected config item
        configs: list of available config names
        current_config_name: name of currently active config
    '''
    # Clear screen with grey background
    screen.fill((64, 64, 64))
    
    # Fonts for menu - scale based on screen size
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    menu_font = pygame.font.SysFont('Consolas', int(h*0.035))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.025))
    
    # Title at top
    title_surf = title_font.render('Configuration Selection', True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.1)
    screen.blit(title_surf, (title_x, title_y))
    
    # Current config indicator
    current_surf = desc_font.render(f'Current: {current_config_name}', True, (200, 200, 200))
    current_x = w // 2 - current_surf.get_width() // 2
    current_y = title_y + title_surf.get_height() + 10
    screen.blit(current_surf, (current_x, current_y))
    
    # Menu items (configs + back button)
    all_items = configs + ['? Back to Main Menu']
    
    button_width = int(w * 0.4)
    button_height = int(h * 0.06)
    start_y = int(h * 0.25)
    
    for i, item in enumerate(all_items):
        y = start_y + i * int(button_height + h * 0.02)
        x = w // 2 - button_width // 2
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.SELECTED
        elif item == current_config_name:
            button_state = ButtonState.ACTIVE  # Different color for current config
        else:
            button_state = ButtonState.NORMAL
        
        # Draw button
        draw_low_poly_button(screen, x, y, button_width, button_height, 
                           item, menu_font, button_state)
    
    # Instructions at bottom
    instructions = [
        '?/? or mouse to navigate',
        'Enter or click to select configuration',
        'Escape to go back'
    ]
    
    for i, inst in enumerate(instructions):
        inst_surf = desc_font.render(inst, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        inst_y = int(h * 0.8) + i * int(h * 0.04)
        screen.blit(inst_surf, (inst_x, inst_y))


def draw_pre_game_settings(screen: pygame.Surface, w: int, h: int, settings: Dict[str, Any], selected_item: int, sound_manager: Optional[Any] = None) -> None:
    '''
    Draw the Laboratory Configuration screen with P(Doom) bureaucracy theme.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        settings: dictionary of current settings values
        selected_item: index of currently selected setting (for keyboard navigation)
        sound_manager: optional SoundManager instance for sound toggle button
    '''
    # Enhanced background with subtle gradient effect
    screen.fill((25, 35, 45))
    
    # Add subtle background pattern for bureaucratic feel
    pattern_color = (35, 45, 55)
    for i in range(0, w, 40):
        pygame.draw.line(screen, pattern_color, (i, 0), (i, h), 1)
    for i in range(0, h, 40):
        pygame.draw.line(screen, pattern_color, (0, i), (w, i), 1)
    
    # Fonts with better hierarchy
    title_font = pygame.font.SysFont('Consolas', int(h*0.055), bold=True)
    subtitle_font = pygame.font.SysFont('Consolas', int(h*0.025))
    pygame.font.SysFont('Consolas', int(h*0.028))
    
    # Laboratory Configuration Header
    title_surf = title_font.render('LABORATORY CONFIGURATION', True, (220, 240, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.12)
    screen.blit(title_surf, (title_x, title_y))
    
    # Subtitle with bureaucratic flair
    subtitle_surf = subtitle_font.render('Initialize Research Parameters & Operating Procedures', True, (180, 200, 220))
    subtitle_x = w // 2 - subtitle_surf.get_width() // 2
    subtitle_y = title_y + title_surf.get_height() + 5
    screen.blit(subtitle_surf, (subtitle_x, subtitle_y))
    
    # Enhanced settings with realistic options (must match click handling expectations)
    settings_options = [
        ('Continue', '? INITIALIZE LABORATORY'),  # Index 0 - Continue button
        ('Player Name', settings.get('player_name', 'Researcher')),  # Index 1 - Player Name
        ('Lab Name', settings.get('lab_name', 'AI Safety Lab')),  # Index 2 - Lab Name
        ('Research Intensity', get_research_intensity_display(settings.get('difficulty', 'STANDARD'))),  # Index 3
        ('Audio Alerts Volume', get_volume_display(settings.get('sound_volume', 80))),  # Index 4
        ('Visual Enhancement', get_graphics_display(settings.get('graphics_quality', 'STANDARD'))),  # Index 5
        ('Safety Protocol Level', get_safety_display(settings.get('safety_level', 'STANDARD')))  # Index 6
    ]
    
    # Improved button layout with more space
    button_width = int(w * 0.55)
    button_height = int(h * 0.07)
    start_y = int(h * 0.32)
    spacing = int(h * 0.085)
    center_x = w // 2
    
    for i, (setting_name, setting_value) in enumerate(settings_options):
        # Calculate button position
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state with enhanced colors
        if i == selected_item:
            button_state = ButtonState.FOCUSED
        else:
            button_state = ButtonState.NORMAL
        
        # Format text for display
        if i == 0:  # Continue button with special styling
            text = setting_value
        else:  # Setting items with values
            text = f'{setting_name}: {setting_value}'
        
        # Draw enhanced button
        if i == 0:  # Continue button gets special treatment
            draw_enhanced_continue_button(screen, button_rect, text, button_state)
        else:
            draw_bureaucratic_setting_button(screen, button_rect, text, button_state, setting_name)
    
    # Enhanced instructions with bureaucratic theme
    inst_font = pygame.font.SysFont('Consolas', int(h*0.022))
    instructions = [
        '[LIST] Use ?? arrow keys to navigate configuration options',
        '? Press ENTER to modify settings or initialize laboratory',
        '[WARNING]?  Ensure all parameters meet institutional safety standards'
    ]
    
    inst_y = int(h * 0.82)
    for i, instruction in enumerate(instructions):
        color = (200, 220, 240) if i < 2 else (255, 200, 150)  # Warning color for safety note
        inst_surf = inst_font.render(instruction, True, color)
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 3
    
    # Draw sound toggle button if sound manager is available (Issue #89)
    if sound_manager:
        draw_mute_button_standalone(screen, sound_manager, w, h)


def draw_audio_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, audio_settings: Dict[str, Any], sound_manager: Any) -> None:
    '''
    Draw the audio settings menu.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height
        selected_item: index of currently selected menu item
        audio_settings: dictionary of current audio settings
        sound_manager: SoundManager instance for current state
    '''
    # Background
    screen.fill((40, 45, 55))
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h*0.055), bold=True)
    title_surf = title_font.render('Audio Settings', True, (220, 240, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.12)
    screen.blit(title_surf, (title_x, title_y))
    
    # Menu items
    pygame.font.SysFont('Consolas', int(h*0.03))
    button_width = int(w * 0.6)
    button_height = int(h * 0.06)
    start_y = int(h * 0.25)
    spacing = int(h * 0.08)
    center_x = w // 2
    
    # Audio menu items with current values
    master_status = 'Enabled' if audio_settings.get('master_enabled', True) else 'Disabled'
    sfx_volume = audio_settings.get('sfx_volume', 80)
    
    menu_items = [
        f'Master Sound: {master_status}',
        f'SFX Volume: {sfx_volume}%',
        'Sound Effects Settings',
        'Test Sound',
        '? Back to Main Menu'
    ]
    
    for i, item in enumerate(menu_items):
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.FOCUSED
        else:
            button_state = ButtonState.NORMAL
        
        # Draw button with text
        draw_low_poly_button(screen, button_rect, item, button_state)
    
    # Instructions
    inst_font = pygame.font.SysFont('Consolas', int(h*0.02))
    instructions = [
        'Use arrow keys to navigate, Enter/Space to select',
        'Left/Right arrows adjust volume settings',
        'Escape to return to main menu'
    ]
    
    inst_y = int(h * 0.75)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 3
    
    # Additional info about sound effects
    if selected_item == 2:
        info_font = pygame.font.SysFont('Consolas', int(h*0.018))
        info_text = 'Individual sound toggles: Click to cycle through sound effects'
        info_surf = info_font.render(info_text, True, (150, 200, 150))
        info_x = w // 2 - info_surf.get_width() // 2
        info_y = int(h * 0.85)
        screen.blit(info_surf, (info_x, info_y))


def draw_start_game_submenu(screen, w, h, selected_item):
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