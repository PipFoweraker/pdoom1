"""
Layout utilities for UI positioning and safe zone management.

This module handles the positioning logic for UI elements to prevent overlap
and maintain usability according to Issue #121.
"""

import pygame


def get_ui_safe_zones(w, h):
    """
    Define safe zones where overlays should not be positioned to avoid obscuring interactive areas.
    
    This function implements the solution for Issue #121 (UI overlap / lack of draggability)
    by defining reserved areas that overlay panels should avoid to maintain UI usability.
    
    Args:
        w, h: screen width and height
        
    Returns:
        List of pygame.Rect representing reserved areas that should be avoided by overlays
    """
    safe_zones = []
    
    # Resource header area (top bar with money, staff, reputation, etc.)
    resource_header = pygame.Rect(0, 0, w, int(h * 0.18))
    safe_zones.append(resource_header)
    
    # Action buttons area (left side) - narrower to allow more overlay space
    action_area = pygame.Rect(0, int(h * 0.18), int(w * 0.35), int(h * 0.55))
    safe_zones.append(action_area)
    
    # Upgrade area (right side) - narrower and shorter to allow more overlay space
    upgrade_area = pygame.Rect(int(w * 0.65), int(h * 0.18), int(w * 0.35), int(h * 0.45))
    safe_zones.append(upgrade_area)
    
    # Event log area (bottom left) - smaller area
    event_log_area = pygame.Rect(0, int(h * 0.73), int(w * 0.45), int(h * 0.27))
    safe_zones.append(event_log_area)
    
    # End turn button area (bottom right) - smaller area
    end_turn_area = pygame.Rect(int(w * 0.75), int(h * 0.85), int(w * 0.25), int(h * 0.15))
    safe_zones.append(end_turn_area)
    
    return safe_zones


def find_safe_overlay_position(overlay_rect, screen_w, screen_h, safe_zones):
    """
    Find a position for an overlay that doesn't intersect with safe zones.
    
    This implements the first-fit positioning algorithm for Issue #121 (UI overlap prevention)
    to ensure overlay panels don't obscure core interactive areas.
    
    Args:
        overlay_rect: pygame.Rect for the overlay to position
        screen_w, screen_h: screen dimensions
        safe_zones: list of pygame.Rect representing areas to avoid
        
    Returns:
        pygame.Rect: positioned overlay rectangle
    """
    # Try different positions, prioritizing the gap between action and upgrade areas
    # Based on safe zones: action area ends at x=280, upgrade area starts at x=520
    # So we have a gap from x=280 to x=520 (width=240)
    gap_start_x = 285  # Just after action area
    gap_end_x = 515    # Just before upgrade area
    gap_width = gap_end_x - gap_start_x
    
    positions_to_try = []
    
    # If overlay fits in the gap, use it
    if overlay_rect.width <= gap_width:
        # Center in the gap
        gap_center_x = gap_start_x + (gap_width - overlay_rect.width) // 2
        positions_to_try.extend([
            (gap_center_x, 180),  # Center of gap, below header
            (gap_center_x, 220),  # Center of gap, a bit lower
            (gap_start_x, 200),   # Left side of gap
            (gap_end_x - overlay_rect.width, 200),  # Right side of gap
        ])
    
    # Add other fallback positions
    positions_to_try.extend([
        # Above event log area (center screen)
        (screen_w // 2 - overlay_rect.width // 2, 350),
        # Top center (below header)
        (screen_w // 2 - overlay_rect.width // 2, 130),
        # Center of screen (last resort)
        (screen_w // 2 - overlay_rect.width // 2, screen_h // 2 - overlay_rect.height // 2),
    ])
    
    for x, y in positions_to_try:
        # Ensure overlay stays within screen bounds
        x = max(0, min(x, screen_w - overlay_rect.width))
        y = max(0, min(y, screen_h - overlay_rect.height))
        
        test_rect = pygame.Rect(x, y, overlay_rect.width, overlay_rect.height)
        
        # Check if this position intersects with any safe zone
        intersects_safe_zone = False
        for safe_zone in safe_zones:
            if test_rect.colliderect(safe_zone):
                intersects_safe_zone = True
                break
        
        if not intersects_safe_zone:
            # Found a position that doesn't intersect with safe zones
            overlay_rect.x = x
            overlay_rect.y = y
            return overlay_rect
    
    # If no safe position found, use the least problematic fallback (center of screen)
    overlay_rect.x = screen_w // 2 - overlay_rect.width // 2
    overlay_rect.y = screen_h // 2 - overlay_rect.height // 2
    return overlay_rect