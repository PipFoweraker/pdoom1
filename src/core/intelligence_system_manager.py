'''
Intelligence System Manager - Handles opponent scouting, espionage, and intelligence operations.

This module extracts intelligence-related functionality from the main GameState class,
providing a focused interface for all opponent intelligence gathering operations.

Key functionality:
- Opponent discovery and scouting
- Espionage operations with risk management  
- Intelligence dialog system for player choices
- Detailed opponent investigations
- Support for magical orb enhancements
'''

from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_state import GameState

from src.services.deterministic_rng import get_rng


class IntelligenceSystemManager:
    '''Manages all intelligence gathering operations and opponent scouting.'''
    
    def __init__(self, game_state: 'GameState') -> None:
        '''Initialize the intelligence system manager.
        
        Args:
            game_state: Reference to the main game state for accessing game data
        '''
        self.game_state = game_state
    
    def scout_opponent(self) -> None:
        '''Scout a specific opponent - unlocked after turn 5'''
        discovered_opponents = [opp for opp in self.game_state.opponents if opp.discovered]
        
        if not discovered_opponents:
            # Try to discover a new opponent
            undiscovered = [opp for opp in self.game_state.opponents if not opp.discovered]
            if undiscovered:
                target = get_rng().choice(undiscovered, f'scout_discover_opponent_turn_{self.game_state.turn}')
                target.discover()
                self.game_state.messages.append(f'Scouting: Discovered new competitor '{target.name}'!')
                self.game_state.messages.append(f''{target.description}'')
            else:
                self.game_state.messages.append('Scouting: All competitors already discovered.')
            return None
            
        # Choose a discovered opponent to scout
        target = get_rng().choice(discovered_opponents, f'scout_target_selection_turn_{self.game_state.turn}')
        
        # Choose what to scout based on what's still unknown
        unknown_stats = [stat for stat, discovered in target.discovered_stats.items() if not discovered]
        
        if unknown_stats:
            stat_to_scout = get_rng().choice(unknown_stats, f'scout_stat_selection_turn_{self.game_state.turn}')
        else:
            # All stats known, scout progress for an update
            stat_to_scout = 'progress'
            
        success, value, message = target.scout_stat(stat_to_scout)
        self.game_state.messages.append(f'Scouting: {message}')
        
        # Update legacy known_opp_progress for UI compatibility if scouting progress
        if stat_to_scout == 'progress' and success:
            self.game_state.known_opp_progress = value
    
    def spy(self) -> None:
        '''Legacy espionage method - now scouts random opponents'''
        discovered_opponents = [opp for opp in self.game_state.opponents if opp.discovered]
        
        if not discovered_opponents:
            # Try to discover a new opponent
            undiscovered = [opp for opp in self.game_state.opponents if not opp.discovered]
            if undiscovered:
                target = get_rng().choice(undiscovered, f'espionage_discover_opponent_turn_{self.game_state.turn}')
                target.discover()
                self.game_state.messages.append(f'Espionage: Discovered new competitor '{target.name}'!')
            else:
                self.game_state.messages.append('Espionage: No new competitors to discover.')
            return None
            
        # Scout a random stat from a discovered opponent
        target = get_rng().choice(discovered_opponents, f'espionage_target_selection_turn_{self.game_state.turn}')
        stats = ['progress', 'budget', 'capabilities_researchers', 'lobbyists', 'compute']
        stat_to_scout = get_rng().choice(stats, f'espionage_stat_selection_turn_{self.game_state.turn}')
        
        success, value, message = target.scout_stat(stat_to_scout)
        self.game_state.messages.append(f'Espionage: {message}')
        
        # Update legacy known_opp_progress for UI compatibility
        if stat_to_scout == 'progress' and success:
            self.game_state.known_opp_progress = value
            
        return None
            
        return None
    
    def espionage_risk(self) -> Optional[str]:
        '''Handle risks and consequences of espionage operations.'''
        first_risk = get_rng().random(f'espionage_risk_1_turn_{self.game_state.turn}')
        if first_risk < 0.25:
            self.game_state._add('reputation', -2)
            self.game_state.messages.append('Espionage scandal! Reputation dropped.')
        else:
            second_risk = get_rng().random(f'espionage_risk_2_turn_{self.game_state.turn}')
            if second_risk < 0.15:
                self.game_state._add('doom', 5, 'espionage operation backfired')
                self.game_state.messages.append('Espionage backfired! Doom increased.')
        return None
    
    def scout_opponents(self) -> None:
        '''Scout competing labs to gather intelligence on their capabilities.'''
        messages = []
        discoveries = 0
        
        # First, check if any opponents can be discovered
        undiscovered_opponents = [opp for opp in self.game_state.opponents if not opp.discovered]
        
        discovery_chance = 0.6
        
        if undiscovered_opponents and get_rng().random('random_context') < discovery_chance:
            # Discover a new opponent
            new_opponent = get_rng().choice(undiscovered_opponents, 'choice_context')
            new_opponent.discover()
            discoveries += 1
            messages.append(f'Intelligence breakthrough! Discovered new competing lab: {new_opponent.name}')
            messages.append(f'? {new_opponent.description}')
        
        # Scout stats from known opponents
        discovered_opponents = [opp for opp in self.game_state.opponents if opp.discovered]
        
        if discovered_opponents:
            # Standard scouting
            target_opponent = get_rng().choice(discovered_opponents, 'choice_context')
            
            # Try to scout a random stat
            stats_to_scout = ['budget', 'capabilities_researchers', 'lobbyists', 'compute', 'progress']
            stat_to_scout = get_rng().choice(stats_to_scout, 'choice_context')
            
            success, value, message = target_opponent.scout_stat(stat_to_scout)
            messages.append(message)
            
            if success:
                discoveries += 1
        
        # Add intelligence gained message
        if discoveries > 0:
            messages.append(f'Intelligence gathering successful! ({discoveries} new insights)')
            # Small reputation gain for successful intelligence work
            self.game_state._add('reputation', 1)
        else:
            messages.append('Intelligence gathering yielded limited results this time.')
        
        # Add all messages to game state
        for msg in messages:
            self.game_state.messages.append(msg)
    
    def trigger_intelligence_dialog(self) -> None:
        '''Trigger the intelligence dialog with available intelligence gathering options.'''
        # Check if any opponents can be scouted
        discovered_opponents = [opp for opp in self.game_state.opponents if opp.discovered]
        undiscovered_opponents = [opp for opp in self.game_state.opponents if not opp.discovered]
        
        intelligence_options = []
        
        # Scout Opponents - Low risk internet research
        intelligence_options.append({
            'id': 'scout_opponents',
            'name': 'Scout Opponents',
            'description': 'Gather intelligence on competing labs via internet research.',
            'cost': 50,
            'ap_cost': 1,
            'available': True,
            'details': f'Known labs: {len(discovered_opponents)}, Unknown labs: {len(undiscovered_opponents)}'
        })
        
        # Espionage - Higher risk, more detailed information
        intelligence_options.append({
            'id': 'espionage', 
            'name': 'Espionage',
            'description': 'Risky operation to reveal detailed opponent progress and capabilities.',
            'cost': self.game_state.economic_config.get_intelligence_cost('espionage') if hasattr(self.game_state, 'economic_config') else 500,
            'ap_cost': 1,
            'available': len(discovered_opponents) > 0,
            'details': f'Target: Random discovered opponent. High risk, detailed intel.'
        })
        
        # Investigate Opponent - Deep dive on specific target
        if len(discovered_opponents) > 0:
            intelligence_options.append({
                'id': 'investigate_opponent',
                'name': 'Investigate Opponent', 
                'description': 'Deep investigation of a specific revealed opponent.',
                'cost': 75,
                'ap_cost': 1,
                'available': True,
                'details': f'Choose from {len(discovered_opponents)} known opponents for detailed analysis.'
            })
        
        # General News Reading - Industry intelligence
        intelligence_options.append({
            'id': 'general_news_reading',
            'name': 'General News Reading',
            'description': 'Read industry news for market intelligence and trends.',
            'cost': 10,
            'ap_cost': 1,
            'available': True,
            'details': 'Low-cost intelligence gathering from public sources.'
        })
        
        # General Networking - Social intelligence
        intelligence_options.append({
            'id': 'general_networking',
            'name': 'General Networking',
            'description': 'Network with industry contacts for insider intelligence.',
            'cost': 25,
            'ap_cost': 1,
            'available': True,
            'details': 'Build relationships and gather social intelligence.'
        })
        
        self.game_state.pending_intelligence_dialog = {
            'options': intelligence_options,
            'title': 'Intelligence Operations',
            'description': 'Select an intelligence gathering operation to execute.'
        }
    
    def select_intelligence_option(self, option_id: str) -> Tuple[bool, str]:
        '''Handle player selection of an intelligence option.'''
        if not self.game_state.pending_intelligence_dialog:
            return False, 'No intelligence dialog active.'
        
        # Find the selected option
        selected_option = None
        for option in self.game_state.pending_intelligence_dialog['options']:
            if option['id'] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return False, f'Invalid intelligence option: {option_id}'
        
        if not selected_option['available']:
            return False, f'Option not available: {selected_option['name']}'
        
        # Check costs
        if selected_option['cost'] > self.game_state.money:
            return False, f'Cannot afford {selected_option['name']} - need ${selected_option['cost']}'
        
        if selected_option['ap_cost'] > self.game_state.action_points:
            return False, f'Cannot execute {selected_option['name']} - need {selected_option['ap_cost']} AP'
        
        # Execute the selected intelligence operation
        if option_id == 'scout_opponents':
            # Deduct costs
            self.game_state.money -= selected_option['cost']
            self.game_state.action_points -= selected_option['ap_cost']
            
            # Execute scout opponents functionality
            self.scout_opponent()
            # Apply espionage risk
            self.espionage_risk()
            
        elif option_id == 'espionage':
            # Deduct costs
            self.game_state.money -= selected_option['cost']
            self.game_state.action_points -= selected_option['ap_cost']
            
            # Execute espionage functionality
            self.spy()
            # Apply espionage risk
            self.espionage_risk()
            
        elif option_id == 'investigate_opponent':
            # Deduct costs
            self.game_state.money -= selected_option['cost']
            self.game_state.action_points -= selected_option['ap_cost']
            
            # Execute investigation functionality
            self.investigate_specific_opponent()
            # Apply espionage risk
            self.espionage_risk()
            
        elif option_id == 'general_news_reading':
            # Deduct costs
            self.game_state.money -= selected_option['cost']
            self.game_state.action_points -= selected_option['ap_cost']
            
            # Execute news reading functionality
            self.game_state._general_news_reading()
            
        elif option_id == 'general_networking':
            # Deduct costs
            self.game_state.money -= selected_option['cost']
            self.game_state.action_points -= selected_option['ap_cost']
            
            # Execute networking functionality
            self.game_state._general_networking()
            
        else:
            return False, f'Unknown intelligence option: {option_id}'
        
        # Clear the intelligence dialog
        self.game_state.pending_intelligence_dialog = None
        return True, 'Intelligence operation complete.'
    
    def has_revealed_opponents(self) -> bool:
        '''Check if any opponents have been discovered and can be investigated.'''
        return any(opp.discovered for opp in self.game_state.opponents)

    def investigate_specific_opponent(self) -> None:
        '''Deep investigation of a specific revealed opponent - more detailed than scouting.'''
        discovered_opponents = [opp for opp in self.game_state.opponents if opp.discovered]
        
        if not discovered_opponents:
            self.game_state.messages.append('Investigation failed: No opponents have been revealed yet. Try scouting first.')
            return
            
        # Choose a discovered opponent to investigate deeply
        target = get_rng().choice(discovered_opponents, f'investigate_target_selection_turn_{self.game_state.turn}')
        
        # Detailed investigation reveals more information than basic scouting
        self.game_state.messages.append(f'INVESTIGATION: Deep analysis of {target.name}')
        
        # Reveal detailed stats (more than basic scouting)
        all_stats = ['budget', 'compute', 'progress', 'reputation', 'staff_count', 'strategy_focus']
        num_stats = 3
        stats_revealed = get_rng().sample(all_stats, min(num_stats, len(all_stats)), 'opponent_investigation_stats')
        
        for stat in stats_revealed:
            if stat == 'budget':
                range_desc = 'massive' if target.budget > 800 else 'substantial' if target.budget > 400 else 'limited'
                self.game_state.messages.append(f'? Financial analysis: {target.name} operates with {range_desc} funding reserves')
            elif stat == 'compute':
                range_desc = 'cutting-edge' if target.compute > 80 else 'advanced' if target.compute > 40 else 'basic'
                self.game_state.messages.append(f'? Infrastructure scan: {target.name} uses {range_desc} compute resources')
            elif stat == 'progress':
                range_desc = 'alarming' if target.progress > 70 else 'significant' if target.progress > 40 else 'early-stage'
                self.game_state.messages.append(f'? Research assessment: {target.name} shows {range_desc} development progress')
            elif stat == 'reputation':
                range_desc = 'renowned' if target.reputation > 80 else 'respected' if target.reputation > 40 else 'emerging'
                self.game_state.messages.append(f'? Public standing: {target.name} maintains {range_desc} industry reputation')
            elif stat == 'staff_count':
                range_desc = 'large' if target.staff_count > 30 else 'medium' if target.staff_count > 15 else 'small'
                self.game_state.messages.append(f'? Team analysis: {target.name} employs a {range_desc} research team')
            elif stat == 'strategy_focus':
                self.game_state.messages.append(f'? Strategic focus: {target.name} prioritizes {target.strategy} development approaches')
        
        # Chance to reveal current action or priority
        if get_rng().random(f'investigate_action_reveal_turn_{self.game_state.turn}') < 0.4:
            action_insights = [
                f'? Current priority: {target.name} is heavily investing in compute infrastructure',
                f'? Strategic shift: {target.name} recently pivoted to focus on {target.strategy}',
                f'? Intelligence leak: {target.name} planning major announcement within 2-3 turns',
                f'? Internal memo: {target.name} concerned about recent safety research developments',
                f'? Hiring spree: {target.name} aggressively recruiting top AI researchers'
            ]
            self.game_state.messages.append(get_rng().choice(action_insights, f'investigate_insight_turn_{self.game_state.turn}'))