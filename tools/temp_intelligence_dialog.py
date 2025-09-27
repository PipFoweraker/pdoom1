
def draw_intelligence_dialog(screen: pygame.Surface, intelligence_dialog: Dict[str, Any], w: int, h: int) -> List[Dict[str, Any]]:
    """
    Draw the intelligence operations dialog showing available intelligence gathering options.
    
    Args:
        screen: pygame surface to draw on
        intelligence_dialog: intelligence dialog configuration
        w, h: screen dimensions
        
    Returns:
        List of clickable rect information for handling clicks
    """
    # Create semi-transparent background overlay
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Dialog dimensions (smaller than hiring dialog)
    dialog_width = int(w * 0.7)
    dialog_height = int(h * 0.6)
    dialog_x = (w - dialog_width) // 2
    dialog_y = (h - dialog_height) // 2
    
    # Draw main dialog background
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    pygame.draw.rect(screen, (40, 40, 45), dialog_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 120), dialog_rect, width=3, border_radius=5)
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title_text = title_font.render(intelligence_dialog["title"], True, (255, 255, 255))
    title_rect = title_text.get_rect(centerx=dialog_rect.centerx, y=dialog_y + 20)
    screen.blit(title_text, title_rect)
    
    # Description
    desc_font = pygame.font.Font(None, 28)
    desc_y = title_rect.bottom + 15
    desc_lines = wrap_text(intelligence_dialog["description"], desc_font, dialog_width - 40)
    for line in desc_lines:
        desc_surface = desc_font.render(line, True, (200, 200, 200))
        desc_rect = desc_surface.get_rect(centerx=dialog_rect.centerx, y=desc_y)
        screen.blit(desc_surface, desc_rect)
        desc_y += desc_surface.get_height() + 5
    
    # Intelligence options
    clickable_rects = []
    option_font = pygame.font.Font(None, 32)
    detail_font = pygame.font.Font(None, 24)
    
    option_y = desc_y + 20
    button_height = 60
    button_margin = 10
    
    for option in intelligence_dialog["options"]:
        # Option button
        button_rect = pygame.Rect(dialog_x + 20, option_y, dialog_width - 40, button_height)
        
        # Color based on availability
        if option["available"]:
            if option["cost"] == 0:
                button_color = (50, 80, 50)  # Green for free options
                hover_color = (70, 100, 70)
            else:
                button_color = (60, 60, 80)  # Blue for paid options
                hover_color = (80, 80, 100)
        else:
            button_color = (60, 40, 40)  # Red for unavailable
            hover_color = (80, 60, 60)
        
        # Check if mouse is hovering
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = button_rect.collidepoint(mouse_pos) if option["available"] else False
        current_color = hover_color if is_hovering else button_color
        
        pygame.draw.rect(screen, current_color, button_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 120, 140), button_rect, width=2, border_radius=8)
        
        # Option name
        name_surface = option_font.render(option["name"], True, (255, 255, 255))
        name_rect = name_surface.get_rect(x=button_rect.x + 15, y=button_rect.y + 8)
        screen.blit(name_surface, name_rect)
        
        # Cost info
        cost_text = f"Cost: ${option['cost']}, {option['ap_cost']} AP"
        cost_surface = detail_font.render(cost_text, True, (180, 180, 180))
        cost_rect = cost_surface.get_rect(x=button_rect.right - cost_surface.get_width() - 15, y=button_rect.y + 8)
        screen.blit(cost_surface, cost_rect)
        
        # Description
        desc_surface = detail_font.render(option["description"], True, (200, 200, 200))
        desc_rect = desc_surface.get_rect(x=button_rect.x + 15, y=name_rect.bottom + 3)
        screen.blit(desc_surface, desc_rect)
        
        # Details (if available)
        if "details" in option:
            details_surface = detail_font.render(option["details"], True, (160, 160, 160))
            details_rect = details_surface.get_rect(x=button_rect.x + 15, y=desc_rect.bottom + 2)
            screen.blit(details_surface, details_rect)
        
        # Add to clickable rects if available
        if option["available"]:
            clickable_rects.append({
                'rect': button_rect,
                'type': 'intelligence_option',
                'option_id': option["id"]
            })
        
        option_y += button_height + button_margin
    
    # Cancel button
    cancel_button_width = 120
    cancel_button_height = 40
    cancel_x = dialog_rect.centerx - cancel_button_width // 2
    cancel_y = dialog_rect.bottom - cancel_button_height - 20
    cancel_rect = pygame.Rect(cancel_x, cancel_y, cancel_button_width, cancel_button_height)
    
    # Check if mouse is hovering over cancel button
    mouse_pos = pygame.mouse.get_pos()
    is_cancel_hovering = cancel_rect.collidepoint(mouse_pos)
    cancel_color = (80, 60, 60) if is_cancel_hovering else (60, 40, 40)
    
    pygame.draw.rect(screen, cancel_color, cancel_rect, border_radius=5)
    pygame.draw.rect(screen, (120, 120, 140), cancel_rect, width=2, border_radius=5)
    
    cancel_font = pygame.font.Font(None, 28)
    cancel_text = cancel_font.render("Cancel", True, (255, 255, 255))
    cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
    screen.blit(cancel_text, cancel_text_rect)
    
    clickable_rects.append({
        'rect': cancel_rect,
        'type': 'cancel'
    })
    
    return clickable_rects
