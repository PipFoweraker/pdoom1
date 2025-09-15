"""
Dialog drawing functions for the P(Doom) game interface.

This module contains all the dialog box drawing functions including
hiring dialogs, fundraising dialogs, research dialogs, and forms.
"""

import pygame
from typing import Dict, Any, List
from src.ui.rendering import wrap_text


def draw_researcher_pool_dialog(screen: pygame.Surface, hiring_dialog: Dict[str, Any], w: int, h: int, game_state: Any = None) -> List[Dict[str, Any]]:
    """
    Draw the researcher pool hiring dialog showing available specialist researchers.
    
    Args:
        screen: pygame surface to draw on
        hiring_dialog: hiring dialog configuration
        w, h: screen dimensions
        game_state: game state object containing available_researchers (optional for backward compatibility)
    """
    # Get available researchers from game_state if provided, otherwise use empty list
    if game_state and hasattr(game_state, 'available_researchers'):
        available_researchers = game_state.available_researchers
    else:
        # Fallback for backward compatibility or when game_state unavailable
        available_researchers = []
    
    # Create semi-transparent background overlay
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Dialog dimensions
    dialog_width = int(w * 0.9)
    dialog_height = int(h * 0.9)
    dialog_x = (w - dialog_width) // 2
    dialog_y = (h - dialog_height) // 2
    
    # Draw main dialog background
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    pygame.draw.rect(screen, (40, 40, 45), dialog_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 120), dialog_rect, width=3, border_radius=10)
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title_text = title_font.render("Researcher Pool", True, (255, 255, 255))
    title_rect = title_text.get_rect(centerx=dialog_rect.centerx, y=dialog_y + 20)
    screen.blit(title_text, title_rect)
    
    # Subtitle
    subtitle_font = pygame.font.Font(None, 24)
    subtitle_text = subtitle_font.render("Select a specialist researcher to hire", True, (200, 200, 200))
    subtitle_rect = subtitle_text.get_rect(centerx=dialog_rect.centerx, y=title_rect.bottom + 10)
    screen.blit(subtitle_text, subtitle_rect)
    
    # Content area
    content_y = subtitle_rect.bottom + 30
    content_height = dialog_height - (content_y - dialog_y) - 80  # Reserve space for buttons
    
    # Calculate researcher card dimensions
    cards_per_row = 3
    card_width = (dialog_width - 80) // cards_per_row - 20
    card_height = 160
    
    clickable_rects = []
    detail_font = pygame.font.Font(None, 20)
    
    # Draw researcher cards
    for i, researcher in enumerate(available_researchers):
        row = i // cards_per_row
        col = i % cards_per_row
        
        card_x = dialog_x + 40 + col * (card_width + 20)
        card_y = content_y + row * (card_height + 20)
        
        # Skip if card would be below visible area
        if card_y + card_height > dialog_y + dialog_height - 80:
            break
            
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        
        # Card background
        pygame.draw.rect(screen, (55, 55, 65), card_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 120, 140), card_rect, width=2, border_radius=8)
        
        # Researcher name
        name_text = detail_font.render(researcher['name'], True, (255, 255, 255))
        name_rect = name_text.get_rect(centerx=card_rect.centerx, y=card_y + 10)
        screen.blit(name_text, name_rect)
        
        # Researcher specialty
        specialty_text = detail_font.render(f"Specialty: {researcher['specialty']}", True, (180, 180, 200))
        specialty_rect = specialty_text.get_rect(centerx=card_rect.centerx, y=name_rect.bottom + 5)
        screen.blit(specialty_text, specialty_rect)
        
        # Researcher skills/stats
        skills_y = specialty_rect.bottom + 10
        for j, (skill, value) in enumerate(researcher.get('skills', {}).items()):
            skill_text = detail_font.render(f"{skill}: {value}", True, (160, 200, 160))
            skill_rect = skill_text.get_rect(x=card_x + 10, y=skills_y + j * 20)
            screen.blit(skill_text, skill_rect)
        
        # Hire button
        hire_button_width = card_width - 20
        hire_button_height = 25
        hire_button_x = card_x + 10
        hire_button_y = card_y + card_height - hire_button_height - 10
        
        hire_rect = pygame.Rect(hire_button_x, hire_button_y, hire_button_width, hire_button_height)
        pygame.draw.rect(screen, (60, 100, 60), hire_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 160, 100), hire_rect, width=2, border_radius=5)
        
        hire_text = detail_font.render("Hire", True, (255, 255, 255))
        hire_text_rect = hire_text.get_rect(center=hire_rect.center)
        screen.blit(hire_text, hire_text_rect)
        
        clickable_rects.append({
            'rect': hire_rect,
            'type': 'hire_researcher',
            'researcher_id': researcher['id']
        })
    
    # Back button
    button_width = 100
    button_height = 40
    button_y = dialog_y + dialog_height - 60
    
    back_x = dialog_rect.centerx - button_width - 10
    back_rect = pygame.Rect(back_x, button_y, button_width, button_height)
    pygame.draw.rect(screen, (80, 80, 90), back_rect, border_radius=5)
    pygame.draw.rect(screen, (140, 140, 160), back_rect, width=2, border_radius=5)
    
    back_text = detail_font.render("Back", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, back_text_rect)
    
    clickable_rects.append({
        'rect': back_rect,
        'type': 'back_to_subtypes'
    })
    
    # Cancel button
    cancel_x = dialog_rect.centerx + 10
    cancel_rect = pygame.Rect(cancel_x, button_y, button_width, button_height)
    pygame.draw.rect(screen, (100, 60, 60), cancel_rect, border_radius=5)
    pygame.draw.rect(screen, (160, 100, 100), cancel_rect, width=2, border_radius=5)
    
    cancel_text = detail_font.render("Cancel", True, (255, 255, 255))
    cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
    screen.blit(cancel_text, cancel_text_rect)
    
    clickable_rects.append({
        'rect': cancel_rect,
        'type': 'cancel'
    })
    
    return clickable_rects


