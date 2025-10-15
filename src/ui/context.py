'''
Context information creation utilities for UI components.

This module handles creating context information dictionaries that are displayed
in context windows when hovering over actions, upgrades, or other UI elements.
'''

from typing import Dict, Any


def create_action_context_info(action: Dict[str, Any], game_state: Any, action_idx: int) -> Dict[str, Any]:
    '''Create context info for an action to display in the context window.'''
    ap_cost = action.get('ap_cost', 1)
    
    # Build title with shortcut key if available
    title = action['name']
    if action_idx < 9:  # Only first 9 actions get keyboard shortcuts
        try:
            from src.services.keybinding_manager import keybinding_manager
            shortcut_key = keybinding_manager.get_action_display_key(f'action_{action_idx + 1}')
            title = f'[{shortcut_key}] {action['name']}'
        except ImportError:
            pass
    
    # Enhanced description for research actions showing current quality
    base_desc = action['desc']
    if hasattr(game_state, 'research_quality_unlocked') and game_state.research_quality_unlocked:
        if 'Research' in action['name'] and action['name'] not in ['Set Research Quality: Rushed', 'Set Research Quality: Standard', 'Set Research Quality: Thorough']:
            quality_suffix = f' [{game_state.current_research_quality.value.title()}]'
            base_desc += quality_suffix
    
    # Build details list - handle dynamic costs
    action_cost = action['cost']
    if callable(action_cost):
        action_cost = action_cost(game_state)
    
    details = [
        f'Cost: ${action_cost}',
        f'Action Points: {ap_cost}',
    ]
    
    # Add delegation info if available
    if action.get('delegatable', False):
        staff_req = action.get('delegate_staff_req', 1)
        delegate_ap = action.get('delegate_ap_cost', 0)
        effectiveness = action.get('delegate_effectiveness', 1.0)
        details.append(f'Delegatable: Requires {staff_req} admin staff, {delegate_ap} AP, {int(effectiveness*100)}% effective')
    
    # Add availability status
    if game_state.action_points < ap_cost:
        details.append('! Not enough Action Points')
    
    # Handle dynamic cost evaluation (for economic config system)
    action_cost = action['cost']
    if callable(action_cost):
        action_cost = action_cost(game_state)
    
    if game_state.money < action_cost:
        details.append('! Not enough Money')
    
    return {
        'title': title,
        'description': base_desc,
        'details': details
    }


def create_upgrade_context_info(upgrade: Dict[str, Any], game_state: Any, upgrade_idx: int) -> Dict[str, Any]:
    '''Create context info for an upgrade to display in the context window.'''
    is_purchased = upgrade.get('purchased', False)
    
    title = upgrade['name']
    if is_purchased:
        title += ' (Purchased)'
    
    details = [
        f'Cost: ${upgrade['cost']}',
    ]
    
    # Add availability status
    if not is_purchased:
        if game_state.money < upgrade['cost']:
            details.append('! Not enough Money')
        else:
            details.append('+ Available for purchase')
    else:
        details.append('+ Effect is active')
    
    return {
        'title': title,
        'description': upgrade['desc'],
        'details': details
    }


def get_default_context_info(game_state: Any) -> Dict[str, Any]:
    '''Get default context info when nothing is hovered.'''
    lab_name = getattr(game_state, 'lab_name', 'Unknown Labs')
    return {
        'title': f'{lab_name}',
        'description': 'Hover over actions or upgrades to see detailed information here.',
        'details': [
            f'Turn {game_state.turn} - {game_state.game_clock.get_formatted_date()}',
            f'Money: ${game_state.money}',
            f'Action Points: {game_state.action_points}',
            f'p(Doom): {game_state.doom}'
        ]
    }
