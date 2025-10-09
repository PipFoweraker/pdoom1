'''
Turn Processing Manager - Extracted from game_state.py monolith

This module handles all turn processing logic, extracted from the massive
end_turn() method to improve maintainability and fix processing state bugs.

Following patterns established in:
- docs/TURN_SEQUENCING_FIX.md
- docs/MONOLITH_BREAKDOWN_SESSION_2025-09-15_COMPLETION.md
'''

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_state import GameState


class TurnProcessingState(Enum):
    '''Turn processing states for proper state management'''
    IDLE = 'idle'
    PROCESSING = 'processing'
    COMPLETE = 'complete'
    ERROR = 'error'


class TurnManager:
    '''
    Manages turn processing with proper state management.
    
    Extracted from GameState.end_turn() to fix processing state bugs
    and follow monolith breakdown patterns.
    '''
    
    def __init__(self, game_state: 'GameState'):
        self.game_state = game_state
        self.processing_state = TurnProcessingState.IDLE
        self.processing_timer = 0
        self.processing_duration = 30  # frames
    
    def can_end_turn(self) -> bool:
        '''Check if turn can be ended (not already processing)'''
        return self.processing_state == TurnProcessingState.IDLE
    
    def is_processing(self) -> bool:
        '''Check if turn is currently being processed'''
        return self.processing_state == TurnProcessingState.PROCESSING
    
    def is_processing_stuck(self) -> bool:
        '''Check if turn processing has been stuck too long'''
        return (self.processing_state == TurnProcessingState.PROCESSING and 
                self.processing_timer <= -30)  # 1 second at 30fps
    
    def reset_processing(self) -> None:
        '''Reset stuck turn processing'''
        self.processing_state = TurnProcessingState.IDLE
        self.processing_timer = 0
    
    def begin_turn_processing(self) -> bool:
        '''
        Start turn processing with proper state management.
        
        Returns True if processing started, False if already processing.
        '''
        if not self.can_end_turn():
            # Play error sound for rejected input
            if hasattr(self.game_state, 'sound_manager'):
                self.game_state.sound_manager.play_sound('error_beep')
            return False
        
        # Start processing
        self.processing_state = TurnProcessingState.PROCESSING
        self.processing_timer = self.processing_duration
        
        # Play accepted sound
        if hasattr(self.game_state, 'sound_manager'):
            self.game_state.sound_manager.play_sound('popup_accept')
        
        return True
    
    def process_turn(self) -> bool:
        '''
        Process the complete turn following established sequence.
        
        Sequence from docs/TURN_SEQUENCING_FIX.md:
        1. Events (moved to beginning)
        2. Check for pending popups (blocks turn if needed)
        3. Clear messages and prepare turn
        4. Execute selected actions
        5. Process staff maintenance
        6. Process opponent actions
        7. Check milestones
        8. Handle deferred events
        9. Increment turn and reset action points
        10. Check win/loss conditions
        '''
        try:
            gs = self.game_state
            
            # Phase 1: Events (from TURN_SEQUENCING_FIX.md)
            gs.trigger_events()
            
            # Phase 2: Check for pending popup events that block turn completion
            if (hasattr(gs, 'enhanced_events_enabled') and gs.enhanced_events_enabled and
                hasattr(gs, 'deferred_events') and hasattr(gs.deferred_events, 'pending_popup_events') and
                gs.deferred_events.pending_popup_events):
                # Events need to be resolved before turn can complete
                self._reset_processing_state()
                return False
            
            # Phase 3: Message management (scrollable log handling)
            self._handle_message_history()
            
            # Phase 4: Execute selected actions
            self._execute_selected_actions()
            
            # Phase 5: Employee productivity and research processing
            self._process_employee_productivity()
            
            # Phase 6: Staff maintenance and doom calculations
            self._process_staff_maintenance()
            
            # Phase 7: Opponent processing
            self._process_opponents()
            
            # Phase 8: Milestone checks
            self._check_milestones()
            
            # Phase 9: Deferred events
            self._process_deferred_events()
            
            # Phase 10: Turn increment and reset
            self._advance_turn()
            
            # Phase 11: Win/loss conditions
            self._check_game_over_conditions()
            
            # Phase 12: UI updates
            self._update_ui_state()
            
            # Complete processing
            self._complete_turn_processing()
            
            return True
            
        except Exception as e:
            # Error handling
            self.processing_state = TurnProcessingState.ERROR
            self.processing_timer = 0
            print(f'Turn processing error: {e}')
            return False
    
    def update_processing_timer(self) -> None:
        '''Update processing timer and handle transitions (called from main loop)'''
        if self.processing_state == TurnProcessingState.PROCESSING:
            self.processing_timer -= 1
            if self.processing_timer <= 0:
                # Timer expired, force completion to prevent stuck states
                self._reset_processing_state()
    
    def _reset_processing_state(self) -> None:
        '''Reset processing state (internal cleanup)'''
        self.processing_state = TurnProcessingState.IDLE
        self.processing_timer = 0
        # Also reset legacy flags for compatibility
        self.game_state.turn_processing = False
        self.game_state.turn_processing_timer = 0
    
    def _complete_turn_processing(self) -> None:
        '''Complete turn processing successfully'''
        self.processing_state = TurnProcessingState.COMPLETE
        # Immediately reset to idle to prevent stuck states
        self._reset_processing_state()
    
    # Phase implementation methods (delegating to game_state for now)
    # These could be further extracted in future monolith breakdown sessions
    
    def _handle_message_history(self):
        '''Handle scrollable event log message history'''
        gs = self.game_state
        if gs.scrollable_event_log_enabled and gs.messages:
            turn_header = f'=== Turn {gs.turn} ==='
            gs.event_log_history.append(turn_header)
            gs.event_log_history.extend(gs.messages)
        gs.messages = []
    
    def _execute_selected_actions(self):
        '''Execute all selected gameplay actions'''
        gs = self.game_state
        for idx in gs.selected_gameplay_actions:
            action = gs.gameplay_actions[idx]
            
            # Get delegation info
            delegation_info = getattr(gs, '_action_delegations', {}).get(idx, {
                'delegated': False,
                'effectiveness': 1.0,
                'ap_cost': action.get('ap_cost', 1)
            })
            
            ap_cost = delegation_info['ap_cost']
            effectiveness = delegation_info['effectiveness']
            
            # Deduct Action Points
            gs.action_points -= ap_cost
            gs.ap_spent_this_turn = True
            gs.ap_glow_timer = 30
            
            # Invalidate action availability cache
            from src.services.action_availability_manager import get_action_availability_manager
            get_action_availability_manager().invalidate_cache()
            
            # Deduct money cost
            action_cost = gs._get_action_cost(action)
            gs._add('money', -action_cost)
            
            # Log and execute action
            action['name']
            effect_type = action.get('effect_type', 'unknown')
            gs._execute_action_with_effectiveness(action, effect_type, effectiveness)
        
        # Clear selections for next turn
        gs.selected_gameplay_actions = []
        gs.selected_gameplay_action_instances = []
        gs.gameplay_action_clicks_this_turn = {}
        gs._action_delegations = {}
    
    def _process_employee_productivity(self):
        '''Process employee productivity and research progress'''
        gs = self.game_state
        
        # Update employee productivity and compute consumption (weekly cycle)
        gs._update_employee_productivity()

        # Check if research threshold reached for paper publication
        if gs.research_progress >= 100:
            papers_to_publish = gs.research_progress // 100
            gs.papers_published += papers_to_publish
            gs.research_progress = gs.research_progress % 100
            gs._add('reputation', papers_to_publish * 5)  # Papers boost reputation
            gs.messages.append(f'Research paper{'s' if papers_to_publish > 1 else ''} published! (+{papers_to_publish}, total: {gs.papers_published})')
            # Play Zabinga sound for paper completion
            gs.sound_manager.play_zabinga_sound()
    
    def _process_staff_maintenance(self):
        '''Process staff maintenance costs and effects'''
        gs = self.game_state
        
        # Staff maintenance logic (existing implementation)
        total_staff = gs.staff + gs.admin_staff + gs.research_staff + gs.ops_staff
        if total_staff > 0:
            # Calculate maintenance costs
            first_staff_maintenance = 600
            additional_staff_maintenance = 800
            
            if total_staff == 1:
                maintenance_cost = first_staff_maintenance
            else:
                maintenance_cost = first_staff_maintenance + (total_staff - 1) * additional_staff_maintenance
            
            # Apply maintenance
            if gs.money >= maintenance_cost:
                gs._add('money', -maintenance_cost, f'Staff maintenance for {total_staff} staff')
            else:
                # Handle unpaid staff (existing logic)
                unpaid_amount = maintenance_cost - gs.money
                gs._add('money', -gs.money)  # Spend all remaining money
                
                if 'comfy_chairs' in gs.upgrade_effects:
                    gs.messages.append('Comfy chairs helped staff endure unpaid turn.')
                else:
                    staff_loss = max(1, total_staff // 3)
                    gs._add('staff', -staff_loss, f'Staff left due to unpaid maintenance (${unpaid_amount:,} short)')
        
        # Office Cat upkeep costs (if adopted) - part of responsible pet ownership
        self._process_office_cat_upkeep()
    
    def _process_office_cat_upkeep(self):
        '''Process office cat upkeep costs and morale benefits'''
        gs = self.game_state
        
        if not getattr(gs, 'office_cat_adopted', False):
            return
            
        # Weekly cat food costs: $1.25 (wet) + $0.80 (dry) = $2.05/day * 7 = $14.35/week
        cat_food_cost = 14  # Rounded down for game balance
        gs._add('money', -cat_food_cost)
        gs.office_cat_total_food_cost = getattr(gs, 'office_cat_total_food_cost', 0) + cat_food_cost
        gs.messages.append(f'[CAT] Cat upkeep: ${cat_food_cost} (total: ${gs.office_cat_total_food_cost})')
        
        # Small morale benefit (reduce doom slightly) - dev engagement reward
        from src.services.deterministic_rng import get_rng
        if get_rng().random(f'cat_morale_turn_{gs.turn}') < 0.3:  # 30% chance per turn
            gs._add('doom', -1)
            gs.messages.append('[PAWS] Office cat provides small morale boost!')
        
        # Update cat love emoji timer
        if hasattr(gs, 'office_cat_love_emoji_timer') and gs.office_cat_love_emoji_timer > 0:
            gs.office_cat_love_emoji_timer -= 1
    
    def _process_opponents(self):
        '''Process opponent turns and doom contributions'''
        gs = self.game_state
        
        # Process doom calculations first
        doom_rise = 1  # Base doom increase (dramatically reduced for extended gameplay)
        
        # Safety research doom reduction
        if gs.research_staff > 0:
            doom_reduction = gs.research_staff * 3.5  # Increased from 2.5 for better staff ROI
            doom_rise = max(0, doom_rise - doom_reduction)
            gs.messages.append(f'Safety researchers reduced doom increase by {doom_reduction:.1f}')
        
        # Capabilities research doom increase
        capabilities_researchers = sum(1 for r in getattr(gs, 'researchers', []) 
                                     if getattr(r, 'specialization', '') == 'capabilities')
        if capabilities_researchers > 0:
            capabilities_doom = capabilities_researchers * 3.0
            doom_rise += capabilities_doom
            gs.messages.append(f'Capabilities research increased doom risk by {capabilities_doom:.1f}')
        
        # Process opponents
        opponent_doom = 0
        for opponent in gs.opponents:
            messages = opponent.take_turn(gs.turn)
            gs.messages.extend(messages)
            opponent_doom += opponent.get_impact_on_doom()
        
        # Apply total doom increase
        doom_rise += opponent_doom
        total_doom_increase = doom_rise
        gs.doom = min(gs.max_doom, gs.doom + doom_rise)
        
        # Add compact doom summary for debugging
        doom_sources = []
        if total_doom_increase > 0:
            doom_sources.append(f'Base+{1}')  # We know base is 1 now
        if opponent_doom > 0:
            doom_sources.append(f'Opponents+{opponent_doom}')
        if hasattr(gs, 'research_staff') and gs.research_staff > 0:
            doom_sources.append(f'Safety-{gs.research_staff * 3.5:.1f}')
        
        if doom_sources:
            gs.messages.append(f'[DOOM] Turn doom change: {' '.join(doom_sources)} = +{total_doom_increase}')
        
        # Advance researchers
        if hasattr(gs, 'researchers') and gs.researchers:
            gs.advance_researchers()
    
    def _check_milestones(self):
        '''Check and process milestone triggers'''
        gs = self.game_state
        gs._check_board_member_milestone()
    
    def _process_deferred_events(self):
        '''Process deferred events'''
        gs = self.game_state
        if hasattr(gs, 'deferred_events'):
            gs.deferred_events.tick_all_events(gs)
    
    def _advance_turn(self):
        '''Advance turn counter and related systems'''
        gs = self.game_state
        
        gs.turn += 1
        
        # Update RNG for new turn
        from src.services.deterministic_rng import get_rng
        get_rng().set_turn(gs.turn)
        
        # Advance economic systems
        gs.economic_config.advance_compute_cost_reduction()
        
        # Advance game clock
        gs.game_clock.tick()
        formatted_date = gs.game_clock.get_formatted_date()
        gs.messages.append(f'Week of {formatted_date} (Mon)')
        
        # Reset action points for new turn
        calculated_max_ap = gs.calculate_max_ap()
        gs.max_action_points = calculated_max_ap
        gs.action_points = calculated_max_ap
        gs.ap_spent_this_turn = False
        
        # Decay AP glow effect
        if gs.ap_glow_timer > 0:
            gs.ap_glow_timer -= 1
    
    def _check_game_over_conditions(self):
        '''Check win/loss conditions'''
        gs = self.game_state
        
        # Store messages in scrollable log if enabled
        if gs.scrollable_event_log_enabled and gs.messages:
            current_turn_header = f'=== Turn {gs.turn} ==='
            if not (gs.event_log_history and current_turn_header in gs.event_log_history[-5:]):
                gs.event_log_history.append(current_turn_header)
            gs.event_log_history.extend(gs.messages)
        
        # Log turn summary
        gs.logger.log_turn_summary(gs.turn, gs.money, gs.staff, gs.reputation, gs.doom)
        
        # Check game over conditions
        game_end_reason = None
        
        if gs.doom >= gs.max_doom:
            gs.game_over = True
            game_end_reason = 'p(Doom) reached maximum'
            gs.messages.append('p(Doom) has reached maximum! The world is lost.')
        else:
            # Check opponent victory
            for opponent in gs.opponents:
                if opponent.progress >= 100:
                    gs.game_over = True
                    game_end_reason = f'{opponent.name} deployed dangerous AGI'
                    gs.messages.append(f'{opponent.name} has deployed dangerous AGI. Game over!')
                    break
        
        # Check staff loss condition if enabled
        if not gs.game_over and gs.staff == 0:
            from src.services.config_manager import get_current_config
            config = get_current_config()
            staff_loss_enabled = config.get('resource_limits', {}).get('enable_staff_loss_condition', False)
            
            if staff_loss_enabled:
                gs.game_over = True
                game_end_reason = 'All staff left'
                gs.messages.append('All your staff have left. Game over!')
        
        # Clamp resources
        gs.staff = max(0, gs.staff)
        gs.reputation = max(0, gs.reputation)
        gs.money = max(gs.money, 0)
        
        # Handle game over scenario
        if gs.game_over and game_end_reason:
            from src.features.end_game_scenarios import EndGameScenariosManager
            scenarios_manager = EndGameScenariosManager()
            gs.end_game_scenario = scenarios_manager.get_scenario(gs)
            
            if gs.end_game_scenario:
                gs.messages.append(f'GAME OVER: {gs.end_game_scenario.title}')
            
            # Final logging and leaderboard
            final_resources = {
                'money': gs.money,
                'staff': gs.staff,
                'reputation': gs.reputation,
                'doom': gs.doom,
                'turn': gs.turn
            }
            gs.logger.log_game_end(game_end_reason, gs.turn, final_resources)
            
            # Update leaderboard
            success, rank, session = gs.leaderboard_manager.end_game_session(gs)
            if success:
                print(f'Game session ended. Final rank: {rank}')
    
    def _update_ui_state(self):
        '''Update UI transitions and state'''
        gs = self.game_state
        gs._update_ui_transitions()
