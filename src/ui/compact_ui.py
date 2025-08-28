"""
Compact UI mode for P(Doom) - Starcraft 2 inspired interface.

Provides icon-based compact buttons with shortcut key indicators to maximize
screen real estate when tutorial mode is disabled.
"""

import pygame
from src.features.visual_feedback import visual_feedback, ButtonState, FeedbackStyle
from src.services.keybinding_manager import keybinding_manager


def get_action_icon(action_name: str, action_index: int) -> str:
    """
    Get placeholder icon character for an action.
    
    These are temporary placeholders that can be replaced with actual icons later.
    
    Args:
        action_name: Name of the action
        action_index: Index of the action (0-based)
        
    Returns:
        str: Single character icon
    """
    # Map common action names to icon characters
    icon_mapping = {
        # Research actions
        "hire_researcher": "👨‍🔬",
        "conduct_research": "📊", 
        "publish_paper": "📄",
        "research": "🔬",
        
        # Business actions
        "hire_staff": "👥",
        "marketing": "📢",
        "fundraising": "💰",
        "hire": "➕",
        "marketing_campaign": "📈",
        
        # Infrastructure
        "buy_computer": "💻",
        "upgrade_equipment": "⚡",
        "rent_office": "🏢",
        "infrastructure": "🏗️",
        
        # Intelligence/Security
        "espionage": "🕵️",
        "scout": "👁️",
        "security": "🛡️",
        "counter_intelligence": "🔒",
        
        # Training/Development
        "training": "📚",
        "workshop": "🔧",
        "seminar": "🎓",
        "development": "📈",
        
        # Special actions
        "lobby": "🏛️",
        "pr_campaign": "📺",
        "patent": "📜",
        "acquisition": "🤝",
    }
    
    # Try to find icon by name (case insensitive partial matching)
    action_lower = action_name.lower()
    for key, icon in icon_mapping.items():
        if key in action_lower:
            return icon
    
    # Fallback to letter based on index or first letter
    if action_index < 26:
        return chr(ord('A') + action_index)
    else:
        return action_name[0].upper() if action_name else "?"


def get_upgrade_icon(upgrade_name: str, upgrade_index: int) -> str:
    """
    Get placeholder icon character for an upgrade.
    
    Args:
        upgrade_name: Name of the upgrade
        upgrade_index: Index of the upgrade (0-based)
        
    Returns:
        str: Single character icon
    """
    # Map upgrades to icons
    icon_mapping = {
        "accounting": "📊",
        "software": "💾",
        "hardware": "🖥️",
        "networking": "🌐",
        "security": "🔒",
        "automation": "🤖",
        "ai": "🧠",
        "quantum": "⚛️",
        "cloud": "☁️",
        "database": "💿",
        "office": "🏢",
        "equipment": "⚡",
        "laboratory": "🔬",
        "supercomputer": "🖥️",
        "scanner": "📡",
        "server": "🗄️",
    }
    
    upgrade_lower = upgrade_name.lower()
    for key, icon in icon_mapping.items():
        if key in upgrade_lower:
            return icon
    
    # Fallback to first letter
    return upgrade_name[0].upper() if upgrade_name else "⚙️"


