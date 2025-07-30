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

def draw_ui(screen, game_state, w, h):
    # ... [existing code above] ...

    # Example: rendering an upgrade description with wrapping instead of direct render
    # We'll assume this pattern is repeated for upgrades and actions wherever description text is rendered

    # For upgrades
    upgrade_rects = game_state._get_upgrade_rects(w, h)
    for idx, rect in enumerate(upgrade_rects):
        upg = game_state.upgrades[idx]
        desc = upg["desc"] + f" (Cost: ${upg['cost']})"
        # Let's wrap descriptions to button width minus some padding
        desc_lines = wrap_text(desc, small_font, rect[2] - int(w*0.02))
        for i, line in enumerate(desc_lines):
            screen.blit(small_font.render(line, True, (200, 255, 200)), (rect[0] + int(w*0.01), rect[1] + int(h*0.04) + i * small_font.get_height()))
        # [rest of your drawing code for upgrades here...]

    # For actions (similar logic)
    action_rects = game_state._get_action_rects(w, h)
    for idx, rect in enumerate(action_rects):
        act = game_state.actions[idx]
        desc = act["desc"] + f" (Cost: ${act['cost']})"
        desc_lines = wrap_text(desc, font, rect[2] - int(w*0.02))
        for i, line in enumerate(desc_lines):
            screen.blit(font.render(line, True, (190, 210, 255)), (rect[0] + int(w*0.01), rect[1] + int(h*0.04) + i * font.get_height()))
        # [rest of your drawing code for actions here...]

    # Additional: wrap message log if desired (could be done similarly).

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

    # ... [rest of your draw_ui as before] ...