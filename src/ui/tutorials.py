'''
Tutorial UI functions for the P(Doom) game interface.

This module contains all tutorial-related drawing functions including
tutorial overlays, stepwise tutorials, help popups, and new player experience.
'''

import pygame
from typing import Dict, Any, Optional, Tuple
from src.ui.rendering import wrap_text
from src.features.visual_feedback import draw_low_poly_button, ButtonState


def draw_tutorial_overlay(screen: pygame.Surface, tutorial_message: Dict[str, str], w: int, h: int) -> pygame.Rect:
    '''
    Draw a tutorial overlay with message content and dismiss button.
    
    Args:
        screen: pygame surface to draw on
        tutorial_message: dict with 'title' and 'content' keys
        w, h: screen width and height
        
    Returns:
        Rect of the dismiss button for click detection
    '''
    if not tutorial_message:
        return None
        
    # Create semi-transparent background overlay
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Tutorial dialog dimensions
    dialog_width = int(w * 0.6)
    dialog_height = int(h * 0.7)
    dialog_x = (w - dialog_width) // 2
    dialog_y = (h - dialog_height) // 2
    
    # Dialog background
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    pygame.draw.rect(screen, (40, 50, 60), dialog_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 150, 200), dialog_rect, width=3, border_radius=10)
    
    # Fonts
    title_font = pygame.font.Font(None, int(h * 0.04))
    content_font = pygame.font.Font(None, int(h * 0.025))
    button_font = pygame.font.Font(None, int(h * 0.03))
    
    # Title
    title = tutorial_message['title']
    title_surface = title_font.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect(centerx=dialog_rect.centerx, y=dialog_y + 20)
    screen.blit(title_surface, title_rect)
    
    # Content area
    content = tutorial_message['content']
    content_y = title_rect.bottom + 30
    content_width = dialog_width - 40
    content_height = dialog_height - 120  # Leave space for title and button
    
    # Wrap and render content text
    wrapped_lines = wrap_text(content, content_font, content_width)
    line_height = content_font.get_height() + 5
    
    for i, line in enumerate(wrapped_lines):
        line_y = content_y + i * line_height
        if line_y + line_height > content_y + content_height:
            # Add '...' if content is too long
            if i < len(wrapped_lines) - 1:
                ellipsis = content_font.render('...', True, (200, 200, 200))
                screen.blit(ellipsis, (dialog_x + 20, line_y))
            break
        line_surface = content_font.render(line, True, (220, 220, 220))
        screen.blit(line_surface, (dialog_x + 20, line_y))
    
    # Dismiss button
    button_width = 150
    button_height = 40
    button_x = dialog_rect.centerx - button_width // 2
    button_y = dialog_rect.bottom - 60
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    pygame.draw.rect(screen, (80, 120, 160), button_rect, border_radius=5)
    pygame.draw.rect(screen, (120, 180, 240), button_rect, width=2, border_radius=5)
    
    button_text = button_font.render('Got it!', True, (255, 255, 255))
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)
    
    # Footer text
    footer_text = pygame.font.Font(None, int(h * 0.02)).render(
        'Click 'Got it!' or press Enter to dismiss', True, (150, 150, 150)
    )
    footer_rect = footer_text.get_rect(centerx=dialog_rect.centerx, y=button_rect.bottom + 10)
    screen.blit(footer_text, footer_rect)
    
    return button_rect