def draw_compact_action_button(screen, rect, action, action_index, button_state, shortcut_key=None):
    """
    Draw a compact action button with icon and shortcut key indicator.
    
    Args:
        screen: pygame surface to draw on
        rect: pygame.Rect for button area
        action: action dictionary with name, desc, cost, etc.
        action_index: 0-based index of the action
        button_state: ButtonState (NORMAL, HOVER, PRESSED, DISABLED)
        shortcut_key: optional override for shortcut key display
    """
    # Get shortcut key display
    if shortcut_key is None:
        shortcut_key = keybinding_manager.get_action_display_key(f"action_{action_index + 1}")
    
    # Draw base button using visual feedback system
    visual_feedback.draw_button(screen, rect, "", button_state, FeedbackStyle.BUTTON)
    
    # Get action icon
    icon = get_action_icon(action["name"], action_index)
    
    # Draw icon in center of button
    icon_font = pygame.font.SysFont('Consolas', int(min(rect.width, rect.height) * 0.4), bold=True)
    icon_surface = icon_font.render(icon, True, (255, 255, 255))
    icon_x = rect.centerx - icon_surface.get_width() // 2
    icon_y = rect.centery - icon_surface.get_height() // 2
    screen.blit(icon_surface, (icon_x, icon_y))
    
    # Draw shortcut key in top-right corner
    key_font = pygame.font.SysFont('Consolas', int(min(rect.width, rect.height) * 0.2), bold=True)
    key_surface = key_font.render(shortcut_key, True, (255, 255, 100))
    key_x = rect.right - key_surface.get_width() - 2
    key_y = rect.top + 2
    
    # Draw small background for key
    key_bg_rect = pygame.Rect(key_x - 1, key_y, key_surface.get_width() + 2, key_surface.get_height())
    pygame.draw.rect(screen, (40, 40, 40), key_bg_rect, border_radius=2)
    pygame.draw.rect(screen, (100, 100, 100), key_bg_rect, width=1, border_radius=2)
    
    screen.blit(key_surface, (key_x, key_y))


def draw_compact_upgrade_button(screen, rect, upgrade, upgrade_index, button_state, is_purchased=False):
    """
    Draw a compact upgrade button with icon.
    
    Args:
        screen: pygame surface to draw on
        rect: pygame.Rect for button area
        upgrade: upgrade dictionary with name, desc, cost, etc.
        upgrade_index: 0-based index of the upgrade
        button_state: ButtonState (NORMAL, HOVER, PRESSED, DISABLED)
        is_purchased: whether the upgrade is already purchased
    """
    if is_purchased:
        # Draw as small icon for purchased upgrades
        visual_feedback.draw_icon_button(screen, rect, "", ButtonState.NORMAL)
        
        # Get upgrade icon
        icon = get_upgrade_icon(upgrade["name"], upgrade_index)
        
        # Draw icon slightly smaller for purchased items
        icon_font = pygame.font.SysFont('Consolas', int(min(rect.width, rect.height) * 0.6), bold=True)
        icon_surface = icon_font.render(icon, True, (100, 255, 100))  # Green tint for purchased
        icon_x = rect.centerx - icon_surface.get_width() // 2
        icon_y = rect.centery - icon_surface.get_height() // 2
        screen.blit(icon_surface, (icon_x, icon_y))
    else:
        # Draw base button
        visual_feedback.draw_button(screen, rect, "", button_state, FeedbackStyle.BUTTON)
        
        # Get upgrade icon
        icon = get_upgrade_icon(upgrade["name"], upgrade_index)
        
        # Draw icon
        icon_font = pygame.font.SysFont('Consolas', int(min(rect.width, rect.height) * 0.4), bold=True)
        icon_color = (255, 255, 255) if button_state != ButtonState.DISABLED else (120, 120, 120)
        icon_surface = icon_font.render(icon, True, icon_color)
        icon_x = rect.centerx - icon_surface.get_width() // 2
        icon_y = rect.centery - icon_surface.get_height() // 2
        screen.blit(icon_surface, (icon_x, icon_y))
        
        # Draw cost in bottom-right corner for available upgrades
        cost_font = pygame.font.SysFont('Consolas', int(min(rect.width, rect.height) * 0.15), bold=True)
        cost_text = f"${upgrade['cost']}"
        cost_surface = cost_font.render(cost_text, True, (255, 255, 100))
        cost_x = rect.right - cost_surface.get_width() - 1
        cost_y = rect.bottom - cost_surface.get_height() - 1
        
        # Draw small background for cost
        cost_bg_rect = pygame.Rect(cost_x - 1, cost_y, cost_surface.get_width() + 1, cost_surface.get_height())
        pygame.draw.rect(screen, (40, 40, 40), cost_bg_rect, border_radius=2)
        pygame.draw.rect(screen, (100, 100, 100), cost_bg_rect, width=1, border_radius=2)
        
        screen.blit(cost_surface, (cost_x, cost_y))


