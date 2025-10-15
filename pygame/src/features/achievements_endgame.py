'''
Achievements & Endgame System

This module implements achievement tracking, enhanced warnings, and victory conditions
for P(Doom). It expands beyond binary win/lose scenarios to include partial successes,
pyrrhic victories, and comprehensive endgame analysis.

Key Features:
- Achievement milestones tracking progress toward ultimate goals
- Enhanced warning system for critical game state thresholds
- Pyrrhic victory conditions based on cost-benefit analysis
- Deep integration with existing systems (technical debt, economic cycles, opponents)
- Semi-programmatic endgame text generation based on player strategy analysis

Architecture follows established patterns from technical_failures.py and economic_cycles.py.
'''

from typing import Dict, List, Optional, Any
from enum import Enum


class AchievementType(Enum):
    '''Categories of achievements for organizational purposes.'''
    SURVIVAL = 'survival'           # Time-based survival milestones
    WORKFORCE = 'workforce'         # Employee and productivity achievements  
    RESEARCH = 'research'           # Research and publication accomplishments
    FINANCIAL = 'financial'        # Economic stability and growth
    SAFETY = 'safety'              # P(Doom) reduction and safety achievements
    REPUTATION = 'reputation'      # Reputation and influence milestones
    COMPETITIVE = 'competitive'    # Opponent-related achievements
    RARE = 'rare'                  # Exceptional circumstances achievements


class Achievement:
    '''Represents a single achievement with tracking and reward information.'''
    
    def __init__(self, achievement_id: str, name: str, description: str, 
                 achievement_type: AchievementType, check_condition, 
                 rarity: str = 'common', unlock_message: str = None):
        self.id = achievement_id
        self.name = name
        self.description = description
        self.type = achievement_type
        self.check_condition = check_condition  # Function that takes game_state and returns bool
        self.rarity = rarity  # 'common', 'uncommon', 'rare', 'legendary'
        self.unlock_message = unlock_message or f'Achievement Unlocked: {name}'
        self.unlocked_turn = None  # Turn when achievement was unlocked
        
    def check_unlock(self, game_state) -> bool:
        '''Check if this achievement should be unlocked.'''
        try:
            return self.check_condition(game_state)
        except Exception:
            # Defensive programming - achievement checks should never crash the game
            return False


class EndGameType(Enum):
    '''Extended end game types beyond simple defeat.'''
    DEFEAT = 'defeat'                    # Traditional failure (existing system)
    ACHIEVEMENT_VICTORY = 'achievement'  # Reached ultimate goal (p(Doom) = 0)
    PYRRHIC_VICTORY = 'pyrrhic'         # Victory at severe cost
    CLOSE_CALL_SURVIVAL = 'close_call'  # Survived extreme danger but ongoing risk
    STRATEGIC_SUCCESS = 'strategic'     # Major progress toward goals without completion


class WarningType(Enum):
    '''Types of critical warnings that require player attention.'''
    DOOM_CRITICAL = 'doom_critical'         # High p(Doom) levels
    FINANCIAL_CRISIS = 'financial_crisis'   # Low cash reserves  
    REPUTATION_COLLAPSE = 'reputation_collapse'  # Severe reputation loss
    TECHNICAL_DEBT_CRISIS = 'technical_debt_crisis'  # Unsustainable technical debt
    COMPETITIVE_THREAT = 'competitive_threat'  # Opponents gaining significant advantage


