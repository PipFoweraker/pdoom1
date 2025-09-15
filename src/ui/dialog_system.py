"""
Dialog System Module

Handles all dialog rendering functions for P(Doom) UI system.
Extracted from monolithic ui.py for better maintainability.

Functions:
- draw_fundraising_dialog: Renders fundraising strategy dialog
- draw_research_dialog: Renders research strategy dialog  
- draw_hiring_dialog: Renders employee hiring dialog
- draw_researcher_pool_dialog: Renders specialist researcher pool dialog
"""

import pygame
from typing import Dict, Any, Optional, List, Tuple


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """Wrap text to fit within max_width using the provided font."""
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        word_width = font.size(word + ' ')[0]
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                # Word is too long for the line, force it
                lines.append(word)
                current_line = []
                current_width = 0
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


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


def draw_researcher_pool_dialog(screen: pygame.Surface, hiring_dialog: Dict[str, Any], w: int, h: int, game_state=None) -> List[Dict[str, Any]]:
    """
    Draw the researcher pool hiring dialog showing available specialist researchers.
    
    Args:
        screen: pygame surface to draw on
        hiring_dialog: dict with hiring dialog state
        w, h: screen width and height
        game_state: optional game state for accessing researcher data
        
    Returns:
        List of clickable rects for interaction
    """
    # Get available researchers from game_state if provided
    if game_state and hasattr(game_state, 'available_researchers'):
        available_researchers = game_state.available_researchers
    else:
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
    
    # Dialog background
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    pygame.draw.rect(screen, (40, 50, 60), dialog_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 150, 200), dialog_rect, width=3, border_radius=10)
    
    # Fonts
    title_font = pygame.font.Font(None, int(h * 0.04))
    desc_font = pygame.font.Font(None, int(h * 0.025))
    researcher_font = pygame.font.Font(None, int(h * 0.026))
    detail_font = pygame.font.Font(None, int(h * 0.022))
    
    # Title
    title_surface = title_font.render("Available Specialist Researchers", True, (255, 255, 255))
    title_rect = title_surface.get_rect(centerx=dialog_rect.centerx, y=dialog_y + 20)
    screen.blit(title_surface, title_rect)
    
    # Description
    desc_text = "Select a researcher to hire for your team. Each has unique specializations and traits."
    desc_surface = desc_font.render(desc_text, True, (200, 200, 200))
    desc_rect = desc_surface.get_rect(centerx=dialog_rect.centerx, y=title_rect.bottom + 15)
    screen.blit(desc_surface, desc_rect)
    
    clickable_rects = []
    
    # Researcher list
    researcher_area_y = desc_rect.bottom + 30
    researcher_item_height = 120
    researcher_padding = 10
    
    for i, researcher in enumerate(available_researchers):
        # Check affordability using game_state if available
        if game_state and hasattr(researcher, 'cost') and hasattr(game_state, 'money'):
            affordable = game_state.money >= researcher.cost
        else:
            affordable = True  # Default to affordable if we can't check
        
        # Researcher item background
        item_y = researcher_area_y + i * (researcher_item_height + researcher_padding)
        item_rect = pygame.Rect(dialog_x + 20, item_y, dialog_width - 40, researcher_item_height)
        
        # Color based on affordability
        if affordable:
            bg_color = (60, 80, 100)
            border_color = (120, 180, 240)
            text_color = (255, 255, 255)
        else:
            bg_color = (40, 40, 40)
            border_color = (80, 80, 80)
            text_color = (150, 150, 150)
        
        pygame.draw.rect(screen, bg_color, item_rect, border_radius=5)
        pygame.draw.rect(screen, border_color, item_rect, width=2, border_radius=5)
        
        # Researcher name and specialization
        name_text = f"{researcher.name}"
        specialization_text = f"Specialization: {researcher.specialization.replace('_', ' ').title()}"
        
        name_surface = researcher_font.render(name_text, True, text_color)
        spec_surface = detail_font.render(specialization_text, True, text_color)
        
        name_rect = name_surface.get_rect(x=item_rect.x + 15, y=item_rect.y + 10)
        spec_rect = spec_surface.get_rect(x=item_rect.x + 15, y=name_rect.bottom + 5)
        
        screen.blit(name_surface, name_rect)
        screen.blit(spec_surface, spec_rect)
        
        # Skill level and salary
        skill_text = f"Skill Level: {researcher.skill_level}/10"
        salary_text = f"Salary: ${researcher.salary_expectation} - 2 AP"
        
        skill_surface = detail_font.render(skill_text, True, text_color)
        salary_surface = detail_font.render(salary_text, True, text_color)
        
        skill_rect = skill_surface.get_rect(x=item_rect.x + 15, y=spec_rect.bottom + 5)
        salary_rect = salary_surface.get_rect(x=item_rect.right - 15 - salary_surface.get_width(), y=item_rect.y + 10)
        
        screen.blit(skill_surface, skill_rect)
        screen.blit(salary_surface, salary_rect)
        
        # Traits
        if researcher.traits:
            traits_text = f"Traits: {', '.join(trait.replace('_', ' ').title() for trait in researcher.traits)}"
        else:
            traits_text = "Traits: None"
        
        # Limit traits text length
        if len(traits_text) > 60:
            traits_text = traits_text[:57] + "..."
        
        traits_surface = detail_font.render(traits_text, True, text_color)
        traits_rect = traits_surface.get_rect(x=item_rect.x + 15, y=skill_rect.bottom + 5)
        screen.blit(traits_surface, traits_rect)
        
        # Store clickable rect
        if affordable:
            clickable_rects.append({
                'rect': item_rect,
                'researcher_index': i,
                'type': 'researcher_option'
            })
    
    # Back and Cancel buttons
    button_width = 120
    button_height = 40
    button_y = dialog_rect.bottom - 60
    
    # Back button (return to employee selection)
    back_x = dialog_rect.centerx - button_width - 10
    back_rect = pygame.Rect(back_x, button_y, button_width, button_height)
    pygame.draw.rect(screen, (80, 120, 160), back_rect, border_radius=5)
    pygame.draw.rect(screen, (120, 160, 200), back_rect, width=2, border_radius=5)
    
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


def draw_hiring_dialog(screen: pygame.Surface, hiring_dialog: Dict[str, Any], w: int, h: int, game_state=None) -> List[Dict[str, Any]]:
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
