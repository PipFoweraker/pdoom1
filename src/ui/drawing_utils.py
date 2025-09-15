"""
Drawing Utilities Module

This module provides drawing utility functions for the P(Doom) UI system.
Extracted from the main ui.py monolith as part of the Phase 3 refactoring effort.

Functions:
- draw_resource_icon: 8-bit style resource icons (money, research, papers, compute)
- draw_tooltip: Hover tooltips with automatic positioning
- should_show_ui_element: Tutorial progress UI element visibility
- draw_seed_prompt: Seed selection screen rendering
- Context info creation helpers
"""

import pygame
from typing import Dict, Any, Tuple


def draw_resource_icon(screen: pygame.Surface, icon_type: str, x: int, y: int, size: int = 16) -> None:
    """
    Draw 8-bit style resource icons.
    
    Args:
        screen: pygame surface to draw on
        icon_type: 'money', 'research', 'papers', 'compute'
        x, y: position to draw at
        size: icon size in pixels
    """
    if icon_type == 'money':
        # Stylized $ sign in 8-bit style
        # Vertical line
        pygame.draw.rect(screen, (255, 230, 60), (x + size//2 - 1, y, 2, size))
        # Top horizontal
        pygame.draw.rect(screen, (255, 230, 60), (x + 2, y + 2, size - 4, 2))
        # Middle horizontal (shorter)
        pygame.draw.rect(screen, (255, 230, 60), (x + 3, y + size//2 - 1, size - 6, 2))
        # Bottom horizontal
        pygame.draw.rect(screen, (255, 230, 60), (x + 2, y + size - 4, size - 4, 2))
        
    elif icon_type == 'research':
        # Light bulb icon
        # Bulb top (round)
        pygame.draw.circle(screen, (150, 200, 255), (x + size//2, y + size//3), size//3)
        # Bulb base (rectangle)
        pygame.draw.rect(screen, (150, 200, 255), (x + size//2 - 2, y + size//2, 4, size//3))
        # Filament lines
        pygame.draw.line(screen, (100, 150, 200), (x + size//2 - 2, y + size//3), (x + size//2 + 2, y + size//3))
        pygame.draw.line(screen, (100, 150, 200), (x + size//2 - 1, y + size//3 + 2), (x + size//2 + 1, y + size//3 + 2))
        
    elif icon_type == 'papers':
        # Paper/document icon
        # Main rectangle
        pygame.draw.rect(screen, (255, 200, 100), (x + 2, y + 2, size - 6, size - 4))
        # Border
        pygame.draw.rect(screen, (200, 150, 50), (x + 2, y + 2, size - 6, size - 4), 1)
        # Text lines
        for i in range(3):
            line_y = y + 5 + i * 3
            pygame.draw.line(screen, (200, 150, 50), (x + 4, line_y), (x + size - 6, line_y))
            
    elif icon_type == 'compute':
        # Exponential/power symbol (like e^x or 2^n)
        # Draw "2" 
        pygame.draw.rect(screen, (100, 255, 150), (x + 2, y + 2, 4, 2))
        pygame.draw.rect(screen, (100, 255, 150), (x + 6, y + 4, 2, 3))
        pygame.draw.rect(screen, (100, 255, 150), (x + 2, y + 7, 6, 2))
        # Draw superscript "n"
        pygame.draw.rect(screen, (100, 255, 150), (x + 10, y + 2, 2, 4))
        pygame.draw.rect(screen, (100, 255, 150), (x + 12, y + 3, 1, 1))
        pygame.draw.rect(screen, (100, 255, 150), (x + 13, y + 4, 2, 2))


def draw_tooltip(screen: pygame.Surface, text: str, mouse_pos: Tuple[int, int], w: int, h: int) -> None:
    """
    Draw a tooltip at the mouse position with automatic boundary checking.
    
    Args:
        screen: pygame surface to draw on
        text: tooltip text content
        mouse_pos: (x, y) mouse position
        w, h: screen dimensions for boundary checking
    """
    font = pygame.font.SysFont('Consolas', int(h*0.018))
    surf = font.render(text, True, (230,255,200))
    tw, th = surf.get_size()
    px, py = mouse_pos
    # Prevent tooltip going off screen
    if px+tw > w: px = w-tw-10
    if py+th > h: py = h-th-10
    pygame.draw.rect(screen, (40, 40, 80), (px, py, tw+12, th+12), border_radius=6)
    screen.blit(surf, (px+6, py+6))


def should_show_ui_element(game_state: Any, element_id: str) -> bool:
    """
    Check if a UI element should be visible based on tutorial progress.
    
    Args:
        game_state: The current game state
        element_id: String identifier for the UI element
        
    Returns:
        bool: True if the element should be visible
    """
    # Import onboarding here to avoid circular imports
    try:
        from src.features.onboarding import onboarding
        
        # If tutorial is not active, show all elements
        if not onboarding.show_tutorial_overlay:
            return True
        
        # Check if element should be visible based on tutorial progress
        return onboarding.should_show_ui_element(element_id)
    except ImportError:
        # If onboarding not available, show all elements
        return True


def create_action_context_info(action: Dict[str, Any], game_state: Any, action_idx: int) -> Dict[str, Any]:
    """Create context info for an action to display in the context window."""
    ap_cost = action.get("ap_cost", 1)
    
    # Build title with shortcut key if available
    title = action["name"]
    if action_idx < 9:  # Only first 9 actions get keyboard shortcuts
        try:
            from src.services.keybinding_manager import keybinding_manager
            shortcut_key = keybinding_manager.get_action_display_key(f"action_{action_idx + 1}")
            title = f"[{shortcut_key}] {action['name']}"
        except ImportError:
            pass
    
    # Enhanced description for research actions showing current quality
    base_desc = action['desc']
    if hasattr(game_state, 'research_quality_unlocked') and game_state.research_quality_unlocked:
        if 'Research' in action['name'] and action['name'] not in ['Set Research Quality: Rushed', 'Set Research Quality: Standard', 'Set Research Quality: Thorough']:
            quality_suffix = f" [{game_state.current_research_quality.value.title()}]"
            base_desc += quality_suffix
    
    # Build details list - handle dynamic costs
    action_cost = action['cost']
    if callable(action_cost):
        action_cost = action_cost(game_state)
    
    details = [
        f"Cost: ${action_cost}",
        f"Action Points: {ap_cost}",
    ]
    
    # Add delegation info if available
    if action.get("delegatable", False):
        staff_req = action.get("delegate_staff_req", 1)
        delegate_ap = action.get("delegate_ap_cost", 0)
        effectiveness = action.get("Delegate_effectiveness", 1.0)
        details.append(f"Delegatable: Requires {staff_req} admin staff, {delegate_ap} AP, {int(effectiveness*100)}% effective")
    
    # Add availability status
    if game_state.action_points < ap_cost:
        details.append("! Not enough Action Points")
    
    # Handle dynamic cost evaluation (for economic config system)
    action_cost = action['cost']
    if callable(action_cost):
        action_cost = action_cost(game_state)
    
    if game_state.money < action_cost:
        details.append("! Not enough Money")
    
    return {
        'title': title,
        'description': base_desc,
        'details': details
    }


def create_upgrade_context_info(upgrade: Dict[str, Any], game_state: Any, upgrade_idx: int) -> Dict[str, Any]:
    """Create context info for an upgrade to display in the context window."""
    is_purchased = upgrade.get("purchased", False)
    
    title = upgrade["name"]
    if is_purchased:
        title += " (Purchased)"
    
    details = [
        f"Cost: ${upgrade['cost']}",
    ]
    
    # Add availability status
    if not is_purchased:
        if game_state.money < upgrade['cost']:
            details.append("! Not enough Money")
        else:
            details.append("+ Available for purchase")
    else:
        details.append("+ Effect is active")
    
    return {
        'title': title,
        'description': upgrade["desc"],
        'details': details
    }


def get_default_context_info(game_state: Any) -> Dict[str, Any]:
    """Get default context info when nothing is hovered."""
    lab_name = getattr(game_state, 'lab_name', 'Unknown Labs')
    return {
        'title': f'{lab_name}',
        'description': 'Your AI research laboratory. Hover over actions and upgrades for detailed information.',
        'details': [
            f'Turn: {game_state.turn}',
            f'Staff: {game_state.staff}',
            f'Money: ${game_state.money}',
            f'Reputation: {game_state.reputation}',
            'Tip: Use keyboard shortcuts 1-9 for quick actions'
        ]
    }


def draw_seed_prompt(screen: pygame.Surface, current_input: str, weekly_suggestion: str) -> None:
    """
    Draw the seed selection prompt screen.
    
    Args:
        screen: pygame surface to draw on
        current_input: current text input from user
        weekly_suggestion: suggested weekly challenge seed
    """
    font = pygame.font.SysFont('Consolas', 40)
    small = pygame.font.SysFont('Consolas', 24)
    title = pygame.font.SysFont('Consolas', 70, bold=True)
    w, h = screen.get_size()
    
    # Fix alignment: center title properly without hardcoded offset
    title_text = title.render("P(Doom)", True, (240,255,220))
    title_x = (w - title_text.get_width()) // 2  # Proper centering
    screen.blit(title_text, (title_x, h//6))
    
    # Center prompt text properly
    prompt_text = font.render("Enter Seed (for weekly challenge, or blank for default):", True, (210,210,255))
    prompt_x = (w - prompt_text.get_width()) // 2
    screen.blit(prompt_text, (prompt_x, h//3))
    
    # Use consistent box positioning
    box = pygame.Rect(w//4, h//2, w//2, 60)
    pygame.draw.rect(screen, (60,60,110), box, border_radius=8)
    pygame.draw.rect(screen, (130,130,210), box, width=3, border_radius=8)
    txt = font.render(current_input, True, (255,255,255))
    screen.blit(txt, (box.x+10, box.y+10))
    
    # Center additional text properly
    weekly_text = small.render(f"Suggested weekly seed: {weekly_suggestion}", True, (200,255,200))
    weekly_x = (w - weekly_text.get_width()) // 2
    screen.blit(weekly_text, (weekly_x, h//2 + 80))
    
    instruction_text = small.render("Press [Enter] to start, [Esc] to quit.", True, (255,255,180))
    instruction_x = (w - instruction_text.get_width()) // 2
    screen.blit(instruction_text, (instruction_x, h//2 + 120))
