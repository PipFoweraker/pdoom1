'''Research System Management Module

This module handles all research quality management, technical debt tracking,
researcher assignments, and related functionality extracted from GameState.

Created as part of the monolith extraction effort to improve maintainability
and separation of concerns.
'''

from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING
from src.services.deterministic_rng import get_rng
from src.core.research_quality import ResearchQuality, ResearchProject

if TYPE_CHECKING:
    from src.core.game_state import GameState


class ResearchSystemManager:
    '''Manages research quality, technical debt, and researcher assignments.'''
    
    def __init__(self, game_state: 'GameState') -> None:
        '''Initialize research system with reference to game state.'''
        self.game_state = game_state
    
    # --- Research Quality and Project Management --- #
    
    def set_research_quality(self, quality: ResearchQuality) -> None:
        '''
        Set the current research quality approach for future research actions.
        
        Args:
            quality: The research quality level to use (rushed, standard, thorough)
        '''
        self.game_state.current_research_quality = quality
        self.game_state.messages.append(f'Research approach set to: {quality.value.title()}')
        
        # Unlock the research quality system on first use
        if not self.game_state.research_quality_unlocked:
            self.game_state.research_quality_unlocked = True
            self.game_state.messages.append('? Research Quality System unlocked! Choose your approach wisely.')
    
    def create_research_project(self, name: str, base_cost: int, base_duration: int) -> ResearchProject:
        '''
        Create a new research project with the current quality settings.
        
        Args:
            name: Project name/identifier
            base_cost: Base monetary cost
            base_duration: Base time cost in action points
            
        Returns:
            Configured ResearchProject instance
        '''
        project = ResearchProject(name, base_cost, base_duration)
        project.set_quality_level(self.game_state.current_research_quality)
        self.game_state.active_research_projects.append(project)
        return project
    
    def complete_research_project(self, project: ResearchProject) -> None:
        '''
        Mark a research project as completed and apply debt changes.
        
        Args:
            project: The research project to complete
        '''
        if project in self.game_state.active_research_projects:
            self.game_state.active_research_projects.remove(project)
        
        project.completed = True
        self.game_state.completed_research_projects.append(project)
        
        # Apply technical debt changes
        modifiers = project.get_quality_modifiers()
        if modifiers.debt_change != 0:
            if modifiers.debt_change > 0:
                self.game_state.technical_debt.add_debt(modifiers.debt_change)
                self.game_state.messages.append(f'[WARNING]? Technical debt increased by {modifiers.debt_change} points')
            else:
                reduced = self.game_state.technical_debt.reduce_debt(abs(modifiers.debt_change))
                if reduced > 0:
                    self.game_state.messages.append(f'? Technical debt reduced by {reduced} points')
    
    # --- Technical Debt Management --- #
    
    def execute_debt_reduction_action(self, action_name: str) -> bool:
        '''
        Execute a technical debt reduction action.
        
        Args:
            action_name: Name of the debt reduction action to execute
            
        Returns:
            True if action was successfully executed, False otherwise
        '''
        from src.core.research_quality import get_debt_reduction_actions
        
        debt_actions = get_debt_reduction_actions()
        action = next((a for a in debt_actions if a['name'] == action_name), None)
        
        if not action:
            return False
        
        # Check cost requirements
        if action.get('cost', 0) > self.game_state.money:
            self.game_state.messages.append(f'? Insufficient funds for {action_name}')
            return False
        
        # Check staff requirements
        if action.get('requires_staff', False):
            staff_type = action.get('staff_type', 'research_staff')
            min_staff = action.get('min_staff', 1)
            available_staff = getattr(self.game_state, staff_type, 0)
            
            if available_staff < min_staff:
                self.game_state.messages.append(f'? Need {min_staff} {staff_type.replace('_', ' ')} for {action_name}')
                return False
        
        # Check action points
        ap_cost = action.get('ap_cost', 1)
        if self.game_state.action_points < ap_cost:
            self.game_state.messages.append(f'? Need {ap_cost} Action Points for {action_name}')
            return False
        
        # Execute the action
        self.game_state.action_points -= ap_cost
        
        if action_name == 'Refactoring Sprint':
            cost = self.game_state._get_action_cost(action)
            self.game_state._add('money', -cost)
            debt_reduction = get_rng().randint(*action['debt_reduction'], 'randint_context')
            reduced = self.game_state.technical_debt.reduce_debt(debt_reduction)
            self.game_state.messages.append(f'? Refactoring sprint completed! Reduced technical debt by {reduced} points')
            
        elif action_name == 'Safety Audit':
            cost = self.game_state._get_action_cost(action)
            self.game_state._add('money', -cost)
            reduced = self.game_state.technical_debt.reduce_debt(action['debt_reduction'][0])
            rep_bonus = action.get('reputation_bonus', 0)
            if rep_bonus > 0:
                self.game_state._add('reputation', rep_bonus)
            self.game_state.messages.append(f'[SHIELD]? Safety audit completed! Reduced debt by {reduced} points, gained reputation')
            
        elif action_name == 'Code Review':
            available_researchers = getattr(self.game_state, 'research_staff', 0)
            cost_per = action['cost_per_researcher']
            total_cost = cost_per * available_researchers
            
            if self.game_state.money < total_cost:
                self.game_state.messages.append(f'? Need ${total_cost}k for full code review')
                return False
                
            self.game_state._add('money', -total_cost)
            debt_reduction_per = action['debt_reduction_per_researcher']
            total_reduction = debt_reduction_per * available_researchers
            reduced = self.game_state.technical_debt.reduce_debt(total_reduction)
            self.game_state.messages.append(f'? Code review with {available_researchers} researchers completed! Reduced debt by {reduced} points')
        
        return True
    
    def execute_technical_debt_audit(self) -> Dict[str, Any]:
        '''
        Execute a technical debt audit requiring Administrator staff.
        Reveals exact debt numbers and provides detailed breakdown.
        
        Returns:
            Dict with audit results, or empty dict if audit cannot be performed
        '''
        # Check if administrator is available
        if self.game_state.admin_staff < 1:
            self.game_state.messages.append('? Technical debt audit requires at least 1 Administrator')
            return {}
        
        # Check action points cost
        audit_ap_cost = 2
        if self.game_state.action_points < audit_ap_cost:
            self.game_state.messages.append(f'? Technical debt audit requires {audit_ap_cost} Action Points')
            return {}
        
        # Perform the audit
        self.game_state.action_points -= audit_ap_cost
        
        # Get detailed debt breakdown
        debt_summary = self.game_state.technical_debt.get_debt_summary()
        
        # Calculate risk assessment
        speed_penalty = self.game_state.technical_debt.get_research_speed_penalty()
        accident_chance = self.game_state.technical_debt.get_accident_chance()
        reputation_risk = self.game_state.technical_debt.has_reputation_risk()
        system_failure_risk = self.game_state.technical_debt.can_trigger_system_failure()
        
        # Determine risk level for UI display
        total_debt = debt_summary['total']
        if total_debt <= 5:
            risk_level = 'Low Risk'
            risk_color = 'green'
        elif total_debt <= 15:
            risk_level = 'Medium Risk' 
            risk_color = 'yellow'
        else:
            risk_level = 'High Risk'
            risk_color = 'red'
        
        # Generate audit report
        audit_results = {
            'total_debt': total_debt,
            'debt_breakdown': debt_summary,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'speed_penalty_percent': int((1.0 - speed_penalty) * 100),
            'accident_chance_percent': int(accident_chance * 100),
            'reputation_risk': reputation_risk,
            'system_failure_risk': system_failure_risk,
            'recommendations': []
        }
        
        # Add specific recommendations
        if total_debt > 20:
            audit_results['recommendations'].append('CRITICAL: Execute emergency refactoring sprint immediately')
            audit_results['recommendations'].append('Consider halting new development until debt is reduced')
        elif total_debt > 15:
            audit_results['recommendations'].append('HIGH PRIORITY: Schedule comprehensive safety audit')
            audit_results['recommendations'].append('Reduce research pace and focus on quality')
        elif total_debt > 10:
            audit_results['recommendations'].append('MODERATE: Plan refactoring sprint within 3 turns')
            audit_results['recommendations'].append('Monitor for system failures')
        elif total_debt > 5:
            audit_results['recommendations'].append('LOW: Consider code review sessions')
            audit_results['recommendations'].append('Maintain current quality standards')
        else:
            audit_results['recommendations'].append('EXCELLENT: Technical debt well-managed')
            audit_results['recommendations'].append('Current practices are sustainable')
        
        # Add per-category analysis
        category_analysis = []
        for category, debt in debt_summary.items():
            if category != 'total' and debt > 0:
                category_analysis.append(f'{category.replace('_', ' ').title()}: {debt} points')
        
        if category_analysis:
            audit_results['category_breakdown'] = category_analysis
        
        # Log the audit
        self.game_state.messages.append(f'[CHART] Technical Debt Audit completed by Administrator')
        self.game_state.messages.append(f'[TARGET] Risk Assessment: {risk_level} ({total_debt} total debt points)')
        
        if audit_results['recommendations']:
            self.game_state.messages.append(f'[LIST] Top Recommendation: {audit_results['recommendations'][0]}')
        
        # Store audit results for UI display
        if not hasattr(self.game_state, 'last_audit_results'):
            self.game_state.last_audit_results = {}
        self.game_state.last_audit_results = audit_results
        
        return audit_results
    
    def get_debt_risk_indicator(self) -> str:
        '''
        Get simplified debt risk indicator for UI without requiring audit.
        Returns 'Low Risk', 'Medium Risk', or 'High Risk'.
        '''
        total_debt = self.game_state.technical_debt.accumulated_debt
        
        if total_debt <= 5:
            return 'Low Risk'
        elif total_debt <= 15:
            return 'Medium Risk'
        else:
            return 'High Risk'
    
    def get_research_effectiveness_modifier(self) -> float:
        '''
        Get the current research effectiveness modifier based on technical debt.
        
        Returns:
            Multiplier for research effectiveness (0.85 = 15% penalty)
        '''
        return self.game_state.technical_debt.get_research_speed_penalty()
    
    def check_debt_consequences(self) -> None:
        '''
        Check and apply consequences of accumulated technical debt.
        Called during end_turn processing.
        '''
        self.game_state.technical_debt.accumulated_debt
        
        # Check for accident events
        accident_chance = self.game_state.technical_debt.get_accident_chance()
        if accident_chance > 0 and get_rng().random('random_context') < accident_chance:
            self._trigger_debt_accident()
        
        # Check for reputation risks
        if self.game_state.technical_debt.has_reputation_risk() and get_rng().random('random_context') < 0.1:
            rep_loss = get_rng().randint(1, 3, 'randint_context')
            self.game_state._add('reputation', -rep_loss)
            self.game_state.messages.append(f'[NEWS] Technical debt issues exposed in media! Lost {rep_loss} reputation')
        
        # Check for system failure events
        if self.game_state.technical_debt.can_trigger_system_failure() and get_rng().random('random_context') < 0.05:
            self._trigger_system_failure()
    
    def get_debt_summary_for_ui(self) -> Dict[str, int]:
        '''
        Get technical debt summary for UI display.
        
        Returns:
            Dictionary with debt information for UI rendering
        '''
        summary = self.game_state.technical_debt.get_debt_summary()
        summary['research_penalty'] = int((1.0 - self.get_research_effectiveness_modifier()) * 100)
        summary['accident_chance'] = int(self.game_state.technical_debt.get_accident_chance() * 100)
        summary['has_reputation_risk'] = self.game_state.technical_debt.has_reputation_risk()
        summary['can_system_failure'] = self.game_state.technical_debt.can_trigger_system_failure()
        return summary
    
    def _trigger_debt_accident(self) -> None:
        '''Trigger a technical debt-related accident.'''
        accident_types = [
            ('Research setback due to buggy code', lambda: self.game_state._add('research_progress', -get_rng().randint(5, 15, 'randint_context'))),
            ('Security breach from poor validation', lambda: self.game_state._add('reputation', -get_rng().randint(2, 4, 'randint_context'))),
            ('Compute system crash from technical debt', lambda: self.game_state._add('compute', -get_rng().randint(5, 10, 'randint_context'))),
        ]
        
        accident_name, accident_effect = get_rng().choice(accident_types, 'choice_context')
        accident_effect()
        self.game_state.messages.append(f'[EXPLOSION] ACCIDENT: {accident_name}')
    
    def _trigger_system_failure(self) -> None:
        '''Trigger a major system failure due to excessive technical debt.'''
        failure_types = [
            ('Critical system failure! Major research setback', 
             lambda: (self.game_state._add('research_progress', -get_rng().randint(20, 40, 'randint_context')),
                     self.game_state._add('reputation', -get_rng().randint(3, 6, 'randint_context')))),
            ('Catastrophic infrastructure collapse! Financial and reputation damage',
             lambda: (self.game_state._add('money', -get_rng().randint(50, 100, 'randint_context')),
                     self.game_state._add('reputation', -get_rng().randint(4, 8, 'randint_context')))),
            ('Major safety incident due to accumulated shortcuts!',
             lambda: (self.game_state._add('doom', get_rng().randint(10, 20, 'randint_context'), 'technical debt cascade failure'),
                     self.game_state._add('reputation', -get_rng().randint(5, 10, 'randint_context')))),
        ]
        
        failure_name, failure_effect = get_rng().choice(failure_types, 'choice_context')
        failure_effect()
        self.game_state.messages.append(f'[ALERT] SYSTEM FAILURE: {failure_name}')
        
        # Reduce some technical debt after a major failure (lessons learned)
        reduced = self.game_state.technical_debt.reduce_debt(get_rng().randint(3, 7, 'randint_context'))
        self.game_state.messages.append(f'Lessons learned from failure. Technical debt reduced by {reduced} points.')
    
    # --- Researcher Assignment System --- #
    
    def assign_researcher_to_task(self, researcher_id: str, task_name: str, 
                                  quality_override: Optional[ResearchQuality] = None) -> bool:
        '''
        Assign a specific researcher to a specific task.
        
        Args:
            researcher_id: Unique identifier for the researcher
            task_name: Name of the research task/action
            quality_override: Optional quality level override for this task
            
        Returns:
            True if assignment was successful, False otherwise
        '''
        # Find the researcher
        researcher = self.get_researcher_by_id(researcher_id)
        if not researcher:
            self.game_state.messages.append(f'? Researcher {researcher_id} not found')
            return False
        
        # Check if researcher is already assigned
        if researcher_id in self.game_state.researcher_assignments:
            old_task = self.game_state.researcher_assignments[researcher_id]
            self.game_state.messages.append(f'[LIST] {researcher.name} reassigned from {old_task} to {task_name}')
        
        # Make the assignment
        self.game_state.researcher_assignments[researcher_id] = task_name
        
        # Set quality override if provided
        if quality_override:
            self.game_state.task_quality_overrides[task_name] = quality_override
        
        self.game_state.messages.append(f'? {researcher.name} assigned to {task_name}')
        return True
    
    def unassign_researcher(self, researcher_id: str) -> bool:
        '''
        Remove assignment for a specific researcher.
        
        Args:
            researcher_id: Unique identifier for the researcher
            
        Returns:
            True if unassignment was successful, False otherwise
        '''
        researcher = self.get_researcher_by_id(researcher_id)
        if not researcher:
            return False
        
        if researcher_id in self.game_state.researcher_assignments:
            task_name = self.game_state.researcher_assignments[researcher_id]
            del self.game_state.researcher_assignments[researcher_id]
            self.game_state.messages.append(f'[LIST] {researcher.name} unassigned from {task_name}')
            return True
        
        return False
    
    def set_researcher_default_quality(self, researcher_id: str, quality: ResearchQuality) -> bool:
        '''
        Set the default research quality preference for a researcher.
        
        Args:
            researcher_id: Unique identifier for the researcher
            quality: Default quality level for this researcher
            
        Returns:
            True if setting was successful, False otherwise
        '''
        researcher = self.get_researcher_by_id(researcher_id)
        if not researcher:
            return False
        
        self.game_state.researcher_default_quality[researcher_id] = quality
        quality_name = quality.value.title()
        self.game_state.messages.append(f'?? {researcher.name}\'s default quality set to {quality_name}')
        return True
    
    def get_researcher_by_id(self, researcher_id: str) -> Optional[Any]:
        '''
        Get a researcher by their unique identifier.
        
        Args:
            researcher_id: Unique identifier for the researcher
            
        Returns:
            Researcher object if found, None otherwise
        '''
        for researcher in self.game_state.researchers:
            if getattr(researcher, 'id', researcher.name) == researcher_id:
                return researcher
        return None
    
    def get_task_quality_setting(self, task_name: str, assigned_researcher_id: str = None) -> ResearchQuality:
        '''
        Get the effective quality setting for a task.
        
        Args:
            task_name: Name of the research task
            assigned_researcher_id: ID of researcher assigned to this task
            
        Returns:
            Effective ResearchQuality level for the task
        '''
        # Check task-specific override first
        if task_name in self.game_state.task_quality_overrides:
            return self.game_state.task_quality_overrides[task_name]
        
        # Check researcher default if researcher is assigned
        if assigned_researcher_id and assigned_researcher_id in self.game_state.researcher_default_quality:
            return self.game_state.researcher_default_quality[assigned_researcher_id]
        
        # Fall back to global research quality
        return self.game_state.current_research_quality
    
    def get_researcher_assignments_summary(self) -> Dict[str, Any]:
        '''
        Get a summary of current researcher assignments for UI display.
        
        Returns:
            Dictionary with assignment information
        '''
        summary = {
            'assigned': {},
            'unassigned': [],
            'task_qualities': {}
        }
        
        # Track assigned researchers
        for researcher_id, task_name in self.game_state.researcher_assignments.items():
            researcher = self.get_researcher_by_id(researcher_id)
            if researcher:
                summary['assigned'][researcher_id] = {
                    'name': researcher.name,
                    'task': task_name,
                    'specialization': researcher.specialization,
                    'quality_setting': self.get_task_quality_setting(task_name, researcher_id).value
                }
        
        # Track unassigned researchers
        assigned_ids = set(self.game_state.researcher_assignments.keys())
        for researcher in self.game_state.researchers:
            researcher_id = getattr(researcher, 'id', researcher.name)
            if researcher_id not in assigned_ids:
                summary['unassigned'].append({
                    'id': researcher_id,
                    'name': researcher.name,
                    'specialization': researcher.specialization,
                    'default_quality': self.game_state.researcher_default_quality.get(researcher_id, self.game_state.current_research_quality).value
                })
        
        return summary
    
    # --- Technical Debt Dialog System --- #
    
    def trigger_technical_debt_dialog(self) -> None:
        '''Trigger the technical debt dialog with available debt management options.'''
        debt_options = []
        
        # Check current technical debt level
        current_debt = getattr(self.game_state.technical_debt, 'accumulated_debt', 0) if hasattr(self.game_state, 'technical_debt') else 0
        
        # Refactoring Sprint
        debt_options.append({
            'id': 'refactoring_sprint',
            'name': 'Refactoring Sprint',
            'description': 'Intensive code refactoring to reduce technical debt and improve maintainability.', 
            'cost': self.game_state.economic_config.get_technical_debt_cost('refactoring_sprint') if hasattr(self.game_state, 'economic_config') else 250,
            'ap_cost': 2,
            'available': current_debt >= 5,  # Need significant debt to justify
            'details': f'Requires 5+ debt (current: {current_debt}). Major debt reduction effort.'
        })
        
        # Technical Debt Audit (Safety Audit)
        debt_options.append({
            'id': 'technical_debt_audit',
            'name': 'Technical Debt Audit',
            'description': 'External safety audit to identify and assess technical debt risks.',
            'cost': self.game_state.economic_config.get_technical_debt_cost('safety_audit_external') if hasattr(self.game_state, 'economic_config') else 400,
            'ap_cost': 1,
            'available': current_debt >= 3,  # Need some debt to audit
            'details': f'Requires 3+ debt (current: {current_debt}). Professional assessment of risks.'
        })
        
        # Code Review
        debt_options.append({
            'id': 'code_review', 
            'name': 'Code Review',
            'description': 'Systematic peer code review to prevent technical debt accumulation.',
            'cost': 80,
            'ap_cost': 1,
            'available': self.game_state.research_staff >= 1 and current_debt >= 1,
            'details': f'Requires 1+ research staff and 1+ debt. Staff: {self.game_state.research_staff}, Debt: {current_debt}'
        })
        
        self.game_state.pending_technical_debt_dialog = {
            'options': debt_options,
            'title': 'Technical Debt Management',
            'description': 'Select a technical debt management operation to execute.'
        }
    
    def select_technical_debt_option(self, option_id: str) -> Tuple[bool, str]:
        '''Handle player selection of a technical debt option.'''
        if not self.game_state.pending_technical_debt_dialog:
            return False, 'No technical debt dialog active.'
        
        # Find the selected option
        selected_option = None
        for option in self.game_state.pending_technical_debt_dialog['options']:
            if option['id'] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return False, f'Invalid technical debt option: {option_id}'
        
        if not selected_option['available']:
            return False, f'Technical debt option not available: {selected_option['name']}'
        
        # Check costs
        if self.game_state.money < selected_option['cost']:
            return False, f'Insufficient funds. Need ${selected_option['cost']}, have ${self.game_state.money}.'
        
        if self.game_state.action_points < selected_option['ap_cost']:
            return False, f'Insufficient action points. Need {selected_option['ap_cost']}, have {self.game_state.action_points}.'
        
        # Execute the selected technical debt option
        if option_id == 'refactoring_sprint':
            # Deduct costs
            self.game_state.money -= selected_option['cost']
            self.game_state.action_points -= selected_option['ap_cost']
            
            # Execute refactoring sprint functionality
            self.execute_debt_reduction_action('Refactoring Sprint')
            
        elif option_id == 'technical_debt_audit':
            # Deduct costs
            self.game_state.money -= selected_option['cost']
            self.game_state.action_points -= selected_option['ap_cost']
            
            # Execute technical debt audit functionality
            self.execute_debt_reduction_action('Safety Audit')
            
        elif option_id == 'code_review':
            # Deduct costs
            self.game_state.money -= selected_option['cost'] 
            self.game_state.action_points -= selected_option['ap_cost']
            
            # Execute code review functionality
            self.execute_debt_reduction_action('Code Review')
            
        else:
            return False, f'Unknown technical debt option: {option_id}'
        
        # Clear the technical debt dialog
        self.game_state.pending_technical_debt_dialog = None
        return True, 'Technical debt management operation complete.'
    
    def dismiss_technical_debt_dialog(self) -> None:
        '''Dismiss the technical debt dialog without making a selection.'''
        from src.core.dialog_manager import DialogManager
        DialogManager.dismiss_dialog(self.game_state, 'technical_debt')