def draw_fundraising_dialog(screen: pygame.Surface, fundraising_dialog: Dict[str, Any], w: int, h: int) -> List[Dict[str, Any]]:
    """
    Draw the fundraising strategy dialog with multiple funding options.
    
    Args:
        screen: pygame surface to draw on
        fundraising_dialog: dict with fundraising dialog state including available_options
        w, h: screen width and height
        
    Returns:
        List of rects for each fundraising option and dismiss button for click detection
    """
    if not fundraising_dialog:
        return []
        
    # Create semi-transparent background overlay
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Dialog dimensions
    dialog_width = int(w * 0.85)
    dialog_height = int(h * 0.9)
    dialog_x = (w - dialog_width) // 2
    dialog_y = (h - dialog_height) // 2
    
    # Dialog background
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    pygame.draw.rect(screen, (40, 60, 50), dialog_rect, border_radius=10)  # Slightly green tint for money theme
    pygame.draw.rect(screen, (100, 200, 150), dialog_rect, width=3, border_radius=10)
    
    # Fonts
    title_font = pygame.font.Font(None, int(h * 0.04))
    desc_font = pygame.font.Font(None, int(h * 0.025))
    option_font = pygame.font.Font(None, int(h * 0.028))
    button_font = pygame.font.Font(None, int(h * 0.025))
    detail_font = pygame.font.Font(None, int(h * 0.022))
    
    # Title
    title = fundraising_dialog["title"]
    title_surface = title_font.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect(centerx=dialog_rect.centerx, y=dialog_y + 20)
    screen.blit(title_surface, title_rect)
    
    # Description
    description = fundraising_dialog["description"]
    desc_surface = desc_font.render(description, True, (220, 220, 220))
    desc_rect = desc_surface.get_rect(centerx=dialog_rect.centerx, y=title_rect.bottom + 15)
    screen.blit(desc_surface, desc_rect)
    
    # Fundraising options area
    options_start_y = desc_rect.bottom + 30
    option_height = 100
    option_spacing = 15
    clickable_rects = []
    
    available_options = fundraising_dialog["available_options"]
    
    for i, option in enumerate(available_options):
        # Option background
        option_y = options_start_y + i * (option_height + option_spacing)
        option_rect = pygame.Rect(dialog_x + 20, option_y, dialog_width - 40, option_height)
        
        # Color based on availability and affordability
        if option["available"] and option["affordable"]:
            bg_color = (60, 90, 70)  # Green tint for money
            border_color = (120, 200, 150)
            text_color = (255, 255, 255)
        elif option["available"]:
            bg_color = (70, 70, 50)  # Yellow tint for expensive but available
            border_color = (150, 150, 100)
            text_color = (255, 255, 200)
        else:
            bg_color = (40, 40, 40)  # Gray for unavailable
            border_color = (80, 80, 80)
            text_color = (150, 150, 150)
        
        pygame.draw.rect(screen, bg_color, option_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, option_rect, width=2, border_radius=8)
        
        # Option name
        name_surface = option_font.render(option["name"], True, text_color)
        name_rect = name_surface.get_rect(x=option_rect.x + 15, y=option_rect.y + 10)
        screen.blit(name_surface, name_rect)
        
        # Amount range and AP cost info
        if option.get("creates_debt"):
            cost_text = f"${option['min_amount']}-{option['max_amount']}k (DEBT) - {option['ap_cost']} AP"
        else:
            cost_text = f"${option['min_amount']}-{option['max_amount']}k - {option['ap_cost']} AP"
        cost_surface = button_font.render(cost_text, True, text_color)
        cost_rect = cost_surface.get_rect(x=option_rect.right - 15 - cost_surface.get_width(), y=option_rect.y + 10)
        screen.blit(cost_surface, cost_rect)
        
        # Description
        desc_lines = wrap_text(option["description"], detail_font, dialog_width - 80)
        for j, line in enumerate(desc_lines[:2]):  # Limit to 2 lines
            line_surface = detail_font.render(line, True, text_color)
            line_y = name_rect.bottom + 5 + j * (detail_font.get_height() + 2)
            screen.blit(line_surface, (option_rect.x + 15, line_y))
        
        # Requirements/status line
        if not option["available"]:
            req_text = f"Locked: {option['requirements']}"
            req_color = (200, 100, 100)
        else:
            req_text = f"Available: {option['requirements']}"
            req_color = (100, 200, 100)
        
        req_surface = detail_font.render(req_text, True, req_color)
        req_rect = req_surface.get_rect(x=option_rect.x + 15, y=option_rect.bottom - 25)
        screen.blit(req_surface, req_rect)
        
        # Store clickable rect with option ID
        if option["available"] and option["affordable"]:
            clickable_rects.append({
                'rect': option_rect,
                'option_id': option["id"],
                'type': 'funding_option'
            })
    
    # Cancel/Dismiss button
    button_width = 140
    button_height = 45
    button_x = dialog_rect.centerx - button_width // 2
    button_y = dialog_rect.bottom - 80
    cancel_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Cancel button styling
    pygame.draw.rect(screen, (120, 70, 70), cancel_rect, border_radius=8)
    pygame.draw.rect(screen, (200, 120, 120), cancel_rect, width=3, border_radius=8)
    
    # Cancel button text
    cancel_text = button_font.render("Cancel", True, (255, 255, 255))
    text_rect = cancel_text.get_rect(center=(cancel_rect.centerx, cancel_rect.centery - 8))
    screen.blit(cancel_text, text_rect)
    
    # Keyboard shortcut hint on button  
    shortcut_font = pygame.font.Font(None, int(h * 0.018))
    shortcut_text = shortcut_font.render("(ESC or Backspace)", True, (200, 200, 200))
    shortcut_rect = shortcut_text.get_rect(center=(cancel_rect.centerx, cancel_rect.centery + 10))
    screen.blit(shortcut_text, shortcut_rect)
    
    clickable_rects.append({
        'rect': cancel_rect,
        'type': 'cancel'
    })
    
    # Instructions
    instructions = [
        "Click a funding option to execute your strategy",
        "Each approach has different risk/reward profiles", 
        "Choose wisely based on your current position"
    ]
    
    inst_font = pygame.font.Font(None, int(h * 0.022))
    inst_y = cancel_rect.bottom + 15
    
    for i, instruction in enumerate(instructions):
        if i == 0:
            # Main instruction - white
            inst_surface = inst_font.render(instruction, True, (255, 255, 255))
        else:
            # Secondary instructions - lighter gray
            inst_surface = inst_font.render(instruction, True, (180, 180, 180))
        
        inst_rect = inst_surface.get_rect(centerx=dialog_rect.centerx, y=inst_y)
        screen.blit(inst_surface, inst_rect)
        inst_y += inst_surface.get_height() + 3
    
    return clickable_rects


