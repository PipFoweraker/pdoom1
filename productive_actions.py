# Productive Actions System
# Defines ongoing productive actions that employees perform when requirements are met
# Each action provides a multiplicative effectiveness bonus

# Productive actions for each employee category
PRODUCTIVE_ACTIONS = {
    # Junior Researcher actions (maps to "researcher" subtype)
    "junior_researcher": [
        {
            "name": "Literature Review",
            "description": "Systematically reviews recent AI safety papers to identify research gaps and opportunities",
            "effectiveness_bonus": 1.08,  # +8% bonus
            "requirements": {
                "compute_per_employee": 0.5,  # Lower compute requirement
                "min_reputation": 0  # No reputation requirement
            }
        },
        {
            "name": "Data Collection",
            "description": "Gathers and organizes training data and experimental results for research projects",
            "effectiveness_bonus": 1.12,  # +12% bonus
            "requirements": {
                "compute_per_employee": 1.0,  # Standard compute requirement
                "min_reputation": 5  # Requires some reputation for data access
            }
        },
        {
            "name": "Experiment Documentation",
            "description": "Meticulously documents experimental procedures and maintains research notebooks",
            "effectiveness_bonus": 1.06,  # +6% bonus
            "requirements": {
                "compute_per_employee": 0.3,  # Very low compute requirement
                "min_reputation": 0  # No reputation requirement
            }
        }
    ],
    
    # Senior Researcher actions (maps to "data_scientist" subtype)
    "senior_researcher": [
        {
            "name": "Advanced Algorithm Development",
            "description": "Develops novel AI safety algorithms and mathematical frameworks",
            "effectiveness_bonus": 1.15,  # +15% bonus
            "requirements": {
                "compute_per_employee": 2.0,  # High compute requirement
                "min_reputation": 15  # Requires significant reputation
            }
        },
        {
            "name": "Research Mentorship",
            "description": "Guides junior researchers and coordinates cross-team research initiatives",
            "effectiveness_bonus": 1.10,  # +10% bonus
            "requirements": {
                "compute_per_employee": 0.8,  # Moderate compute requirement
                "min_reputation": 10,  # Moderate reputation requirement
                "min_research_staff": 2  # Requires other researchers to mentor
            }
        },
        {
            "name": "Publication Pipeline",
            "description": "Prepares high-impact research papers and manages peer review process",
            "effectiveness_bonus": 1.18,  # +18% bonus
            "requirements": {
                "compute_per_employee": 1.5,  # High compute requirement
                "min_reputation": 20,  # High reputation requirement for top journals
                "min_research_progress": 25  # Requires substantial research progress
            }
        }
    ],
    
    # Security Engineer actions (maps to "security_specialist" subtype)
    "security_engineer": [
        {
            "name": "Security Auditing",
            "description": "Continuously monitors AI systems for safety vulnerabilities and alignment issues",
            "effectiveness_bonus": 1.12,  # +12% bonus
            "requirements": {
                "compute_per_employee": 1.0,  # Standard compute requirement
                "min_reputation": 8  # Requires moderate reputation for security clearance
            }
        },
        {
            "name": "Threat Modeling",
            "description": "Develops comprehensive threat models for advanced AI systems and deployment scenarios",
            "effectiveness_bonus": 1.15,  # +15% bonus
            "requirements": {
                "compute_per_employee": 1.5,  # High compute requirement for simulations
                "min_reputation": 12,  # Higher reputation requirement
                "min_staff": 8  # Requires larger team to model complex threats
            }
        },
        {
            "name": "Incident Response",
            "description": "Maintains rapid response protocols and containment procedures for AI safety incidents",
            "effectiveness_bonus": 1.08,  # +8% bonus
            "requirements": {
                "compute_per_employee": 0.7,  # Lower compute requirement
                "min_reputation": 5  # Basic reputation requirement
            }
        }
    ],
    
    # Operations Specialist actions (maps to "engineer" subtype)
    "operations_specialist": [
        {
            "name": "Infrastructure Optimization",
            "description": "Optimizes computing infrastructure and reduces operational overhead",
            "effectiveness_bonus": 1.10,  # +10% bonus
            "requirements": {
                "compute_per_employee": 0.8,  # Moderate compute requirement
                "min_reputation": 3  # Low reputation requirement
            }
        },
        {
            "name": "System Monitoring",
            "description": "Implements comprehensive monitoring and alerting for AI training systems",
            "effectiveness_bonus": 1.14,  # +14% bonus
            "requirements": {
                "compute_per_employee": 1.2,  # Higher compute requirement for monitoring tools
                "min_reputation": 8,  # Moderate reputation requirement
                "min_compute": 50  # Requires substantial compute infrastructure
            }
        },
        {
            "name": "Technical Documentation",
            "description": "Creates and maintains technical documentation and operational procedures",
            "effectiveness_bonus": 1.07,  # +7% bonus
            "requirements": {
                "compute_per_employee": 0.4,  # Low compute requirement
                "min_reputation": 0  # No reputation requirement
            }
        }
    ],
    
    # Administrative Staff actions (maps to "administrator" subtype)
    "administrative_staff": [
        {
            "name": "Process Optimization",
            "description": "Streamlines organizational processes and reduces bureaucratic overhead",
            "effectiveness_bonus": 1.09,  # +9% bonus
            "requirements": {
                "compute_per_employee": 0.3,  # Very low compute requirement
                "min_reputation": 5,  # Moderate reputation requirement
                "min_staff": 5  # Requires moderate team size to optimize
            }
        },
        {
            "name": "Stakeholder Relations",
            "description": "Manages relationships with funders, regulators, and research partners",
            "effectiveness_bonus": 1.13,  # +13% bonus
            "requirements": {
                "compute_per_employee": 0.2,  # Minimal compute requirement
                "min_reputation": 15,  # High reputation requirement for stakeholder access
                "min_money": 200  # Requires financial stability for networking
            }
        },
        {
            "name": "Compliance Management",
            "description": "Ensures regulatory compliance and manages audit preparation processes",
            "effectiveness_bonus": 1.06,  # +6% bonus
            "requirements": {
                "compute_per_employee": 0.5,  # Low compute requirement
                "min_reputation": 10,  # Moderate reputation requirement
                "min_board_members": 1  # Requires board oversight for compliance
            }
        }
    ],
    
    # Manager actions (maps to "manager" subtype)
    "manager": [
        {
            "name": "Strategic Planning",
            "description": "Develops long-term research strategies and coordinates organizational priorities",
            "effectiveness_bonus": 1.11,  # +11% bonus
            "requirements": {
                "compute_per_employee": 0.6,  # Moderate compute requirement for analytics
                "min_reputation": 12,  # High reputation requirement for strategic credibility
                "min_staff": 9  # Requires large team to manage
            }
        },
        {
            "name": "Team Coordination",
            "description": "Facilitates cross-functional collaboration and optimizes team productivity",
            "effectiveness_bonus": 1.16,  # +16% bonus
            "requirements": {
                "compute_per_employee": 0.4,  # Low compute requirement
                "min_reputation": 8,  # Moderate reputation requirement
                "min_staff": 6,  # Requires multiple teams to coordinate
                "min_admin_staff": 1  # Requires admin support
            }
        },
        {
            "name": "Resource Allocation",
            "description": "Optimizes allocation of compute, funding, and personnel across projects",
            "effectiveness_bonus": 1.13,  # +13% bonus
            "requirements": {
                "compute_per_employee": 0.8,  # Moderate compute requirement for optimization
                "min_reputation": 10,  # Moderate reputation requirement
                "min_money": 300,  # Requires substantial resources to allocate
                "min_compute": 30  # Requires compute resources to manage
            }
        }
    ]
}

