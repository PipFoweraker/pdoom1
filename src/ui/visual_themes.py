"""
Visual Themes and Color Coding System for P(Doom)

Provides consistent color schemes for action buttons and employee visual differentiation.
"""

from typing import Dict, Tuple, Optional
from enum import Enum


class ActionCategory(Enum):
    """Categories for action button color coding"""
    BUSINESS = "business"          # Fundraising, PR, outreach
    HIRING = "hiring"             # Hire staff, hire specialists  
    RESEARCH = "research"         # Research actions, publications
    INFRASTRUCTURE = "infrastructure"  # Compute, upgrades, facilities
    SECURITY = "security"         # Safety measures, security actions
    MANAGEMENT = "management"     # Strategic, administrative actions


class EmployeeType(Enum):
    """Employee types for visual differentiation"""
    GENERALIST = "generalist"
    RESEARCHER = "researcher" 
    ENGINEER = "engineer"
    ADMINISTRATOR = "administrator"
    SECURITY_SPECIALIST = "security_specialist"
    DATA_SCIENTIST = "data_scientist"
    MANAGER = "manager"


# Action button color schemes by category
ACTION_COLORS = {
    ActionCategory.BUSINESS: {
        'bg': (40, 120, 60),        # Green tones - money/growth
        'border': (80, 200, 100),
        'text': (220, 255, 230),
        'hover_bg': (60, 140, 80),
        'pressed_bg': (20, 100, 40)
    },
    ActionCategory.HIRING: {
        'bg': (120, 80, 40),        # Brown/orange tones - people
        'border': (200, 140, 80),
        'text': (255, 230, 200),
        'hover_bg': (140, 100, 60),
        'pressed_bg': (100, 60, 20)  
    },
    ActionCategory.RESEARCH: {
        'bg': (40, 80, 120),        # Blue tones - knowledge/science
        'border': (80, 140, 200),
        'text': (220, 230, 255),
        'hover_bg': (60, 100, 140), 
        'pressed_bg': (20, 60, 100)
    },
    ActionCategory.INFRASTRUCTURE: {
        'bg': (100, 60, 120),       # Purple tones - technology
        'border': (160, 100, 200),
        'text': (240, 220, 255),
        'hover_bg': (120, 80, 140),
        'pressed_bg': (80, 40, 100)
    },
    ActionCategory.SECURITY: {
        'bg': (120, 40, 40),        # Red tones - danger/safety
        'border': (200, 80, 80),
        'text': (255, 220, 220),
        'hover_bg': (140, 60, 60),
        'pressed_bg': (100, 20, 20)
    },
    ActionCategory.MANAGEMENT: {
        'bg': (80, 80, 80),         # Gray tones - administrative
        'border': (140, 140, 140),
        'text': (240, 240, 240),
        'hover_bg': (100, 100, 100),
        'pressed_bg': (60, 60, 60)
    }
}

# Employee visual properties (base colors and hat shapes)
EMPLOYEE_VISUALS = {
    EmployeeType.GENERALIST: {
        'body_color': (100, 150, 200),      # Light blue
        'body_color_productive': (150, 200, 255),  # Brighter when productive
        'hat_shape': 'baseball_cap',         # Casual baseball cap for generalists
        'hat_color': (60, 100, 140)         # Dark blue cap
    },
    EmployeeType.RESEARCHER: {
        'body_color': (80, 180, 80),         # Green - research/growth
        'body_color_productive': (120, 220, 120),
        'hat_shape': 'graduate',             # Mortarboard/graduation cap
        'hat_color': (40, 40, 40)            # Black academic cap
    },
    EmployeeType.ENGINEER: {
        'body_color': (160, 120, 80),        # Brown - practical/building
        'body_color_productive': (200, 160, 120),
        'hat_shape': 'hard_hat',             # Construction/engineering hat
        'hat_color': (255, 255, 0)           # Yellow hard hat
    },
    EmployeeType.ADMINISTRATOR: {
        'body_color': (120, 100, 160),       # Purple - administrative
        'body_color_productive': (160, 140, 200),
        'hat_shape': 'beret',                # Professional beret
        'hat_color': (80, 60, 120)           # Dark purple
    },
    EmployeeType.SECURITY_SPECIALIST: {
        'body_color': (180, 80, 80),         # Red - security/danger
        'body_color_productive': (220, 120, 120),
        'hat_shape': 'cap',                  # Security/military cap
        'hat_color': (40, 40, 40)            # Black security cap
    },
    EmployeeType.DATA_SCIENTIST: {
        'body_color': (100, 200, 180),       # Cyan - data/analysis
        'body_color_productive': (140, 240, 220),
        'hat_shape': 'beanie',               # Casual tech beanie
        'hat_color': (60, 160, 140)          # Dark cyan
    },
    EmployeeType.MANAGER: {
        'body_color': (200, 180, 100),       # Gold - leadership/value
        'body_color_productive': (240, 220, 140),
        'hat_shape': 'fedora',               # Executive hat
        'hat_color': (100, 90, 50)           # Dark gold/brown
    }
}

