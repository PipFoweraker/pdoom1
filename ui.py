import pygame
from typing import Dict, Any, Optional, List, Tuple
from src.features.visual_feedback import visual_feedback, ButtonState, FeedbackStyle, draw_low_poly_button
from src.services.keyboard_shortcuts import get_main_menu_shortcuts, get_in_game_shortcuts, format_shortcut_list

# TEMPORARY: Commenting out extracted functions to avoid circular import issues
# These will be re-enabled once circular dependencies are resolved
# from src.ui.dialog_system import draw_fundraising_dialog, draw_research_dialog, draw_hiring_dialog, draw_researcher_pool_dialog
# from src.ui.bug_report import draw_bug_report_form, draw_bug_report_success


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
        effectiveness = action.get("delegate_effectiveness", 1.0)
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
        'description': 'Hover over actions or upgrades to see detailed information here.',
        'details': [
            f'Turn {game_state.turn} - {game_state.game_clock.get_formatted_date()}',
            f'Money: ${game_state.money}',
            f'Action Points: {game_state.action_points}',
            f'p(Doom): {game_state.doom}'
        ]
    }

def get_ui_safe_zones(w: int, h: int) -> List[pygame.Rect]:
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
    
    # Event log area (bottom left) - smaller area, adjusted for context window
    event_log_area = pygame.Rect(0, int(h * 0.73), int(w * 0.45), int(h * 0.14))  # Reduced height for context window
    safe_zones.append(event_log_area)
    
    # Context window area (bottom bar) - persistent area for context information
    context_area = pygame.Rect(0, int(h * 0.87), w, int(h * 0.13))  # Bottom 13% of screen
    safe_zones.append(context_area)
    
    # End turn button area (bottom right) - adjusted for context window
    end_turn_area = pygame.Rect(int(w * 0.75), int(h * 0.73), int(w * 0.25), int(h * 0.14))  # Moved up for context window
    safe_zones.append(end_turn_area)
    
    return safe_zones


def find_safe_overlay_position(overlay_rect: pygame.Rect, screen_w: int, screen_h: int, safe_zones: List[pygame.Rect]) -> pygame.Rect:
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
            overlay_rect.x = x
            overlay_rect.y = y
            return overlay_rect
    
    # If no safe position found, try to find the position with minimal intersection
    best_position = None
    min_intersection_area = float('inf')
    
    for x, y in positions_to_try:
        x = max(0, min(x, screen_w - overlay_rect.width))
        y = max(0, min(y, screen_h - overlay_rect.height))
        test_rect = pygame.Rect(x, y, overlay_rect.width, overlay_rect.height)
        
        total_intersection_area = 0
        for safe_zone in safe_zones:
            if test_rect.colliderect(safe_zone):
                intersection = test_rect.clip(safe_zone)
                total_intersection_area += intersection.width * intersection.height
        
        if total_intersection_area < min_intersection_area:
            min_intersection_area = total_intersection_area
            best_position = (x, y)
    
    # Use the position with minimal intersection
    if best_position:
        overlay_rect.x = best_position[0]
        overlay_rect.y = best_position[1]
    else:
        # Ultimate fallback: center of screen
        overlay_rect.x = screen_w // 2 - overlay_rect.width // 2
        overlay_rect.y = screen_h // 2 - overlay_rect.height // 2
    
    return overlay_rect

def should_show_back_button(depth: int) -> bool:
    """
    Helper function to determine if back button should be shown.
    
    Args:
        depth: current navigation depth
        
    Returns:
        bool: True if back button should be shown (depth >= 1), False otherwise
    
    Note: 
        Changed from depth > 1 to depth >= 1 to fix Issue #122/#118 
        (No back functionality / duplicate back button issue)
    """
    return depth >= 1

def draw_back_button(screen: pygame.Surface, w: int, h: int, navigation_depth: int, font: Optional[pygame.font.Font] = None) -> Optional[pygame.Rect]:
    """
    Draw a Back button when navigation depth >= 1.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for positioning
        navigation_depth: current navigation depth from navigation stack
        font: optional font for the button text
    
    Returns:
        pygame.Rect: The button rectangle for click detection, or None if not rendered
    """
    if not should_show_back_button(navigation_depth):
        return None
    
    if font is None:
        font = pygame.font.SysFont('Consolas', max(16, int(h * 0.025)))
    
    # Position button in top-left corner with margin
    margin = int(h * 0.02)
    button_text = "< Back"
    text_surf = font.render(button_text, True, (255, 255, 255))
    
    # Button styling
    padding = int(h * 0.01)
    button_width = text_surf.get_width() + padding * 2
    button_height = text_surf.get_height() + padding * 2
    button_rect = pygame.Rect(margin, margin, button_width, button_height)
    
    # Draw button background with subtle styling
    pygame.draw.rect(screen, (60, 60, 80), button_rect)
    pygame.draw.rect(screen, (120, 120, 140), button_rect, 2)
    
    # Center text in button
    text_x = button_rect.x + (button_rect.width - text_surf.get_width()) // 2
    text_y = button_rect.y + (button_rect.height - text_surf.get_height()) // 2
    screen.blit(text_surf, (text_x, text_y))
    
    return button_rect

def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """
    Splits the text into multiple lines so that each line fits within max_width.
    Returns a list of strings, each representing a line.
    Improved to handle overflow with better word breaking.
    """
    lines = []
    # Use textwrap to split into words, then try to pack as many as possible per line
    words = text.split(' ')
    curr_line = ''
    for word in words:
        test_line = curr_line + (' ' if curr_line else '') + word
        if font.size(test_line)[0] <= max_width:
            curr_line = test_line
        else:
            if curr_line:
                lines.append(curr_line)
                curr_line = word
            else:
                # Handle very long words that don't fit on a line
                # Break them using character-level wrapping as fallback
                if font.size(word)[0] > max_width:
                    # Character-level breaking for extremely long words
                    for i in range(1, len(word) + 1):
                        if font.size(word[:i])[0] > max_width:
                            if i > 1:
                                lines.append(word[:i-1])
                                word = word[i-1:]
                            break
                curr_line = word
    if curr_line:
        lines.append(curr_line)
    return lines

def render_text(text: str, font: pygame.font.Font, max_width: Optional[int] = None, color: Tuple[int, int, int] = (255,255,255), line_height_multiplier: float = 1.35) -> Tuple[List[Tuple[pygame.Surface, Tuple[int, int]]], pygame.Rect]:
    """Render text with optional word wrapping and consistent line height. Returns [(surface, (x_offset, y_offset)), ...], bounding rect."""
    lines = [text]
    if max_width:
        lines = wrap_text(text, font, max_width)
    surfaces = [font.render(line, True, color) for line in lines]
    
    # Use consistent line height for better visual spacing
    font_height = font.get_height()
    line_height = int(font_height * line_height_multiplier)
    
    widths = [surf.get_width() for surf in surfaces]
    total_width = max(widths) if widths else 0
    total_height = line_height * len(lines) if lines else 0
    
    # Calculate offsets with consistent line spacing
    offsets = [(0, i * line_height) for i in range(len(lines))]
    return list(zip(surfaces, offsets)), pygame.Rect(0, 0, total_width, total_height)

def draw_main_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, sound_manager: Optional[Any] = None) -> None:
    """
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
    """
    # Fonts for menu - scale based on screen size
    title_font = pygame.font.SysFont('Consolas', int(h*0.08), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.035))
    
    # Title at top
    title_surf = title_font.render("P(Doom)", True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.15)
    screen.blit(title_surf, (title_x, title_y))
    
    # Subtitle
    subtitle_font = pygame.font.SysFont('Consolas', int(h*0.025))
    subtitle_surf = subtitle_font.render("Bureaucracy Strategy Prototype", True, (200, 200, 200))
    subtitle_x = w // 2 - subtitle_surf.get_width() // 2
    subtitle_y = title_y + title_surf.get_height() + 10
    screen.blit(subtitle_surf, (subtitle_x, subtitle_y))
    
    # Menu items
    menu_items = [
        "Launch Lab",
        "Launch with Custom Seed", 
        "Settings",
        "Player Guide",
        "View Leaderboard",
        "Exit"
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
        "Use mouse or arrow keys to navigate",
        "Press Enter or click to select", 
        "Press Escape to quit"
    ]
    
    # Add DEV MODE specific instructions if enabled
    try:
        from src.services.dev_mode import is_dev_mode_enabled
        if is_dev_mode_enabled():
            instructions.append("F10 to toggle DEV MODE")
    except ImportError:
        pass
    
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
    
    left_title_surf = shortcut_font.render("Menu Controls:", True, (160, 160, 160))
    left_x = int(w * 0.05)
    left_y = int(h * 0.25)
    screen.blit(left_title_surf, (left_x, left_y))
    
    for i, shortcut_text in enumerate(left_formatted):
        shortcut_surf = shortcut_font.render(shortcut_text, True, (140, 140, 140))
        screen.blit(shortcut_surf, (left_x, left_y + 30 + i * 25))
    
    # Right side - In-Game shortcuts preview
    right_shortcuts = get_in_game_shortcuts()[:4]  # Show first 4 to fit space
    right_formatted = format_shortcut_list(right_shortcuts)
    
    right_title_surf = shortcut_font.render("In-Game Controls:", True, (160, 160, 160))
    right_x = int(w * 0.75)
    right_y = int(h * 0.25)
    screen.blit(right_title_surf, (right_x, right_y))
    
    for i, shortcut_text in enumerate(right_formatted):
        shortcut_surf = shortcut_font.render(shortcut_text, True, (140, 140, 140))
        screen.blit(shortcut_surf, (right_x, right_y + 30 + i * 25))
    
    # Draw sound toggle button if sound manager is available (Issue #89)
    if sound_manager:
        draw_mute_button_standalone(screen, sound_manager, w, h)
    
    # Draw DEV MODE indicator (top-left) and version (bottom-right)
    draw_dev_mode_indicator(screen, w, h)
    draw_version_footer(screen, w, h)

def draw_start_game_submenu(screen: pygame.Surface, w: int, h: int, selected_item: int) -> None:
    """Draw the start game submenu with different game launch options."""
    # Clear background
    screen.fill((50, 50, 50))
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.03))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.022))
    
    # Title
    title_surf = title_font.render("Start Game", True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.15)
    screen.blit(title_surf, (title_x, title_y))
    
    # Subtitle
    subtitle_text = "Choose your starting configuration:"
    subtitle_surf = desc_font.render(subtitle_text, True, (200, 200, 200))
    subtitle_x = w // 2 - subtitle_surf.get_width() // 2
    subtitle_y = title_y + title_surf.get_height() + 10
    screen.blit(subtitle_surf, (subtitle_x, subtitle_y))
    
    # Menu items with descriptions
    items_with_desc = [
        ("Basic New Game (Default Global Seed)", "Quick start with weekly seed - zero configuration"),
        ("Configure Game / Custom Seed", "Choose your own seed for reproducible games"), 
        ("Config Settings", "Modify game difficulty and starting resources"),
        ("Game Options", "Audio, display, and accessibility settings")
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
        "Use arrow keys or mouse to navigate",
        "Press Enter or click to select ? Press Escape to go back"
    ]
    
    inst_y = int(h * 0.85)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 5

def draw_sounds_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, game_state: Optional[Any] = None) -> None:
    """
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
    """
    # Fonts for menu - scale based on screen size
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.03))
    
    # Title at top
    title_surf = title_font.render("Sound Options", True, (255, 255, 255))
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
        f"Master Sound: {'ON' if master_enabled else 'OFF'}",
        f"Money Spend Sound: {'ON' if (sound_manager and sound_manager.is_sound_enabled('money_spend')) else 'OFF'}",
        f"Action Points Sound: {'ON' if (sound_manager and sound_manager.is_sound_enabled('ap_spend')) else 'OFF'}",
        f"Employee Hire Sound: {'ON' if (sound_manager and sound_manager.is_sound_enabled('blob')) else 'OFF'}",
        f"Error Beep Sound: {'ON' if (sound_manager and sound_manager.is_sound_enabled('error_beep')) else 'OFF'}",
        "Back to Main Menu"
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
        "Use arrow keys to navigate, Enter to toggle",
        "Press Escape or select Back to return to Main Menu"
    ]
    
    for i, instruction in enumerate(instructions):
        inst_surf = instruction_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        inst_y = int(h * 0.85) + i * 25
        screen.blit(inst_surf, (inst_x, inst_y))

