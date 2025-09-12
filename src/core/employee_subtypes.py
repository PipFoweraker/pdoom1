# Employee Subtypes System
# Defines different employee roles and their specializations

# Employee subtype definitions
EMPLOYEE_SUBTYPES = {
    # Basic generalist (existing "Hire Staff" equivalent)
    "generalist": {
        "name": "Generalist",
        "description": "Versatile employee who can handle various tasks. No advertising costs for basic roles.",
        "cost": 0,
        "ap_cost": 1,
        "effects": {
            "staff": 1
        },
        "specialization": None,
        "unlock_condition": None  # Always available
    },
    
    # Specialized roles (extending existing system)
    "researcher": {
        "name": "Researcher", 
        "description": "Research specialist with PhD background. Increases research progress and enables advanced projects.",
        "cost": 0,
        "ap_cost": 2,
        "effects": {
            "staff": 1,
            "research_staff": 1,
            "research_progress": 5  # Immediate research boost
        },
        "specialization": "research",
        "unlock_condition": None  # Always available
    },
    
    "engineer": {
        "name": "Engineer",
        "description": "Technical specialist who improves compute efficiency and system reliability.", 
        "cost": 0,
        "ap_cost": 2,
        "effects": {
            "staff": 1,
            "ops_staff": 1,
            "compute": 10  # Immediate compute boost
        },
        "specialization": "engineering",
        "unlock_condition": None  # Always available
    },
    
    "administrator": {
        "name": "Administrator",
        "description": "Executive assistant who provides significant action point boost for complex operations.",
        "cost": 0,
        "ap_cost": 2,
        "effects": {
            "staff": 1,
            "admin_staff": 1
        },
        "specialization": "administration", 
        "unlock_condition": None  # Always available
    },
    
    # Advanced roles (unlocked later)
    "security_specialist": {
        "name": "Security Specialist",
        "description": "AI safety expert who reduces doom risk and provides security against espionage.",
        "cost": 0,
        "ap_cost": 2,
        "effects": {
            "staff": 1,
            "ops_staff": 1,
            "doom": -2  # Immediate doom reduction
        },
        "specialization": "security",
        "unlock_condition": lambda gs: gs.staff >= 5  # Unlocks with larger teams
    },
    
    "data_scientist": {
        "name": "Data Scientist", 
        "description": "Advanced analytics specialist who accelerates research and provides insights.",
        "cost": 0,
        "ap_cost": 2,
        "effects": {
            "staff": 1,
            "research_staff": 1,
            "research_progress": 8,
            "reputation": 1  # Slight reputation boost from publications
        },
        "specialization": "data_science",
        "unlock_condition": lambda gs: gs.research_progress >= 20  # Unlocks with research progress
    },
    
    "manager": {
        "name": "Manager",
        "description": "Team leader for large organizations. Required to maintain productivity beyond 9 employees.",
        "cost": 0,
        "ap_cost": 1,
        "effects": {
            "staff": 1,
            # Manager effects handled by existing _hire_manager() method
        },
        "specialization": "management",
        "unlock_condition": lambda gs: gs.staff >= 9  # Existing manager unlock condition
    },
    
    # Enhanced Personnel System - Specialist Researcher
    "specialist_researcher": {
        "name": "Specialist Researcher",
        "description": "Individual researcher with unique specialization, traits, and management needs.",
        "cost": 0,  # No upfront hiring costs for bootstrap nonprofit
        "ap_cost": 2,
        "effects": {
            "staff": 1,
            "research_staff": 1,
            # Effects handled by researcher specialization system
        },
        "specialization": "specialist",
        "unlock_condition": lambda gs: hasattr(gs, 'researchers')  # Always available if system enabled
    }
}

def get_available_subtypes(game_state):
    """
    Returns list of employee subtypes available for hiring based on game state.
    Includes unlock conditions and current availability.
    """
    available = []
    
    for subtype_id, subtype in EMPLOYEE_SUBTYPES.items():
        # Check unlock condition
        if subtype["unlock_condition"] is None or subtype["unlock_condition"](game_state):
            # Check if player can afford it
            can_afford = game_state.money >= subtype["cost"] and game_state.action_points >= subtype["ap_cost"]
            available.append({
                "id": subtype_id,
                "data": subtype,
                "affordable": can_afford
            })
    
    return available

def get_hiring_complexity_level(game_state):
    """
    Determines the complexity level for hiring based on organization size.
    Returns the level and description of what's available.
    """
    staff_count = game_state.staff
    
    if staff_count <= 3:
        return {
            "level": 1,
            "description": "Small Team",
            "available_roles": ["generalist", "researcher", "engineer", "administrator"],
            "complexity_note": "Basic hiring - choose from core roles"
        }
    elif staff_count <= 8:
        return {
            "level": 2, 
            "description": "Growing Organization",
            "available_roles": ["generalist", "researcher", "engineer", "administrator", "security_specialist"],
            "complexity_note": "Specialized roles unlocked - security considerations emerge"
        }
    else:
        return {
            "level": 3,
            "description": "Large Organization", 
            "available_roles": list(EMPLOYEE_SUBTYPES.keys()),
            "complexity_note": "Full complexity - all roles available, management required"
        }

def apply_subtype_effects(game_state, subtype_id):
    """
    Apply the effects of hiring a specific employee subtype.
    Returns success message and any special effects.
    """
    if subtype_id not in EMPLOYEE_SUBTYPES:
        return False, f"Unknown employee subtype: {subtype_id}"
    
    subtype = EMPLOYEE_SUBTYPES[subtype_id]
    
    # Special handling for manager
    if subtype_id == "manager":
        game_state._hire_manager()
        # Set subtype for manager blob
        if game_state.employee_blobs and game_state.employee_blobs[-1]['type'] == 'manager':
            game_state.employee_blobs[-1]['subtype'] = subtype_id
        return True, f"Manager hired! Specialized in {subtype['specialization']}."
    
    # Apply standard effects
    messages = []
    for attribute, value in subtype["effects"].items():
        game_state._add(attribute, value)
        if value > 0:
            messages.append(f"+{value} {attribute}")
        else:
            messages.append(f"{value} {attribute}")
    
    # Set subtype for the most recently added employee blob
    if game_state.employee_blobs:
        for blob in reversed(game_state.employee_blobs):
            if blob['type'] == 'employee' and blob['subtype'] == 'generalist':
                blob['subtype'] = subtype_id
                # Get productive action category and set default action
                from src.core.productive_actions import get_employee_category, get_default_action_index
                category = get_employee_category(subtype_id)
                if category:
                    default_action_index = get_default_action_index(category)
                    if default_action_index is not None:
                        blob['productive_action_index'] = default_action_index
                break
    
    effect_summary = ", ".join(messages)
    success_msg = f"{subtype['name']} hired! Effects: {effect_summary}"
    
    # Add specialization bonus message if applicable
    if subtype["specialization"]:
        success_msg += f" Specialized in {subtype['specialization']}."
    
    return True, success_msg