# Action name to category mapping
ACTION_CATEGORY_MAPPING = {
    # Business/Financial actions
    'fundraising': ActionCategory.BUSINESS,
    'angel_investor': ActionCategory.BUSINESS, 
    'venture_capital': ActionCategory.BUSINESS,
    'pr_outreach': ActionCategory.BUSINESS,
    'marketing': ActionCategory.BUSINESS,
    'publicity': ActionCategory.BUSINESS,
    
    # Hiring actions
    'hire_staff': ActionCategory.HIRING,
    'hire_researcher': ActionCategory.HIRING,
    'hire_engineer': ActionCategory.HIRING,
    'hire_manager': ActionCategory.HIRING,
    'employee_benefits': ActionCategory.HIRING,
    
    # Research actions
    'conduct_research': ActionCategory.RESEARCH,
    'research': ActionCategory.RESEARCH,
    'publish_paper': ActionCategory.RESEARCH,
    'peer_review': ActionCategory.RESEARCH,
    'academic_collaboration': ActionCategory.RESEARCH,
    
    # Infrastructure actions
    'buy_compute': ActionCategory.INFRASTRUCTURE,
    'upgrade_compute': ActionCategory.INFRASTRUCTURE,
    'optimize_compute': ActionCategory.INFRASTRUCTURE,
    'data_center': ActionCategory.INFRASTRUCTURE,
    'cloud_migration': ActionCategory.INFRASTRUCTURE,
    
    # Security actions  
    'security_audit': ActionCategory.SECURITY,
    'ai_safety_research': ActionCategory.SECURITY,
    'safety_measures': ActionCategory.SECURITY,
    'risk_assessment': ActionCategory.SECURITY,
    
    # Management actions
    'strategic_planning': ActionCategory.MANAGEMENT,
    'board_meeting': ActionCategory.MANAGEMENT,
    'team_building': ActionCategory.MANAGEMENT,
    'process_improvement': ActionCategory.MANAGEMENT
}


def get_action_colors(action_name: str) -> Dict[str, Tuple[int, int, int]]:
    """
    Get color scheme for an action button based on its category.
    
    Args:
        action_name: Name of the action
        
    Returns:
        Dict with color values for different button states
    """
    # Normalize action name (remove underscores, lowercase)
    normalized_name = action_name.lower().replace('_', '')
    
    # Find matching category
    category = None
    for action_key, action_category in ACTION_CATEGORY_MAPPING.items():
        if action_key.replace('_', '') in normalized_name or normalized_name in action_key:
            category = action_category
            break
    
    # Default to management if no category found
    if category is None:
        category = ActionCategory.MANAGEMENT
    
    return ACTION_COLORS[category]


def get_employee_visuals(employee_subtype: str) -> Dict:
    """
    Get visual properties for an employee based on their subtype.
    
    Args:  
        employee_subtype: Employee subtype string
        
    Returns:
        Dict with visual properties (colors, hat info)
    """
    try:
        employee_type = EmployeeType(employee_subtype)
        return EMPLOYEE_VISUALS[employee_type]
    except ValueError:
        # Default to generalist if subtype not found
        return EMPLOYEE_VISUALS[EmployeeType.GENERALIST]