def draw_config_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, configs: List[str], current_config_name: str) -> None:
    """
    Draw the configuration selection menu.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected config item
        configs: list of available config names
        current_config_name: name of currently active config
    """
    # Clear screen with grey background
    screen.fill((64, 64, 64))
    
    # Fonts for menu - scale based on screen size
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.035))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.025))
    
    # Title at top
    title_surf = title_font.render("Configuration Selection", True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.1)
    screen.blit(title_surf, (title_x, title_y))
    
    # Current config indicator
    current_surf = desc_font.render(f"Current: {current_config_name}", True, (200, 200, 200))
    current_x = w // 2 - current_surf.get_width() // 2
    current_y = title_y + title_surf.get_height() + 10
    screen.blit(current_surf, (current_x, current_y))
    
    # Menu items (configs + back button)
    all_items = configs + ["< Back to Main Menu"]
    
    button_width = int(w * 0.4)
    button_height = int(h * 0.06)
    start_y = int(h * 0.25)
    
    for i, item in enumerate(all_items):
        y = start_y + i * int(button_height + h * 0.02)
        x = w // 2 - button_width // 2
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.FOCUSED  # Use FOCUSED instead of SELECTED
        elif item == current_config_name:
            button_state = ButtonState.HOVER  # Use HOVER instead of ACTIVE
        else:
            button_state = ButtonState.NORMAL
        
        # Draw button using correct parameters
        button_rect = pygame.Rect(x, y, button_width, button_height)
        draw_low_poly_button(screen, button_rect, item, button_state)
    
    # Instructions at bottom
    instructions = [
        "Up/Down or mouse to navigate",
        "Enter or click to select configuration",
        "Escape to go back"
    ]
    
    for i, inst in enumerate(instructions):
        inst_surf = desc_font.render(inst, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        inst_y = int(h * 0.8) + i * int(h * 0.04)
        screen.blit(inst_surf, (inst_x, inst_y))

def draw_overlay(screen: pygame.Surface, title: Optional[str], content: Optional[str], scroll_offset: int, w: int, h: int, navigation_depth: int = 0) -> Optional[pygame.Rect]:
    """
    Draw a scrollable overlay for displaying README or Player Guide content.
    
    Args:
        screen: pygame surface to draw on
        title: string title to display at top of overlay (can be None)
        content: full text content to display (can be None)
        scroll_offset: vertical scroll position in pixels
        w, h: screen width and height for responsive layout
        navigation_depth: current navigation depth for Back button display
    
    Returns:
        back_button_rect: Rectangle for Back button click detection (or None)
    
    Features:
    - Semi-transparent dark background overlay
    - Centered content area with border
    - Scrollable text with line wrapping
    - Scroll indicators (up/down arrows) when content exceeds view area  
    - Responsive text sizing based on screen dimensions
    - Clear navigation instructions
    - Defensive handling of None title/content values
    - Back button when navigation depth > 1
    
    The overlay handles long documents by breaking them into lines and showing
    only the visible portion based on scroll_offset. Users can scroll with
    arrow keys to view the full document.
    """
    # Defensive handling for None values
    if title is None:
        title = "Error: No Title"
    if content is None:
        content = "Error: No content available.\n\nThis appears to be a bug where overlay content was not properly initialized.\nPlease report this issue."
    # Overlay background - semi-transparent dark background
    overlay_surface = pygame.Surface((w, h))
    overlay_surface.set_alpha(240)
    overlay_surface.fill((20, 20, 30))
    screen.blit(overlay_surface, (0, 0))
    
    # Draw Back button if needed
    back_button_rect = draw_back_button(screen, w, h, navigation_depth)
    
    # Content area
    margin = int(w * 0.1)
    content_x = margin
    content_y = int(h * 0.1)
    content_width = w - 2 * margin
    content_height = int(h * 0.7)
    
    # Background for content area
    content_rect = pygame.Rect(content_x, content_y, content_width, content_height)
    pygame.draw.rect(screen, (40, 40, 50), content_rect, border_radius=15)
    pygame.draw.rect(screen, (100, 100, 150), content_rect, width=3, border_radius=15)
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h*0.04), bold=True)
    title_surf = title_font.render(title, True, (255, 255, 255))
    title_x = content_x + (content_width - title_surf.get_width()) // 2
    title_y = content_y + int(h * 0.02)
    screen.blit(title_surf, (title_x, title_y))
    
    # Content text area
    text_area_y = title_y + title_surf.get_height() + int(h * 0.03)
    text_area_height = content_height - (text_area_y - content_y) - int(h * 0.05)
    text_margin = int(w * 0.02)
    text_width = content_width - 2 * text_margin
    
    # Font for content
    content_font = pygame.font.SysFont('Consolas', int(h*0.02))
    line_height = content_font.get_height()
    
    # Split content into lines and handle scrolling
    lines = content.split('\n')
    visible_lines = int(text_area_height // line_height)
    start_line = scroll_offset // line_height
    end_line = min(start_line + visible_lines, len(lines))
    
    # Draw visible lines
    for i in range(start_line, end_line):
        if i < len(lines):
            line = lines[i]
            # Simple text wrapping for long lines
            wrapped_lines = wrap_text(line, content_font, text_width)
            
            for j, wrapped_line in enumerate(wrapped_lines):
                y_pos = text_area_y + (i - start_line + j) * line_height - (scroll_offset % line_height)
                if y_pos >= text_area_y and y_pos < text_area_y + text_area_height:
                    line_surf = content_font.render(wrapped_line, True, (220, 220, 220))
                    screen.blit(line_surf, (content_x + text_margin, y_pos))
    
    # Scroll indicators
    if scroll_offset > 0:
        # Up arrow
        arrow_font = pygame.font.SysFont('Consolas', int(h*0.03), bold=True)
        up_arrow = arrow_font.render("^", True, (255, 255, 255))
        screen.blit(up_arrow, (content_x + content_width - 30, text_area_y))
    
    if (start_line + visible_lines) < len(lines):
        # Down arrow
        arrow_font = pygame.font.SysFont('Consolas', int(h*0.03), bold=True)
        down_arrow = arrow_font.render("v", True, (255, 255, 255))
        screen.blit(down_arrow, (content_x + content_width - 30, text_area_y + text_area_height - 30))
    
    # Instructions at bottom
    instruction_font = pygame.font.SysFont('Consolas', int(h*0.025))
    instructions = "Use arrow keys to scroll - Press Escape or click to return to menu"
    inst_surf = instruction_font.render(instructions, True, (180, 200, 255))
    inst_x = w // 2 - inst_surf.get_width() // 2
    inst_y = content_y + content_height + int(h * 0.03)
    screen.blit(inst_surf, (inst_x, inst_y))
    
    return back_button_rect

def draw_window_with_header(screen: pygame.Surface, rect: pygame.Rect, title: str, content: Optional[str] = None, minimized: bool = False, font: Optional[pygame.font.Font] = None) -> Tuple[pygame.Rect, pygame.Rect]:
    """
    Draw a window with a draggable header and minimize button.
    
    Args:
        screen: pygame surface to draw on
        rect: pygame.Rect defining window position and size
        title: window title text
        content: optional content to draw in window body
        minimized: whether window is in minimized state
        font: optional font for title text
        
    Returns:
        tuple: (header_rect, minimize_button_rect) for interaction handling
    """
    if font is None:
        font = pygame.font.SysFont('Consolas', 16)
    
    # Window colors
    header_color = (60, 60, 80)
    header_border = (120, 120, 140)
    body_color = (40, 40, 55)
    body_border = (100, 100, 120)
    
    # Header dimensions
    header_height = 30
    header_rect = pygame.Rect(rect.x, rect.y, rect.width, header_height)
    
    # Draw header
    pygame.draw.rect(screen, header_color, header_rect)
    pygame.draw.rect(screen, header_border, header_rect, 2)
    
    # Draw title text
    title_surf = font.render(title, True, (255, 255, 255))
    title_x = header_rect.x + 8
    title_y = header_rect.y + (header_height - title_surf.get_height()) // 2
    screen.blit(title_surf, (title_x, title_y))
    
    # Draw minimize button ([] or - based on state)
    button_size = 20
    button_margin = 5
    minimize_button_rect = pygame.Rect(
        header_rect.right - button_size - button_margin,
        header_rect.y + (header_height - button_size) // 2,
        button_size, button_size
    )
    
    # Button background
    button_color = (80, 80, 100)
    pygame.draw.rect(screen, button_color, minimize_button_rect)
    pygame.draw.rect(screen, header_border, minimize_button_rect, 1)
    
    # Button icon
    icon_color = (255, 255, 255)
    if minimized:
        # Restore icon ([])
        icon_rect = pygame.Rect(
            minimize_button_rect.x + 4, minimize_button_rect.y + 4,
            minimize_button_rect.width - 8, minimize_button_rect.height - 8
        )
        pygame.draw.rect(screen, icon_color, icon_rect, 2)
    else:
        # Minimize icon (-)
        line_y = minimize_button_rect.centery
        line_start = minimize_button_rect.x + 4
        line_end = minimize_button_rect.right - 4
        pygame.draw.line(screen, icon_color, (line_start, line_y), (line_end, line_y), 2)
    
    # Draw body if not minimized
    if not minimized:
        body_rect = pygame.Rect(rect.x, rect.y + header_height, rect.width, rect.height - header_height)
        pygame.draw.rect(screen, body_color, body_rect)
        pygame.draw.rect(screen, body_border, body_rect, 2)
        
        # Draw content if provided
        if content:
            content_rect = pygame.Rect(
                body_rect.x + 8, body_rect.y + 8,
                body_rect.width - 16, body_rect.height - 16
            )
            if isinstance(content, str):
                # Simple text content
                lines = content.split('\n')
                line_height = font.get_height() + 2
                for i, line in enumerate(lines):
                    if i * line_height < content_rect.height:
                        text_surf = font.render(line, True, (255, 255, 255))
                        screen.blit(text_surf, (content_rect.x, content_rect.y + i * line_height))
    
    return header_rect, minimize_button_rect

def draw_dev_mode_indicator(screen: pygame.Surface, w: int, h: int, font: Optional[pygame.font.Font] = None) -> None:
    """
    Draw developer mode indicator in top-left corner if DEV MODE is enabled.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for positioning
        font: optional font for dev mode text
    """
    try:
        from src.services.dev_mode import get_dev_status_text
        dev_text = get_dev_status_text()
        
        if not dev_text:
            return  # DEV MODE not enabled
        
        if font is None:
            font = pygame.font.SysFont('Consolas', max(14, int(h * 0.022)), bold=True)
        
        # Create text with bright orange/yellow color for visibility
        dev_surf = font.render(f"[{dev_text}]", True, (255, 165, 0))
        
        # Position in top-left corner with margin
        margin = int(h * 0.015)
        screen.blit(dev_surf, (margin, margin))
        
    except ImportError:
        pass  # Silently fail if dev_mode module not available


def draw_version_footer(screen: pygame.Surface, w: int, h: int, font: Optional[pygame.font.Font] = None) -> None:
    """
    Draw version information in the footer area.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for positioning
        font: optional font for version text
    """
    try:
        from src.services.version import get_display_version
        version_text = get_display_version()
    except ImportError:
        version_text = "dev"
    
    if font is None:
        font = pygame.font.SysFont('Consolas', max(12, int(h * 0.02)))
    
    # Position in bottom right corner with margin
    margin = int(h * 0.02)
    version_surf = font.render(version_text, True, (120, 120, 120))
    
    version_x = w - version_surf.get_width() - margin
    version_y = h - version_surf.get_height() - margin
    
    screen.blit(version_surf, (version_x, version_y))

def draw_version_header(screen: pygame.Surface, w: int, h: int, font: Optional[pygame.font.Font] = None) -> None:
    """
    Draw version information in the header area (alternative placement).
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for positioning
        font: optional font for version text
    """
    try:
        from src.services.version import get_display_version
        version_text = get_display_version()
    except ImportError:
        version_text = "dev"
    
    if font is None:
        font = pygame.font.SysFont('Consolas', max(12, int(h * 0.02)))
    
    # Position in top right corner with margin
    margin = int(h * 0.02)
    version_surf = font.render(version_text, True, (120, 120, 120))
    
    version_x = w - version_surf.get_width() - margin
    version_y = margin
    
    screen.blit(version_surf, (version_x, version_y))

def draw_loading_screen(screen: pygame.Surface, w: int, h: int, progress: float = 0, status_text: str = "Loading...", font: Optional[pygame.font.Font] = None) -> None:
    """
    Draw a loading screen with progress indicator and accessibility support.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height
        progress: loading progress (0.0 to 1.0)
        status_text: text to display for screen readers and status
        font: optional font for status text
        
    Returns:
        None
    
    Accessibility:
    - role="status" equivalent through clear status text
    - High contrast colors for visibility
    - Clear progress indication
    """
    if font is None:
        font = pygame.font.SysFont('Consolas', max(16, int(h * 0.03)))
    
    # Dark background
    screen.fill((20, 20, 30))
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h * 0.06), bold=True)
    title_text = title_font.render("P(Doom)", True, (255, 255, 255))
    title_x = w // 2 - title_text.get_width() // 2
    title_y = int(h * 0.3)
    screen.blit(title_text, (title_x, title_y))
    
    # Subtitle
    subtitle_font = pygame.font.SysFont('Consolas', int(h * 0.025))
    subtitle_text = subtitle_font.render("Bureaucracy Strategy Prototype", True, (180, 180, 180))
    subtitle_x = w // 2 - subtitle_text.get_width() // 2
    subtitle_y = title_y + title_text.get_height() + 10
    screen.blit(subtitle_text, (subtitle_x, subtitle_y))
    
    # Progress bar
    bar_width = int(w * 0.4)
    bar_height = int(h * 0.02)
    bar_x = w // 2 - bar_width // 2
    bar_y = int(h * 0.5)
    
    # Progress bar background
    pygame.draw.rect(screen, (60, 60, 80), (bar_x, bar_y, bar_width, bar_height))
    
    # Progress bar fill
    fill_width = int(bar_width * max(0, min(1, progress)))
    if fill_width > 0:
        pygame.draw.rect(screen, (100, 150, 255), (bar_x, bar_y, fill_width, bar_height))
    
    # Progress bar border
    pygame.draw.rect(screen, (120, 120, 140), (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Status text
    status_surf = font.render(status_text, True, (200, 200, 200))
    status_x = w // 2 - status_surf.get_width() // 2
    status_y = bar_y + bar_height + 20
    screen.blit(status_surf, (status_x, status_y))
    
    # Progress percentage
    if progress > 0:
        percent_text = subtitle_font.render(f"{int(progress * 100)}%", True, (150, 150, 150))
        percent_x = w // 2 - percent_text.get_width() // 2
        percent_y = status_y + status_surf.get_height() + 10
        screen.blit(percent_text, (percent_x, percent_y))


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


def should_show_ui_element(game_state, element_id: str) -> bool:
    """
    Check if a UI element should be visible based on tutorial progress.
    
    Args:
        game_state: The current game state
        element_id: String identifier for the UI element
        
    Returns:
        bool: True if the element should be visible
    """
    # Import onboarding here to avoid circular imports
    from src.features.onboarding import onboarding
    
    # If tutorial is not active, show all elements
    if not onboarding.show_tutorial_overlay:
        return True
    
    # Check if element should be visible based on tutorial progress
    return onboarding.should_show_ui_element(element_id)


def draw_top_bar_info(screen: pygame.Surface, game_state: Any, w: int, h: int, small_font: pygame.font.Font, font: pygame.font.Font) -> None:
    """
    Draw enhanced top bar with game date, version, and debug hotkeys.
    
    Args:
        screen: pygame screen surface
        game_state: current game state
        w, h: screen dimensions
        small_font, font: pygame font objects
    """
    from src.services.version import get_display_version
    from src.services.config_manager import get_current_config
    
    top_y = int(h * 0.01)  # Very top of screen
    
    # 1. GAME DATE (Top Left)
    if hasattr(game_state, 'game_clock') and game_state.game_clock:
        date_text = f"Week of {game_state.game_clock.get_formatted_date()}"
        date_color = (180, 220, 255)  # Light blue
        date_surface = small_font.render(date_text, True, date_color)
        screen.blit(date_surface, (int(w * 0.02), top_y))
    
    # 2. VERSION NUMBER (Top Right)
    version_text = f"v{get_display_version()}"
    version_color = (200, 200, 200)  # Light gray
    version_surface = small_font.render(version_text, True, version_color)
    version_x = w - version_surface.get_width() - int(w * 0.02)
    screen.blit(version_surface, (version_x, top_y))
    
    # 3. DEBUG HOTKEYS (Top Center) - Configurable based on debug mode
    config = get_current_config()
    debug_mode = config.get('advanced', {}).get('debug_mode', True)  # Default to True for beta
    
    if debug_mode:
        # Debug hotkey hints in center
        hotkeys_text = "[H] Help  [C] Clear UI  [[] Screenshot  [M] Menu"
        hotkeys_color = (160, 160, 160)  # Dim gray so not distracting
        hotkeys_surface = small_font.render(hotkeys_text, True, hotkeys_color)
        hotkeys_x = (w - hotkeys_surface.get_width()) // 2
        screen.blit(hotkeys_surface, (hotkeys_x, top_y))


def draw_ui(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    # Import the extracted game UI functions
    from src.ui.game_ui import (
        draw_resource_display, draw_secondary_resources, draw_research_quality_system,
        draw_action_buttons, draw_upgrade_buttons, draw_end_turn_button,
        draw_activity_log, draw_game_context_window
    )
    
    # Fonts, scaled by screen size
    title_font = pygame.font.SysFont('Consolas', int(h*0.045), bold=True)
    big_font = pygame.font.SysFont('Consolas', int(h*0.033))
    font = pygame.font.SysFont('Consolas', int(h*0.025))
    small_font = pygame.font.SysFont('Consolas', int(h*0.018))

    # Title
    title = title_font.render("P(Doom): Bureaucracy Strategy", True, (205, 255, 220))
    screen.blit(title, (int(w*0.04), int(h*0.03)))
    
    # DEV MODE indicator (top-left corner, above title)
    draw_dev_mode_indicator(screen, w, h)
    
    # TOP BAR ENHANCEMENTS: Date, Version, Debug Hotkeys
    draw_top_bar_info(screen, game_state, w, h, small_font, font)

    # Primary resource display (money, staff, reputation, action points, doom, opponent progress)
    draw_resource_display(screen, game_state, w, h, big_font, font, small_font)
    
    # Secondary resources (compute, research, papers, board members)
    draw_secondary_resources(screen, game_state, w, h, big_font, font, small_font)
    
    # Research quality system (technical debt, effectiveness modifiers)
    draw_research_quality_system(screen, game_state, w, h, font, small_font)
    
    # Turn and Date display (top right)
    turn_text = f"Turn: {game_state.turn}"
    date_text = f"Date: {game_state.game_clock.get_formatted_date()}"
    
    screen.blit(small_font.render(turn_text, True, (220, 220, 220)), (int(w*0.91), int(h*0.03)))
    screen.blit(small_font.render(date_text, True, (200, 200, 220)), (int(w*0.91), int(h*0.055)))  # Slightly below turn
    screen.blit(small_font.render(f"Seed: {game_state.seed}", True, (140, 200, 160)), (int(w*0.77), int(h*0.03)))

    # Doom bar
    doom_bar_x, doom_bar_y = int(w*0.62), int(h*0.16)
    doom_bar_width, doom_bar_height = int(w*0.28), int(h*0.025)
    pygame.draw.rect(screen, (70, 50, 50), (doom_bar_x, doom_bar_y, doom_bar_width, doom_bar_height))
    filled = int(doom_bar_width * (game_state.doom / game_state.max_doom))
    pygame.draw.rect(screen, (255, 60, 60), (doom_bar_x, doom_bar_y, filled, doom_bar_height))

    # Opponents information panel (between resources and actions)
    draw_opponents_panel(screen, game_state, w, h, font, small_font)

    # Action buttons with visual feedback and compact UI support
    draw_action_buttons(screen, game_state, w, h, small_font)

    # Upgrade buttons with visual feedback and compact UI support
    draw_upgrade_buttons(screen, game_state, w, h, small_font)

    # Balance change display (after buying accounting software)
    if hasattr(game_state, "accounting_software_bought") and game_state.accounting_software_bought:
        # Show the last balance change if available
        change = getattr(game_state, "last_balance_change", 0)
        sign = "+" if change > 0 else ""
        # Render in green if positive, red if negative
        screen.blit(
            font.render(f"({sign}{change})", True, (200, 255, 200) if change >= 0 else (255, 180, 180)),
            (int(w*0.18), int(h*0.135))
        )

    # Draw UI transitions (on top of everything else)
    draw_ui_transitions(screen, game_state, w, h, big_font)

    # End Turn button with visual feedback
    draw_end_turn_button(screen, game_state, w, h)

    # Activity log with scrollable history and minimize functionality
    draw_activity_log(screen, game_state, w, h, font, small_font)

    # Draw employee blobs (lower middle area)
    draw_employee_blobs(screen, game_state, w, h)
    
    # Draw deferred events zone (lower right)
    draw_deferred_events_zone(screen, game_state, w, h, small_font)
    
    # Draw mute button (bottom right)
    draw_mute_button(screen, game_state, w, h)
    
    # Draw debug console (bottom left) - using manager
    try:
        from src.ui.debug_console_manager import debug_console_manager
        debug_console_manager.draw(screen, game_state, w, h)
    except ImportError:
        pass  # Debug console not available
    
    # Draw version in bottom right corner (unobtrusive)
    draw_version_footer(screen, w, h)
    
    # Context window with action/upgrade details
    context_rect, context_button_rect = draw_game_context_window(screen, game_state, w, h)
    
    # Store context window rects for click handling
    game_state.context_window_rect = context_rect
    game_state.context_window_button_rect = context_button_rect
    
    # Draw popup events (overlay, drawn last to be on top)
    draw_popup_events(screen, game_state, w, h, font, big_font)

def draw_employee_blobs(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    """Draw employee blobs with dynamic positioning that avoids UI overlap"""
    
    # Update blob positions dynamically to avoid UI elements
    # This is called every frame to ensure continuous repositioning
    game_state._update_blob_positions_dynamically(w, h)
    
    # Handle initial positioning for new blobs that haven't been positioned yet
    for i, blob in enumerate(game_state.employee_blobs):
        # Initialize position for new blobs or those that need repositioning
        if blob.get('needs_position_update', False):
            new_x, new_y = game_state._calculate_blob_position(i, w, h)
            blob['target_x'] = new_x
            blob['target_y'] = new_y
            # If blob is already animated in, update current position too
            if blob['animation_progress'] >= 1.0:
                blob['x'] = new_x
                blob['y'] = new_y
            blob['needs_position_update'] = False
    
    # Update blob animations for new employees sliding in from left side
    for blob in game_state.employee_blobs:
        if blob['animation_progress'] < 1.0:
            blob['animation_progress'] = min(1.0, blob['animation_progress'] + 0.05)
            # Animate from starting position to target
            start_x = -50
            blob['x'] = start_x + (blob['target_x'] - start_x) * blob['animation_progress']
    
    # Draw each blob
    for blob in game_state.employee_blobs:
        x, y = int(blob['x']), int(blob['y'])
        
        # Skip if still animating in and off-screen
        if x < 0:
            continue
            
        # Draw halo for productive employees (those with compute)
        if blob['has_compute']:
            # Glowing halo effect
            halo_radius = 35
            for i in range(3):
                alpha = 80 - i * 20
                halo_color = (100, 255, 150, alpha)
                # Create a surface for the halo with alpha
                halo_surface = pygame.Surface((halo_radius * 2, halo_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(halo_surface, halo_color, (halo_radius, halo_radius), halo_radius - i * 3)
                screen.blit(halo_surface, (x - halo_radius, y - halo_radius))
        
        # Draw the main blob (employee or manager)
        blob_radius = 20
        
        # Different colors for managers vs employees
        if blob.get('type') == 'manager':
            blob_color = (100, 255, 100) if blob['has_compute'] else (80, 200, 80)  # Green for managers
        else:
            blob_color = (150, 200, 255) if blob['has_compute'] else (100, 150, 200)  # Blue for employees
        
        # Main blob body
        pygame.draw.circle(screen, blob_color, (x, y), blob_radius)
        pygame.draw.circle(screen, (255, 255, 255), (x, y), blob_radius, 2)
        
        # Simple face (eyes)
        eye_offset = 6
        eye_radius = 3
        pygame.draw.circle(screen, (50, 50, 100), (x - eye_offset, y - 4), eye_radius)
        pygame.draw.circle(screen, (50, 50, 100), (x + eye_offset, y - 4), eye_radius)
        
        # Productivity indicator (small dot)
        if blob['productivity'] > 0:
            pygame.draw.circle(screen, (100, 255, 100), (x, y + 8), 4)

def draw_mute_button(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    """Draw mute/unmute button in bottom right corner"""
    # Button position (bottom right) - made larger per issue #89
    button_size = int(min(w, h) * 0.06)  # Increased from 0.04 to 0.06 for better visibility
    button_x = w - button_size - 20
    button_y = h - button_size - 20
    
    # Button colors
    if hasattr(game_state, 'sound_manager') and game_state.sound_manager and game_state.sound_manager.is_enabled():
        bg_color = (100, 200, 100)  # Green when sound is on
        icon_color = (255, 255, 255)
        symbol = "~"  # Musical note when sound is on
    else:
        bg_color = (200, 100, 100)  # Red when sound is off
        icon_color = (255, 255, 255) 
        symbol = "X"  # Muted symbol when sound is off
    
    # Draw button background
    button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
    pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, width=2, border_radius=8)
    
    # Draw icon
    font_size = int(button_size * 0.6)
    font = pygame.font.SysFont('Arial', font_size)
    icon_surf = font.render(symbol, True, icon_color)
    icon_x = button_x + (button_size - icon_surf.get_width()) // 2
    icon_y = button_y + (button_size - icon_surf.get_height()) // 2
    screen.blit(icon_surf, (icon_x, icon_y))

def draw_mute_button_standalone(screen: pygame.Surface, sound_manager, w: int, h: int) -> None:
    """Draw mute/unmute button in bottom right corner (standalone version for menus)"""
    # Button position (bottom right) - made larger per issue #89
    button_size = int(min(w, h) * 0.06)  # Same size as main game mute button
    button_x = w - button_size - 20
    button_y = h - button_size - 20
    
    # Button colors
    if sound_manager and sound_manager.is_enabled():
        bg_color = (100, 200, 100)  # Green when sound is on
        icon_color = (255, 255, 255)
        symbol = "~"  # Musical note when sound is on
    else:
        bg_color = (200, 100, 100)  # Red when sound is off
        icon_color = (255, 255, 255) 
        symbol = "X"  # Muted symbol when sound is off
    
    # Draw button background
    button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
    pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, width=2, border_radius=8)
    
    # Draw icon
    font_size = int(button_size * 0.6)
    font = pygame.font.SysFont('Arial', font_size)
    icon_surf = font.render(symbol, True, icon_color)
    icon_x = button_x + (button_size - icon_surf.get_width()) // 2
    icon_y = button_y + (button_size - icon_surf.get_height()) // 2
    screen.blit(icon_surf, (icon_x, icon_y))

def draw_tooltip(screen: pygame.Surface, text: str, mouse_pos: Tuple[int, int], w: int, h: int) -> None:
    font = pygame.font.SysFont('Consolas', int(h*0.018))
    surf = font.render(text, True, (230,255,200))
    tw, th = surf.get_size()
    px, py = mouse_pos
    # Prevent tooltip going off screen
    if px+tw > w: px = w-tw-10
    if py+th > h: py = h-th-10
    pygame.draw.rect(screen, (40, 40, 80), (px, py, tw+12, th+12), border_radius=6)
    screen.blit(surf, (px+6, py+6))

def draw_context_window(screen: pygame.Surface, context_info: Dict[str, Any], w: int, h: int, minimized: bool = False, config: Optional[Dict[str, Any]] = None) -> None:
    """
    Draw a context window at the bottom of the screen showing detailed information.
    
    Args:
        screen: pygame screen surface
        context_info: dict with 'title', 'description', 'details' keys
        w, h: screen dimensions
        minimized: whether the context window is minimized
        config: optional config dict for customization
    """
    if not context_info:
        return None, None  # No context to show
    
    # Get configuration settings - reduced height to save screen space
    if config and 'ui' in config and 'context_window' in config['ui']:
        ctx_config = config['ui']['context_window']
        expanded_height_percent = ctx_config.get('height_percent', 0.07)  # Reduced from 0.10 to 0.07
        minimized_height_percent = ctx_config.get('minimized_height_percent', 0.04)  # Reduced from 0.05 to 0.04
    else:
        # Default values if no config - bottom 6-7% of screen (much more compact)
        expanded_height_percent = 0.07
        minimized_height_percent = 0.04
    
    # Context window dimensions - positioned at bottom with configurable height
    window_height = int(h * minimized_height_percent) if minimized else int(h * expanded_height_percent)
    window_width = int(w * 0.98)
    window_x = int(w * 0.01)
    window_y = h - window_height - 5  # 5px margin from bottom
    
    # Background with rounded corners - 80's techno green theme
    context_rect = pygame.Rect(window_x, window_y, window_width, window_height)
    # Light readable techno green background
    pygame.draw.rect(screen, (40, 80, 40), context_rect, border_radius=8)  # Dark green base
    pygame.draw.rect(screen, (100, 200, 100), context_rect, width=2, border_radius=8)  # Bright green border
    
    # Header with title and minimize button - retro DOS style
    header_height = 22
    header_rect = pygame.Rect(window_x, window_y, window_width, header_height)
    pygame.draw.rect(screen, (60, 120, 60), header_rect, border_radius=8)  # Darker green header
    
    # Title - ALL CAPS DOS style
    title_font = pygame.font.SysFont('Courier', max(12, int(h*0.018)), bold=True)  # Courier for DOS feel
    title_color = (200, 255, 200)  # Bright green text
    title_text = title_font.render(str(context_info.get('title', 'CONTEXT')).upper(), True, title_color)
    screen.blit(title_text, (window_x + 8, window_y + 3))
    
    # Minimize/Maximize button - green theme
    button_size = 16
    button_x = window_x + window_width - button_size - 4
    button_y = window_y + 3
    button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
    
    # Button background
    pygame.draw.rect(screen, (80, 150, 80), button_rect, border_radius=3)  # Green button
    pygame.draw.rect(screen, (150, 255, 150), button_rect, width=1, border_radius=3)  # Bright green border
    
    # Button symbol
    symbol_font = pygame.font.SysFont('Courier', 10, bold=True)  # DOS font
    symbol = '-' if not minimized else '+'
    symbol_text = symbol_font.render(symbol, True, (200, 255, 200))  # Bright green text
    symbol_rect = symbol_text.get_rect(center=button_rect.center)
    screen.blit(symbol_text, symbol_rect)
    
    if not minimized:
        # Content area
        content_y = window_y + header_height + 3
        window_height - header_height - 6
        content_x = window_x + 8
        
        # Description - DOS style ALL CAPS
        desc_font = pygame.font.SysFont('Courier', max(10, int(h*0.016)))  # Courier for DOS, slightly larger
        description = str(context_info.get('description', ''))
        
        if description:
            # Convert to ALL CAPS for DOS terminal feel
            description = description.upper()
            
            # Simple word wrap for description
            words = description.split(' ')
            current_line = ''
            lines = []
            max_chars_per_line = max(25, (window_width - 16) // 8)  # Adjusted for Courier font
            
            for word in words:
                test_line = current_line + (' ' if current_line else '') + word
                if len(test_line) <= max_chars_per_line:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            # Render description lines
            line_height = desc_font.get_height() + 1
            current_y = content_y
            
            for line in lines[:2]:  # Show up to 2 lines of description
                if current_y + line_height > window_y + window_height - 3:
                    break
                line_text = desc_font.render(line, True, (180, 255, 180))  # Bright green text
                screen.blit(line_text, (content_x, current_y))
                current_y += line_height
            
            # Move to details section
            current_y += 3  # Small gap
        else:
            current_y = content_y
        
        # Details section - DOS style
        details = context_info.get('details', [])
        if details and current_y < window_y + window_height - 15:
            detail_font = pygame.font.SysFont('Courier', max(9, int(h*0.014)))  # Courier for DOS
            
            # Horizontal layout for details to save space
            detail_x = content_x
            detail_y = current_y
            
            for i, detail in enumerate(details[:4]):  # Show up to 4 details
                # Convert details to ALL CAPS
                detail_str = str(detail).upper()
                detail_text = detail_font.render(detail_str, True, (150, 220, 150))  # Medium green text
                
                # Check if detail fits on current line
                if detail_x + detail_text.get_width() + 20 > window_x + window_width - 10:
                    # Move to next line
                    detail_y += detail_font.get_height() + 1
                    detail_x = content_x
                    
                    # Check if we have room for another line
                    if detail_y + detail_font.get_height() > window_y + window_height - 3:
                        break
                
                screen.blit(detail_text, (detail_x, detail_y))
                detail_x += detail_text.get_width() + 20  # Space between details
    
    return context_rect, button_rect

def draw_scoreboard(screen: pygame.Surface, game_state, w: int, h: int, seed: str) -> None:
    # Scoreboard after game over
    font = pygame.font.SysFont('Consolas', int(h*0.035))
    title = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    big = pygame.font.SysFont('Consolas', int(h*0.05))
    small = pygame.font.SysFont('Consolas', int(h*0.02))

    # Box
    pygame.draw.rect(screen, (40,40,70), (w//6, h//7, w*2//3, h*3//5), border_radius=24)
    pygame.draw.rect(screen, (130, 190, 255), (w//6, h//7, w*2//3, h*3//5), width=5, border_radius=24)

    # Headline
    screen.blit(title.render("GAME OVER", True, (255,0,0)), (w//2 - int(w*0.09), h//7 + int(h*0.05)))
    msg = game_state.messages[-1] if game_state.messages else ""
    screen.blit(big.render(msg, True, (255,220,220)), (w//6 + int(w*0.04), h//7 + int(h*0.16)))

    # Score details
    lines = [
        f"Survived until Turn: {game_state.turn}",
        f"Final Staff: {game_state.staff}",
        f"Final Money: ${game_state.money}",
        f"Final Reputation: {game_state.reputation}",
        f"Final p(Doom): {game_state.doom}",
        f"Seed: {seed}",
        f"High Score (turns): {game_state.highscore}"
    ]
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, (240,255,255)), (w//6 + int(w*0.04), h//7 + int(h*0.27) + i*int(h*0.05)))
    screen.blit(small.render("Click anywhere to restart.", True, (255,255,180)), (w//2 - int(w*0.1), h//7 + int(h*0.5)))

def draw_seed_prompt(screen: pygame.Surface, current_input: str, weekly_suggestion: str) -> None:
    # Prompt the user for a seed
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
    # Example: rendering an upgrade description with wrapping instead of direct render
    # We'll assume this pattern is repeated for upgrades and actions wherever description text is rendered

  
    # Additional: wrap message log if desired (could be done similarly).


# Bug report functions moved to src/ui/bug_report.py
# Reduced lines: ~220 lines (bug report form and success screens)


def draw_opponents_panel(screen: pygame.Surface, game_state, w: int, h: int, font: pygame.font.Font, small_font: pygame.font.Font) -> None:
    """
    Draw the opponents information panel showing discovered competitors.
    
    Args:
        screen: pygame surface to draw on
        game_state: current game state containing opponents data
        w, h: screen width and height
        font: font for opponent names
        small_font: font for opponent stats
    """
    # Panel position and dimensions
    panel_x = int(w * 0.04)
    panel_y = int(h * 0.19)  # Below resources, above actions
    panel_width = int(w * 0.92)
    panel_height = int(h * 0.08)
    
    # Draw panel background
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, (30, 30, 50), panel_rect, border_radius=8)
    pygame.draw.rect(screen, (80, 80, 120), panel_rect, width=2, border_radius=8)
    
    # Panel title
    title_text = font.render("Competitors:", True, (255, 200, 100))
    screen.blit(title_text, (panel_x + int(w * 0.01), panel_y + int(h * 0.01)))
    
    # Get discovered opponents
    discovered = [opp for opp in game_state.opponents if opp.discovered]
    
    if not discovered:
        # No opponents discovered yet
        no_info = small_font.render("Use Espionage or Scout Opponent to discover competitors", True, (180, 180, 180))
        screen.blit(no_info, (panel_x + int(w * 0.15), panel_y + int(h * 0.035)))
        return
    
    # Calculate spacing for discovered opponents
    opponent_width = panel_width // len(discovered)
    
    for i, opponent in enumerate(discovered):
        opp_x = panel_x + i * opponent_width + int(w * 0.01)
        opp_y = panel_y + int(h * 0.025)
        
        # Opponent name
        name_text = font.render(opponent.name, True, (255, 255, 200))
        screen.blit(name_text, (opp_x, opp_y))
        
        # Known stats (show with different colors based on discovery status)
        stats_y = opp_y + int(h * 0.025)
        
        # Progress (most important stat)
        if opponent.discovered_stats['progress']:
            progress_val = opponent.known_stats['progress']
            progress_color = (255, 100, 100) if progress_val > 70 else (255, 200, 100) if progress_val > 40 else (100, 255, 100)
            progress_text = small_font.render(f"Progress: {progress_val}/100", True, progress_color)
        else:
            progress_text = small_font.render("Progress: ???", True, (120, 120, 120))
        screen.blit(progress_text, (opp_x, stats_y))
        
        # Other stats (compact display)
        stats_y += int(h * 0.02)
        
        # Budget
        if opponent.discovered_stats['budget']:
            budget_text = small_font.render(f"Budget: ${opponent.known_stats['budget']}k", True, (100, 255, 100))
        else:
            budget_text = small_font.render("Budget: ???", True, (120, 120, 120))
        screen.blit(budget_text, (opp_x, stats_y))
        
        # Researchers and Compute (on same line if space allows)
        if opponent_width > 150:  # Only show if enough space
            researchers_y = stats_y + int(h * 0.015)
            
            if opponent.discovered_stats['capabilities_researchers']:
                researchers_text = small_font.render(f"Researchers: {opponent.known_stats['capabilities_researchers']}", True, (255, 150, 150))
            else:
                researchers_text = small_font.render("Researchers: ???", True, (120, 120, 120))
            screen.blit(researchers_text, (opp_x, researchers_y))
            
            compute_y = researchers_y + int(h * 0.015)
            if opponent.discovered_stats['compute']:
                compute_text = small_font.render(f"Compute: {opponent.known_stats['compute']}", True, (150, 200, 255))
            else:
                compute_text = small_font.render("Compute: ???", True, (120, 120, 120))
            screen.blit(compute_text, (opp_x, compute_y))


def draw_deferred_events_zone(screen: pygame.Surface, game_state, w: int, h: int, small_font: pygame.font.Font) -> None:
    """
    Draw the deferred events zone in the lower right corner.
    
    Shows deferred events with turn counters in a greyed-out area.
    This is a UI stub for future enhancement.
    """
    # Only draw if deferred events exist
    if not hasattr(game_state, 'deferred_events') or not game_state.deferred_events.deferred_events:
        return
    
    # Zone position and dimensions
    zone_width = int(w * 0.25)
    zone_height = int(h * 0.15)
    zone_x = w - zone_width - int(w * 0.02)
    zone_y = h - zone_height - int(h * 0.12)  # Above mute button
    
    # Draw zone background
    zone_rect = pygame.Rect(zone_x, zone_y, zone_width, zone_height)
    pygame.draw.rect(screen, (60, 60, 60), zone_rect, border_radius=8)
    pygame.draw.rect(screen, (120, 120, 120), zone_rect, width=2, border_radius=8)
    
    # Zone title
    title_text = small_font.render("Deferred Events", True, (200, 200, 200))
    screen.blit(title_text, (zone_x + 5, zone_y + 5))
    
    # List deferred events
    deferred_events = game_state.deferred_events.get_deferred_events()
    for i, event in enumerate(deferred_events[:4]):  # Show max 4 events
        y_pos = zone_y + 25 + i * 20
        if y_pos + 15 > zone_y + zone_height:
            break
        
        # Event text with turn counter
        turns_left = event.max_deferred_turns - event.turns_deferred
        event_text = f"- {event.name} ({turns_left}T)"
        text_surface = small_font.render(event_text, True, (180, 180, 180))
        
        # Truncate if too long
        if text_surface.get_width() > zone_width - 10:
            truncated = f"- {event.name[:15]}... ({turns_left}T)"
            text_surface = small_font.render(truncated, True, (180, 180, 180))
        
        screen.blit(text_surface, (zone_x + 5, y_pos))
    
    # Show count if more events exist
    if len(deferred_events) > 4:
        more_text = small_font.render(f"...and {len(deferred_events) - 4} more", True, (150, 150, 150))
        screen.blit(more_text, (zone_x + 5, zone_y + zone_height - 20))


def draw_popup_events(screen: pygame.Surface, game_state, w: int, h: int, font: pygame.font.Font, big_font: pygame.font.Font) -> List[Tuple[pygame.Rect, str, Any]]:
    """
    Draw popup events that dominate the screen and require immediate attention.
    
    Returns a list of (button_rect, action, event) tuples for click detection.
    """
    # Only draw if popup events exist
    if not hasattr(game_state, 'pending_popup_events') or not game_state.pending_popup_events:
        return []
    
    # Get the first popup event
    event = game_state.pending_popup_events[0]
    
    # Semi-transparent overlay
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Popup dimensions
    popup_width = int(w * 0.6)
    popup_height = int(h * 0.4)
    popup_x = (w - popup_width) // 2
    popup_y = (h - popup_height) // 2
    
    # Draw popup background
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    pygame.draw.rect(screen, (40, 40, 60), popup_rect, border_radius=15)
    pygame.draw.rect(screen, (255, 200, 100), popup_rect, width=4, border_radius=15)
    
    # Event title
    title_text = big_font.render(event.name, True, (255, 255, 100))
    title_x = popup_x + (popup_width - title_text.get_width()) // 2
    screen.blit(title_text, (title_x, popup_y + 20))
    
    # Event description (with word wrapping)
    desc_lines = wrap_text(event.desc, font, popup_width - 40)
    for i, line in enumerate(desc_lines):
        line_surface = font.render(line, True, (255, 255, 255))
        screen.blit(line_surface, (popup_x + 20, popup_y + 70 + i * 25))
    
    # Action buttons
    button_y = popup_y + popup_height - 80
    button_width = 120
    button_height = 40
    button_spacing = 20
    
    # Calculate button positions
    available_actions = event.available_actions
    total_width = len(available_actions) * button_width + (len(available_actions) - 1) * button_spacing
    start_x = popup_x + (popup_width - total_width) // 2
    
    # Store clickable button rectangles
    button_rects = []
    
    for i, action in enumerate(available_actions):
        button_x = start_x + i * (button_width + button_spacing)
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Store button info for click detection
        button_rects.append((button_rect, action, event))
        
        # Button colors based on action type
        if action.value == "accept":
            color = (100, 200, 100)
        elif action.value == "defer":
            color = (200, 200, 100)
        elif action.value == "dismiss":
            color = (200, 100, 100)
        elif action.value == "deny":
            color = (200, 100, 100)  # Same as dismiss - red for negative action
        else:
            color = (150, 150, 200)
        
        pygame.draw.rect(screen, color, button_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, width=2, border_radius=8)
        
        # Button text
        button_text = font.render(action.value.title(), True, (0, 0, 0))
        text_x = button_x + (button_width - button_text.get_width()) // 2
        text_y = button_y + (button_height - button_text.get_height()) // 2
        screen.blit(button_text, (text_x, text_y))
    
    # Instructions
    instruction_text = font.render("Click a button to proceed!", True, (255, 200, 200))
    inst_x = popup_x + (popup_width - instruction_text.get_width()) // 2
    screen.blit(instruction_text, (inst_x, popup_y + popup_height - 20))
    
    return button_rects


def draw_ui_transitions(screen: pygame.Surface, game_state, w: int, h: int, big_font: pygame.font.Font) -> None:
    """
    Draw smooth UI transition animations for upgrades and other elements.
    
    This function renders visual feedback for UI state changes:
    - Upgrade transitions from button to icon with curved arc trails
    - Glow effects on destination locations
    - Semi-transparent trail effects that fade over time
    
    Args:
        screen: pygame surface to draw on
        game_state: current game state containing active transitions
        w, h: screen width and height
        big_font: font for rendering transition elements
    """
    for transition in game_state.ui_transitions:
        if transition['type'] == 'upgrade_transition':
            draw_upgrade_transition(screen, transition, game_state, w, h, big_font)


def draw_upgrade_transition(screen: pygame.Surface, transition, game_state, w: int, h: int, big_font: pygame.font.Font) -> None:
    """
    Draw a single upgrade transition animation with enhanced visual effects.
    
    Features:
    - Enhanced curved arc trail with particle effects
    - Multi-layered glow effects with smooth pulsing
    - Dynamic trail with size and color variations
    - Particle system for more organic visual feedback
    - Smooth size and opacity interpolation
    
    Args:
        screen: pygame surface to draw on
        transition: transition data containing animation state
        game_state: current game state for upgrade info
        w, h: screen width and height  
        big_font: font for rendering upgrade text
    """
    upgrade_idx = transition['upgrade_idx']
    upgrade = game_state.upgrades[upgrade_idx]
    
    # Draw enhanced particle trail first (background layer)
    for particle in transition.get('particle_trail', []):
        if particle['alpha'] > 0:
            # Dynamic particle colors with variation
            base_color = (100, 255, 150)
            color_shift = particle.get('color_shift', 0)
            particle_color = (
                max(0, min(255, base_color[0] + color_shift)),
                max(0, min(255, base_color[1] + color_shift//2)),
                max(0, min(255, base_color[2] + color_shift)),
                particle['alpha']
            )
            
            # Create particle surface with gradient effect
            particle_size = particle['size']
            particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
            
            # Multi-layer particle for depth
            for layer in range(2):
                layer_alpha = particle['alpha'] // (1 + layer)
                layer_size = max(1, particle_size - layer)
                layer_color = (*particle_color[:3], layer_alpha)
                
                pygame.draw.circle(particle_surface, layer_color, 
                                 (particle_size, particle_size), layer_size)
            
            screen.blit(particle_surface, (int(particle['pos'][0]) - particle_size, 
                                         int(particle['pos'][1]) - particle_size))
    
    # Draw enhanced trail points (main trail effect)
    for i, point in enumerate(transition['trail_points']):
        if point['alpha'] > 0:
            # Enhanced trail with size and color variations
            trail_size = max(2, int(point['size']))
            
            # Dynamic trail colors with organic variation
            base_green = 150 + point.get('color_variation', 0)
            trail_color = (100, max(100, min(255, base_green)), 150, point['alpha'])
            
            # Create trail surface with soft edges
            trail_surface = pygame.Surface((trail_size * 3, trail_size * 3), pygame.SRCALPHA)
            
            # Multi-layer trail for smooth gradients
            for layer in range(3):
                layer_alpha = point['alpha'] // (1 + layer * 2)
                layer_size = max(1, trail_size - layer)
                layer_color = (*trail_color[:3], layer_alpha)
                
                if layer_alpha > 0:
                    pygame.draw.circle(trail_surface, layer_color,
                                     (trail_size * 3 // 2, trail_size * 3 // 2), layer_size)
            
            screen.blit(trail_surface, (point['pos'][0] - trail_size * 3 // 2, 
                                      point['pos'][1] - trail_size * 3 // 2))
    
    # Draw moving upgrade preview during transition with enhanced effects
    if not transition['completed']:
        current_pos = game_state._interpolate_position(
            transition['start_rect'], 
            transition['end_rect'], 
            transition['progress'],
            transition.get('arc_height', 80)
        )
        
        # Enhanced size interpolation with slight overshoot for bounce effect
        start_size = min(transition['start_rect'][2], transition['start_rect'][3])
        end_size = min(transition['end_rect'][2], transition['end_rect'][3])
        
        # Add slight bounce/overshoot near the end
        progress = transition['progress']
        if progress > 0.8:
            bounce_factor = 1.0 + 0.1 * (1.0 - progress) * 5  # Slight overshoot
            current_size = (start_size + (end_size - start_size) * progress) * bounce_factor
        else:
            current_size = start_size + (end_size - start_size) * progress
        
        current_size = int(max(end_size * 0.5, current_size))  # Minimum size
        
        # Draw enhanced moving upgrade with glow
        moving_rect = (
            current_pos[0] - current_size//2,
            current_pos[1] - current_size//2,
            current_size,
            current_size
        )
        
        # Add glow around moving element
        glow_size = current_size + 8
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_color = (100, 255, 150, 60)
        pygame.draw.circle(glow_surface, glow_color, (glow_size//2, glow_size//2), glow_size//2)
        screen.blit(glow_surface, (current_pos[0] - glow_size//2, current_pos[1] - glow_size//2))
        
        # Enhanced moving element background
        moving_surface = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
        
        # Multi-layer background for depth
        bg_color = (90, 170, 90, 200)
        border_color = (140, 210, 140, 230)
        
        pygame.draw.rect(moving_surface, bg_color, (0, 0, current_size, current_size), border_radius=8)
        pygame.draw.rect(moving_surface, border_color, (0, 0, current_size, current_size), width=2, border_radius=8)
        
        # Add inner highlight for 3D effect
        highlight_color = (180, 240, 180, 100)
        pygame.draw.rect(moving_surface, highlight_color, (2, 2, current_size-4, current_size//3), border_radius=4)
        
        # Scaled upgrade letter
        font_size = max(12, int(current_size * 0.4))
        scaled_font = pygame.font.SysFont('Consolas', font_size, bold=True)
        letter_surf = scaled_font.render(upgrade["name"][0], True, (255, 255, 255))
        letter_x = (current_size - letter_surf.get_width()) // 2
        letter_y = (current_size - letter_surf.get_height()) // 2
        moving_surface.blit(letter_surf, (letter_x, letter_y))
        
        screen.blit(moving_surface, (moving_rect[0], moving_rect[1]))
    
    # Draw enhanced destination glow effect
    glow_intensity = transition.get('glow_intensity', 0)
    if glow_intensity > 0:
        end_rect = transition['end_rect']
        
        # Enhanced pulsing with multiple frequencies
        import math
        time_factor = (90 - transition.get('glow_timer', 0)) / 90.0
        pulse1 = 1.0 + 0.3 * math.sin(time_factor * 8 * math.pi) * (glow_intensity / 255.0)
        pulse2 = 1.0 + 0.15 * math.sin(time_factor * 12 * math.pi) * (glow_intensity / 255.0)
        
        base_glow_size = max(end_rect[2], end_rect[3])
        
        # Multiple glow layers with different pulsing patterns
        glow_layers = [
            {'size': base_glow_size * pulse1 * 1.5, 'alpha': glow_intensity // 4, 'color': (150, 255, 150)},
            {'size': base_glow_size * pulse2 * 1.2, 'alpha': glow_intensity // 3, 'color': (120, 220, 120)},
            {'size': base_glow_size * 1.0, 'alpha': glow_intensity // 2, 'color': (100, 200, 100)},
        ]
        
        center_x = end_rect[0] + end_rect[2] // 2
        center_y = end_rect[1] + end_rect[3] // 2
        
        for layer in glow_layers:
            if layer['alpha'] > 0:
                layer_size = int(layer['size'])
                glow_surface = pygame.Surface((layer_size * 2, layer_size * 2), pygame.SRCALPHA)
                
                # Gradient glow effect
                for ring in range(layer_size, 0, -2):
                    ring_alpha = max(0, int(layer['alpha'] * (layer_size - ring) / layer_size))
                    ring_color = (*layer['color'], ring_alpha)
                    if ring_alpha > 0:
                        pygame.draw.circle(glow_surface, ring_color, (layer_size, layer_size), ring)
                
                glow_x = center_x - layer_size
                glow_y = center_y - layer_size
                screen.blit(glow_surface, (glow_x, glow_y))



def draw_end_game_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, game_state, seed: str) -> None:
    """
    Draw the end-of-game menu with game summary and options.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected menu item (for keyboard navigation)
        game_state: GameState object for displaying final stats
        seed: Game seed used for this session
    
    Features:
    - Displays final game statistics
    - Menu options: Relaunch, Main Menu, Settings, Submit Feedback, Submit Bug
    - Keyboard navigation support
    - Consistent styling with main menu
    """
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.05), bold=True)
    subtitle_font = pygame.font.SysFont('Consolas', int(h*0.035))
    stats_font = pygame.font.SysFont('Consolas', int(h*0.025))
    menu_font = pygame.font.SysFont('Consolas', int(h*0.03), bold=True)
    small_font = pygame.font.SysFont('Consolas', int(h*0.02))
    
    # Colors
    title_color = (255, 100, 100)  # Red for "GAME OVER"
    subtitle_color = (255, 220, 220)
    stats_color = (240, 255, 255)
    menu_active_color = (100, 200, 255)
    menu_inactive_color = (180, 180, 180)
    button_bg_active = (70, 130, 180)
    button_bg_inactive = (60, 60, 100)
    
    # Title
    if game_state.end_game_scenario:
        title_text = title_font.render(game_state.end_game_scenario.title, True, title_color)
    else:
        title_text = title_font.render("GAME OVER", True, title_color)
    title_rect = title_text.get_rect(center=(w//2, int(h*0.08)))
    screen.blit(title_text, title_rect)
    
    # Game end scenario description
    if game_state.end_game_scenario:
        # Wrap the description text
        description_lines = wrap_text(game_state.end_game_scenario.description, subtitle_font, w*2//3)
        start_y = int(h*0.13)
        for i, line in enumerate(description_lines[:4]):  # Limit to 4 lines to fit layout
            desc_text = subtitle_font.render(line, True, subtitle_color)
            desc_rect = desc_text.get_rect(center=(w//2, start_y + i * int(h*0.025)))
            screen.blit(desc_text, desc_rect)
    else:
        # Fallback to last message
        end_message = game_state.messages[-1] if game_state.messages else "Game ended"
        subtitle_text = subtitle_font.render(end_message, True, subtitle_color)
        subtitle_rect = subtitle_text.get_rect(center=(w//2, int(h*0.15)))
        screen.blit(subtitle_text, subtitle_rect)
    
    # ENHANCED: Get leaderboard data for celebration
    try:
        from src.scores.enhanced_leaderboard import EnhancedLeaderboardManager
        leaderboard_manager = EnhancedLeaderboardManager()
        leaderboard = leaderboard_manager.get_leaderboard_for_seed(game_state.seed)
        
        # Check if this is a new record
        is_new_record = False
        current_rank = None
        if leaderboard.entries:
            for i, entry in enumerate(leaderboard.entries):
                if entry.player_name == game_state.lab_name and entry.score == game_state.turn:
                    current_rank = i + 1
                    is_new_record = (i == 0)  # New #1 position
                    break
        
        # Celebration title if new record!
        if is_new_record and current_rank == 1:
            celebration_font = pygame.font.SysFont('Consolas', int(h*0.04), bold=True)
            celebration_text = celebration_font.render("NEW HIGH SCORE!", True, (255, 255, 100))
            celebration_rect = celebration_text.get_rect(center=(w//2, int(h*0.18)))
            # Add glow effect
            glow_text = celebration_font.render("NEW HIGH SCORE!", True, (255, 200, 0))
            screen.blit(glow_text, (celebration_rect.x + 2, celebration_rect.y + 2))
            screen.blit(celebration_text, celebration_rect)
    except:
        current_rank = None
        is_new_record = False
    
    # Game statistics in a box - adjust position to make room for scenario details
    stats_box_y = int(h*0.27) if game_state.end_game_scenario else int(h*0.24)
    stats_box = pygame.Rect(w//6, stats_box_y, w*2//3, int(h*0.24))
    
    # Enhanced box styling for celebration
    box_color = (60, 80, 40) if is_new_record else (40, 40, 70)
    border_color = (150, 255, 100) if is_new_record else (130, 190, 255)
    pygame.draw.rect(screen, box_color, stats_box, border_radius=12)
    pygame.draw.rect(screen, border_color, stats_box, width=3, border_radius=12)
    
    # Enhanced Statistics content
    stats_lines = [
        f"Lab: {game_state.lab_name}",
        f"Survived {game_state.turn} turns",
        f"Final Staff: {game_state.staff} researchers",
        f"Final Money: ${game_state.money:,}",
        f"Final Reputation: {game_state.reputation}",
        f"Final p(Doom): {game_state.doom}%"
    ]
    
    # Add rank information if available
    if current_rank:
        rank_suffix = {1: "st", 2: "nd", 3: "rd"}.get(current_rank, "th")
        rank_line = f"Leaderboard Rank: #{current_rank}{rank_suffix} for seed '{game_state.seed}'"
        stats_lines.append(rank_line)
    else:
        stats_lines.append(f"Seed: '{game_state.seed}'")
    
    # Add high score comparison
    if hasattr(game_state, 'highscore') and game_state.highscore > 0:
        if game_state.turn > game_state.highscore:
            stats_lines.append(f"Previous Best: {game_state.highscore} turns (BEATEN!)")
        else:
            stats_lines.append(f"Personal Best: {game_state.highscore} turns")
    
    stats_start_y = stats_box.y + 15
    line_height = int(h*0.025)
    
    for i, line in enumerate(stats_lines):
        stats_text = stats_font.render(line, True, stats_color)
        screen.blit(stats_text, (stats_box.x + 20, stats_start_y + i * line_height))
    
    # Cause Analysis section (if scenario available)
    if game_state.end_game_scenario and game_state.end_game_scenario.cause_analysis:
        analysis_y = stats_box.y + stats_box.height + 15
        analysis_box = pygame.Rect(w//6, analysis_y, w*2//3, int(h*0.12))
        pygame.draw.rect(screen, (50, 30, 30), analysis_box, border_radius=8)
        pygame.draw.rect(screen, (200, 100, 100), analysis_box, width=2, border_radius=8)
        
        # Analysis title
        analysis_title = small_font.render("What Went Wrong:", True, (255, 200, 200))
        screen.blit(analysis_title, (analysis_box.x + 15, analysis_box.y + 8))
        
        # Analysis text (wrapped)
        analysis_lines = wrap_text(game_state.end_game_scenario.cause_analysis, small_font, analysis_box.width - 30)
        for i, line in enumerate(analysis_lines[:3]):  # Limit to 3 lines
            analysis_text = small_font.render(line, True, (255, 220, 220))
            screen.blit(analysis_text, (analysis_box.x + 15, analysis_box.y + 25 + i * 16))
    
    # Legacy Note section (if scenario available)
    if game_state.end_game_scenario and game_state.end_game_scenario.legacy_note:
        legacy_y_offset = int(h*0.12) + 20 if game_state.end_game_scenario.cause_analysis else 15
        legacy_y = stats_box.y + stats_box.height + legacy_y_offset
        legacy_box = pygame.Rect(w//6, legacy_y, w*2//3, int(h*0.08))
        pygame.draw.rect(screen, (30, 50, 30), legacy_box, border_radius=8)
        pygame.draw.rect(screen, (100, 200, 100), legacy_box, width=2, border_radius=8)
        
        # Legacy title
        legacy_title = small_font.render("Your Legacy:", True, (200, 255, 200))
        screen.blit(legacy_title, (legacy_box.x + 15, legacy_box.y + 8))
        
        # Legacy text (wrapped)
        legacy_lines = wrap_text(game_state.end_game_scenario.legacy_note, small_font, legacy_box.width - 30)
        for i, line in enumerate(legacy_lines[:2]):  # Limit to 2 lines
            legacy_text = small_font.render(line, True, (220, 255, 220))
            screen.blit(legacy_text, (legacy_box.x + 15, legacy_box.y + 25 + i * 16))
    
    # SPECTACULAR: Mini Leaderboard Preview!
    try:
        if current_rank and leaderboard.entries:
            leaderboard_y = int(h * 0.52)
            leaderboard_box = pygame.Rect(w//4, leaderboard_y, w//2, int(h * 0.15))
            
            # Celebration styling for leaderboard
            board_bg = (30, 60, 30) if is_new_record else (30, 30, 60)
            board_border = (100, 255, 100) if is_new_record else (100, 150, 255)
            pygame.draw.rect(screen, board_bg, leaderboard_box, border_radius=10)
            pygame.draw.rect(screen, board_border, leaderboard_box, width=2, border_radius=10)
            
            # Leaderboard title
            board_title_font = pygame.font.SysFont('Consolas', int(h*0.025), bold=True)
            board_title_color = (150, 255, 150) if is_new_record else (150, 200, 255)
            title_text = f"Leaderboard for '{game_state.seed}'"
            board_title = board_title_font.render(title_text, True, board_title_color)
            title_rect = board_title.get_rect(center=(leaderboard_box.centerx, leaderboard_box.y + 15))
            screen.blit(board_title, title_rect)
            
            # Show top 3 entries with current player highlighted
            entry_font = pygame.font.SysFont('Consolas', int(h*0.02))
            entry_y = leaderboard_box.y + 35
            shown_entries = 0
            
            for i, entry in enumerate(leaderboard.entries[:5]):  # Show top 5
                if shown_entries >= 3:
                    break
                    
                rank_num = i + 1
                is_current_player = (entry.player_name == game_state.lab_name and entry.score == game_state.turn)
                
                # Highlight current player's entry
                if is_current_player:
                    highlight_color = (255, 255, 100) if is_new_record else (100, 255, 255)
                    entry_text = f"#{rank_num}. {entry.player_name}: {entry.score} turns ← YOU!"
                    text_color = (0, 0, 0) if is_new_record else (255, 255, 255)
                    # Draw highlight background
                    text_surface = entry_font.render(entry_text, True, text_color)
                    highlight_rect = pygame.Rect(leaderboard_box.x + 10, entry_y - 2, text_surface.get_width() + 10, text_surface.get_height() + 4)
                    pygame.draw.rect(screen, highlight_color, highlight_rect, border_radius=4)
                else:
                    entry_text = f"#{rank_num}. {entry.player_name}: {entry.score} turns"
                    text_color = (200, 255, 200) if is_new_record else (200, 200, 255)
                
                entry_surface = entry_font.render(entry_text, True, text_color)
                screen.blit(entry_surface, (leaderboard_box.x + 15, entry_y))
                entry_y += 22
                shown_entries += 1
                
            # Show total entries count
            total_font = pygame.font.SysFont('Consolas', int(h*0.018))
            total_text = f"({len(leaderboard.entries)} total entries for this seed)"
            total_color = (150, 200, 150) if is_new_record else (150, 150, 200)
            total_surface = total_font.render(total_text, True, total_color)
            total_rect = total_surface.get_rect(center=(leaderboard_box.centerx, leaderboard_box.bottom - 15))
            screen.blit(total_surface, total_rect)
            
            # Encouraging hint for leaderboard viewing
            if current_rank:
                hint_font = pygame.font.SysFont('Consolas', int(h*0.016))
                if is_new_record:
                    hint_text = "Press ENTER to view full leaderboard and celebrate your achievement!"
                    hint_color = (255, 255, 150)
                else:
                    hint_text = "Press ENTER to view full leaderboard and see all competitors"
                    hint_color = (200, 200, 255)
                hint_surface = hint_font.render(hint_text, True, hint_color)
                hint_rect = hint_surface.get_rect(center=(w//2, int(h * 0.68)))
                screen.blit(hint_surface, hint_rect)
    except:
        pass  # Graceful fallback if leaderboard fails

    # Menu options with "View Leaderboard" as TOP priority for natural flow
    menu_items = ["View Full Leaderboard", "Play Again", "Main Menu", "Settings", "Submit Feedback"]
    
    button_width = int(w * 0.35) 
    button_height = int(h * 0.055)  # Slightly smaller to fit
    start_y = int(h * 0.69)  # Moved down for leaderboard space
    spacing = int(h * 0.07)   # Tighter spacing
    center_x = w // 2
    
    for i, item in enumerate(menu_items):
        # Button rectangle
        button_x = center_x - button_width // 2
        button_y = start_y + i * spacing
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Button styling based on selection
        if i == selected_item:
            pygame.draw.rect(screen, button_bg_active, button_rect, border_radius=8)
            pygame.draw.rect(screen, menu_active_color, button_rect, width=3, border_radius=8)
            text_color = (255, 255, 255)
        else:
            pygame.draw.rect(screen, button_bg_inactive, button_rect, border_radius=8)
            pygame.draw.rect(screen, menu_inactive_color, button_rect, width=2, border_radius=8)
            text_color = menu_inactive_color
        
        # Button text
        button_text = menu_font.render(item, True, text_color)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
    
    # Instructions
    instruction_text = small_font.render("Use arrow keys to navigate, Enter to select, Escape for Main Menu", True, (200, 200, 200))
    inst_rect = instruction_text.get_rect(center=(w//2, int(h*0.92)))
    screen.blit(instruction_text, inst_rect)

# Tutorial functions moved to src.ui.tutorials














# Dialog functions moved to src/ui/dialog_system.py
# Reduced lines: ~635 lines (fundraising, research, hiring, researcher pool dialogs)


def draw_first_time_help(screen: pygame.Surface, help_content: Dict[str, Any], w: int, h: int, mouse_pos: Optional[Tuple[int, int]] = None) -> None:
    """
    Draw a small help popup for first-time mechanics.
    
    Args:
        screen: pygame surface to draw on
        help_content: dict with title and content for the help popup
        w, h: screen width and height
        mouse_pos: current mouse position for hover effects (optional)
    """
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
    close_text = close_font.render("X", True, close_text_color)
    close_text_rect = close_text.get_rect(center=close_button_rect.center)
    screen.blit(close_text, close_text_rect)
    
    # Add dismiss instructions at bottom of popup
    dismiss_font = pygame.font.SysFont('Consolas', int(h*0.015))
    dismiss_text = dismiss_font.render("Press Esc to dismiss, Enter to accept", True, (180, 180, 180))
    dismiss_y = popup_y + popup_height - 25
    screen.blit(dismiss_text, (popup_x + 10, dismiss_y))
    
    return close_button_rect

def draw_pre_game_settings(screen: pygame.Surface, w: int, h: int, settings: Dict[str, Any], selected_item: int, sound_manager=None) -> None:
    """
    Draw the Laboratory Configuration screen with P(Doom) bureaucracy theme.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        settings: dictionary of current settings values
        selected_item: index of currently selected setting (for keyboard navigation)
        sound_manager: optional SoundManager instance for sound toggle button
    """
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
    title_surf = title_font.render("LABORATORY CONFIGURATION", True, (220, 240, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.12)
    screen.blit(title_surf, (title_x, title_y))
    
    # Subtitle with bureaucratic flair
    subtitle_surf = subtitle_font.render("Initialize Research Parameters & Operating Procedures", True, (180, 200, 220))
    subtitle_x = w // 2 - subtitle_surf.get_width() // 2
    subtitle_y = title_y + title_surf.get_height() + 5
    screen.blit(subtitle_surf, (subtitle_x, subtitle_y))
    
    # Enhanced settings with realistic options including identity fields
    settings_options = [
        ("Continue", "> INITIALIZE LABORATORY"),
        ("Player Name", settings.get("player_name", "Anonymous")),
        ("Laboratory Name", settings.get("lab_name", "") or "[Auto-Generated]"),
        ("Research Intensity", get_research_intensity_display(settings.get("difficulty", "STANDARD"))),
        ("Audio Alerts Volume", get_volume_display(settings.get("sound_volume", 80))),
        ("Visual Enhancement", get_graphics_display(settings.get("graphics_quality", "STANDARD"))),
        ("Safety Protocol Level", get_safety_display(settings.get("safety_level", "STANDARD")))
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
        if i == 0:  # Continue button (now first)
            text = setting_value
        else:  # Setting items with values
            # Special handling for name fields to show input mode
            if (i == 1 or i == 2) and setting_name in ["Player Name", "Laboratory Name"]:
                # Check if this field is in text input mode using the manager
                try:
                    from src.ui.pre_game_settings import pre_game_settings_manager
                    is_editing = (pre_game_settings_manager.is_text_input_active() and 
                                pre_game_settings_manager.get_text_input_field() == ("player_name" if i == 1 else "lab_name"))
                except:
                    is_editing = False
                cursor = " |" if is_editing else ""
                display_value = setting_value if setting_value else "[Click to enter]"
                text = f"{setting_name}: {display_value}{cursor}"
            else:
                text = f"{setting_name}: {setting_value}"
        
        # Draw enhanced button
        if i == 0:  # Continue button gets special treatment (now first)
            draw_enhanced_continue_button(screen, button_rect, text, button_state)
        else:
            draw_bureaucratic_setting_button(screen, button_rect, text, button_state, setting_name)
            
            # Add random lab name button next to Laboratory Name field
            if i == 2 and setting_name == "Laboratory Name":
                random_button_size = int(button_height * 0.8)
                random_button_x = center_x + button_width // 2 + 10
                random_button_y = button_y + (button_height - random_button_size) // 2
                random_button_rect = pygame.Rect(random_button_x, random_button_y, random_button_size, random_button_size)
                
                # Draw random button with dice icon style
                button_color = (70, 90, 120) if button_state == ButtonState.NORMAL else (90, 110, 140)
                border_color = (120, 140, 180)
                pygame.draw.rect(screen, button_color, random_button_rect, border_radius=4)
                pygame.draw.rect(screen, border_color, random_button_rect, width=2, border_radius=4)
                
                # Draw dice dots (simple 3x3 grid with some dots filled)
                dot_size = 2
                dot_spacing = random_button_size // 4
                start_x = random_button_x + dot_spacing
                start_y = random_button_y + dot_spacing
                
                # Draw dice pattern (like showing "5" on a die)
                dice_dots = [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)]  # Positions for dots
                for dot_x, dot_y in dice_dots:
                    pygame.draw.circle(screen, (220, 240, 255), 
                                     (start_x + dot_x * dot_spacing, start_y + dot_y * dot_spacing), 
                                     dot_size)
    
    # Enhanced instructions with bureaucratic theme
    inst_font = pygame.font.SysFont('Consolas', int(h*0.022))
    instructions = [
        "- Use Up/Down arrow keys to navigate configuration options",
        "- Press ENTER to modify settings or initialize laboratory",
        "! Ensure all parameters meet institutional safety standards"
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


def get_research_intensity_display(difficulty: float) -> str:
    """Convert difficulty setting to bureaucratic terminology."""
    mapping = {
        "EASY": "CONSERVATIVE",
        "STANDARD": "REGULATORY",
        "HARD": "AGGRESSIVE",
        "DUMMY": "REGULATORY"
    }
    return mapping.get(difficulty, "REGULATORY")


def get_volume_display(volume: float) -> str:
    """Convert volume to descriptive levels."""
    if isinstance(volume, str) or volume == 123:  # Handle dummy value
        volume = 80
    if volume >= 90:
        return "MAXIMUM"
    elif volume >= 70:
        return "HIGH"
    elif volume >= 50:
        return "MODERATE"
    elif volume >= 30:
        return "LOW"
    else:
        return "MINIMAL"


def get_graphics_display(quality: str) -> str:
    """Convert graphics quality to bureaucratic terms."""
    mapping = {
        "LOW": "EFFICIENT", 
        "STANDARD": "COMPLIANT",
        "HIGH": "ENHANCED",
        "DUMMY": "COMPLIANT"
    }
    return mapping.get(quality, "COMPLIANT")


def get_safety_display(safety_level: str) -> str:
    """Safety protocol levels for the bureaucratic theme."""
    mapping = {
        "MINIMAL": "MINIMAL",
        "STANDARD": "STANDARD", 
        "ENHANCED": "ENHANCED",
        "MAXIMUM": "MAXIMUM",
        "DUMMY": "STANDARD"
    }
    return mapping.get(safety_level, "STANDARD")


def draw_enhanced_continue_button(screen: pygame.Surface, rect: pygame.Rect, text: str, button_state: str) -> None:
    """Draw the continue button with special highlighting."""
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


def draw_bureaucratic_setting_button(screen: pygame.Surface, rect: pygame.Rect, text: str, button_state: str, setting_name: str) -> None:
    """Draw setting buttons with bureaucratic styling."""
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
    if "Research" in setting_name:
        pygame.draw.circle(screen, accent_color, (icon_x, icon_y), 4)
    elif "Audio" in setting_name:
        pygame.draw.polygon(screen, accent_color, [(icon_x-3, icon_y-3), (icon_x+3, icon_y), (icon_x-3, icon_y+3)])
    elif "Visual" in setting_name:
        pygame.draw.rect(screen, accent_color, (icon_x-3, icon_y-3, 6, 6))
    elif "Safety" in setting_name:
        pygame.draw.polygon(screen, accent_color, [(icon_x, icon_y-4), (icon_x-3, icon_y+2), (icon_x+3, icon_y+2)])
    
    # Draw text with proper spacing
    font = pygame.font.SysFont('Consolas', int(rect.height * 0.32))
    text_surf = font.render(text, True, text_color)
    text_x = rect.x + 35  # Account for icon space
    text_y = rect.centery - text_surf.get_height() // 2
    screen.blit(text_surf, (text_x, text_y))


def draw_seed_selection(screen: pygame.Surface, w: int, h: int, selected_item: int, seed_input: str = "", sound_manager=None) -> None:
    """
    Draw the seed selection screen.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected item (0=Weekly, 1=Custom)
        seed_input: current custom seed input text
    """
    # Clear background
    screen.fill((50, 50, 50))
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.03))
    
    # Title
    title_surf = title_font.render("Select Seed", True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.15)
    screen.blit(title_surf, (title_x, title_y))
    
    # Seed options
    seed_items = ["Use Weekly Seed", "Use Custom Seed"]
    
    # Button layout
    button_width = int(w * 0.4)
    button_height = int(h * 0.08)
    start_y = int(h * 0.35)
    spacing = int(h * 0.12)
    center_x = w // 2
    
    for i, item in enumerate(seed_items):
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
    
    # If custom seed is selected, show input field
    if selected_item == 1:
        input_y = start_y + 2 * spacing
        input_width = int(w * 0.5)
        input_height = int(h * 0.06)
        input_x = center_x - input_width // 2
        input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
        
        # Draw input background
        pygame.draw.rect(screen, (80, 80, 80), input_rect)
        pygame.draw.rect(screen, (120, 120, 120), input_rect, 2)
        
        # Draw input text
        input_font = pygame.font.SysFont('Consolas', int(h*0.03))
        display_text = seed_input if seed_input else "Enter custom seed..."
        text_color = (255, 255, 255) if seed_input else (150, 150, 150)
        input_text_surf = input_font.render(display_text, True, text_color)
        text_x = input_rect.x + 10
        text_y = input_rect.centery - input_text_surf.get_height() // 2
        screen.blit(input_text_surf, (text_x, text_y))
    
    # Instructions
    inst_font = pygame.font.SysFont('Consolas', int(h*0.025))
    instructions = [
        "Use arrow keys to navigate, Enter to continue",
        "Custom seed: type your seed and press Enter"
    ]
    
    inst_y = int(h * 0.85)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 5
    
    # Draw sound toggle button if sound manager is available (Issue #89)
    if sound_manager:
        draw_mute_button_standalone(screen, sound_manager, w, h)


def draw_tutorial_choice(screen: pygame.Surface, w: int, h: int, selected_item: int) -> None:
    """
    Draw the tutorial choice screen.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected item (0=No, 1=Yes)
    """
    # Clear background
    screen.fill((50, 50, 50))
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.03))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.025))
    
    # Title
    title_surf = title_font.render("Tutorial Mode?", True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.15)
    screen.blit(title_surf, (title_x, title_y))
    
    # Description
    desc_text = "Would you like to play with tutorial guidance?"
    desc_surf = desc_font.render(desc_text, True, (200, 200, 200))
    desc_x = w // 2 - desc_surf.get_width() // 2
    desc_y = title_y + title_surf.get_height() + 20
    screen.blit(desc_surf, (desc_x, desc_y))
    
    # Tutorial options - No tutorial first (default), Yes tutorial second
    tutorial_items = ["No - Regular Mode", "Yes - Enable Tutorial"]
    
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
        "Use arrow keys or mouse to navigate, Enter/Space to confirm",
        "Tutorial mode provides helpful guidance for new players"
    ]
    
    inst_y = int(h * 0.8)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 5


def draw_new_player_experience(screen: pygame.Surface, w: int, h: int, selected_item: int, tutorial_enabled: bool, intro_enabled: bool) -> None:
    """
    Draw the new player experience screen with tutorial and intro checkboxes.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected item (0=Tutorial, 1=Intro, 2=Start button)
        tutorial_enabled: whether tutorial checkbox is checked
        intro_enabled: whether intro checkbox is checked
    """
    # Clear background
    screen.fill((50, 50, 50))
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    option_font = pygame.font.SysFont('Consolas', int(h*0.03))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.025))
    
    # Title
    title_surf = title_font.render("New Player Experience", True, (255, 255, 255))
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.12)
    screen.blit(title_surf, (title_x, title_y))
    
    # Description
    desc_text = "Choose your starting options:"
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
        ("Tutorial", "Get helpful guidance for new players", tutorial_enabled),
        ("Intro", "Read an introduction to the scenario", intro_enabled)
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
    draw_low_poly_button(screen, button_rect, "Start Game", button_state)
    
    # Intro text preview if intro is enabled
    if intro_enabled:
        intro_y = button_y + button_height + 30
        intro_font = pygame.font.SysFont('Consolas', int(h*0.022))
        intro_lines = [
            "Doom is coming. You convinced a funder to give you $1,000.",
            "You'll be assigned a lab name for pseudonymous competition.",
            "Your job is to save the world. Good luck!"
        ]
        
        for line in intro_lines:
            intro_surf = intro_font.render(line, True, (255, 200, 100))
            intro_x = w // 2 - intro_surf.get_width() // 2
            screen.blit(intro_surf, (intro_x, intro_y))
            intro_y += intro_surf.get_height() + 5
    
    # Instructions
    inst_font = pygame.font.SysFont('Consolas', int(h*0.02))
    instructions = [
        "Use arrow keys or mouse to navigate",
        "Space/Enter to toggle checkboxes or start game",
        "Escape to return to main menu"
    ]
    
    inst_y = int(h * 0.85)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (150, 150, 150))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 3


def draw_turn_transition_overlay(screen: pygame.Surface, w: int, h: int, timer: float, duration: float) -> None:
    """
    Draw a turn transition overlay with darkening/lightening effect.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height
        timer: current timer value (counts down from duration to 0)
        duration: total duration of the transition
    """
    if timer <= 0 or duration <= 0:
        return
    
    # Calculate transition progress (0.0 to 1.0)
    progress = 1.0 - (timer / duration)
    
    # Create overlay surface
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(128)  # Semi-transparent
    
    # Calculate overlay color based on progress
    # Start dark, then lighten, then back to normal
    if progress < 0.5:
        # First half: darken
        darkness = int(100 * (progress * 2))  # 0 to 100
        overlay.fill((darkness, darkness, darkness))
    else:
        # Second half: lighten back to normal
        lightness = int(100 * (2 - progress * 2))  # 100 to 0
        overlay.fill((lightness, lightness, lightness))
    
    # Draw overlay
    screen.blit(overlay, (0, 0))
    
    # Add "Processing Turn..." text in center
    font = pygame.font.SysFont('Consolas', int(h * 0.04), bold=True)
    text_color = (255, 255, 255) if progress < 0.5 else (50, 50, 50)  # White on dark, dark on light
    text_surf = font.render("Processing Turn...", True, text_color)
    text_x = w // 2 - text_surf.get_width() // 2
    text_y = h // 2 - text_surf.get_height() // 2
    screen.blit(text_surf, (text_x, text_y))
    
    # Add progress indicator
    progress_width = int(w * 0.3)
    progress_height = 8
    progress_x = w // 2 - progress_width // 2
    progress_y = text_y + text_surf.get_height() + 20
    
    # Background bar
    progress_bg = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
    pygame.draw.rect(screen, (100, 100, 100), progress_bg)
    
    # Progress bar
    progress_fill_width = int(progress_width * progress)
    progress_fill = pygame.Rect(progress_x, progress_y, progress_fill_width, progress_height)
    progress_color = (100, 200, 100)  # Green progress bar
    pygame.draw.rect(screen, progress_color, progress_fill)


def draw_audio_menu(screen: pygame.Surface, w: int, h: int, selected_item: int, audio_settings: Dict[str, Any], sound_manager) -> None:
    """
    Draw the audio settings menu.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height
        selected_item: index of currently selected menu item
        audio_settings: dictionary of current audio settings
        sound_manager: SoundManager instance for current state
    """
    # Background
    screen.fill((40, 45, 55))
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h*0.055), bold=True)
    title_surf = title_font.render("Audio Settings", True, (220, 240, 255))
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
    master_status = "Enabled" if audio_settings.get('master_enabled', True) else "Disabled"
    sfx_volume = audio_settings.get('sfx_volume', 80)
    
    menu_items = [
        f"Master Sound: {master_status}",
        f"SFX Volume: {sfx_volume}%",
        "Sound Effects Settings",
        "Test Sound",
        "< Back to Main Menu"
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
        "Use arrow keys to navigate, Enter/Space to select",
        "Left/Right arrows adjust volume settings",
        "Escape to return to main menu"
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
        info_text = "Individual sound toggles: Click to cycle through sound effects"
        info_surf = info_font.render(info_text, True, (150, 200, 150))
        info_x = w // 2 - info_surf.get_width() // 2
        info_y = int(h * 0.85)
        screen.blit(info_surf, (info_x, info_y))


def draw_high_score_screen(screen: pygame.Surface, w: int, h: int, game_state, seed: str, submit_to_leaderboard: bool, selected_item: int = 0, from_main_menu: bool = False) -> None:
    """
    Draw the enhanced high score screen with seed-specific leaderboards and interactive menu.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        game_state: GameState object for displaying final stats
        seed: Game seed used for this session
        submit_to_leaderboard: Whether to submit score to leaderboard
        selected_item: Currently selected menu item (0=Play Again/Launch New Game as default)
        from_main_menu: True if accessed from main menu, False if from completed game
    """
    # Clear screen with grey background (matching config menu)
    screen.fill((64, 64, 64))
    
    # Fonts for consistent styling with config menu
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    pygame.font.SysFont('Consolas', int(h*0.035))
    desc_font = pygame.font.SysFont('Consolas', int(h*0.025))
    stats_font = pygame.font.SysFont('Consolas', int(h*0.022))
    
    # Colors matching lab config menu theme
    white = (255, 255, 255)
    light_gray = (200, 200, 200) 
    gray = (150, 150, 150)
    gold = (255, 215, 0)
    silver = (192, 192, 192)
    bronze = (205, 127, 50)
    
    # Title at top
    title_surf = title_font.render("High Scores & Leaderboard", True, white)
    title_x = w // 2 - title_surf.get_width() // 2
    title_y = int(h * 0.05)
    screen.blit(title_surf, (title_x, title_y))
    
    # Seed and configuration info
    config_y = int(h * 0.1)
    seed_info = f"Seed: '{seed}' | Economic Model: Bootstrap v0.4.1"
    seed_surf = desc_font.render(seed_info, True, light_gray)
    seed_x = w // 2 - seed_surf.get_width() // 2
    screen.blit(seed_surf, (seed_x, config_y))
    
    # Current game stats if available (compact display)
    if game_state:
        stats_y = int(h * 0.13)
        stats_text = f"Your Score: {game_state.turn} turns | Money: ${game_state.money}k | Staff: {game_state.staff} | Doom: {game_state.doom:.1f}%"
        stats_surf = stats_font.render(stats_text, True, white)
        stats_x = w // 2 - stats_surf.get_width() // 2
        screen.blit(stats_surf, (stats_x, stats_y))
    
    # Leaderboard display (more compact)
    leaderboard_y = int(h * 0.17)
    try:
        from src.scores.enhanced_leaderboard import leaderboard_manager
        
        # Handle case where seed is None (accessed from main menu)
        if seed is None or seed == 'None':
            # Show a general message when no specific seed is selected
            no_seed_text = "Select a seed to view its leaderboard"
            no_seed_surf = desc_font.render(no_seed_text, True, gray)
            no_seed_x = w // 2 - no_seed_surf.get_width() // 2
            screen.blit(no_seed_surf, (no_seed_x, leaderboard_y + 30))
            
            hint_text = "Play a game or use 'Launch with Custom Seed' to see scores"
            hint_surf = pygame.font.SysFont('Consolas', int(h*0.018)).render(hint_text, True, light_gray)
            hint_x = w // 2 - hint_surf.get_width() // 2
            screen.blit(hint_surf, (hint_x, leaderboard_y + 60))
        else:
            leaderboard = leaderboard_manager.get_leaderboard_for_seed(seed)
            entries = leaderboard.get_top_scores(10)  # Top 10 for more compact display
            
            if entries:
                header_surf = desc_font.render("Top Scores:", True, white)
                header_x = w // 2 - header_surf.get_width() // 2
                screen.blit(header_surf, (header_x, leaderboard_y))
                
                # Compact leaderboard entries
                entry_y = leaderboard_y + 30
                for i, entry in enumerate(entries[:8]):  # Limit to 8 entries for space
                    if entry_y > h * 0.45:  # Stop if approaching menu area
                        break
                        
                    rank = i + 1
                    
                    # Rank color based on position
                    if rank == 1:
                        rank_color = gold
                    elif rank == 2:
                        rank_color = silver
                    elif rank == 3:
                        rank_color = bronze
                    else:
                        rank_color = light_gray
                    
                    # Compact entry format
                    entry_text = f"#{rank}: {entry.score} turns - {entry.player_name[:15]} ({entry.date.strftime('%m/%d')})"
                    entry_surf = pygame.font.SysFont('Consolas', int(h*0.018)).render(entry_text, True, rank_color)
                    entry_x = w // 2 - entry_surf.get_width() // 2
                    screen.blit(entry_surf, (entry_x, entry_y))
                    entry_y += 20
            
            else:
                no_scores_text = "No scores recorded yet for this seed."
                no_scores_surf = desc_font.render(no_scores_text, True, gray)
                no_scores_x = w // 2 - no_scores_surf.get_width() // 2
                screen.blit(no_scores_surf, (no_scores_x, leaderboard_y + 30))
    
    except Exception as e:
        error_text = f"Leaderboard error: {str(e)[:50]}..."
        error_surf = desc_font.render(error_text, True, (255, 100, 100))
        error_x = w // 2 - error_surf.get_width() // 2
        screen.blit(error_surf, (error_x, leaderboard_y + 30))
    
    # Interactive menu buttons (matching config menu style)
    # Dynamically choose first menu item based on context
    first_button = "Launch New Game" if from_main_menu else "Play Again"
    menu_items = [first_button, "Main Menu", "Settings", "Submit Feedback", "View Full Leaderboard"]
    
    button_width = int(w * 0.4)
    button_height = int(h * 0.06)
    start_y = int(h * 0.52)
    
    for i, item in enumerate(menu_items):
        y = start_y + i * int(button_height + h * 0.02)
        x = w // 2 - button_width // 2
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.FOCUSED  # Use FOCUSED instead of SELECTED
        else:
            button_state = ButtonState.NORMAL
        
        # Create rect and draw button using correct parameters
        button_rect = pygame.Rect(x, y, button_width, button_height)
        draw_low_poly_button(screen, button_rect, item, button_state)
    
    # Instructions at bottom (matching config menu)
    instructions = [
        "Up/Down or mouse to navigate",
        "Enter or click to select",
        "Escape to return to main menu"
    ]
    
    for i, inst in enumerate(instructions):
        inst_surf = pygame.font.SysFont('Consolas', int(h*0.02)).render(inst, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        inst_y = int(h * 0.87) + i * int(h * 0.025)
        screen.blit(inst_surf, (inst_x, inst_y))

# REMOVED: draw_high_score_screen_legacy (151 lines)
# This legacy function was unused and duplicated functionality