def draw_stepwise_tutorial_overlay(screen: pygame.Surface, tutorial_data: Dict[str, Any], w: int, h: int) -> Dict[str, pygame.Rect]:
    '''
    Draw the stepwise tutorial overlay for onboarding new players.
    
    Args:
        screen: pygame surface to draw on
        tutorial_data: dict containing tutorial step data with navigation info
        w, h: screen width and height
    
    Returns:
        dict with button rectangles for click detection
    '''
    if not tutorial_data:
        return {}
    
    # Semi-transparent overlay
    overlay_surface = pygame.Surface((w, h))
    overlay_surface.set_alpha(180)
    overlay_surface.fill((0, 0, 0))
    screen.blit(overlay_surface, (0, 0))
    
    # Tutorial box dimensions
    box_width = int(w * 0.6)
    box_height = int(h * 0.5)
    box_x = (w - box_width) // 2
    box_y = (h - box_height) // 2
    
    # Tutorial box background
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
    pygame.draw.rect(screen, (40, 50, 70), box_rect, border_radius=15)
    pygame.draw.rect(screen, (100, 150, 255), box_rect, width=4, border_radius=15)
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.04), bold=True)
    content_font = pygame.font.SysFont('Consolas', int(h*0.025))
    button_font = pygame.font.SysFont('Consolas', int(h*0.03), bold=True)
    progress_font = pygame.font.SysFont('Consolas', int(h*0.02))
    
    # Progress indicator
    step_number = tutorial_data.get('step_number', 1)
    total_steps = tutorial_data.get('total_steps', 1)
    progress_text = f'Step {step_number} of {total_steps}'
    progress_surface = progress_font.render(progress_text, True, (200, 200, 200))
    progress_rect = progress_surface.get_rect(topright=(box_x + box_width - 20, box_y + 15))
    screen.blit(progress_surface, progress_rect)
    
    # Tutorial title
    title = tutorial_data.get('title', 'Tutorial')
    title_text = title_font.render(title, True, (255, 255, 100))
    title_rect = title_text.get_rect(center=(w//2, box_y + int(h*0.06)))
    screen.blit(title_text, title_rect)
    
    # Tutorial content with word wrapping
    content = tutorial_data.get('content', '')
    content_area_width = box_width - 40
    content_area_height = box_height - 160  # Space for title and buttons
    content_y = box_y + int(h*0.1)
    
    # Split content into lines and wrap
    content_lines = content.split('\\n')
    wrapped_lines = []
    for line in content_lines:
        if line.strip():
            wrapped = wrap_text(line, content_font, content_area_width)
            wrapped_lines.extend(wrapped)
        else:
            wrapped_lines.append('')  # Preserve empty lines
    
    # Draw content lines
    line_height = content_font.get_height() + 4
    max_lines = content_area_height // line_height
    
    for i, line in enumerate(wrapped_lines[:max_lines]):
        if line:  # Skip empty lines for rendering
            line_surface = content_font.render(line, True, (255, 255, 255))
            screen.blit(line_surface, (box_x + 20, content_y + i * line_height))
    
    # Tutorial navigation buttons
    button_min_width = 120
    button_height = 45
    button_y = box_y + box_height - 60
    
    buttons = {}
    
    # Back button (if can go back)
    can_go_back = tutorial_data.get('can_go_back', False)
    if can_go_back:
        back_button_x = box_x + 30
        back_button_rect = pygame.Rect(back_button_x, button_y, button_min_width, button_height)
        pygame.draw.rect(screen, (150, 150, 150), back_button_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), back_button_rect, width=2, border_radius=8)
        
        back_text = button_font.render('Back', True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        screen.blit(back_text, back_text_rect)
        buttons['back'] = back_button_rect
    
    # Skip button (always available)
    skip_button_x = box_x + box_width // 2 - button_min_width // 2
    skip_button_rect = pygame.Rect(skip_button_x, button_y, button_min_width, button_height)
    pygame.draw.rect(screen, (180, 100, 100), skip_button_rect, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), skip_button_rect, width=2, border_radius=8)
    
    skip_text = button_font.render('Skip (S)', True, (255, 255, 255))
    skip_text_rect = skip_text.get_rect(center=skip_button_rect.center)
    screen.blit(skip_text, skip_text_rect)
    buttons['skip'] = skip_button_rect
    
    # Next/Finish button
    tutorial_data.get('can_go_forward', True)
    is_final_step = step_number >= total_steps
    
    next_button_x = box_x + box_width - button_min_width - 30
    next_button_rect = pygame.Rect(next_button_x, button_y, button_min_width, button_height)
    pygame.draw.rect(screen, (100, 200, 100), next_button_rect, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), next_button_rect, width=2, border_radius=8)
    
    next_label = 'Finish' if is_final_step else 'Next'
    next_text = button_font.render(next_label, True, (255, 255, 255))
    next_text_rect = next_text.get_rect(center=next_button_rect.center)
    screen.blit(next_text, next_text_rect)
    buttons['next'] = next_button_rect
    
    # Focus area highlight (if specified)
    focus_area = tutorial_data.get('focus_area')
    if focus_area:
        # Add a subtle highlight around the focus area
        # This could be expanded to highlight specific UI elements
        pass
    
    return buttons