class AchievementsEndgameSystem:
    '''
    Manages achievement tracking, warning systems, and enhanced endgame scenarios.
    
    Integrates with existing game systems to provide comprehensive feedback on
    player performance and progress toward ultimate goals.
    '''
    
    def __init__(self):
        self.achievements = self._initialize_achievements()
        self.unlocked_achievements = set()  # Achievement IDs that have been unlocked
        self.warning_history = []  # Track warnings to avoid spam
        self.strategic_analysis = {}  # Track player strategy patterns
        
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        '''Initialize the comprehensive achievement system.'''
        achievements = {}
        
        # Survival Achievements (Time-based progression)
        achievements['first_month'] = Achievement(
            'first_month', 'First Month Survived', 
            'Survived the initial startup chaos and kept your organization running for 4 turns.',
            AchievementType.SURVIVAL, 
            lambda gs: gs.turn >= 4,
            'common'
        )
        
        achievements['quarter_survival'] = Achievement(
            'quarter_survival', 'Quarterly Survivor',
            'Maintained operations for a full quarter (13 turns) - demonstrating organizational sustainability.',
            AchievementType.SURVIVAL,
            lambda gs: gs.turn >= 13,
            'common'
        )
        
        achievements['yearly_survivor'] = Achievement(
            'yearly_survivor', 'Annual Operations',
            'Sustained operations for an entire year (52 turns) - proving long-term viability.',
            AchievementType.SURVIVAL,
            lambda gs: gs.turn >= 52,
            'uncommon'
        )
        
        achievements['multi_year_veteran'] = Achievement(
            'multi_year_veteran', 'Multi-Year Veteran',
            'Operated successfully for multiple years (104 turns) - demonstrating industry leadership.',
            AchievementType.SURVIVAL,
            lambda gs: gs.turn >= 104,
            'rare'
        )
        
        achievements['campaign_completion'] = Achievement(
            'campaign_completion', '2017-2025 Campaign Veteran',
            'Survived the complete historical period from 2017 to 2025 (450 turns) - witnessed the entire AI revolution.',
            AchievementType.SURVIVAL,
            lambda gs: gs.turn >= 450,
            'legendary'
        )
        
        # Workforce Achievements
        achievements['productive_workforce'] = Achievement(
            'productive_workforce', 'Productive Workforce',
            'Achieved 10+ simultaneously productive employees - demonstrating effective organizational management.',
            AchievementType.WORKFORCE,
            lambda gs: self._count_productive_employees(gs) >= 10,
            'common'
        )
        
        achievements['major_employer'] = Achievement(
            'major_employer', 'Major AI Safety Employer', 
            'Employed 25+ staff members simultaneously - becoming a significant player in the AI safety field.',
            AchievementType.WORKFORCE,
            lambda gs: gs.staff >= 25,
            'uncommon'
        )
        
        achievements['industry_leader'] = Achievement(
            'industry_leader', 'Industry Leadership',
            'Employed 50+ staff members - establishing your organization as an industry leader.',
            AchievementType.WORKFORCE,
            lambda gs: gs.staff >= 50,
            'rare'
        )
        
        # Research Achievements
        achievements['first_publication'] = Achievement(
            'first_publication', 'First Publication',
            'Published your first research paper - contributing to the academic discourse on AI safety.',
            AchievementType.RESEARCH,
            lambda gs: gs.papers_published >= 1,
            'common'
        )
        
        achievements['prolific_researcher'] = Achievement(
            'prolific_researcher', 'Prolific Research Output',
            'Published 10+ research papers - establishing a significant academic presence.',
            AchievementType.RESEARCH,
            lambda gs: gs.papers_published >= 10,
            'uncommon'
        )
        
        achievements['prestigious_publication'] = Achievement(
            'prestigious_publication', 'Prestigious Publication',
            'Achieved high research quality and reputation - likely published in top-tier venues.',
            AchievementType.RESEARCH,
            lambda gs: gs.reputation >= 150 and gs.papers_published >= 5,
            'rare'
        )
        
        # Financial Achievements
        achievements['financial_stability'] = Achievement(
            'financial_stability', 'Financial Stability',
            'Maintained cash reserves of $5,000+ - demonstrating sound financial management.',
            AchievementType.FINANCIAL,
            lambda gs: gs.money >= 5000,
            'common'
        )
        
        achievements['major_funding'] = Achievement(
            'major_funding', 'Major Funding Success',
            'Secured $25,000+ in funding - attracting significant investment in your mission.',
            AchievementType.FINANCIAL,
            lambda gs: gs.money >= 25000,
            'uncommon'
        )
        
        achievements['financial_powerhouse'] = Achievement(
            'financial_powerhouse', 'Financial Powerhouse',
            'Built a war chest of $100,000+ - commanding substantial resources for your mission.',
            AchievementType.FINANCIAL,
            lambda gs: gs.money >= 100000,
            'rare'
        )
        
        # Safety Achievements
        achievements['doom_reducer'] = Achievement(
            'doom_reducer', 'Doom Reducer',
            'Reduced p(Doom) below starting levels - making meaningful progress on existential risk.',
            AchievementType.SAFETY,
            lambda gs: gs.doom < 25,  # Below starting doom of 25
            'uncommon'
        )
        
        achievements['safety_champion'] = Achievement(
            'safety_champion', 'Safety Champion', 
            'Achieved remarkably low p(Doom) levels (<=10%) - demonstrating exceptional safety practices.',
            AchievementType.SAFETY,
            lambda gs: gs.doom <= 10,
            'rare'
        )
        
        achievements['doom_defeater'] = Achievement(
            'doom_defeater', 'Doom Defeater',
            'Achieved the impossible: p(Doom) = 0 - completely solved the AI alignment problem.',
            AchievementType.SAFETY,
            lambda gs: gs.doom <= 0,
            'legendary'
        )
        
        # Reputation Achievements  
        achievements['respected_organization'] = Achievement(
            'respected_organization', 'Respected Organization',
            'Built substantial reputation (100+) - gaining recognition in the AI safety community.',
            AchievementType.REPUTATION,
            lambda gs: gs.reputation >= 100,
            'common'
        )
        
        achievements['influential_voice'] = Achievement(
            'influential_voice', 'Influential Voice',
            'Achieved major influence (150+ reputation) - your organization\'s voice carries significant weight.',
            AchievementType.REPUTATION,
            lambda gs: gs.reputation >= 150,
            'uncommon'
        )
        
        achievements['thought_leader'] = Achievement(
            'thought_leader', 'Thought Leadership',
            'Established thought leadership (200+ reputation) - setting the agenda for AI safety discussions.',
            AchievementType.REPUTATION,
            lambda gs: gs.reputation >= 200,
            'rare'
        )
        
        # Competitive Achievements
        achievements['intelligence_network'] = Achievement(
            'intelligence_network', 'Intelligence Network',
            'Successfully discovered all major AI competitors - maintaining comprehensive situational awareness.',
            AchievementType.COMPETITIVE,
            lambda gs: self._count_discovered_opponents(gs) >= 3,
            'uncommon'
        )
        
        achievements['competitive_advantage'] = Achievement(
            'competitive_advantage', 'Competitive Advantage',
            'Maintained research lead over all known competitors - staying ahead in the AI race.',
            AchievementType.COMPETITIVE,
            lambda gs: self._has_research_lead(gs),
            'rare'
        )
        
        # Rare/Special Achievements
        achievements['crisis_survivor'] = Achievement(
            'crisis_survivor', 'Crisis Survivor',
            'Survived a major technical failure cascade without catastrophic losses.',
            AchievementType.RARE,
            lambda gs: self._survived_major_technical_crisis(gs),
            'rare'
        )
        
        achievements['transparency_champion'] = Achievement(
            'transparency_champion', 'Transparency Champion',
            'Maintained transparency policy through multiple technical failures - building public trust.',
            AchievementType.RARE,
            lambda gs: self._maintained_transparency_through_crisis(gs),
            'rare'
        )
        
        return achievements
    
    def check_new_achievements(self, game_state) -> List[Achievement]:
        '''
        Check for newly unlocked achievements and return them.
        
        Args:
            game_state: Current game state
            
        Returns:
            List of newly unlocked achievements
        '''
        newly_unlocked = []
        
        for achievement_id, achievement in self.achievements.items():
            if (achievement_id not in self.unlocked_achievements and 
                achievement.check_unlock(game_state)):
                
                achievement.unlocked_turn = game_state.turn
                self.unlocked_achievements.add(achievement_id)
                newly_unlocked.append(achievement)
                
        return newly_unlocked
    
    def check_critical_warnings(self, game_state) -> List[Dict[str, Any]]:
        '''
        Check for critical warnings that need immediate player attention.
        
        Args:
            game_state: Current game state
            
        Returns:
            List of warning dictionaries with type, message, and severity
        '''
        warnings = []
        
        # Doom Critical Warnings (expanded from existing >=70% system)
        doom_warnings = [
            (80, 'CRITICAL', 'P(Doom) Warning: 80% Risk Level', 
             'Your probability of doom has reached 80%. Immediate safety measures recommended.'),
            (90, 'SEVERE', 'SEVERE P(Doom) Warning: 90% Risk Level',
             'Existential risk is at 90%. Emergency safety protocols should be implemented immediately.'),
            (95, 'EXTREME', 'EXTREME P(Doom) Warning: 95% Risk Level', 
             'You are approaching catastrophic failure. All resources should focus on safety measures.'),
            (98, 'IMMINENT', 'IMMINENT DOOM Warning: 98% Risk Level',
             'Catastrophic failure is imminent. Only the most drastic safety measures may prevent disaster.')
        ]
        
        for threshold, severity, title, message in doom_warnings:
            if (game_state.doom >= threshold and 
                not self._warning_recently_shown(f'doom_{threshold}')):
                warnings.append({
                    'type': WarningType.DOOM_CRITICAL,
                    'severity': severity,
                    'title': title,
                    'message': message,
                    'threshold': threshold
                })
                self._mark_warning_shown(f'doom_{threshold}')
        
        # Financial Crisis Warnings (based on starting money of $1000)
        starting_money = 1000
        financial_warnings = [
            (0.35, 'WARNING', 'Financial Concern', 
             f'Cash reserves below 35% of starting capital (${int(starting_money * 0.35)}). Monitor spending carefully.'),
            (0.10, 'CRITICAL', 'Financial Crisis', 
             f'Cash reserves critically low - only ${int(starting_money * 0.10)} remaining. Immediate fundraising needed.'),
            (0.05, 'EMERGENCY', 'Financial Emergency',
             f'Cash reserves at emergency levels (${int(starting_money * 0.05)}). Organization at risk of bankruptcy.')
        ]
        
        for threshold, severity, title, message in financial_warnings:
            if (game_state.money <= starting_money * threshold and
                not self._warning_recently_shown(f'financial_{threshold}')):
                warnings.append({
                    'type': WarningType.FINANCIAL_CRISIS,
                    'severity': severity,
                    'title': title,
                    'message': message,
                    'threshold': threshold
                })
                self._mark_warning_shown(f'financial_{threshold}')
        
        # Reputation Collapse Warnings (based on peak reputation achieved)
        peak_reputation = getattr(game_state, 'peak_reputation', game_state.reputation)
        if game_state.reputation > peak_reputation:
            game_state.peak_reputation = game_state.reputation
            peak_reputation = game_state.reputation
            
        if peak_reputation > 50:  # Only warn if they had significant reputation to lose
            reputation_warnings = [
                (0.50, 'WARNING', 'Reputation Decline',
                 f'Reputation has declined 50% from peak ({peak_reputation} ? {game_state.reputation}). Public trust is eroding.'),
                (0.25, 'CRITICAL', 'Reputation Crisis', 
                 f'Reputation has collapsed 75% from peak. Severe damage to public standing and funding prospects.'),
                (0.10, 'EMERGENCY', 'Reputation Emergency',
                 f'Reputation has catastrophically declined 90% from peak. Organization credibility in ruins.')
            ]
            
            for threshold, severity, title, message in reputation_warnings:
                current_ratio = game_state.reputation / peak_reputation
                if (current_ratio <= threshold and
                    not self._warning_recently_shown(f'reputation_{threshold}')):
                    warnings.append({
                        'type': WarningType.REPUTATION_COLLAPSE,
                        'severity': severity,
                        'title': title,
                        'message': message,
                        'threshold': threshold
                    })
                    self._mark_warning_shown(f'reputation_{threshold}')
        
        # Technical Debt Crisis Warnings (if technical debt system is active)
        if hasattr(game_state, 'technical_debt') and hasattr(game_state.technical_debt, 'total_debt'):
            debt_warnings = [
                (15, 'WARNING', 'Technical Debt Concern',
                 'Technical debt is accumulating. Consider safety audits and refactoring efforts.'),
                (25, 'CRITICAL', 'Technical Debt Crisis', 
                 'Technical debt at dangerous levels. Major system failures becoming likely.'),
                (35, 'EMERGENCY', 'Technical Debt Emergency',
                 'Technical debt at catastrophic levels. Immediate debt reduction required.')
            ]
            
            for threshold, severity, title, message in debt_warnings:
                if (game_state.technical_debt.total_debt >= threshold and
                    not self._warning_recently_shown(f'tech_debt_{threshold}')):
                    warnings.append({
                        'type': WarningType.TECHNICAL_DEBT_CRISIS,
                        'severity': severity,
                        'title': title,
                        'message': message,
                        'threshold': threshold
                    })
                    self._mark_warning_shown(f'tech_debt_{threshold}')
        
        # Competitive Threat Warnings
        if hasattr(game_state, 'opponents'):
            for opponent in game_state.opponents:
                if hasattr(opponent, 'progress') and opponent.progress >= 85:
                    warning_key = f'competitor_{opponent.name}_{opponent.progress//5*5}'  # Group by 5% increments
                    if not self._warning_recently_shown(warning_key):
                        warnings.append({
                            'type': WarningType.COMPETITIVE_THREAT,
                            'severity': 'CRITICAL',
                            'title': 'Competitive Threat',
                            'message': f'{opponent.name} is approaching dangerous AGI deployment ({opponent.progress}% progress). Immediate action required.',
                            'threshold': opponent.progress
                        })
                        self._mark_warning_shown(warning_key)
        
        return warnings
    
    def analyze_pyrrhic_victory_conditions(self, game_state) -> Optional[Dict[str, Any]]:
        '''
        Analyze if current game state represents a pyrrhic victory scenario.
        
        A pyrrhic victory occurs when primary goals are achieved but at devastating cost.
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary with pyrrhic victory analysis or None if not applicable
        '''
        # Check if player has achieved primary safety goal (low doom)
        achieved_safety_goal = game_state.doom <= 15  # Significantly below starting 25
        
        if not achieved_safety_goal:
            return None
            
        # Analyze costs paid for this achievement
        costs = []
        severity_score = 0
        
        # Financial devastation
        if game_state.money < 200:  # Less than 20% of starting money
            costs.append('Financial ruin - organization operating on fumes')
            severity_score += 3
        elif game_state.money < 500:  # Less than 50% of starting money
            costs.append('Severe financial strain')
            severity_score += 2
            
        # Reputation collapse
        peak_reputation = getattr(game_state, 'peak_reputation', game_state.reputation)
        if peak_reputation > 75 and game_state.reputation < peak_reputation * 0.3:
            costs.append('Catastrophic reputation loss - public trust destroyed')
            severity_score += 3
        elif peak_reputation > 50 and game_state.reputation < peak_reputation * 0.5:
            costs.append('Severe reputation damage')
            severity_score += 2
            
        # Workforce devastation  
        if game_state.staff < 3:  # Skeleton crew
            costs.append('Organization reduced to skeleton crew')
            severity_score += 2
            
        # Technical debt burden
        if hasattr(game_state, 'technical_debt') and hasattr(game_state.technical_debt, 'total_debt'):
            if game_state.technical_debt.total_debt > 30:
                costs.append('Crippling technical debt - systems barely functional')
                severity_score += 3
            elif game_state.technical_debt.total_debt > 20:
                costs.append('Substantial technical debt burden')
                severity_score += 2
                
        # Global authoritarianism (placeholder for future implementation)
        # if getattr(game_state, 'global_authoritarianism', 0) > 0.7:
        #     costs.append('Global surveillance state established')
        #     severity_score += 4
            
        # Privacy erosion (placeholder for future implementation)  
        # if getattr(game_state, 'privacy_erosion', 0) > 0.8:
        #     costs.append('Personal privacy eliminated')
        #     severity_score += 3
        
        # Only consider it pyrrhic if significant costs were paid
        if severity_score >= 4:
            return {
                'type': 'pyrrhic_victory',
                'severity': severity_score,
                'costs': costs,
                'achievement': f'Reduced p(Doom) to {game_state.doom}%',
                'analysis': f'Victory achieved through devastating sacrifices: {', '.join(costs)}'
            }
            
        return None
    
    def generate_strategic_analysis(self, game_state) -> Dict[str, Any]:
        '''
        Generate comprehensive analysis of player strategy and performance.
        
        This provides contextual information for endgame scenarios and achievement
        descriptions, analyzing the player's dominant strategies and critical moments.
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary containing strategic analysis
        '''
        analysis = {}
        
        # Dominant Strategy Analysis
        strategy_indicators = {
            'safety_focused': 0,
            'growth_focused': 0, 
            'research_focused': 0,
            'financial_focused': 0,
            'competitive_focused': 0
        }
        
        # Analyze resource allocation patterns
        if game_state.doom < 20:  # Below starting doom
            strategy_indicators['safety_focused'] += 2
        if game_state.staff > 15:
            strategy_indicators['growth_focused'] += 2
        if game_state.papers_published > 5:
            strategy_indicators['research_focused'] += 2
        if game_state.money > 5000:
            strategy_indicators['financial_focused'] += 1
        if len([opp for opp in getattr(game_state, 'opponents', []) if hasattr(opp, 'discovered') and opp.discovered]) > 1:
            strategy_indicators['competitive_focused'] += 1
            
        # Technical debt analysis (if available)
        if hasattr(game_state, 'technical_debt'):
            if hasattr(game_state.technical_debt, 'total_debt'):
                if game_state.technical_debt.total_debt > 20:
                    strategy_indicators['safety_focused'] -= 1  # High debt suggests less safety focus
                elif game_state.technical_debt.total_debt < 5:
                    strategy_indicators['safety_focused'] += 1  # Low debt suggests good safety practices
        
        # Determine dominant strategy
        dominant_strategy = max(strategy_indicators.items(), key=lambda x: x[1])
        analysis['dominant_strategy'] = dominant_strategy[0]
        analysis['strategy_confidence'] = dominant_strategy[1]
        
        # Critical Moments Analysis
        critical_moments = []
        
        # High doom survival
        if getattr(game_state, 'max_doom_reached', game_state.doom) > 85:
            critical_moments.append(f'Survived extreme existential risk ({getattr(game_state, 'max_doom_reached', game_state.doom)}% doom)')
            
        # Financial crisis survival
        if getattr(game_state, 'min_money_reached', game_state.money) < 100:
            critical_moments.append(f'Survived severe financial crisis (${getattr(game_state, 'min_money_reached', game_state.money)} minimum)')
            
        # Reputation recovery
        peak_reputation = getattr(game_state, 'peak_reputation', game_state.reputation)
        if peak_reputation > game_state.reputation * 2:
            critical_moments.append(f'Recovered from major reputation damage ({peak_reputation} peak ? {game_state.reputation} current)')
            
        analysis['critical_moments'] = critical_moments
        
        # Resource Trajectory Analysis
        analysis['resource_trajectory'] = {
            'money_trend': 'stable',  # Could be enhanced with historical tracking
            'reputation_trend': 'stable',
            'doom_trend': 'stable',
            'staff_trend': 'stable'
        }
        
        # Performance Assessment
        performance_score = 0
        performance_factors = []
        
        # Survival time bonus
        if game_state.turn > 100:
            performance_score += 3
            performance_factors.append('Long-term survival')
        elif game_state.turn > 50:
            performance_score += 2
            performance_factors.append('Medium-term stability')
        elif game_state.turn > 25:
            performance_score += 1
            performance_factors.append('Short-term viability')
            
        # Safety performance
        if game_state.doom < 15:
            performance_score += 3
            performance_factors.append('Exceptional safety record')
        elif game_state.doom < 25:
            performance_score += 1
            performance_factors.append('Adequate safety measures')
            
        # Growth performance
        if game_state.staff > 25:
            performance_score += 2
            performance_factors.append('Major organizational growth')
        elif game_state.staff > 10:
            performance_score += 1
            performance_factors.append('Moderate organizational development')
            
        # Research impact
        if game_state.papers_published > 10:
            performance_score += 2
            performance_factors.append('Significant research contributions')
        elif game_state.papers_published > 3:
            performance_score += 1
            performance_factors.append('Notable research output')
            
        analysis['performance_score'] = performance_score
        analysis['performance_factors'] = performance_factors
        
        # Overall assessment
        if performance_score >= 8:
            analysis['overall_assessment'] = 'exceptional'
        elif performance_score >= 6:
            analysis['overall_assessment'] = 'excellent'
        elif performance_score >= 4:
            analysis['overall_assessment'] = 'good'
        elif performance_score >= 2:
            analysis['overall_assessment'] = 'adequate'
        else:
            analysis['overall_assessment'] = 'struggling'
            
        return analysis
    
    # Helper methods for achievement conditions
    def _count_productive_employees(self, game_state) -> int:
        '''Count employees who are currently productive.'''
        if not hasattr(game_state, 'employee_blobs'):
            return 0
            
        productive_count = 0
        for blob in game_state.employee_blobs:
            # Employee is productive if they don't have unproductive reasons
            if blob.get('unproductive_reason') is None:
                productive_count += 1
                
        return productive_count
    
    def _count_discovered_opponents(self, game_state) -> int:
        '''Count opponents that have been discovered.'''
        if not hasattr(game_state, 'opponents'):
            return 0
            
        return sum(1 for opp in game_state.opponents if hasattr(opp, 'discovered') and opp.discovered)
    
    def _has_research_lead(self, game_state) -> bool:
        '''Check if player has research lead over all known competitors.'''
        if not hasattr(game_state, 'opponents'):
            return True  # No competition
            
        player_research_metric = game_state.papers_published * 10 + game_state.reputation
        
        for opponent in game_state.opponents:
            if hasattr(opponent, 'discovered') and opponent.discovered:
                if hasattr(opponent, 'progress') and opponent.progress > player_research_metric:
                    return False
                    
        return True
    
    def _survived_major_technical_crisis(self, game_state) -> bool:
        '''Check if player survived a major technical failure cascade.'''
        if not hasattr(game_state, 'technical_failures'):
            return False
            
        # Check if there was a major cascade that was survived
        return (hasattr(game_state.technical_failures, 'cascades_survived') and 
                game_state.technical_failures.cascades_survived > 0)
    
    def _maintained_transparency_through_crisis(self, game_state) -> bool:
        '''Check if player maintained transparency policy through technical crises.'''
        if not hasattr(game_state, 'technical_failures'):
            return False
            
        # Check transparency maintenance through multiple failures
        return (hasattr(game_state.technical_failures, 'transparency_maintained') and
                game_state.technical_failures.transparency_maintained >= 3)
    
    def _warning_recently_shown(self, warning_key: str) -> bool:
        '''Check if a warning was recently shown to avoid spam.'''
        # Simple implementation - more sophisticated timing could be added
        return warning_key in [w.get('key') for w in self.warning_history[-10:]]
    
    def _mark_warning_shown(self, warning_key: str):
        '''Mark a warning as shown.'''
        self.warning_history.append({
            'key': warning_key,
            'turn': getattr(self, '_current_turn', 0)  # Would be set by game_state
        })
        
        # Keep history manageable
        if len(self.warning_history) > 50:
            self.warning_history = self.warning_history[-25:]


# Global instance for use throughout the application
achievements_endgame_system = AchievementsEndgameSystem()
