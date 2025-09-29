"""
Context creation helpers for the 3-column UI layout.

Provides context information for actions and UI elements in the new layout.
"""

from typing import Dict, Any


def create_action_context_info(action: Dict[str, Any], game_state: Any, action_idx: int) -> Dict[str, Any]:
    """Create context information for an action."""
    # Format action cost information
    cost_info = []
    
    if action.get('cost', 0) > 0:
        cost_info.append(f"Cost: ${action['cost']}")
    
    ap_cost = action.get('ap_cost', 1)
    cost_info.append(f"Action Points: {ap_cost}")
    
    # Check if action is affordable
    can_afford = True
    afford_details = []
    
    if action.get('cost', 0) > game_state.money:
        can_afford = False
        afford_details.append(f"Need ${action['cost'] - game_state.money} more money")
    
    if ap_cost > game_state.action_points:
        can_afford = False
        afford_details.append(f"Need {ap_cost - game_state.action_points} more AP")
    
    # Build context info
    context_info = {
        'title': action['name'],
        'description': action.get('desc', 'No description available'),
        'details': cost_info
    }
    
    # Add affordability info
    if not can_afford:
        context_info['details'].extend(afford_details)
    elif can_afford:
        context_info['details'].append("[OK] Can afford this action")
    
    # Add delegation info if available
    if action.get('delegatable', False):
        staff_req = action.get('delegate_staff_req', 1)
        context_info['details'].append(f"Can delegate (needs {staff_req} staff)")
    
    return context_info


def create_upgrade_context_info(upgrade: Dict[str, Any], game_state: Any, upgrade_idx: int) -> Dict[str, Any]:
    """Create context information for an upgrade."""
    context_info = {
        'title': upgrade['name'],
        'description': upgrade.get('desc', 'No description available'),
        'details': [f"Cost: ${upgrade['cost']}"]
    }
    
    # Check affordability
    if upgrade['cost'] > game_state.money:
        context_info['details'].append(f"Need ${upgrade['cost'] - game_state.money} more money")
    else:
        context_info['details'].append("[OK] Can afford this upgrade")
    
    # Check if already purchased
    if upgrade.get('purchased', False):
        context_info['details'].append("[OK] Already purchased")
    
    return context_info


def get_default_context_info(game_state: Any) -> Dict[str, Any]:
    """Get default context information when nothing is hovered."""
    # Check current game state
    details = []
    
    # Money situation
    if game_state.money < 50:
        details.append("[WARNING] Low on funds - consider Fundraising")
    elif game_state.money > 500:
        details.append("? Good financial situation")
    
    # Action points
    if game_state.action_points == 0:
        details.append("[WARNING] No Action Points - End Turn to refresh")
    elif game_state.action_points == game_state.max_action_points:
        details.append("[LIGHTNING] Full Action Points available")
    
    # Doom level
    doom_percent = (game_state.doom / game_state.max_doom) * 100
    if doom_percent > 80:
        details.append("[FIRE] CRITICAL: Very high p(Doom)!")
    elif doom_percent > 60:
        details.append("[WARNING] High p(Doom) - focus on safety research")
    elif doom_percent < 30:
        details.append("[OK] p(Doom) under control")
    
    # Research progress
    if hasattr(game_state, 'research_progress'):
        if game_state.research_progress > 80:
            details.append("? Close to research breakthrough!")
        elif game_state.research_progress < 20:
            details.append("? Early research phase")
    
    return {
        'title': 'GAME STATUS',
        'description': f'Turn {game_state.turn} ? Hover over actions for details',
        'details': details if details else ['All systems operational']
    }