def draw_employee_hat(surface, x: int, y: int, hat_shape: str, hat_color: Tuple[int, int, int], size: int = 20):
    """
    Draw a hat on an employee blob using geometric shapes.
    
    Args:
        surface: pygame surface to draw on
        x, y: Center position of employee blob
        hat_shape: Type of hat to draw
        hat_color: RGB color tuple for the hat
        size: Base size for hat scaling
    """
    import pygame
    
    if hat_shape == 'none':
        return
    
    hat_y = y - size - 5  # Position above blob
    
    if hat_shape == 'graduate':
        # Mortarboard/graduation cap - square with tassel
        cap_size = int(size * 0.8)
        cap_rect = pygame.Rect(x - cap_size//2, hat_y - cap_size//2, cap_size, cap_size)
        pygame.draw.rect(surface, hat_color, cap_rect)
        pygame.draw.rect(surface, (255, 255, 255), cap_rect, 2)
        # Tassel
        pygame.draw.circle(surface, (255, 215, 0), (x + cap_size//3, hat_y - cap_size//3), 3)
        
    elif hat_shape == 'hard_hat':
        # Construction hard hat - dome shape
        hat_width = int(size * 1.2)
        hat_height = int(size * 0.6)
        # Main dome
        pygame.draw.ellipse(surface, hat_color, (x - hat_width//2, hat_y - hat_height//2, hat_width, hat_height))
        pygame.draw.ellipse(surface, (200, 200, 200), (x - hat_width//2, hat_y - hat_height//2, hat_width, hat_height), 2)
        # Brim
        brim_rect = pygame.Rect(x - hat_width//2 - 3, hat_y + hat_height//4, hat_width + 6, 4)
        pygame.draw.rect(surface, hat_color, brim_rect)
        
    elif hat_shape == 'beret':
        # Professional beret - circular, tilted
        pygame.draw.circle(surface, hat_color, (x - 3, hat_y - 2), int(size * 0.7))
        pygame.draw.circle(surface, (150, 150, 150), (x - 3, hat_y - 2), int(size * 0.7), 2)
        
    elif hat_shape == 'cap':
        # Security/military cap - rectangular with visor
        cap_width = int(size * 0.9)
        cap_height = int(size * 0.5)
        # Main cap
        cap_rect = pygame.Rect(x - cap_width//2, hat_y - cap_height//2, cap_width, cap_height)
        pygame.draw.rect(surface, hat_color, cap_rect)
        # Visor
        visor_rect = pygame.Rect(x - cap_width//3, hat_y + cap_height//4, cap_width//2, 3)
        pygame.draw.rect(surface, (40, 40, 40), visor_rect)
        
    elif hat_shape == 'beanie':
        # Casual tech beanie - rounded top
        pygame.draw.circle(surface, hat_color, (x, hat_y), int(size * 0.6))
        pygame.draw.circle(surface, (100, 100, 100), (x, hat_y), int(size * 0.6), 2)
        # Folded brim
        brim_rect = pygame.Rect(x - int(size * 0.6), hat_y + int(size * 0.3), int(size * 1.2), 4)
        pygame.draw.rect(surface, (80, 80, 80), brim_rect)
        
    elif hat_shape == 'fedora':
        # Executive fedora - classic hat with band
        hat_width = int(size * 1.1)
        hat_height = int(size * 0.7)
        # Crown
        crown_rect = pygame.Rect(x - hat_width//3, hat_y - hat_height//2, hat_width//1.5, hat_height)
        pygame.draw.rect(surface, hat_color, crown_rect, border_radius=hat_height//4)
        # Brim
        brim_ellipse = pygame.Rect(x - hat_width//2, hat_y + hat_height//4, hat_width, hat_height//2)
        pygame.draw.ellipse(surface, hat_color, brim_ellipse)
        # Hat band
        band_rect = pygame.Rect(x - hat_width//3, hat_y, hat_width//1.5, 3)
        pygame.draw.rect(surface, (40, 40, 40), band_rect)
        
    elif hat_shape == 'baseball_cap':
        # Casual baseball cap - dome with forward visor
        hat_width = int(size * 0.9)
        hat_height = int(size * 0.6)
        # Main cap dome
        cap_rect = pygame.Rect(x - hat_width//2, hat_y - hat_height//2, hat_width, hat_height)
        pygame.draw.ellipse(surface, hat_color, cap_rect)
        pygame.draw.ellipse(surface, (120, 120, 120), cap_rect, 2)
        # Forward visor
        visor_points = [
            (x - hat_width//4, hat_y + hat_height//3),
            (x + hat_width//4, hat_y + hat_height//3),
            (x + hat_width//3, hat_y + hat_height//2 + 8),
            (x - hat_width//3, hat_y + hat_height//2 + 8)
        ]
        pygame.draw.polygon(surface, hat_color, visor_points)
        pygame.draw.polygon(surface, (120, 120, 120), visor_points, 2)