def draw_first_time_help(screen: pygame.Surface, help_content: Dict[str, Any], w: int, h: int, mouse_pos: Optional[Tuple[int, int]] = None) -> Optional[pygame.Rect]:
    '''
    Draw a small help popup for first-time mechanics.
    
    Args:
        screen: pygame surface to draw on
        help_content: dict with title and content for the help popup
        w, h: screen width and height
        mouse_pos: current mouse position for hover effects (optional)
    '''
    if not help_content or not isinstance(help_content, dict):
        return None
        
    # Small popup dimensions
    popup_width = int(w * 0.4)
    popup_height = int(h * 0.25)
    popup_x = w - popup_width - 20  # Top right corner
    popup_y = 20
    
    # Popup background
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    pygame.draw.rect(screen, (60, 80, 100), popup_rect, border_radius=10)
    pygame.draw.rect(screen, (150, 200, 255), popup_rect, width=3, border_radius=10)
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.025), bold=True)
    content_font = pygame.font.SysFont('Consolas', int(h*0.02))
    
    # Title
    title_text = title_font.render(help_content.get('title', 'Tip'), True, (255, 255, 100))
    screen.blit(title_text, (popup_x + 10, popup_y + 10))
    
    # Content with word wrapping
    content = help_content.get('content', '')
    content_width = popup_width - 20
    wrapped_content = wrap_text(content, content_font, content_width)
    
    for i, line in enumerate(wrapped_content[:6]):  # Max 6 lines
        line_surface = content_font.render(line, True, (255, 255, 255))
        screen.blit(line_surface, (popup_x + 10, popup_y + 40 + i * 20))
    
    # Close button (X) with hover effect
    close_button_size = 20
    close_button_x = popup_x + popup_width - close_button_size - 5
    close_button_y = popup_y + 5
    close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)
    
    # Check for hover effect
    close_button_color = (200, 100, 100)  # Default red
    close_text_color = (255, 255, 255)    # Default white
    
    if mouse_pos and close_button_rect.collidepoint(mouse_pos):
        close_button_color = (255, 120, 120)  # Brighter red on hover
        close_text_color = (255, 255, 100)    # Yellow text on hover
    
    pygame.draw.rect(screen, close_button_color, close_button_rect, border_radius=3)
    
    close_font = pygame.font.SysFont('Consolas', int(h*0.02), bold=True)
    close_text = close_font.render('X', True, close_text_color)
    close_text_rect = close_text.get_rect(center=close_button_rect.center)
    screen.blit(close_text, close_text_rect)
    
    # Add dismiss instructions at bottom of popup
    dismiss_font = pygame.font.SysFont('Consolas', int(h*0.015))
    dismiss_text = dismiss_font.render('Press Esc to dismiss, Enter to accept', True, (180, 180, 180))
    dismiss_y = popup_y + popup_height - 25
    screen.blit(dismiss_text, (popup_x + 10, dismiss_y))
    
    return close_button_rect


def draw_tutorial_choice(screen: pygame.Surface, w: int, h: int, selected_item: int) -> None:
    '''
    Draw the tutorial choice screen.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected item (0=No, 1=Yes)
    '''
    # Clear background
    screen.fill((50, 50, 50))
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    desc_font = pygame.font.SysFont('Consolas', int(h*0.025))
    
    # Title
    title_surf = title_font.render('Tutorial Mode?', True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.15)
    screen.blit(title_surf, (title_x, title_y))
    
    # Description
    desc_text = 'Would you like to play with tutorial guidance?'
    desc_surf = desc_font.render(desc_text, True, (200, 200, 200))
    desc_x = w // 2 - desc_surf.get_width() // 2
    desc_y = title_y + title_surf.get_height() + 20
    screen.blit(desc_surf, (desc_x, desc_y))
    
    # Tutorial options - No tutorial first (default), Yes tutorial second
    tutorial_items = ['No - Regular Mode', 'Yes - Enable Tutorial']
    
    # Button layout
    button_width = int(w * 0.4)
    button_height = int(h * 0.08)
    start_y = int(h * 0.4)
    spacing = int(h * 0.12)
    center_x = w // 2
    
    for i, item in enumerate(tutorial_items):
        # Calculate button position
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
    inst_font = pygame.font.SysFont('Consolas', int(h*0.025))
    instructions = [
        'Use arrow keys or mouse to navigate, Enter/Space to confirm',
        'Tutorial mode provides helpful guidance for new players'
    ]
    
    inst_y = int(h * 0.8)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 5


