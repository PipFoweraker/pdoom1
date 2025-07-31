import pygame
import textwrap

def wrap_text(text, font, max_width):
    """
    Splits the text into multiple lines so that each line fits within max_width.
    Returns a list of strings, each representing a line.
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
    if curr_line:
        lines.append(curr_line)
    return lines

def render_text(text, font, max_width=None, color=(255,255,255)):
    """Render text with optional word wrapping. Returns [(surface, (x_offset, y_offset)), ...], bounding rect."""
    lines = [text]
    if max_width:
        lines = wrap_text(text, font, max_width)
    surfaces = [font.render(line, True, color) for line in lines]
    widths = [surf.get_width() for surf in surfaces]
    heights = [surf.get_height() for surf in surfaces]
    total_width = max(widths)
    total_height = sum(heights)
    offsets = [(0, sum(heights[:i])) for i in range(len(heights))]
    return list(zip(surfaces, offsets)), pygame.Rect(0, 0, total_width, total_height)

def draw_main_menu(screen, w, h, selected_item):
    """
    Draw the main menu with vertically stacked, center-oriented buttons.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected menu item (for keyboard navigation)
    
    Features:
    - Grey background as specified in requirements
    - Centered title and subtitle
    - 5 vertically stacked buttons with distinct visual states:
      * Normal: dark blue with light border
      * Selected: bright blue with white border (keyboard navigation)
      * Inactive: grey (Options button is placeholder)
    - Responsive sizing based on screen dimensions
    - Clear usage instructions at bottom
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
        
        # Determine button colors
        if i == 2:  # Options - greyed out/inactive
            bg_color = (80, 80, 80)
            border_color = (120, 120, 120)
            text_color = (150, 150, 150)
        elif i == selected_item:  # Selected item
            bg_color = (100, 150, 200)
            border_color = (150, 200, 255)
            text_color = (255, 255, 255)
        else:  # Normal items
            bg_color = (60, 60, 120)
            border_color = (100, 100, 180)
            text_color = (220, 220, 255)
        
        # Draw button
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(screen, bg_color, button_rect, border_radius=12)
        pygame.draw.rect(screen, border_color, button_rect, width=3, border_radius=12)
        
        # Draw button text
        text_surf = menu_font.render(item, True, text_color)
        text_x = button_x + (button_width - text_surf.get_width()) // 2
        text_y = button_y + (button_height - text_surf.get_height()) // 2
        screen.blit(text_surf, (text_x, text_y))
    
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

def draw_overlay(screen, title, content, scroll_offset, w, h):
    """
    Draw a scrollable overlay for displaying README or Player Guide content.
    
    Args:
        screen: pygame surface to draw on
        title: string title to display at top of overlay
        content: full text content to display (markdown rendered as plain text)
        scroll_offset: vertical scroll position in pixels
        w, h: screen width and height for responsive layout
    
    Features:
    - Semi-transparent dark background overlay
    - Centered content area with border
    - Scrollable text with line wrapping
    - Scroll indicators (up/down arrows) when content exceeds view area  
    - Responsive text sizing based on screen dimensions
    - Clear navigation instructions
    
    The overlay handles long documents by breaking them into lines and showing
    only the visible portion based on scroll_offset. Users can scroll with
    arrow keys to view the full document.
    """
    # Overlay background - semi-transparent dark background
    overlay_surface = pygame.Surface((w, h))
    overlay_surface.set_alpha(240)
    overlay_surface.fill((20, 20, 30))
    screen.blit(overlay_surface, (0, 0))
    
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
    