def get_compact_action_rects(w, h, num_actions=9):
    """
    Get rectangles for compact action buttons arranged in a grid.
    
    Args:
        w, h: screen width and height
        num_actions: number of action buttons to arrange
        
    Returns:
        List of pygame.Rect for action button positions
    """
    # Make buttons smaller and arrange in a grid
    button_size = int(min(w, h) * 0.06)  # Smaller than original buttons
    start_x = int(w * 0.02)
    start_y = int(h * 0.2)
    
    # Arrange in 3x3 grid
    rects = []
    for i in range(min(num_actions, 9)):
        row = i // 3
        col = i % 3
        x = start_x + col * (button_size + 4)
        y = start_y + row * (button_size + 4)
        rects.append(pygame.Rect(x, y, button_size, button_size))
    
    return rects


def get_compact_upgrade_rects(w, h, num_upgrades, num_purchased=0):
    """
    Get rectangles for compact upgrade buttons.
    
    Purchased upgrades are shown as small icons at the top right.
    Available upgrades are shown as larger buttons on the right side.
    
    Args:
        w, h: screen width and height
        num_upgrades: total number of upgrades
        num_purchased: number of purchased upgrades (shown as icons)
        
    Returns:
        List of pygame.Rect for upgrade button positions
    """
    rects = []
    
    # Purchased upgrades as small icons in top right
    if num_purchased > 0:
        icon_size = int(min(w, h) * 0.03)
        start_x = w - int(w * 0.02) - icon_size
        start_y = int(h * 0.03)
        
        # Arrange purchased upgrades in rows from right to left
        for i in range(num_purchased):
            col = i % 10  # Max 10 per row
            row = i // 10
            x = start_x - col * (icon_size + 2)
            y = start_y + row * (icon_size + 2)
            rects.append(pygame.Rect(x, y, icon_size, icon_size))
    
    # Available upgrades as buttons on right side
    if num_upgrades > num_purchased:
        button_size = int(min(w, h) * 0.05)
        start_x = w - int(w * 0.08)
        start_y = int(h * 0.2)
        
        for i in range(num_purchased, num_upgrades):
            idx = i - num_purchased
            y = start_y + idx * (button_size + 4)
            rects.append(pygame.Rect(start_x, y, button_size, button_size))
    
    return rects


def should_use_compact_ui(game_state) -> bool:
    """
    Determine if compact UI mode should be used.
    
    Args:
        game_state: current game state
        
    Returns:
        bool: True if compact mode should be used
    """
    # Use compact mode when tutorial is disabled
    return not getattr(game_state, 'tutorial_enabled', True)


def draw_compact_end_turn_button(screen, w, h, button_state):
    """
    Draw compact end turn button with shortcut key indicator.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen dimensions
        button_state: ButtonState for the button
    """
    # Position in bottom center, but smaller
    button_width = int(w * 0.12)
    button_height = int(h * 0.04)
    button_x = w // 2 - button_width // 2
    button_y = h - button_height - int(h * 0.02)
    
    rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Get shortcut key
    shortcut_key = keybinding_manager.get_action_display_key("end_turn")
    
    # Draw base button
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
        screen, rect, "", button_state, 
        FeedbackStyle.BUTTON, custom_colors.get(button_state)
    )
    
    # Draw "END" text in center
    font = pygame.font.SysFont('Consolas', int(button_height * 0.4), bold=True)
    text_surface = font.render("END", True, (255, 240, 240))
    text_x = rect.centerx - text_surface.get_width() // 2
    text_y = rect.centery - text_surface.get_height() // 2
    screen.blit(text_surface, (text_x, text_y))
    
    # Draw shortcut key in corner
    key_font = pygame.font.SysFont('Consolas', int(button_height * 0.25), bold=True)
    key_surface = key_font.render(shortcut_key, True, (255, 255, 100))
    key_x = rect.right - key_surface.get_width() - 2
    key_y = rect.top + 2
    
    # Draw small background for key
    key_bg_rect = pygame.Rect(key_x - 1, key_y, key_surface.get_width() + 2, key_surface.get_height())
    pygame.draw.rect(screen, (40, 40, 40), key_bg_rect, border_radius=2)
    pygame.draw.rect(screen, (100, 100, 100), key_bg_rect, width=1, border_radius=2)
    
    screen.blit(key_surface, (key_x, key_y))
    
    return rect  # Return rect for click detection