"""
Bug report screen for P(Doom) - Bug reporting and feedback forms

This module provides the bug report form and success screens for players
to report bugs and suggest features.
"""

import pygame


def draw_bug_report_form(screen, form_data, selected_field, w, h):
    """
    Draw the bug reporting form interface.
    
    Args:
        screen: pygame surface to draw on
        form_data: dict containing form field values
        selected_field: index of currently selected field
        w, h: screen width and height
    """
    # Colors
    bg_color = (40, 40, 50)
    field_color = (60, 60, 70)
    selected_color = (80, 80, 100)
    text_color = (255, 255, 255)
    label_color = (200, 200, 255)
    button_color = (70, 130, 180)
    button_hover_color = (100, 160, 210)
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', 32, bold=True)
    label_font = pygame.font.SysFont('Consolas', 18, bold=True)
    field_font = pygame.font.SysFont('Consolas', 16)
    button_font = pygame.font.SysFont('Consolas', 20, bold=True)
    
    # Fill background
    screen.fill(bg_color)
    
    # Title
    title_text = title_font.render("Report Bug / Suggest Feature", True, text_color)
    title_rect = title_text.get_rect(center=(w//2, 40))
    screen.blit(title_text, title_rect)
    
    # Form fields configuration
    fields = [
        {"key": "type", "label": "Type", "type": "dropdown"},
        {"key": "title", "label": "Title (brief summary)", "type": "text"},
        {"key": "description", "label": "Description", "type": "textarea"},
        {"key": "steps", "label": "Steps to Reproduce (optional)", "type": "textarea"},
        {"key": "expected", "label": "Expected Behavior (optional)", "type": "text"},
        {"key": "actual", "label": "Actual Behavior (optional)", "type": "text"},
        {"key": "attribution", "label": "Include your name?", "type": "checkbox"},
        {"key": "name", "label": "Your name (if attribution enabled)", "type": "text"},
        {"key": "contact", "label": "Contact info (optional)", "type": "text"},
    ]
    
    # Calculate layout
    start_y = 80
    field_height = 35
    field_spacing = 45
    margin = 40
    field_width = w - 2 * margin
    
    # Draw fields
    for i, field in enumerate(fields):
        y_pos = start_y + i * field_spacing
        
        # Skip name field if attribution is not checked
        if field["key"] == "name" and not form_data.get("attribution", False):
            continue
            
        # Field label
        label_text = label_font.render(field["label"], True, label_color)
        screen.blit(label_text, (margin, y_pos))
        
        # Field input area
        field_rect = pygame.Rect(margin, y_pos + 20, field_width, field_height)
        
        # Highlight selected field
        if i == selected_field:
            pygame.draw.rect(screen, selected_color, field_rect, border_radius=5)
        else:
            pygame.draw.rect(screen, field_color, field_rect, border_radius=5)
        
        pygame.draw.rect(screen, (100, 100, 120), field_rect, width=2, border_radius=5)
        
        # Field content
        field_value = form_data.get(field["key"], "")
        
        if field["type"] == "dropdown" and field["key"] == "type":
            # Type dropdown
            type_options = ["Bug Report", "Feature Request", "Feedback/Suggestion"]
            type_index = form_data.get("type_index", 0)
            display_text = type_options[type_index] if type_index < len(type_options) else "Bug Report"
            text_surface = field_font.render(display_text, True, text_color)
            screen.blit(text_surface, (field_rect.x + 10, field_rect.y + 8))
            
            # Dropdown arrow
            arrow_text = field_font.render("▼", True, text_color)
            screen.blit(arrow_text, (field_rect.right - 30, field_rect.y + 8))
            
        elif field["type"] == "checkbox":
            # Checkbox
            checkbox_rect = pygame.Rect(field_rect.x + 10, field_rect.y + 8, 20, 20)
            pygame.draw.rect(screen, (200, 200, 200), checkbox_rect, border_radius=3)
            if form_data.get(field["key"], False):
                pygame.draw.rect(screen, (100, 255, 100), checkbox_rect.inflate(-6, -6), border_radius=2)
            
            # Checkbox label
            checkbox_label = field_font.render("Yes, credit me in the report", True, text_color)
            screen.blit(checkbox_label, (checkbox_rect.right + 10, field_rect.y + 8))
            
        else:
            # Text input
            display_text = field_value
            if field["type"] == "textarea" and len(display_text) > 60:
                display_text = display_text[:60] + "..."
            elif len(display_text) > 80:
                display_text = display_text[:80] + "..."
                
            text_surface = field_font.render(display_text, True, text_color)
            screen.blit(text_surface, (field_rect.x + 10, field_rect.y + 8))
            
            # Show cursor on selected field
            if i == selected_field:
                cursor_x = field_rect.x + 10 + text_surface.get_width()
                pygame.draw.line(screen, text_color, 
                               (cursor_x, field_rect.y + 5), 
                               (cursor_x, field_rect.bottom - 5), 2)
    
    # Buttons
    button_y = start_y + len(fields) * field_spacing + 20
    button_width = 150
    button_height = 40
    button_spacing = 20
    
    buttons = [
        {"text": "Save Locally", "action": "save_local"},
        {"text": "Submit to GitHub", "action": "submit_github"},
        {"text": "Cancel", "action": "cancel"}
    ]
    
    # Calculate button positions
    total_button_width = len(buttons) * button_width + (len(buttons) - 1) * button_spacing
    start_x = (w - total_button_width) // 2
    
    for i, button in enumerate(buttons):
        button_x = start_x + i * (button_width + button_spacing)
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Button color (could be enhanced with hover detection)
        color = button_color
        if button["action"] == "cancel":
            color = (120, 80, 80)
        
        pygame.draw.rect(screen, color, button_rect, border_radius=8)
        pygame.draw.rect(screen, (150, 150, 150), button_rect, width=2, border_radius=8)
        
        # Button text
        button_text = button_font.render(button["text"], True, text_color)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
        
        # Store button rect for click detection
        button["rect"] = button_rect
    
    # Instructions
    instruction_y = button_y + button_height + 20
    instructions = [
        "Use Up/Down arrows to navigate fields, Enter to edit, Tab to move to next field",
        "Bug reports help improve the game and are greatly appreciated!",
        "All reports are privacy-focused - only technical info needed for debugging is collected"
    ]
    
    instruction_font = pygame.font.SysFont('Consolas', 14)
    for i, instruction in enumerate(instructions):
        instruction_text = instruction_font.render(instruction, True, (180, 180, 180))
        text_rect = instruction_text.get_rect(center=(w//2, instruction_y + i * 20))
        screen.blit(instruction_text, text_rect)
    
    return buttons  # Return button data for click handling


def draw_bug_report_success(screen, message, w, h):
    """
    Draw success message after bug report submission.
    
    Args:
        screen: pygame surface to draw on
        message: success message to display
        w, h: screen width and height
    """
    # Colors
    bg_color = (40, 60, 40)
    text_color = (255, 255, 255)
    success_color = (100, 255, 100)
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', 36, bold=True)
    message_font = pygame.font.SysFont('Consolas', 18)
    instruction_font = pygame.font.SysFont('Consolas', 16)
    
    # Fill background
    screen.fill(bg_color)
    
    # Success title
    title_text = title_font.render("Report Submitted Successfully!", True, success_color)
    title_rect = title_text.get_rect(center=(w//2, h//3))
    screen.blit(title_text, title_rect)
    
    # Message
    # Split message into lines if it's long
    lines = message.split('\n')
    y_offset = h//2 - len(lines) * 15
    
    for line in lines:
        line_text = message_font.render(line, True, text_color)
        line_rect = line_text.get_rect(center=(w//2, y_offset))
        screen.blit(line_text, line_rect)
        y_offset += 30
    
    # Instructions
    instruction_text = instruction_font.render("Press any key to return to main menu", True, (200, 200, 200))
    instruction_rect = instruction_text.get_rect(center=(w//2, h - 100))
    screen.blit(instruction_text, instruction_rect)