def draw_research_dialog(screen: pygame.Surface, research_dialog: Dict[str, Any], w: int, h: int) -> List[Dict[str, Any]]:
    """
    Draw the research strategy dialog with multiple research approaches.
    
    Args:
        screen: pygame surface to draw on
        research_dialog: dict with research dialog state including available_options
        w, h: screen width and height
        
    Returns:
        List of rects for each research option and dismiss button for click detection
    """
    if not research_dialog:
        return []
        
    # Create semi-transparent background overlay
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Dialog dimensions
    dialog_width = int(w * 0.85)
    dialog_height = int(h * 0.9)
    dialog_x = (w - dialog_width) // 2
    dialog_y = (h - dialog_height) // 2
    
    # Dialog background - research theme (blue/purple)
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    pygame.draw.rect(screen, (30, 40, 70), dialog_rect, border_radius=10)  # Science blue theme
    pygame.draw.rect(screen, (80, 120, 200), dialog_rect, width=3, border_radius=10)
    
    # Fonts
    title_font = pygame.font.Font(None, int(h * 0.04))
    desc_font = pygame.font.Font(None, int(h * 0.025))
    option_font = pygame.font.Font(None, int(h * 0.028))
    button_font = pygame.font.Font(None, int(h * 0.025))
    detail_font = pygame.font.Font(None, int(h * 0.022))
    
    # Title
    title = research_dialog["title"]
    title_surface = title_font.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect(centerx=dialog_rect.centerx, y=dialog_y + 20)
    screen.blit(title_surface, title_rect)
    
    # Description
    description = research_dialog["description"]
    desc_surface = desc_font.render(description, True, (220, 220, 220))
    desc_rect = desc_surface.get_rect(centerx=dialog_rect.centerx, y=title_rect.bottom + 15)
    screen.blit(desc_surface, desc_rect)
    
    # Research options area
    options_start_y = desc_rect.bottom + 30
    option_height = 100
    option_spacing = 15
    clickable_rects = []
    
    available_options = research_dialog["available_options"]
    
    for i, option in enumerate(available_options):
        # Option background
        option_y = options_start_y + i * (option_height + option_spacing)
        option_rect = pygame.Rect(dialog_x + 20, option_y, dialog_width - 40, option_height)
        
        # Color based on availability and affordability
        if option["available"] and option["affordable"]:
            bg_color = (50, 70, 100)  # Blue for research
            border_color = (100, 150, 220)
            text_color = (255, 255, 255)
        elif option["available"]:
            bg_color = (70, 60, 50)  # Brown for expensive but available
            border_color = (150, 120, 100)
            text_color = (255, 255, 200)
        else:
            bg_color = (40, 40, 40)  # Gray for unavailable
            border_color = (80, 80, 80)
            text_color = (150, 150, 150)
        
        pygame.draw.rect(screen, bg_color, option_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, option_rect, width=2, border_radius=8)
        
        # Option name
        name_surface = option_font.render(option["name"], True, text_color)
        name_rect = name_surface.get_rect(x=option_rect.x + 15, y=option_rect.y + 10)
        screen.blit(name_surface, name_rect)
        
        # Cost and AP info
        cost_text = f"${option['cost']}k - {option['ap_cost']} AP"
        cost_surface = button_font.render(cost_text, True, text_color)
        cost_rect = cost_surface.get_rect(x=option_rect.right - 15 - cost_surface.get_width(), y=option_rect.y + 10)
        screen.blit(cost_surface, cost_rect)
        
        # Description
        desc_lines = wrap_text(option["description"], detail_font, dialog_width - 80)
        for j, line in enumerate(desc_lines[:2]):  # Limit to 2 lines
            line_surface = detail_font.render(line, True, text_color)
            line_y = name_rect.bottom + 5 + j * (detail_font.get_height() + 2)
            screen.blit(line_surface, (option_rect.x + 15, line_y))
        
        # Research effectiveness info
        effectiveness_text = f"Doom reduction: {option['min_doom_reduction']}-{option['max_doom_reduction']}%, Rep: +{option['reputation_gain']}"
        effectiveness_surface = detail_font.render(effectiveness_text, True, (150, 200, 255))
        effectiveness_y = option_rect.y + option_rect.height - 45
        screen.blit(effectiveness_surface, (option_rect.x + 15, effectiveness_y))
        
        # Technical debt risk
        debt_risk_color = {
            "None": (100, 255, 100),
            "Very Low": (150, 255, 150), 
            "Low": (200, 255, 100),
            "High": (255, 200, 100)
        }.get(option["technical_debt_risk"], (200, 200, 200))
        
        debt_text = f"Technical Debt Risk: {option['technical_debt_risk']}"
        debt_surface = detail_font.render(debt_text, True, debt_risk_color)
        debt_y = effectiveness_y + detail_font.get_height() + 2
        screen.blit(debt_surface, (option_rect.x + 15, debt_y))
        
        # Requirements/status line
        req_surface = detail_font.render(option['requirements'], True, text_color)
        req_rect = req_surface.get_rect(x=option_rect.right - 15 - req_surface.get_width(), y=option_rect.bottom - 25)
        screen.blit(req_surface, req_rect)
        
        # Store clickable rect with option ID
        if option["available"] and option["affordable"]:
            clickable_rects.append({
                'rect': option_rect,
                'option_id': option["id"],
                'type': 'research_option'
            })
    
    # Cancel/Dismiss button
    button_width = 140
    button_height = 45
    button_x = dialog_rect.centerx - button_width // 2
    button_y = dialog_rect.bottom - 80
    cancel_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Cancel button styling
    pygame.draw.rect(screen, (70, 70, 120), cancel_rect, border_radius=8)
    pygame.draw.rect(screen, (120, 120, 200), cancel_rect, width=3, border_radius=8)
    
    # Cancel button text
    cancel_text = button_font.render("Cancel", True, (255, 255, 255))
    text_rect = cancel_text.get_rect(center=(cancel_rect.centerx, cancel_rect.centery - 8))
    screen.blit(cancel_text, text_rect)
    
    # Keyboard shortcut hint on button  
    shortcut_font = pygame.font.Font(None, int(h * 0.018))
    shortcut_text = shortcut_font.render("(ESC or Backspace)", True, (200, 200, 200))
    shortcut_rect = shortcut_text.get_rect(center=(cancel_rect.centerx, cancel_rect.centery + 10))
    screen.blit(shortcut_text, shortcut_rect)
    
    clickable_rects.append({
        'rect': cancel_rect,
        'type': 'cancel'
    })
    
    return clickable_rects


