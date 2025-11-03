'''
Audio UI Components Module

Extracted from ui.py monolith for modular architecture.
Contains all sound-related UI components:
- Sound settings menus
- Mute buttons and toggles  
- Audio configuration interfaces
- Sound effect controls

This module handles the visual representation of audio controls,
while src.services.sound_manager handles the actual audio playback.
'''

from typing import Any, Dict, Optional
import pygame


def draw_sounds_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, game_state: Optional[Any] = None) -> None:
    '''
    Draw the sounds options menu with toggles for individual sound effects.
    
    Args:
        screen: pygame surface to draw on
        w: screen width 
        h: screen height
        selected_item: currently selected menu item index
        game_state: game state object to access sound manager (can be None for standalone testing)
        
    Features:
    - Master sound on/off toggle
    - Individual sound effect toggles (money spend, AP spend, blob, error beep)
    - Real-time preview of sound settings
    - Consistent with overall game UI theme
    '''
    # Clear screen with dark background
    screen.fill((20, 20, 30))
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title_surf = title_font.render('Sound Options', True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(w // 2, h // 6))
    screen.blit(title_surf, title_rect)
    
    # Get sound manager if available
    sound_manager = None
    if game_state and hasattr(game_state, 'sound_manager'):
        sound_manager = game_state.sound_manager
    
    # Menu items with current status
    menu_font = pygame.font.Font(None, 32)
    items = [
        ('Master Audio', 'Toggle all game sounds'),
        ('Money Spend Sound', 'Sound when spending money'),  
        ('Action Point Sound', 'Sound when spending action points'),
        ('Blob Sound', 'Notification and feedback sounds'),
        ('Error Beep', 'Warning and error sounds'),
        ('Popup Sounds', 'Menu open/close sounds'),
        ('Milestone Sound', 'Achievement and milestone completions'),
        ('Warning Sound', 'High doom and caution alerts'),
        ('Danger Sound', 'Critical doom and emergency alerts'),
        ('Success Sound', 'Action completions and positive events'),
        ('Research Complete', 'Major research milestone completions'),
        ('Back', 'Return to main menu')
    ]
    
    start_y = h // 3
    spacing = 60
    
    for i, (item_text, description) in enumerate(items):
        # Determine if this item is enabled
        enabled = True
        if sound_manager and i < len(items) - 1:  # Not 'Back' option
            if i == 0:  # Master Audio
                enabled = sound_manager.is_enabled()
            elif i == 1:  # Money Spend
                enabled = sound_manager.sound_toggles.get('money_spend', True)
            elif i == 2:  # Action Point
                enabled = sound_manager.sound_toggles.get('ap_spend', True) 
            elif i == 3:  # Blob Sound
                enabled = sound_manager.sound_toggles.get('blob', True)
            elif i == 4:  # Error Beep
                enabled = sound_manager.sound_toggles.get('error_beep', True)
            elif i == 5:  # Popup Sounds
                enabled = sound_manager.sound_toggles.get('popup_open', True)
            elif i == 6:  # Milestone Sound
                enabled = sound_manager.sound_toggles.get('milestone', True)
            elif i == 7:  # Warning Sound
                enabled = sound_manager.sound_toggles.get('warning', True)
            elif i == 8:  # Danger Sound
                enabled = sound_manager.sound_toggles.get('danger', True)
            elif i == 9:  # Success Sound
                enabled = sound_manager.sound_toggles.get('success', True)
            elif i == 10:  # Research Complete
                enabled = sound_manager.sound_toggles.get('research_complete', True)
        
        # Color based on selection and enabled state
        if i == selected_item:
            color = (255, 255, 100)  # Bright yellow for selected
            bg_color = (60, 60, 80)
        else:
            color = (200, 200, 200) if enabled else (100, 100, 100)
            bg_color = None
            
        # Status indicator for toggles
        status = ''
        if i < len(items) - 1:  # Not 'Back' option
            status = ' [ON]' if enabled else ' [OFF]'
            
        # Draw background highlight for selected item
        if bg_color:
            item_rect = pygame.Rect(w // 4, start_y + i * spacing - 10, w // 2, 40)
            pygame.draw.rect(screen, bg_color, item_rect)
            
        # Draw main item text
        full_text = item_text + status
        text_surf = menu_font.render(full_text, True, color)
        text_rect = text_surf.get_rect(center=(w // 2, start_y + i * spacing))
        screen.blit(text_surf, text_rect)
        
        # Draw description for selected item
        if i == selected_item and description:
            desc_font = pygame.font.Font(None, 24)
            desc_surf = desc_font.render(description, True, (150, 150, 150))
            desc_rect = desc_surf.get_rect(center=(w // 2, start_y + i * spacing + 25))
            screen.blit(desc_surf, desc_rect)
    
    # Instructions
    instruction_font = pygame.font.Font(None, 24)
    instructions = [
        'Use UP/DOWN arrows to navigate',
        'Press ENTER to toggle settings',
        'Press ESC to go back'
    ]
    
    inst_y = h - 120
    for instruction in instructions:
        inst_surf = instruction_font.render(instruction, True, (120, 120, 120))
        inst_rect = inst_surf.get_rect(center=(w // 2, inst_y))
        screen.blit(inst_surf, inst_rect)
        inst_y += 30


def draw_mute_button(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    '''
    Draw a mute button in the bottom right corner.
    
    Args:
        screen: pygame surface to draw on
        game_state: game state object with sound_manager
        w: screen width
        h: screen height
    '''
    if not hasattr(game_state, 'sound_manager'):
        return
        
    sound_manager = game_state.sound_manager
    draw_mute_button_standalone(screen, sound_manager, w, h)


def draw_mute_button_standalone(screen: pygame.Surface, sound_manager, w: int, h: int) -> None:
    '''
    Draw a standalone mute button in the bottom right corner.
    
    Args:
        screen: pygame surface to draw on  
        sound_manager: SoundManager instance
        w: screen width
        h: screen height
    '''
    if not sound_manager:
        return
        
    button_size = 40
    margin = 10
    button_x = w - button_size - margin
    button_y = h - button_size - margin
    
    # Button background
    button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
    button_color = (100, 100, 100) if sound_manager.is_enabled() else (150, 50, 50)
    pygame.draw.rect(screen, button_color, button_rect)
    pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)
    
    # Sound icon (simplified speaker representation)
    center_x = button_x + button_size // 2
    center_y = button_y + button_size // 2
    
    if sound_manager.is_enabled():
        # Speaker shape when enabled
        pygame.draw.polygon(screen, (255, 255, 255), [
            (center_x - 8, center_y - 5),
            (center_x - 4, center_y - 5), 
            (center_x + 2, center_y - 10),
            (center_x + 2, center_y + 10),
            (center_x - 4, center_y + 5),
            (center_x - 8, center_y + 5)
        ])
        # Sound waves
        pygame.draw.arc(screen, (255, 255, 255), 
                       pygame.Rect(center_x + 4, center_y - 6, 8, 12), 
                       -0.5, 0.5, 2)
    else:
        # Crossed out speaker when muted
        pygame.draw.polygon(screen, (255, 255, 255), [
            (center_x - 8, center_y - 5),
            (center_x - 4, center_y - 5),
            (center_x + 2, center_y - 10), 
            (center_x + 2, center_y + 10),
            (center_x - 4, center_y + 5),
            (center_x - 8, center_y + 5)
        ])
        # X mark over speaker
        pygame.draw.line(screen, (255, 100, 100), 
                        (center_x - 10, center_y - 10), 
                        (center_x + 10, center_y + 10), 3)
        pygame.draw.line(screen, (255, 100, 100),
                        (center_x - 10, center_y + 10),
                        (center_x + 10, center_y - 10), 3)


def draw_audio_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, 
                   audio_settings: Dict[str, Any], sound_manager) -> None:
    '''
    Draw the audio configuration menu.
    
    Args:
        screen: pygame surface to draw on
        w: screen width
        h: screen height  
        selected_item: currently selected menu item index
        audio_settings: dictionary of audio configuration settings
        sound_manager: SoundManager instance for real-time control
    '''
    # Clear screen
    screen.fill((20, 20, 30))
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title_surf = title_font.render('Audio Settings', True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(w // 2, h // 6))
    screen.blit(title_surf, title_rect)
    
    # Menu items
    menu_font = pygame.font.Font(None, 32)
    items = [
        ('Master Volume', f'{audio_settings.get('master_volume', 100)}%'),
        ('Sound Effects', 'ON' if audio_settings.get('sound_enabled', True) else 'OFF'),
        ('UI Sounds', 'ON' if audio_settings.get('ui_sounds', True) else 'OFF'), 
        ('Test Sound', 'Play test sound'),
        ('Reset to Defaults', 'Restore default audio settings'),
        ('Back', 'Return to previous menu')
    ]
    
    start_y = h // 3
    spacing = 60
    
    for i, (item_text, value_text) in enumerate(items):
        # Color based on selection
        if i == selected_item:
            color = (255, 255, 100)  # Bright yellow for selected
            bg_color = (60, 60, 80)
        else:
            color = (200, 200, 200)
            bg_color = None
            
        # Draw background highlight for selected item
        if bg_color:
            item_rect = pygame.Rect(w // 4, start_y + i * spacing - 10, w // 2, 40)
            pygame.draw.rect(screen, bg_color, item_rect)
            
        # Draw item text
        text_surf = menu_font.render(item_text, True, color)
        text_x = w // 3
        screen.blit(text_surf, (text_x, start_y + i * spacing))
        
        # Draw value text (aligned right)  
        if value_text:
            value_surf = menu_font.render(value_text, True, color)
            value_x = 2 * w // 3
            screen.blit(value_surf, (value_x, start_y + i * spacing))
    
    # Instructions
    instruction_font = pygame.font.Font(None, 24)
    instructions = [
        'Use UP/DOWN to navigate',
        'Use LEFT/RIGHT to adjust values', 
        'Press ENTER to activate',
        'Press ESC to go back'
    ]
    
    inst_y = h - 140
    for instruction in instructions:
        inst_surf = instruction_font.render(instruction, True, (120, 120, 120))
        inst_rect = inst_surf.get_rect(center=(w // 2, inst_y))
        screen.blit(inst_surf, inst_rect)
        inst_y += 30


def handle_sounds_menu_input(selected_item: int, game_state: Optional[Any] = None) -> str:
    '''
    Handle input for the sounds menu and return the action to take.
    
    Args:
        selected_item: currently selected menu item index
        game_state: game state object to access sound manager
        
    Returns:
        Action string: 'toggle_master', 'toggle_money', 'toggle_ap', 'toggle_blob', 
                      'toggle_error', 'toggle_popup', 'toggle_milestone', 'toggle_warning',
                      'toggle_danger', 'toggle_success', 'toggle_research_complete', 'back', or 'none'
    '''
    if not game_state or not hasattr(game_state, 'sound_manager'):
        return 'back' if selected_item == 11 else 'none'  # Updated back button index
        
    actions = [
        'toggle_master',            # Master Audio
        'toggle_money',             # Money Spend Sound  
        'toggle_ap',                # Action Point Sound
        'toggle_blob',              # Blob Sound
        'toggle_error',             # Error Beep
        'toggle_popup',             # Popup Sounds
        'toggle_milestone',         # Milestone Sound
        'toggle_warning',           # Warning Sound
        'toggle_danger',            # Danger Sound
        'toggle_success',           # Success Sound
        'toggle_research_complete', # Research Complete
        'back'                      # Back
    ]
    
    return actions[selected_item] if selected_item < len(actions) else 'none'


def apply_sound_toggle(action: str, game_state: Any) -> None:
    '''
    Apply a sound toggle action to the game state.
    
    Args:
        action: action string from handle_sounds_menu_input
        game_state: game state object with sound manager
    '''
    if not hasattr(game_state, 'sound_manager'):
        return
        
    sound_manager = game_state.sound_manager
    
    if action == 'toggle_master':
        sound_manager.set_enabled(not sound_manager.is_enabled())
    elif action == 'toggle_money':
        current = sound_manager.sound_toggles.get('money_spend', True)
        sound_manager.sound_toggles['money_spend'] = not current
    elif action == 'toggle_ap':
        current = sound_manager.sound_toggles.get('ap_spend', True)  
        sound_manager.sound_toggles['ap_spend'] = not current
    elif action == 'toggle_blob':
        current = sound_manager.sound_toggles.get('blob', True)
        sound_manager.sound_toggles['blob'] = not current
    elif action == 'toggle_error':
        current = sound_manager.sound_toggles.get('error_beep', True)
        sound_manager.sound_toggles['error_beep'] = not current
    elif action == 'toggle_popup':
        current = sound_manager.sound_toggles.get('popup_open', True)
        sound_manager.sound_toggles['popup_open'] = not current
        sound_manager.sound_toggles['popup_close'] = not current
        sound_manager.sound_toggles['popup_accept'] = not current
    elif action == 'toggle_milestone':
        current = sound_manager.sound_toggles.get('milestone', True)
        sound_manager.sound_toggles['milestone'] = not current
    elif action == 'toggle_warning':
        current = sound_manager.sound_toggles.get('warning', True)
        sound_manager.sound_toggles['warning'] = not current
    elif action == 'toggle_danger':
        current = sound_manager.sound_toggles.get('danger', True)
        sound_manager.sound_toggles['danger'] = not current
    elif action == 'toggle_success':
        current = sound_manager.sound_toggles.get('success', True)
        sound_manager.sound_toggles['success'] = not current
    elif action == 'toggle_research_complete':
        current = sound_manager.sound_toggles.get('research_complete', True)
        sound_manager.sound_toggles['research_complete'] = not current