def draw_ui(screen, game_state, w, h):
    # Fonts, scaled by screen size
    title_font = pygame.font.SysFont('Consolas', int(h*0.045), bold=True)
    big_font = pygame.font.SysFont('Consolas', int(h*0.033))
    font = pygame.font.SysFont('Consolas', int(h*0.025))
    small_font = pygame.font.SysFont('Consolas', int(h*0.018))

    # Title
    title = title_font.render("P(Doom): Bureaucracy Strategy", True, (205, 255, 220))
    screen.blit(title, (int(w*0.04), int(h*0.03)))

    # Resources (top bar)
    screen.blit(big_font.render(f"Money: ${game_state.money}", True, (255, 230, 60)), (int(w*0.04), int(h*0.11)))
    screen.blit(big_font.render(f"Staff: {game_state.staff}", True, (255, 210, 180)), (int(w*0.21), int(h*0.11)))
    screen.blit(big_font.render(f"Reputation: {game_state.reputation}", True, (180, 210, 255)), (int(w*0.35), int(h*0.11)))
    screen.blit(big_font.render(f"p(Doom): {game_state.doom}/{game_state.max_doom}", True, (255, 80, 80)), (int(w*0.52), int(h*0.11)))
    screen.blit(font.render(f"Opponent progress: {game_state.known_opp_progress if game_state.known_opp_progress is not None else '???'}/100", True, (240, 200, 160)), (int(w*0.74), int(h*0.11)))
    screen.blit(small_font.render(f"Turn: {game_state.turn}", True, (220, 220, 220)), (int(w*0.91), int(h*0.03)))
    screen.blit(small_font.render(f"Seed: {game_state.seed}", True, (140, 200, 160)), (int(w*0.77), int(h*0.03)))

    # Doom bar
    doom_bar_x, doom_bar_y = int(w*0.52), int(h*0.16)
    doom_bar_width, doom_bar_height = int(w*0.38), int(h*0.025)
    pygame.draw.rect(screen, (70, 50, 50), (doom_bar_x, doom_bar_y, doom_bar_width, doom_bar_height))
    filled = int(doom_bar_width * (game_state.doom / game_state.max_doom))
    pygame.draw.rect(screen, (255, 60, 60), (doom_bar_x, doom_bar_y, filled, doom_bar_height))

    # Action buttons (left)
    action_rects = game_state._get_action_rects(w, h)
    for idx, rect in enumerate(action_rects):
        color = (60, 60, 130) if idx not in game_state.selected_actions else (110, 110, 200)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, (130, 130, 220), rect, width=3, border_radius=10)
        act_text = big_font.render(game_state.actions[idx]["name"], True, (220, 220, 255))
        desc_text = font.render(game_state.actions[idx]["desc"] + f" (Cost: ${game_state.actions[idx]['cost']})", True, (190, 210, 255))
        screen.blit(act_text, (rect[0] + int(w*0.01), rect[1] + int(h*0.01)))
        screen.blit(desc_text, (rect[0] + int(w*0.01), rect[1] + int(h*0.04)))

    # Upgrades (right: purchased as icons at top right, available as buttons)
    upgrade_rects = game_state._get_upgrade_rects(w, h)
    for idx, rect in enumerate(upgrade_rects):
        upg = game_state.upgrades[idx]
        if upg.get("purchased", False):
            # Draw as small icon
            pygame.draw.rect(screen, (90, 170, 90), rect, border_radius=6)
            pygame.draw.rect(screen, (140, 210, 140), rect, width=2, border_radius=6)
            upg_letter = big_font.render(upg["name"][0], True, (255, 255, 255))
            screen.blit(upg_letter, (rect[0]+rect[2]//4, rect[1]+rect[3]//6))
        else:
            # Draw as button
            pygame.draw.rect(screen, (40, 90, 40), rect, border_radius=9)
            pygame.draw.rect(screen, (100, 190, 100), rect, width=2, border_radius=9)
            name = big_font.render(upg["name"], True, (220, 255, 180))
            desc = small_font.render(upg["desc"] + f" (Cost: ${upg['cost']})", True, (200, 255, 200))
            status = small_font.render("PURCHASED" if upg["purchased"] else "AVAILABLE", True, (190, 255, 190) if not upg["purchased"] else (210, 210, 210))
            screen.blit(name, (rect[0] + int(w*0.01), rect[1] + int(h*0.01)))
            screen.blit(desc, (rect[0] + int(w*0.01), rect[1] + int(h*0.04)))
            screen.blit(status, (rect[0] + int(w*0.24), rect[1] + int(h*0.04)))

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


    # End Turn button (bottom center)
    endturn_rect = game_state._get_endturn_rect(w, h)
    pygame.draw.rect(screen, (140, 90, 90), endturn_rect, border_radius=12)
    pygame.draw.rect(screen, (210, 110, 110), endturn_rect, width=4, border_radius=12)
    et_text = big_font.render("END TURN (Space)", True, (255, 240, 240))
    screen.blit(et_text, (endturn_rect[0] + int(w*0.01), endturn_rect[1] + int(h*0.015)))

    # Messages log (bottom left) - Enhanced with scrollable history
    log_x, log_y = int(w*0.04), int(h*0.74)
    
    if game_state.scrollable_event_log_enabled:
        # Enhanced scrollable event log with border and visual indicators
        log_width = int(w * 0.44)
        log_height = int(h * 0.22)
        
        # Draw border around the event log area
        border_rect = pygame.Rect(log_x - 5, log_y - 5, log_width + 10, log_height + 10)
        pygame.draw.rect(screen, (80, 100, 120), border_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 140, 180), border_rect, width=2, border_radius=8)
        
        # Event log title with scroll indicator
        title_text = font.render("Activity Log (Scrollable)", True, (255, 255, 180))
        screen.blit(title_text, (log_x, log_y))
        
        # Scroll indicator
        if len(game_state.event_log_history) > 0 or len(game_state.messages) > 0:
            scroll_info = small_font.render("↑↓ or mouse wheel to scroll", True, (200, 200, 255))
            screen.blit(scroll_info, (log_x + log_width - scroll_info.get_width(), log_y))
        
        # Calculate visible area for messages
        content_y = log_y + int(h * 0.04)
        content_height = log_height - int(h * 0.05)
        line_height = int(h * 0.025)
        max_visible_lines = content_height // line_height
        
        # Combine history and current messages for display
        all_messages = list(game_state.event_log_history) + game_state.messages
        
        # Calculate scrolling
        total_lines = len(all_messages)
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
    screen.blit(title.render("P(Doom)", True, (240,255,220)), (w//2-180, h//6))
    screen.blit(font.render("Enter Seed (for weekly challenge, or blank for default):", True, (210,210,255)), (w//6, h//3))
    box = pygame.Rect(w//4, h//2, w//2, 60)
    pygame.draw.rect(screen, (60,60,110), box, border_radius=8)
    pygame.draw.rect(screen, (130,130,210), box, width=3, border_radius=8)
    txt = font.render(current_input, True, (255,255,255))
    screen.blit(txt, (box.x+10, box.y+10))
    screen.blit(small.render(f"Suggested weekly seed: {weekly_suggestion}", True, (200,255,200)), (w//3, h//2 + 80))
    screen.blit(small.render("Press [Enter] to start, [Esc] to quit.", True, (255,255,180)), (w//3, h//2 + 120))
    # Example: rendering an upgrade description with wrapping instead of direct render
    # We'll assume this pattern is repeated for upgrades and actions wherever description text is rendered

  
    # Additional: wrap message log if desired (could be done similarly).

    