# Mapping from employee subtypes to productive action categories
EMPLOYEE_SUBTYPE_TO_CATEGORY = {
    "researcher": "junior_researcher",
    "data_scientist": "senior_researcher", 
    "security_specialist": "security_engineer",
    "engineer": "operations_specialist",
    "administrator": "administrative_staff",
    "manager": "manager",
    "generalist": "junior_researcher"  # Generalists use junior researcher actions
}

def get_employee_category(employee_subtype):
    """
    Get the productive action category for an employee subtype.
    
    Args:
        employee_subtype (str): The employee subtype from employee_subtypes.py
        
    Returns:
        str: The productive action category, or None if not found
    """
    return EMPLOYEE_SUBTYPE_TO_CATEGORY.get(employee_subtype)

def get_available_actions(category):
    """
    Get the available productive actions for an employee category.
    
    Args:
        category (str): The employee category
        
    Returns:
        list: List of productive action dictionaries, or empty list if category not found
    """
    return PRODUCTIVE_ACTIONS.get(category, [])

def check_action_requirements(action, game_state, compute_per_employee):
    """
    Check if the requirements for a productive action are met.
    
    Args:
        action (dict): The productive action definition
        requirements_dict
        game_state: The current game state
        compute_per_employee (float): Available compute per employee
        
    Returns:
        tuple: (requirements_met (bool), failure_reason (str or None))
    """
    requirements = action.get("requirements", {})
    
    # Check compute requirement
    required_compute = requirements.get("compute_per_employee", 1.0)
    if compute_per_employee < required_compute:
        return False, f"insufficient_compute (need {required_compute}, have {compute_per_employee})"
    
    # Check reputation requirement
    min_reputation = requirements.get("min_reputation", 0)
    if game_state.reputation < min_reputation:
        return False, f"insufficient_reputation (need {min_reputation}, have {game_state.reputation})"
    
    # Check staff requirement
    min_staff = requirements.get("min_staff", 0)
    if game_state.staff < min_staff:
        return False, f"insufficient_staff (need {min_staff}, have {game_state.staff})"
    
    # Check research staff requirement
    min_research_staff = requirements.get("min_research_staff", 0)
    if game_state.research_staff < min_research_staff:
        return False, f"insufficient_research_staff (need {min_research_staff}, have {game_state.research_staff})"
    
    # Check research progress requirement
    min_research_progress = requirements.get("min_research_progress", 0)
    if game_state.research_progress < min_research_progress:
        return False, f"insufficient_research_progress (need {min_research_progress}, have {game_state.research_progress})"
    
    # Check money requirement
    min_money = requirements.get("min_money", 0)
    if game_state.money < min_money:
        return False, f"insufficient_money (need {min_money}, have {game_state.money})"
    
    # Check compute infrastructure requirement
    min_compute = requirements.get("min_compute", 0)
    if game_state.compute < min_compute:
        return False, f"insufficient_compute_infrastructure (need {min_compute}, have {game_state.compute})"
    
    # Check board members requirement
    min_board_members = requirements.get("min_board_members", 0)
    if game_state.board_members < min_board_members:
        return False, f"insufficient_board_members (need {min_board_members}, have {game_state.board_members})"
    
    # Check admin staff requirement
    min_admin_staff = requirements.get("min_admin_staff", 0)
    if game_state.admin_staff < min_admin_staff:
        return False, f"insufficient_admin_staff (need {min_admin_staff}, have {game_state.admin_staff})"
    
    return True, None

def get_default_action_index(category):
    """
    Get the index of the default action for an employee category.
    
    Args:
        category (str): The employee category
        
    Returns:
        int: Index of the default action (always 0 if category exists)
    """
    if category in PRODUCTIVE_ACTIONS:
        return 0
    return None