import pygame
import textwrap
from visual_feedback import visual_feedback, ButtonState, FeedbackStyle, draw_low_poly_button
from keyboard_shortcuts import get_main_menu_shortcuts, get_in_game_shortcuts, format_shortcut_list


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

def draw_back_button(screen, w, h, navigation_depth, font=None):
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
    button_text = "← Back"
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

def wrap_text(text, font, max_width):
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

def render_text(text, font, max_width=None, color=(255,255,255), line_height_multiplier=1.35):
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

def draw_main_menu(screen, w, h, selected_item, sound_manager=None):
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
    menu_font = pygame.font.SysFont('Consolas', int(h*0.035))
    
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
        "Launch with Weekly Seed",
        "Launch with Custom Seed", 
        "Options",
        "Player Guide",
        "README"
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
    
    # Draw version in bottom right corner
    draw_version_footer(screen, w, h)

def draw_sounds_menu(screen, w, h, selected_item, game_state=None):
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
    menu_font = pygame.font.SysFont('Consolas', int(h*0.03))
    
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

def draw_config_menu(screen, w, h, selected_item, configs, current_config_name):
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
    menu_font = pygame.font.SysFont('Consolas', int(h*0.035))
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
    all_items = configs + ["← Back to Main Menu"]
    
    button_width = int(w * 0.4)
    button_height = int(h * 0.06)
    start_y = int(h * 0.25)
    
    for i, item in enumerate(all_items):
        y = start_y + i * int(button_height + h * 0.02)
        x = w // 2 - button_width // 2
        
        # Determine button state
        if i == selected_item:
            button_state = ButtonState.SELECTED
        elif item == current_config_name:
            button_state = ButtonState.ACTIVE  # Different color for current config
        else:
            button_state = ButtonState.NORMAL
        
        # Draw button
        draw_low_poly_button(screen, x, y, button_width, button_height, 
                           item, menu_font, button_state)
    
    # Instructions at bottom
    instructions = [
        "↑/↓ or mouse to navigate",
        "Enter or click to select configuration",
        "Escape to go back"
    ]
    
    for i, inst in enumerate(instructions):
        inst_surf = desc_font.render(inst, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        inst_y = int(h * 0.8) + i * int(h * 0.04)
        screen.blit(inst_surf, (inst_x, inst_y))

def draw_overlay(screen, title, content, scroll_offset, w, h, navigation_depth=0):
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
        up_arrow = arrow_font.render("▲", True, (255, 255, 255))
        screen.blit(up_arrow, (content_x + content_width - 30, text_area_y))
    
    if (start_line + visible_lines) < len(lines):
        # Down arrow
        arrow_font = pygame.font.SysFont('Consolas', int(h*0.03), bold=True)
        down_arrow = arrow_font.render("▼", True, (255, 255, 255))
        screen.blit(down_arrow, (content_x + content_width - 30, text_area_y + text_area_height - 30))
    
    # Instructions at bottom
    instruction_font = pygame.font.SysFont('Consolas', int(h*0.025))
    instructions = "Use arrow keys to scroll • Press Escape or click to return to menu"
    inst_surf = instruction_font.render(instructions, True, (180, 200, 255))
    inst_x = w // 2 - inst_surf.get_width() // 2
    inst_y = content_y + content_height + int(h * 0.03)
    screen.blit(inst_surf, (inst_x, inst_y))
    
    return back_button_rect

def draw_window_with_header(screen, rect, title, content=None, minimized=False, font=None):
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
    
    # Draw minimize button (□ or ─ based on state)
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
        # Restore icon (□)
        icon_rect = pygame.Rect(
            minimize_button_rect.x + 4, minimize_button_rect.y + 4,
            minimize_button_rect.width - 8, minimize_button_rect.height - 8
        )
        pygame.draw.rect(screen, icon_color, icon_rect, 2)
    else:
        # Minimize icon (─)
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

def draw_version_footer(screen, w, h, font=None):
    """
    Draw version information in the footer area.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for positioning
        font: optional font for version text
    """
    try:
        from version import get_display_version
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

def draw_version_header(screen, w, h, font=None):
    """
    Draw version information in the header area (alternative placement).
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for positioning
        font: optional font for version text
    """
    try:
        from version import get_display_version
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

def draw_loading_screen(screen, w, h, progress=0, status_text="Loading...", font=None):
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
    
def should_show_ui_element(game_state, element_id):
    """
    Check if a UI element should be visible based on tutorial progress.
    
    Args:
        game_state: The current game state
        element_id: String identifier for the UI element
        
    Returns:
        bool: True if the element should be visible
    """
    # Import onboarding here to avoid circular imports
    from onboarding import onboarding
    
    # If tutorial is not active, show all elements
    if not onboarding.show_tutorial_overlay:
        return True
    
    # Check if element should be visible based on tutorial progress
    return onboarding.should_show_ui_element(element_id)


def draw_ui(screen, game_state, w, h):
    # Fonts, scaled by screen size
    title_font = pygame.font.SysFont('Consolas', int(h*0.045), bold=True)
    big_font = pygame.font.SysFont('Consolas', int(h*0.033))
    font = pygame.font.SysFont('Consolas', int(h*0.025))
    small_font = pygame.font.SysFont('Consolas', int(h*0.018))

    # Title
    title = title_font.render("P(Doom): Bureaucracy Strategy", True, (205, 255, 220))
    screen.blit(title, (int(w*0.04), int(h*0.03)))

    # Resources (top bar) - controlled by tutorial visibility
    if should_show_ui_element(game_state, 'money_display'):
        screen.blit(big_font.render(f"Money: ${game_state.money}", True, (255, 230, 60)), (int(w*0.04), int(h*0.11)))
        
        # Cash flow indicator if accounting software is purchased
        if hasattr(game_state, 'accounting_software_bought') and game_state.accounting_software_bought:
            if hasattr(game_state, 'last_balance_change') and game_state.last_balance_change != 0:
                change_color = (100, 255, 100) if game_state.last_balance_change > 0 else (255, 100, 100)
                change_sign = "+" if game_state.last_balance_change > 0 else ""
                change_text = f"({change_sign}${game_state.last_balance_change})"
                screen.blit(font.render(change_text, True, change_color), (int(w*0.04), int(h*0.13)))
    
    if should_show_ui_element(game_state, 'staff_display'):
        screen.blit(big_font.render(f"Staff: {game_state.staff}", True, (255, 210, 180)), (int(w*0.21), int(h*0.11)))
    
    if should_show_ui_element(game_state, 'reputation_display'):
        screen.blit(big_font.render(f"Reputation: {game_state.reputation}", True, (180, 210, 255)), (int(w*0.35), int(h*0.11)))
    
    # Action Points with glow effect
    ap_color = (255, 255, 100)  # Yellow base color for AP
    if hasattr(game_state, 'ap_glow_timer') and game_state.ap_glow_timer > 0:
        # Add glow/pulse effect when AP is spent
        glow_intensity = int(127 * (game_state.ap_glow_timer / 30))  # Fade over 30 frames
        ap_color = (min(255, 255 + glow_intensity), min(255, 255 + glow_intensity), min(255, 100 + glow_intensity))
    
    screen.blit(big_font.render(f"AP: {game_state.action_points}/{game_state.max_action_points}", True, ap_color), (int(w*0.49), int(h*0.11)))
    
    screen.blit(big_font.render(f"p(Doom): {game_state.doom}/{game_state.max_doom}", True, (255, 80, 80)), (int(w*0.62), int(h*0.11)))
    screen.blit(font.render(f"Opponent progress: {game_state.known_opp_progress if game_state.known_opp_progress is not None else '???'}/100", True, (240, 200, 160)), (int(w*0.84), int(h*0.11)))
    # Second line of resources
    screen.blit(big_font.render(f"Compute: {game_state.compute}", True, (100, 255, 150)), (int(w*0.04), int(h*0.135)))
    screen.blit(big_font.render(f"Research: {game_state.research_progress}/100", True, (150, 200, 255)), (int(w*0.21), int(h*0.135)))
    screen.blit(big_font.render(f"Papers: {game_state.papers_published}", True, (255, 200, 100)), (int(w*0.38), int(h*0.135)))
    
    # Board member and audit risk display (if applicable)
    if hasattr(game_state, 'board_members') and game_state.board_members > 0:
        screen.blit(font.render(f"Board Members: {game_state.board_members}", True, (255, 150, 150)), (int(w*0.55), int(h*0.135)))
        if hasattr(game_state, 'audit_risk_level') and game_state.audit_risk_level > 0:
            risk_color = (255, 200, 100) if game_state.audit_risk_level <= 5 else (255, 100, 100)
            screen.blit(font.render(f"Audit Risk: {game_state.audit_risk_level}", True, risk_color), (int(w*0.72), int(h*0.135)))
    
    screen.blit(small_font.render(f"Turn: {game_state.turn}", True, (220, 220, 220)), (int(w*0.91), int(h*0.03)))
    screen.blit(small_font.render(f"Seed: {game_state.seed}", True, (140, 200, 160)), (int(w*0.77), int(h*0.03)))

    # Doom bar
    doom_bar_x, doom_bar_y = int(w*0.62), int(h*0.16)
    doom_bar_width, doom_bar_height = int(w*0.28), int(h*0.025)
    pygame.draw.rect(screen, (70, 50, 50), (doom_bar_x, doom_bar_y, doom_bar_width, doom_bar_height))
    filled = int(doom_bar_width * (game_state.doom / game_state.max_doom))
    pygame.draw.rect(screen, (255, 60, 60), (doom_bar_x, doom_bar_y, filled, doom_bar_height))

    # Opponents information panel (between resources and actions)
    draw_opponents_panel(screen, game_state, w, h, font, small_font)

    # Action buttons (left) - Enhanced with visual feedback
    action_rects = game_state._get_action_rects(w, h)
    for idx, rect_tuple in enumerate(action_rects):
        action = game_state.actions[idx]
        ap_cost = action.get("ap_cost", 1)
        
        # Convert tuple to pygame.Rect
        rect = pygame.Rect(rect_tuple)
        
        # Determine button state for visual feedback
        if game_state.action_points < ap_cost:
            button_state = ButtonState.DISABLED
        elif idx in game_state.selected_actions:
            button_state = ButtonState.PRESSED
        elif hasattr(game_state, 'hovered_action_idx') and game_state.hovered_action_idx == idx:
            button_state = ButtonState.HOVER
        else:
            button_state = ButtonState.NORMAL
        
        # Use visual feedback system for consistent styling
        # Include keyboard shortcut in button text for first 9 actions
        button_text = action["name"]
        if idx < 9:  # Only first 9 actions get keyboard shortcuts (1-9 keys)
            shortcut_key = str(idx + 1)
            button_text = f"[{shortcut_key}] {action['name']}"
        
        visual_feedback.draw_button(
            screen, rect, button_text, button_state, FeedbackStyle.BUTTON
        )
        
        # Draw action usage indicators (circles for repeatables)
        if hasattr(game_state, 'selected_action_instances'):
            action_count = sum(1 for inst in game_state.selected_action_instances if inst['action_idx'] == idx)
            if action_count > 0:
                # Draw usage indicators as small circles
                indicator_size = int(min(w, h) * 0.008)  # Small circles
                indicator_color = (100, 255, 100) if button_state != ButtonState.DISABLED else (60, 120, 60)
                
                # Position indicators in top-right of button
                start_x = rect.right - (action_count * indicator_size * 2) - 5
                start_y = rect.top + 5
                
                for i in range(min(action_count, 5)):  # Max 5 indicators to avoid clutter
                    circle_x = start_x + (i * indicator_size * 2)
                    circle_y = start_y + indicator_size
                    pygame.draw.circle(screen, indicator_color, (circle_x, circle_y), indicator_size)
                    
                # If more than 5, show "+N" text
                if action_count > 5:
                    more_text = font.render(f"+{action_count-5}", True, indicator_color)
                    screen.blit(more_text, (start_x + 5 * indicator_size * 2 + 2, start_y))
        
        # Draw description text below button
        desc_color = (190, 210, 255) if game_state.action_points >= ap_cost else (140, 150, 160)
        desc_text = font.render(f"{action['desc']} (Cost: ${action['cost']}, AP: {ap_cost})", True, desc_color)
        screen.blit(desc_text, (rect.x + int(w*0.01), rect.y + int(h*0.04)))

    # Upgrades (right: purchased as icons at top right, available as buttons) - Enhanced with visual feedback
    upgrade_rects = game_state._get_upgrade_rects(w, h)
    for idx, rect_tuple in enumerate(upgrade_rects):
        upg = game_state.upgrades[idx]
        
        # Convert tuple to pygame.Rect
        rect = pygame.Rect(rect_tuple)
        
        if upg.get("purchased", False):
            # Draw as small icon using visual feedback system
            visual_feedback.draw_icon_button(screen, rect, upg["name"][0], ButtonState.NORMAL)
        else:
            # Determine button state
            if upg['cost'] > game_state.money:
                button_state = ButtonState.DISABLED
            elif hasattr(game_state, 'hovered_upgrade_idx') and game_state.hovered_upgrade_idx == idx:
                button_state = ButtonState.HOVER
            else:
                button_state = ButtonState.NORMAL
            
            # Draw upgrade button with consistent styling
            visual_feedback.draw_button(
                screen, rect, upg["name"], button_state, FeedbackStyle.BUTTON
            )
            
            # Draw description and status
            desc_color = (200, 255, 200) if button_state != ButtonState.DISABLED else (120, 150, 120)
            desc = small_font.render(upg["desc"] + f" (Cost: ${upg['cost']})", True, desc_color)
            status = small_font.render("AVAILABLE", True, desc_color)
            screen.blit(desc, (rect.x + int(w*0.01), rect.y + int(h*0.04)))
            screen.blit(status, (rect.x + int(w*0.24), rect.y + int(h*0.04)))

    # --- Balance change display (after buying accounting software) ---
    # If accounting software was bought, show last balance change under Money
    if hasattr(game_state, "accounting_software_bought") and game_state.accounting_software_bought:
        # Show the last balance change if available
        change = getattr(game_state, "last_balance_change", 0)
        sign = "+" if change > 0 else ""
        # Render in green if positive, red if negative
        screen.blit(
            font.render(f"({sign}{change})", True, (200, 255, 200) if change >= 0 else (255, 180, 180)),
            (int(w*0.18), int(h*0.135))
        )
        # Optionally, always show the "monthly costs" indicator here as well


    # Draw UI transitions (on top of everything else)
    draw_ui_transitions(screen, game_state, w, h, big_font)

    # End Turn button (bottom center) - Enhanced with visual feedback
    endturn_rect_tuple = game_state._get_endturn_rect(w, h)
    endturn_rect = pygame.Rect(endturn_rect_tuple)
    
    # Determine button state
    endturn_state = ButtonState.HOVER if hasattr(game_state, 'endturn_hovered') and game_state.endturn_hovered else ButtonState.NORMAL
    
    # Use visual feedback system with custom colors for end turn button
    custom_colors = {
        ButtonState.NORMAL: {
            'bg': (140, 90, 90),
            'border': (210, 110, 110),
            'text': (255, 240, 240),
            'shadow': (60, 40, 40)
        },
        ButtonState.HOVER: {
            'bg': (160, 110, 110),
            'border': (230, 130, 130),
            'text': (255, 255, 255),
            'shadow': (80, 60, 60),
            'glow': (255, 200, 200, 40)
        }
    }
    
    visual_feedback.draw_button(
        screen, endturn_rect, "END TURN (Space)", endturn_state, 
        FeedbackStyle.BUTTON, custom_colors.get(endturn_state)
    )


    # Messages log (bottom left) - Enhanced with scrollable history and minimize option
    # Use current position (including any drag offset)
    if hasattr(game_state, '_get_activity_log_current_position'):
        log_x, log_y = game_state._get_activity_log_current_position(w, h)
    else:
        # Improved fallback positioning with better alignment
        log_x, log_y = int(w*0.04), int(h*0.74)  # Keep existing position for compatibility


    
    # Check if activity log is minimized (only available with compact activity display upgrade)
    if (hasattr(game_state, 'activity_log_minimized') and 
        game_state.activity_log_minimized and 
        "compact_activity_display" in game_state.upgrade_effects):
        # Draw minimized activity log as a small title bar with expand button
        title_text = font.render("Activity Log", True, (255, 255, 180))
        title_width = title_text.get_width()
        
        # Draw small background bar
        bar_height = int(h * 0.04)
        bar_rect = pygame.Rect(log_x - 5, log_y - 5, title_width + 50, bar_height)
        pygame.draw.rect(screen, (60, 80, 100), bar_rect, border_radius=4)
        pygame.draw.rect(screen, (120, 140, 180), bar_rect, width=1, border_radius=4)
        
        screen.blit(title_text, (log_x, log_y))
        
        # Draw expand button (plus icon)
        expand_button_x = log_x + title_width + 10
        expand_button_y = log_y
        expand_button_size = int(h * 0.025)
        
        pygame.draw.rect(screen, (100, 120, 150), 
                        (expand_button_x, expand_button_y, expand_button_size, expand_button_size),
                        border_radius=2)
        
        # Plus icon
        plus_font = pygame.font.SysFont('Consolas', int(h * 0.02), bold=True)
        plus_text = plus_font.render("+", True, (255, 255, 255))
        plus_rect = plus_text.get_rect(center=(expand_button_x + expand_button_size//2, 
                                               expand_button_y + expand_button_size//2))
        screen.blit(plus_text, plus_rect)
        
    elif game_state.scrollable_event_log_enabled:
        # Enhanced scrollable event log with border and visual indicators
        log_width = int(w * 0.22)  # Reduced from 0.44 to 0.22 to avoid upgrade button overlap
        log_height = int(h * 0.22)
        
        # Draw border around the event log area
        border_rect = pygame.Rect(log_x - 5, log_y - 5, log_width + 10, log_height + 10)
        pygame.draw.rect(screen, (80, 100, 120), border_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 140, 180), border_rect, width=2, border_radius=8)
        
        # Event log title with scroll indicator and minimize button
        title_text = font.render("Activity Log (Scrollable)", True, (255, 255, 180))
        screen.blit(title_text, (log_x, log_y))
        
        # Add minimize button if compact display upgrade is available
        if "compact_activity_display" in game_state.upgrade_effects:
            minimize_button_x = log_x + log_width - 30
            minimize_button_y = log_y
            minimize_button_size = int(h * 0.025)
            
            pygame.draw.rect(screen, (100, 120, 150), 
                            (minimize_button_x, minimize_button_y, minimize_button_size, minimize_button_size),
                            border_radius=2)
            
            # Minus icon
            minus_font = pygame.font.SysFont('Consolas', int(h * 0.02), bold=True)
            minus_text = minus_font.render("−", True, (255, 255, 255))
            minus_rect = minus_text.get_rect(center=(minimize_button_x + minimize_button_size//2, 
                                                   minimize_button_y + minimize_button_size//2))
            screen.blit(minus_text, minus_rect)
        
        # Scroll indicator
        if len(game_state.event_log_history) > 0 or len(game_state.messages) > 0:
            scroll_info = small_font.render("↑↓ or mouse wheel to scroll", True, (200, 200, 255))
            scroll_x = log_x + log_width - scroll_info.get_width()
            if "compact_activity_display" in game_state.upgrade_effects:
                scroll_x -= 35  # Make room for minimize button
            screen.blit(scroll_info, (scroll_x, log_y))
        
        # Calculate visible area for messages
        content_y = log_y + int(h * 0.04)
        content_height = log_height - int(h * 0.05)
        line_height = int(h * 0.025)
        max_visible_lines = content_height // line_height
        
        # Combine history and current messages for display
        all_messages = list(game_state.event_log_history) + game_state.messages
        
        # Calculate scrolling - Auto-scroll to bottom by default for new content
        total_lines = len(all_messages)
        
        # Check if we should auto-scroll to bottom (when there are more lines than visible)
        if total_lines > max_visible_lines:
            # If scroll offset is 0 or close to max (user at bottom), keep at bottom
            max_scroll_offset = total_lines - max_visible_lines
            if game_state.event_log_scroll_offset <= 1 or game_state.event_log_scroll_offset >= max_scroll_offset - 1:
                game_state.event_log_scroll_offset = max_scroll_offset
        
        start_line = max(0, min(game_state.event_log_scroll_offset, total_lines - max_visible_lines))
        
        # Draw messages with scrolling
        for i in range(max_visible_lines):
            msg_index = start_line + i
            if msg_index < len(all_messages):
                msg = all_messages[msg_index]
                y_pos = content_y + i * line_height
                
                # Different colors for turn headers vs regular messages
                if msg.startswith("=== Turn"):
                    color = (255, 220, 120)  # Yellow for turn headers
                    font_to_use = font
                else:
                    color = (255, 255, 210)  # White for regular messages
                    font_to_use = small_font
                
                # Truncate long messages to fit width
                max_chars = log_width // 8  # Rough estimate
                if len(msg) > max_chars:
                    msg = msg[:max_chars-3] + "..."
                
                msg_text = font_to_use.render(msg, True, color)
                screen.blit(msg_text, (log_x + int(w*0.01), y_pos))
        
        # Draw scroll indicators if needed
        if start_line > 0:
            # Up arrow indicator
            up_arrow = small_font.render("▲", True, (180, 255, 180))
            screen.blit(up_arrow, (log_x + log_width - 25, content_y))
        
        if start_line + max_visible_lines < total_lines:
            # Down arrow indicator
            down_arrow = small_font.render("▼", True, (180, 255, 180))
            screen.blit(down_arrow, (log_x + log_width - 25, content_y + content_height - 20))
            
            
    else:
        # Original simple event log (for backward compatibility)
        screen.blit(font.render("Activity Log:", True, (255, 255, 180)), (log_x, log_y))
        for i, msg in enumerate(game_state.messages[-7:]):
            msg_text = small_font.render(msg, True, (255, 255, 210))
            screen.blit(msg_text, (log_x + int(w*0.01), log_y + int(h*0.035) + i * int(h*0.03)))

    # Draw employee blobs (lower middle area)
    draw_employee_blobs(screen, game_state, w, h)
    
    # Draw deferred events zone (lower right)
    draw_deferred_events_zone(screen, game_state, w, h, small_font)
    
    # Draw mute button (bottom right)
    draw_mute_button(screen, game_state, w, h)
    
    # Draw version in bottom right corner (unobtrusive)
    draw_version_footer(screen, w, h)
    
    # Draw popup events (overlay, drawn last to be on top)
    draw_popup_events(screen, game_state, w, h, font, big_font)

def draw_employee_blobs(screen, game_state, w, h):
    """Draw employee blobs with dynamic positioning that avoids UI overlap"""
    import math
    
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
            
        # Red slash overlay for unproductive employees due to management issues
        if blob.get('unproductive_reason') == 'no_manager':
            # Draw red diagonal slash across the blob
            slash_color = (255, 50, 50)
            slash_width = 4
            # Diagonal line from top-left to bottom-right
            start_pos = (x - blob_radius + 5, y - blob_radius + 5)
            end_pos = (x + blob_radius - 5, y + blob_radius - 5)
            pygame.draw.line(screen, slash_color, start_pos, end_pos, slash_width)
            # Second diagonal line from top-right to bottom-left
            start_pos = (x + blob_radius - 5, y - blob_radius + 5)
            end_pos = (x - blob_radius + 5, y + blob_radius - 5)
            pygame.draw.line(screen, slash_color, start_pos, end_pos, slash_width)

def draw_mute_button(screen, game_state, w, h):
    """Draw mute/unmute button in bottom right corner"""
    # Button position (bottom right) - made larger per issue #89
    button_size = int(min(w, h) * 0.06)  # Increased from 0.04 to 0.06 for better visibility
    button_x = w - button_size - 20
    button_y = h - button_size - 20
    
    # Button colors
    if hasattr(game_state, 'sound_manager') and game_state.sound_manager and game_state.sound_manager.is_enabled():
        bg_color = (100, 200, 100)  # Green when sound is on
        icon_color = (255, 255, 255)
        symbol = "♪"  # Musical note when sound is on
    else:
        bg_color = (200, 100, 100)  # Red when sound is off
        icon_color = (255, 255, 255) 
        symbol = "🔇"  # Muted symbol when sound is off
    
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

def draw_mute_button_standalone(screen, sound_manager, w, h):
    """Draw mute/unmute button in bottom right corner (standalone version for menus)"""
    # Button position (bottom right) - made larger per issue #89
    button_size = int(min(w, h) * 0.06)  # Same size as main game mute button
    button_x = w - button_size - 20
    button_y = h - button_size - 20
    
    # Button colors
    if sound_manager and sound_manager.is_enabled():
        bg_color = (100, 200, 100)  # Green when sound is on
        icon_color = (255, 255, 255)
        symbol = "♪"  # Musical note when sound is on
    else:
        bg_color = (200, 100, 100)  # Red when sound is off
        icon_color = (255, 255, 255) 
        symbol = "🔇"  # Muted symbol when sound is off
    
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

def draw_tooltip(screen, text, mouse_pos, w, h):
    font = pygame.font.SysFont('Consolas', int(h*0.018))
    surf = font.render(text, True, (230,255,200))
    tw, th = surf.get_size()
    px, py = mouse_pos
    # Prevent tooltip going off screen
    if px+tw > w: px = w-tw-10
    if py+th > h: py = h-th-10
    pygame.draw.rect(screen, (40, 40, 80), (px, py, tw+12, th+12), border_radius=6)
    screen.blit(surf, (px+6, py+6))

def draw_scoreboard(screen, game_state, w, h, seed):
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

def draw_seed_prompt(screen, current_input, weekly_suggestion):
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


def draw_opponents_panel(screen, game_state, w, h, font, small_font):
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


def draw_deferred_events_zone(screen, game_state, w, h, small_font):
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
        event_text = f"• {event.name} ({turns_left}T)"
        text_surface = small_font.render(event_text, True, (180, 180, 180))
        
        # Truncate if too long
        if text_surface.get_width() > zone_width - 10:
            truncated = f"• {event.name[:15]}... ({turns_left}T)"
            text_surface = small_font.render(truncated, True, (180, 180, 180))
        
        screen.blit(text_surface, (zone_x + 5, y_pos))
    
    # Show count if more events exist
    if len(deferred_events) > 4:
        more_text = small_font.render(f"...and {len(deferred_events) - 4} more", True, (150, 150, 150))
        screen.blit(more_text, (zone_x + 5, zone_y + zone_height - 20))


def draw_popup_events(screen, game_state, w, h, font, big_font):
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


def draw_ui_transitions(screen, game_state, w, h, big_font):
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


def draw_upgrade_transition(screen, transition, game_state, w, h, big_font):
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



def draw_end_game_menu(screen, w, h, selected_item, game_state, seed):
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
    
    # Game statistics in a box - adjust position to make room for scenario details
    stats_box_y = int(h*0.25) if game_state.end_game_scenario else int(h*0.22)
    stats_box = pygame.Rect(w//6, stats_box_y, w*2//3, int(h*0.22))
    pygame.draw.rect(screen, (40, 40, 70), stats_box, border_radius=12)
    pygame.draw.rect(screen, (130, 190, 255), stats_box, width=3, border_radius=12)
    
    # Statistics content
    stats_lines = [
        f"Survived until Turn: {game_state.turn}",
        f"Final Staff: {game_state.staff}",
        f"Final Money: ${game_state.money}",
        f"Final Reputation: {game_state.reputation}",
        f"Final p(Doom): {game_state.doom}%",
        f"Seed: {seed}",
        f"High Score (turns): {game_state.highscore}"
    ]
    
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
    
    # Menu options
    menu_items = ["Relaunch Game", "Main Menu", "Settings", "Submit Feedback", "Submit Bug Request"]
    
    button_width = int(w * 0.35)
    button_height = int(h * 0.06)
    start_y = int(h * 0.55)
    spacing = int(h * 0.08)
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

def draw_tutorial_overlay(screen, tutorial_message, w, h):
    """
    Draw a tutorial overlay with message content and dismiss button.
    
    Args:
        screen: pygame surface to draw on
        tutorial_message: dict with 'title' and 'content' keys
        w, h: screen width and height
        
    Returns:
        Rect of the dismiss button for click detection
    """
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
    title = tutorial_message["title"]
    title_surface = title_font.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect(centerx=dialog_rect.centerx, y=dialog_y + 20)
    screen.blit(title_surface, title_rect)
    
    # Content area
    content = tutorial_message["content"]
    content_y = title_rect.bottom + 30
    content_width = dialog_width - 40
    content_height = dialog_height - 120  # Leave space for title and button
    
    # Wrap and render content text
    wrapped_lines = wrap_text(content, content_font, content_width)
    line_height = content_font.get_height() + 5
    
    for i, line in enumerate(wrapped_lines):
        line_y = content_y + i * line_height
        if line_y + line_height > content_y + content_height:
            # Add "..." if content is too long
            if i < len(wrapped_lines) - 1:
                ellipsis = content_font.render("...", True, (200, 200, 200))
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
    
    button_text = button_font.render("Got it!", True, (255, 255, 255))
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)
    
    # Footer text
    footer_text = pygame.font.Font(None, int(h * 0.02)).render(
        "Click 'Got it!' or press Enter to dismiss", True, (150, 150, 150)
    )
    footer_rect = footer_text.get_rect(centerx=dialog_rect.centerx, y=button_rect.bottom + 10)
    screen.blit(footer_text, footer_rect)
    
    return button_rect


def draw_hiring_dialog(screen, hiring_dialog, w, h):
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
        cost_text = f"${subtype_data['cost']} • {subtype_data['ap_cost']} AP"
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
    
    # Cancel/Dismiss button
    button_width = 120
    button_height = 40
    button_x = dialog_rect.centerx - button_width // 2
    button_y = dialog_rect.bottom - 60
    cancel_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    pygame.draw.rect(screen, (100, 60, 60), cancel_rect, border_radius=5)
    pygame.draw.rect(screen, (160, 100, 100), cancel_rect, width=2, border_radius=5)
    
    cancel_text = button_font.render("Cancel", True, (255, 255, 255))
    text_rect = cancel_text.get_rect(center=cancel_rect.center)
    screen.blit(cancel_text, text_rect)
    
    clickable_rects.append({
        'rect': cancel_rect,
        'type': 'cancel'
    })
    
    # Instructions
    instructions = "Click an employee to hire, or Cancel to dismiss"
    inst_surface = pygame.font.Font(None, int(h * 0.02)).render(instructions, True, (150, 150, 150))
    inst_rect = inst_surface.get_rect(centerx=dialog_rect.centerx, y=cancel_rect.bottom + 5)
    screen.blit(inst_surface, inst_rect)
    
    return clickable_rects


def draw_stepwise_tutorial_overlay(screen, tutorial_data, w, h):
    """
    Draw the stepwise tutorial overlay for onboarding new players.
    
    Args:
        screen: pygame surface to draw on
        tutorial_data: dict containing tutorial step data with navigation info
        w, h: screen width and height
    
    Returns:
        dict with button rectangles for click detection
    """
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
    progress_text = f"Step {step_number} of {total_steps}"
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
    content_lines = content.split('\n')
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
        
        back_text = button_font.render("Back", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        screen.blit(back_text, back_text_rect)
        buttons['back'] = back_button_rect
    
    # Skip button (always available)
    skip_button_x = box_x + box_width // 2 - button_min_width // 2
    skip_button_rect = pygame.Rect(skip_button_x, button_y, button_min_width, button_height)
    pygame.draw.rect(screen, (180, 100, 100), skip_button_rect, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), skip_button_rect, width=2, border_radius=8)
    
    skip_text = button_font.render("Skip", True, (255, 255, 255))
    skip_text_rect = skip_text.get_rect(center=skip_button_rect.center)
    screen.blit(skip_text, skip_text_rect)
    buttons['skip'] = skip_button_rect
    
    # Next/Finish button
    can_go_forward = tutorial_data.get('can_go_forward', True)
    is_final_step = step_number >= total_steps
    
    next_button_x = box_x + box_width - button_min_width - 30
    next_button_rect = pygame.Rect(next_button_x, button_y, button_min_width, button_height)
    pygame.draw.rect(screen, (100, 200, 100), next_button_rect, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), next_button_rect, width=2, border_radius=8)
    
    next_label = "Finish" if is_final_step else "Next"
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


def draw_first_time_help(screen, help_content, w, h):
    """
    Draw a small help popup for first-time mechanics.
    
    Args:
        screen: pygame surface to draw on
        help_content: dict with title and content for the help popup
        w, h: screen width and height
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
    
    # Close button (X)
    close_button_size = 20
    close_button_x = popup_x + popup_width - close_button_size - 5
    close_button_y = popup_y + 5
    close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)
    pygame.draw.rect(screen, (200, 100, 100), close_button_rect, border_radius=3)
    
    close_font = pygame.font.SysFont('Consolas', int(h*0.02), bold=True)
    close_text = close_font.render("×", True, (255, 255, 255))
    close_text_rect = close_text.get_rect(center=close_button_rect.center)
    screen.blit(close_text, close_text_rect)
    
    return close_button_rect

def draw_pre_game_settings(screen, w, h, settings, selected_item, sound_manager=None):
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
    menu_font = pygame.font.SysFont('Consolas', int(h*0.028))
    
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
    
    # Enhanced settings with realistic options
    settings_options = [
        ("Research Intensity", get_research_intensity_display(settings.get("difficulty", "STANDARD"))),
        ("Audio Alerts Volume", get_volume_display(settings.get("sound_volume", 80))),
        ("Visual Enhancement", get_graphics_display(settings.get("graphics_quality", "STANDARD"))),
        ("Safety Protocol Level", get_safety_display(settings.get("safety_level", "STANDARD"))),
        ("Continue", "▶ INITIALIZE LABORATORY")
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
        if i < len(settings_options) - 1:  # Setting items with values
            text = f"{setting_name}: {setting_value}"
        else:  # Continue button with special styling
            text = setting_value
        
        # Draw enhanced button
        if i == len(settings_options) - 1:  # Continue button gets special treatment
            draw_enhanced_continue_button(screen, button_rect, text, button_state)
        else:
            draw_bureaucratic_setting_button(screen, button_rect, text, button_state, setting_name)
    
    # Enhanced instructions with bureaucratic theme
    inst_font = pygame.font.SysFont('Consolas', int(h*0.022))
    instructions = [
        "📋 Use ↑↓ arrow keys to navigate configuration options",
        "🔧 Press ENTER to modify settings or initialize laboratory",
        "⚠️  Ensure all parameters meet institutional safety standards"
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


def get_research_intensity_display(difficulty):
    """Convert difficulty setting to bureaucratic terminology."""
    mapping = {
        "EASY": "CONSERVATIVE",
        "STANDARD": "REGULATORY",
        "HARD": "AGGRESSIVE",
        "DUMMY": "REGULATORY"
    }
    return mapping.get(difficulty, "REGULATORY")


def get_volume_display(volume):
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


def get_graphics_display(quality):
    """Convert graphics quality to bureaucratic terms."""
    mapping = {
        "LOW": "EFFICIENT", 
        "STANDARD": "COMPLIANT",
        "HIGH": "ENHANCED",
        "DUMMY": "COMPLIANT"
    }
    return mapping.get(quality, "COMPLIANT")


def get_safety_display(safety_level):
    """Safety protocol levels for the bureaucratic theme."""
    mapping = {
        "MINIMAL": "MINIMAL",
        "STANDARD": "STANDARD", 
        "ENHANCED": "ENHANCED",
        "MAXIMUM": "MAXIMUM",
        "DUMMY": "STANDARD"
    }
    return mapping.get(safety_level, "STANDARD")


def draw_enhanced_continue_button(screen, rect, text, button_state):
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


def draw_bureaucratic_setting_button(screen, rect, text, button_state, setting_name):
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


def draw_seed_selection(screen, w, h, selected_item, seed_input="", sound_manager=None):
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
    menu_font = pygame.font.SysFont('Consolas', int(h*0.03))
    
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


def draw_tutorial_choice(screen, w, h, selected_item):
    """
    Draw the tutorial choice screen.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected item (0=Yes, 1=No)
    """
    # Clear background
    screen.fill((50, 50, 50))
    
    # Fonts
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    menu_font = pygame.font.SysFont('Consolas', int(h*0.03))
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
    
    # Tutorial options
    tutorial_items = ["Yes - Enable Tutorial", "No - Regular Mode"]
    
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
        "Use arrow keys to navigate, Enter to start game",
        "Tutorial mode provides helpful guidance for new players"
    ]
    
    inst_y = int(h * 0.8)
    for instruction in instructions:
        inst_surf = inst_font.render(instruction, True, (180, 180, 180))
        inst_x = w // 2 - inst_surf.get_width() // 2
        screen.blit(inst_surf, (inst_x, inst_y))
        inst_y += inst_surf.get_height() + 5
