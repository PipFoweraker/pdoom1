"""
UI components for keybinding configuration menu.
"""

# Try to import pygame, fallback to dummy values for CI/testing environments
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    # Define dummy pygame for testing environments
    class DummyPygame:
        class Rect:
            def __init__(self, x, y, w, h):
                self.x, self.y, self.width, self.height = x, y, w, h
                self.centerx = x + w // 2
                self.centery = y + h // 2
                self.right = x + w
                self.bottom = y + h
                self.top = y
                self.left = x
            def collidepoint(self, pos): return False
        
        class Surface:
            def get_width(self): return 50
            def get_height(self): return 20
            def set_alpha(self, alpha): pass
            def fill(self, color): pass
        
        class font:
            @staticmethod
            def SysFont(name, size, bold=False):
                class DummyFont:
                    def render(self, text, antialias, color):
                        return DummyPygame.Surface()
                return DummyFont()
        
        class draw:
            @staticmethod
            def rect(*args, **kwargs): pass
    
    pygame = DummyPygame()

try:
    from src.features.visual_feedback import visual_feedback, ButtonState, FeedbackStyle
    VISUAL_FEEDBACK_AVAILABLE = True
except ImportError:
    VISUAL_FEEDBACK_AVAILABLE = False
    # Define dummy classes for testing
    class ButtonState:
        NORMAL = 0
        HOVER = 1
        PRESSED = 2
        DISABLED = 3
        FOCUSED = 4
    
    class FeedbackStyle:
        BUTTON = 0
    
    class DummyVisualFeedback:
        def draw_button(self, *args, **kwargs): pass
    
    visual_feedback = DummyVisualFeedback()

try:
    from src.services.keybinding_manager import keybinding_manager
    KEYBINDING_AVAILABLE = True
except ImportError:
    KEYBINDING_AVAILABLE = False
    # Define dummy keybinding manager for testing
    class DummyKeybindingManager:
        def get_action_display_key(self, action): return "1"
    
    keybinding_manager = DummyKeybindingManager()