def draw_hiring_dialog(screen: pygame.Surface, hiring_dialog: Dict[str, Any], w: int, h: int, game_state: Any = None) -> List[Dict[str, Any]]:
    """
    Draw the employee hiring dialog with available employee subtypes for selection.
    
    Args:
        screen: pygame surface to draw on
        hiring_dialog: dict with hiring dialog state including available_subtypes
        w, h: screen width and height
        
    Returns:
        List of rects for each employee option and dismiss button for click detection
    """
    if not hiring_dialog:
        return []
    
    # Check if we're in researcher pool mode
    if hiring_dialog.get("mode") == "researcher_pool":
        return draw_researcher_pool_dialog(screen, hiring_dialog, w, h, game_state)
        
    # Create semi-transparent background overlay
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Dialog dimensions
    dialog_width = int(w * 0.8)
    dialog_height = int(h * 0.85)
    dialog_x = (w - dialog_width) // 2
    dialog_y = (h - dialog_height) // 2
    
    # Dialog background
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    pygame.draw.rect(screen, (40, 50, 60), dialog_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 150, 200), dialog_rect, width=3, border_radius=10)
    
    # Fonts
    title_font = pygame.font.Font(None, int(h * 0.04))
    desc_font = pygame.font.Font(None, int(h * 0.025))
    employee_font = pygame.font.Font(None, int(h * 0.028))
    button_font = pygame.font.Font(None, int(h * 0.025))
    
    # Title
    title = hiring_dialog["title"]
    title_surface = title_font.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect(centerx=dialog_rect.centerx, y=dialog_y + 20)
    screen.blit(title_surface, title_rect)
    
    # Description
    description = hiring_dialog["description"]
    desc_surface = desc_font.render(description, True, (200, 200, 200))
    desc_rect = desc_surface.get_rect(centerx=dialog_rect.centerx, y=title_rect.bottom + 15)
    screen.blit(desc_surface, desc_rect)
    
    # Employee options area
    options_start_y = desc_rect.bottom + 30
    option_height = 80
    option_spacing = 10
    clickable_rects = []
    
    available_subtypes = hiring_dialog["available_subtypes"]
    
    for i, subtype_info in enumerate(available_subtypes):
        subtype_data = subtype_info["data"]
        affordable = subtype_info["affordable"]
        
        # Option background
        option_y = options_start_y + i * (option_height + option_spacing)
        option_rect = pygame.Rect(dialog_x + 20, option_y, dialog_width - 40, option_height)
        
        # Color based on affordability
        if affordable:
            bg_color = (60, 80, 100)
            border_color = (120, 180, 240)
            text_color = (255, 255, 255)
        else:
            bg_color = (40, 40, 40)
            border_color = (80, 80, 80)
            text_color = (150, 150, 150)
        
        pygame.draw.rect(screen, bg_color, option_rect, border_radius=5)
        pygame.draw.rect(screen, border_color, option_rect, width=2, border_radius=5)
        
        # Employee name
        name_surface = employee_font.render(subtype_data["name"], True, text_color)
        name_rect = name_surface.get_rect(x=option_rect.x + 15, y=option_rect.y + 10)
        screen.blit(name_surface, name_rect)
        
        # Cost and AP info
        cost_text = f"${subtype_data['cost']} - {subtype_data['ap_cost']} AP"
        cost_surface = button_font.render(cost_text, True, text_color)
        cost_rect = cost_surface.get_rect(x=option_rect.right - 15 - cost_surface.get_width(), y=option_rect.y + 10)
        screen.blit(cost_surface, cost_rect)
        
        # Description
        desc_lines = wrap_text(subtype_data["description"], button_font, dialog_width - 80)
        for j, line in enumerate(desc_lines[:2]):  # Limit to 2 lines
            line_surface = button_font.render(line, True, text_color)
            line_y = name_rect.bottom + 5 + j * (button_font.get_height() + 2)
            screen.blit(line_surface, (option_rect.x + 15, line_y))
        
        # Store clickable rect with subtype ID
        if affordable:
            clickable_rects.append({
                'rect': option_rect,
                'subtype_id': subtype_info["id"],
                'type': 'employee_option'
            })
    
    # Cancel/Dismiss button (more prominent)
    button_width = 140
    button_height = 45
    button_x = dialog_rect.centerx - button_width // 2
    button_y = dialog_rect.bottom - 80
    cancel_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # More prominent cancel button styling
    pygame.draw.rect(screen, (120, 70, 70), cancel_rect, border_radius=8)
    pygame.draw.rect(screen, (200, 120, 120), cancel_rect, width=3, border_radius=8)
    
    # Cancel button text with keyboard shortcut
    cancel_text = button_font.render("Cancel", True, (255, 255, 255))
    text_rect = cancel_text.get_rect(center=(cancel_rect.centerx, cancel_rect.centery - 8))
    screen.blit(cancel_text, text_rect)
    
    # Keyboard shortcut hint on button  
    shortcut_font = pygame.font.Font(None, int(h * 0.018))
    shortcut_text = shortcut_font.render("(? or Backspace)", True, (200, 200, 200))
    shortcut_rect = shortcut_text.get_rect(center=(cancel_rect.centerx, cancel_rect.centery + 10))
    screen.blit(shortcut_text, shortcut_rect)
    
    clickable_rects.append({
        'rect': cancel_rect,
        'type': 'cancel'
    })
    
    # Enhanced instructions with clear keyboard mapping
    instructions = [
        "Click an employee type to hire them",
        "? (Left Arrow) or Backspace to cancel ? Escape for emergency exit",
        "One function per key - simple navigation"
    ]
    
    inst_font = pygame.font.Font(None, int(h * 0.022))
    inst_y = cancel_rect.bottom + 15
    
    for i, instruction in enumerate(instructions):
        if i == 0:
            # Main instruction - white
            inst_surface = inst_font.render(instruction, True, (255, 255, 255))
        else:
            # Secondary instructions - lighter gray
            inst_surface = inst_font.render(instruction, True, (180, 180, 180))
        
        inst_rect = inst_surface.get_rect(centerx=dialog_rect.centerx, y=inst_y)
        screen.blit(inst_surface, inst_rect)
        inst_y += inst_surface.get_height() + 3
    
    return clickable_rects
