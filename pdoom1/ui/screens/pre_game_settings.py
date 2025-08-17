"""
Pre-game settings screen for P(Doom) - Laboratory Configuration

This module provides the pre-game settings screen for configuring laboratory
parameters before starting a new game.
"""

import pygame
from visual_feedback import visual_feedback, ButtonState
from ui import draw_enhanced_continue_button, draw_bureaucratic_setting_button, draw_mute_button_standalone


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