def draw_keybinding_menu(screen, w, h, selected_item):
    """
    Draw the keybinding configuration menu.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height
        selected_item: currently selected menu item index
    """
    # Clear screen with dark background
    screen.fill((20, 25, 35))
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h*0.06), bold=True)
    title = title_font.render("Keybinding Configuration", True, (205, 255, 220))
    title_x = w // 2 - title.get_width() // 2
    screen.blit(title, (title_x, int(h*0.05)))
    
    # Subtitle
    subtitle_font = pygame.font.SysFont('Consolas', int(h*0.025))
    subtitle = subtitle_font.render("Press ENTER to change a keybinding, or click the button", True, (180, 200, 220))
    subtitle_x = w // 2 - subtitle.get_width() // 2
    screen.blit(subtitle, (subtitle_x, int(h*0.12)))
    
    # Define keybinding categories
    font = pygame.font.SysFont('Consolas', int(h*0.02))
    button_font = pygame.font.SysFont('Consolas', int(h*0.018), bold=True)
    
    # Action keybindings (1-9)
    action_section_y = int(h * 0.18)
    section_title = font.render("Action Shortcuts:", True, (255, 255, 150))
    screen.blit(section_title, (int(w*0.1), action_section_y))
    
    action_bindings = []
    for i in range(9):
        action_name = f"action_{i + 1}"
        key_display = keybinding_manager.get_action_display_key(action_name)
        action_bindings.append((action_name, f"Action {i + 1}", key_display))
    
    # Game control keybindings
    game_section_y = int(h * 0.45)
    section_title = font.render("Game Controls:", True, (255, 255, 150))
    screen.blit(section_title, (int(w*0.1), game_section_y))
    
    game_bindings = [
        ("end_turn", "End Turn", keybinding_manager.get_action_display_key("end_turn")),
        ("help_guide", "Help Guide", keybinding_manager.get_action_display_key("help_guide")),
        ("quit_to_menu", "Quit to Menu", keybinding_manager.get_action_display_key("quit_to_menu")),
    ]
    
    # Navigation/Menu keybindings
    nav_section_y = int(h * 0.62)
    section_title = font.render("Menu Navigation:", True, (255, 255, 150))
    screen.blit(section_title, (int(w*0.1), nav_section_y))
    
    nav_bindings = [
        ("menu_up", "Menu Up", keybinding_manager.get_action_display_key("menu_up")),
        ("menu_down", "Menu Down", keybinding_manager.get_action_display_key("menu_down")),
        ("menu_select", "Menu Select", keybinding_manager.get_action_display_key("menu_select")),
        ("menu_back", "Menu Back", keybinding_manager.get_action_display_key("menu_back")),
    ]
    
    # Combine all bindings for menu navigation
    all_bindings = action_bindings + game_bindings + nav_bindings
    
    # Add special menu items
    all_bindings.extend([
        ("reset_defaults", "Reset to Defaults", ""),
        ("back_to_menu", "? Back to Main Menu", "")
    ])
    
    # Draw keybinding options
    button_width = int(w * 0.7)
    button_height = int(h * 0.035)
    start_y = int(h * 0.22)
    spacing = int(h * 0.045)
    
    # Calculate sections
    current_item = 0
    
    # Draw action bindings
    for i, (action_key, display_name, key_display) in enumerate(action_bindings):
        y_pos = start_y + i * spacing
        draw_keybinding_item(screen, w, y_pos, button_width, button_height, 
                            display_name, key_display, current_item == selected_item)
        current_item += 1
    
    # Draw game control bindings  
    for i, (action_key, display_name, key_display) in enumerate(game_bindings):
        y_pos = game_section_y + 30 + i * spacing
        draw_keybinding_item(screen, w, y_pos, button_width, button_height,
                            display_name, key_display, current_item == selected_item)
        current_item += 1
    
    # Draw navigation bindings
    for i, (action_key, display_name, key_display) in enumerate(nav_bindings):
        y_pos = nav_section_y + 30 + i * spacing
        draw_keybinding_item(screen, w, y_pos, button_width, button_height,
                            display_name, key_display, current_item == selected_item)
        current_item += 1
    
    # Draw special menu items
    special_y = int(h * 0.85)
    for i, (action_key, display_name, key_display) in enumerate([
        ("reset_defaults", "Reset to Defaults", ""),
        ("back_to_menu", "? Back to Main Menu", "")
    ]):
        y_pos = special_y + i * spacing
        draw_keybinding_item(screen, w, y_pos, button_width, button_height,
                            display_name, key_display, current_item == selected_item,
                            is_special=True)
        current_item += 1
    
    # Instructions removed - users can intuit these actions from the UI design
    
    return all_bindings


def draw_keybinding_item(screen, w, y_pos, button_width, button_height, 
                        display_name, key_display, is_selected, is_special=False):
    """
    Draw a single keybinding configuration item.
    
    Args:
        screen: pygame surface
        w: screen width
        y_pos: y position for this item
        button_width, button_height: button dimensions
        display_name: human readable action name
        key_display: current key binding display
        is_selected: whether this item is currently selected
        is_special: whether this is a special menu item (no key binding)
    """
    button_x = w // 2 - button_width // 2
    rect = pygame.Rect(button_x, y_pos, button_width, button_height)
    
    # Determine button state
    button_state = ButtonState.FOCUSED if is_selected else ButtonState.NORMAL
    
    # Draw button background
    visual_feedback.draw_button(screen, rect, "", button_state, FeedbackStyle.BUTTON)
    
    # Draw action name
    name_font = pygame.font.SysFont('Consolas', int(button_height * 0.5), bold=True)
    name_surface = name_font.render(display_name, True, (255, 255, 255))
    name_x = rect.x + 20
    name_y = rect.centery - name_surface.get_height() // 2
    screen.blit(name_surface, (name_x, name_y))
    
    # Draw key binding (if not special item)
    if not is_special and key_display:
        key_font = pygame.font.SysFont('Consolas', int(button_height * 0.4), bold=True)
        key_surface = key_font.render(f"[{key_display}]", True, (255, 255, 100))
        key_x = rect.right - key_surface.get_width() - 20
        key_y = rect.centery - key_surface.get_height() // 2
        
        # Draw background for key
        key_bg_width = key_surface.get_width() + 10
        key_bg_height = key_surface.get_height() + 4
        key_bg_rect = pygame.Rect(key_x - 5, key_y - 2, key_bg_width, key_bg_height)
        pygame.draw.rect(screen, (60, 60, 60), key_bg_rect, border_radius=4)
        pygame.draw.rect(screen, (120, 120, 120), key_bg_rect, width=1, border_radius=4)
        
        screen.blit(key_surface, (key_x, key_y))


