"""
Overlay and Window System Module

This module provides overlay and window drawing functionality for the P(Doom) UI system.
Extracted from the main ui.py monolith as part of the Phase 3 refactoring effort.

Functions:
- draw_overlay: Full-screen overlays with scrolling content
- draw_window_with_header: Windowed dialogs with minimize functionality
- draw_loading_screen: Loading screen with progress indication
- render_text: Text rendering with word wrapping support
- wrap_text: Text wrapping utility function
- get_ui_safe_zones: UI collision avoidance system
- find_safe_overlay_position: Smart overlay positioning
- should_show_back_button: Navigation depth helper
- draw_back_button: Back navigation button
"""

import pygame
from typing import Dict, Any, Optional, List, Tuple


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
    safe_zones: List[pygame.Rect] = []
    
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
    
    positions_to_try: List[Tuple[int, int]] = []
    
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
    lines: List[str] = []
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
        title = "Information Unavailable"
    if content is None:
        content = "Content Not Available\n\nThe requested information could not be loaded at this time.\n\nPossible solutions:\n• Press Escape or Back to return to the previous screen\n• Try accessing this information again from the main menu\n• Check the Player Guide (F1) for general help\n\nIf this problem persists, it may indicate a technical issue."
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
