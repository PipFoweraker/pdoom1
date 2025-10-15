'''
Enhanced Settings System Demo for P(Doom)

This script demonstrates the new settings and configuration system.
Run this to see the improved menu structure and functionality.
'''

import pygame
from src.ui.settings_integration import settings_state
from src.services.config_manager import initialize_config_system


def demo_enhanced_settings():
    '''Demonstrate the enhanced settings system.'''
    
    # Initialize pygame
    pygame.init()
    
    # Initialize config system
    initialize_config_system()
    
    # Set up display
    w, h = 1024, 768
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption('P(Doom) Enhanced Settings Demo')
    clock = pygame.time.Clock()
    
    # Start in main settings menu
    settings_state.enter_settings()
    current_state = 'settings_main'
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == 'settings_main':
                        running = False  # Exit demo
                    else:
                        # Go back to main settings
                        settings_state.enter_settings()
                        current_state = 'settings_main'
                
                # Handle seed input if in that mode
                if current_state == 'game_config_menu' and settings_state.is_seed_input_mode():
                    result = settings_state.handle_seed_input_keyboard(event)
                    if result == 'seed_confirmed':
                        print(f'Seed confirmed: '{settings_state.get_custom_seed()}'')
                        current_state = 'game_config_menu'
                    elif result == 'seed_cancelled':
                        print('Seed input cancelled')
                        current_state = 'game_config_menu'
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if current_state == 'settings_main':
                    result = settings_state.handle_main_settings_click(mouse_pos, w, h)
                    if result == 'sounds_menu':
                        print('Would transition to audio settings (existing system)')
                        current_state = 'audio_menu'
                    elif result == 'game_config_menu':
                        print('Entering game configuration menu')
                        current_state = 'game_config_menu'
                    elif result == 'gameplay_settings_menu':
                        print('Entering gameplay settings menu')
                        current_state = 'gameplay_settings_menu'
                    elif result == 'keybinding_menu':
                        print('Would transition to keybinding menu (existing system)')
                    elif result == 'main_menu':
                        print('Would return to main menu')
                        running = False
                
                elif current_state == 'game_config_menu':
                    result = settings_state.handle_game_config_click(mouse_pos, w, h)
                    if result == 'config_changed':
                        print('Configuration changed')
                    elif result == 'seed_input_mode':
                        print('Entering custom seed input mode')
                    elif result == 'settings_main_menu':
                        print('Returning to main settings')
                        current_state = 'settings_main'
                    elif result:
                        print(f'Game config action: {result}')
        
        # Clear screen
        screen.fill((40, 45, 55))
        
        # Draw current menu
        settings_state.draw_current_menu(screen, w, h)
        
        # Draw status text
        font = pygame.font.SysFont('Consolas', 20)
        status_lines = [
            f'Current State: {current_state}',
            f'Settings Menu: {settings_state.get_current_menu_type()}',
            f'Seed Input Mode: {settings_state.is_seed_input_mode()}',
            '',
            'ESC: Back/Exit | Mouse: Click options | Arrow keys: Navigate'
        ]
        
        y_offset = h - 120
        for line in status_lines:
            if line:  # Skip empty lines
                text = font.render(line, True, (200, 200, 200))
                screen.blit(text, (10, y_offset))
            y_offset += 22
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == '__main__':
    print('P(Doom) Enhanced Settings System Demo')
    print('=====================================')
    print()
    print('This demo shows the new settings organization:')
    print('- Audio Settings: Sound and volume controls')
    print('- Game Configuration: Custom configs and seeds') 
    print('- Gameplay Settings: Difficulty and automation')
    print('- Accessibility: Visual aids and accommodations')
    print('- Keybindings: Keyboard shortcuts')
    print()
    print('Click through the menus to see the new structure.')
    print('Press ESC to go back or exit.')
    print()
    
    try:
        demo_enhanced_settings()
        print('Demo completed successfully!')
    except KeyboardInterrupt:
        print('\nDemo interrupted by user')
    except Exception as e:
        print(f'Demo error: {e}')
        import traceback
        traceback.print_exc()