def draw_keybinding_change_prompt(screen, w, h, action_name, current_key):
    """
    Draw a prompt asking user to press a new key for binding.
    
    Args:
        screen: pygame surface
        w, h: screen dimensions
        action_name: name of action being rebound
        current_key: current key binding display
    """
    # Semi-transparent overlay
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Prompt box
    box_width = int(w * 0.6)
    box_height = int(h * 0.3)
    box_x = (w - box_width) // 2
    box_y = (h - box_height) // 2
    
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
    pygame.draw.rect(screen, (40, 50, 70), box_rect, border_radius=15)
    pygame.draw.rect(screen, (150, 180, 220), box_rect, width=3, border_radius=15)
    
    # Title
    title_font = pygame.font.SysFont('Consolas', int(h*0.04), bold=True)
    title = title_font.render("Change Keybinding", True, (255, 255, 255))
    title_x = box_x + (box_width - title.get_width()) // 2
    screen.blit(title, (title_x, box_y + 20))
    
    # Action name
    action_font = pygame.font.SysFont('Consolas', int(h*0.03))
    action_text = action_font.render(f"Action: {action_name}", True, (255, 255, 150))
    action_x = box_x + (box_width - action_text.get_width()) // 2
    screen.blit(action_text, (action_x, box_y + 70))
    
    # Current binding
    current_font = pygame.font.SysFont('Consolas', int(h*0.025))
    current_text = current_font.render(f"Current: [{current_key}]", True, (200, 200, 200))
    current_x = box_x + (box_width - current_text.get_width()) // 2
    screen.blit(current_text, (current_x, box_y + 110))
    
    # Instruction
    inst_font = pygame.font.SysFont('Consolas', int(h*0.025), bold=True)
    instruction = inst_font.render("Press any key to assign it to this action", True, (100, 255, 100))
    inst_x = box_x + (box_width - instruction.get_width()) // 2
    screen.blit(instruction, (inst_x, box_y + 150))
    
    # Cancel instruction
    cancel_font = pygame.font.SysFont('Consolas', int(h*0.02))
    cancel_text = cancel_font.render("Press ESC to cancel", True, (255, 150, 150))
    cancel_x = box_x + (box_width - cancel_text.get_width()) // 2
    screen.blit(cancel_text, (cancel_x, box_y + 190))


def get_keybinding_menu_click_item(mouse_pos, w, h, num_items):
    """
    Determine which keybinding menu item was clicked.
    
    Args:
        mouse_pos: (x, y) mouse position
        w, h: screen dimensions
        num_items: total number of menu items
        
    Returns:
        int: clicked item index, or -1 if no item clicked
    """
    mx, my = mouse_pos
    
    button_width = int(w * 0.7)
    button_height = int(h * 0.035)
    spacing = int(h * 0.045)
    
    # Check action bindings (9 items starting at y=0.22)
    start_y = int(h * 0.22)
    for i in range(9):
        y_pos = start_y + i * spacing
        button_x = w // 2 - button_width // 2
        rect = pygame.Rect(button_x, y_pos, button_width, button_height)
        if rect.collidepoint(mouse_pos):
            return i
    
    # Check game control bindings (3 items)
    game_section_y = int(h * 0.45) + 30
    for i in range(3):
        y_pos = game_section_y + i * spacing
        button_x = w // 2 - button_width // 2
        rect = pygame.Rect(button_x, y_pos, button_width, button_height)
        if rect.collidepoint(mouse_pos):
            return 9 + i
    
    # Check navigation bindings (4 items)
    nav_section_y = int(h * 0.62) + 30
    for i in range(4):
        y_pos = nav_section_y + i * spacing
        button_x = w // 2 - button_width // 2
        rect = pygame.Rect(button_x, y_pos, button_width, button_height)
        if rect.collidepoint(mouse_pos):
            return 12 + i
    
    # Check special items (2 items)
    special_y = int(h * 0.85)
    for i in range(2):
        y_pos = special_y + i * spacing
        button_x = w // 2 - button_width // 2
        rect = pygame.Rect(button_x, y_pos, button_width, button_height)
        if rect.collidepoint(mouse_pos):
            return 16 + i
    
    return -1