def draw_new_player_experience(screen: pygame.Surface, w: int, h: int, selected_item: int, tutorial_enabled: bool, intro_enabled: bool) -> None:
    '''
    Draw the new player experience screen with tutorial and intro checkboxes.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected item (0=Tutorial, 1=Intro, 2=Start button)
        tutorial_enabled: whether tutorial checkbox is checked
        intro_enabled: whether intro checkbox is checked
    '''
    # Clear background
    screen.fill((50, 50, 50))
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    option_font = pygame.font.SysFont('Consolas', int(h*0.03))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.025))
    
    # Title
    title_surf = title_font.render('New Player Experience', True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.12)
    screen.blit(title_surf, (title_x, title_y))
    
    # Description
    desc_text = 'Choose your starting options:'
    desc_surf = desc_font.render(desc_text, True, (200, 200, 200))
    desc_x = w // 2 - desc_surf.get_width() // 2
    desc_y = title_y + title_surf.get_height() + 20
    screen.blit(desc_surf, (desc_x, desc_y))
    
    # Layout constants
    center_x = w // 2
    checkbox_size = int(h * 0.04)
    start_y = int(h * 0.35)
    spacing = int(h * 0.08)
    
    # Options with checkboxes
    options = [
        ('Tutorial', 'Get helpful guidance for new players', tutorial_enabled),
        ('Intro', 'Read an introduction to the scenario', intro_enabled)
    ]
    
    for i, (option_name, option_desc, checked) in enumerate(options):
        y_pos = start_y + i * spacing
        
        # Checkbox
        checkbox_x = center_x - checkbox_size // 2 - int(w * 0.15)
        checkbox_y = y_pos
        checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size)
        
        # Checkbox background and border
        checkbox_color = (100, 100, 100) if i == selected_item else (70, 70, 70)
        pygame.draw.rect(screen, checkbox_color, checkbox_rect)
        pygame.draw.rect(screen, (200, 200, 200), checkbox_rect, 2)
        
        # Checkmark if enabled
        if checked:
            # Draw a simple checkmark
            checkmark_color = (100, 255, 100)
            pygame.draw.line(screen, checkmark_color, 
                           (checkbox_x + 5, checkbox_y + checkbox_size // 2),
                           (checkbox_x + checkbox_size // 2, checkbox_y + checkbox_size - 5), 3)
            pygame.draw.line(screen, checkmark_color,
                           (checkbox_x + checkbox_size // 2, checkbox_y + checkbox_size - 5),
                           (checkbox_x + checkbox_size - 5, checkbox_y + 5), 3)
        
        # Option text
        text_x = checkbox_x + checkbox_size + 20
        text_color = (255, 255, 255) if i == selected_item else (200, 200, 200)
        option_surf = option_font.render(option_name, True, text_color)
        screen.blit(option_surf, (text_x, checkbox_y))
        
        # Description text
        desc_surf = desc_font.render(option_desc, True, (180, 180, 180))
        screen.blit(desc_surf, (text_x, checkbox_y + option_surf.get_height() + 5))
    
    # Start button
    button_width = int(w * 0.3)
    button_height = int(h * 0.06)
    button_x = center_x - button_width // 2
    button_y = int(h * 0.65)
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Determine button state
    if selected_item == 2:
        button_state = ButtonState.FOCUSED
    else:
        button_state = ButtonState.NORMAL
    
    # Draw start button
    draw_low_poly_button(screen, button_rect, 'Start Game', button_state)
    
    # Intro text preview if intro is enabled
    if intro_enabled:
        intro_y = button_y + button_height + 30
        intro_font = pygame.font.SysFont('Consolas', int(h*0.022))
        intro_lines = [
            'Doom is coming. You convinced a funder to give you $1,000.',
            'You'll be assigned a lab name for pseudonymous competition.',
            'Your job is to save the world. Good luck!'
        ]
        
        for line in intro_lines:
            intro_surf = intro_font.render(line, True, (255, 200, 100))
            intro_x = w // 2 - intro_surf.get_width() // 2
            screen.blit(intro_surf, (intro_x, intro_y))
            intro_y += intro_surf.get_height() + 5
    
    # Instructions
    inst_font = pygame.font.SysFont('Consolas', int(h*0.02))
    instructions = [
        'Use arrow keys or mouse to navigate',
        'Space/Enter to toggle checkboxes or start game',
        'Escape to return to main menu'
    ]
    
    inst_y = int(h * 0.85)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (150, 150, 150))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 3
