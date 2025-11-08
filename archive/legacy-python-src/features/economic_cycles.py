'''
Economic Cycles & Funding Volatility System
Implementation of Issue #192: Historical AI funding cycles with strategic gameplay

This module implements realistic economic cycles based on historical AI funding patterns
from 2017-2025, with strategic timing mechanics for fundraising and crisis survival.

Design Notes:
- Game starts Jan 1, 2017 (Turn 0), 1 week per turn
- Historical anchors: 2017-18 boom, 2019 correction, 2020-21 COVID boom, 
  2022-23 interest rate correction, 2024-25 AI boom
- Modular design for future features:
  * Regional markets (config-based)
  * Debt/loan system
  * Player influence on cycles
  * Crisis opportunity mechanics
'''

from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from src.services.deterministic_rng import get_rng


class EconomicPhase(Enum):
    '''Economic cycle phases with different funding characteristics.'''
    BOOM = 'boom'          # High funding, easy access, competition
    STABLE = 'stable'      # Normal funding conditions
    CORRECTION = 'correction'  # Reduced funding, higher requirements
    RECESSION = 'recession'    # Minimal funding, survival mode
    RECOVERY = 'recovery'      # Gradually improving conditions


class FundingSource(Enum):
    '''Different funding sources with varying cycle sensitivity.'''
    SEED = 'seed'              # Friends, family, angels - least cycle sensitive
    VENTURE = 'venture'        # VC firms - highly cycle sensitive
    CORPORATE = 'corporate'    # Strategic investments - moderately sensitive
    GOVERNMENT = 'government'  # Grants, contracts - counter-cyclical
    REVENUE = 'revenue'        # Customer revenue - growth dependent


@dataclass
class EconomicState:
    '''Current economic conditions affecting funding.'''
    phase: EconomicPhase
    turn_in_phase: int
    phase_duration: int
    funding_multiplier: float
    availability_threshold: int  # Reputation requirement modifier
    news_headline: str
    cycle_year: int  # Calendar year for historical context


class EconomicCycles:
    '''
    Manages economic cycles and funding volatility based on historical AI market patterns.
    
    Timeline anchors (historically accurate):
    - 2017-2018: AI/crypto boom period
    - 2019: Market correction
    - 2020-2021: COVID tech boom + massive AI investment
    - 2022-2023: Interest rate rises + tech sector correction
    - 2024-2025: Current AI boom cycle
    '''
    
    def __init__(self, game_state):
        '''Initialize economic cycle system.'''
        self.game_state = game_state
        self.rng = get_rng()
        
        # Historical economic timeline (turn-based, starting Jan 1 2017)
        self.historical_phases = self._initialize_historical_timeline()
        
        # Current state
        self.current_state = self._get_phase_for_turn(0)
        
        # Funding source multipliers by phase
        self.phase_multipliers = {
            EconomicPhase.BOOM: {
                FundingSource.VENTURE: 1.8,
                FundingSource.CORPORATE: 1.4,
                FundingSource.SEED: 1.2,
                FundingSource.GOVERNMENT: 0.9,
                FundingSource.REVENUE: 1.3
            },
            EconomicPhase.STABLE: {
                FundingSource.VENTURE: 1.0,
                FundingSource.CORPORATE: 1.0,
                FundingSource.SEED: 1.0,
                FundingSource.GOVERNMENT: 1.0,
                FundingSource.REVENUE: 1.0
            },
            EconomicPhase.CORRECTION: {
                FundingSource.VENTURE: 0.6,
                FundingSource.CORPORATE: 0.8,
                FundingSource.SEED: 0.9,
                FundingSource.GOVERNMENT: 1.2,
                FundingSource.REVENUE: 0.7
            },
            EconomicPhase.RECESSION: {
                FundingSource.VENTURE: 0.3,
                FundingSource.CORPORATE: 0.5,
                FundingSource.SEED: 0.8,
                FundingSource.GOVERNMENT: 1.5,
                FundingSource.REVENUE: 0.4
            },
            EconomicPhase.RECOVERY: {
                FundingSource.VENTURE: 0.8,
                FundingSource.CORPORATE: 0.9,
                FundingSource.SEED: 1.0,
                FundingSource.GOVERNMENT: 1.1,
                FundingSource.REVENUE: 0.9
            }
        }
        
        # Track funding rounds for narrative progression
        self.funding_history = []
        self.last_major_funding = -10  # Turn of last major funding round
        
    def _initialize_historical_timeline(self) -> List[Tuple[int, int, EconomicPhase, str]]:
        '''
        Initialize historically-anchored economic timeline.
        Returns: List of (start_turn, end_turn, phase, news_headline)
        '''
        timeline = [
            # 2017: Early AI boom beginning (Jan-Jun)
            (0, 25, EconomicPhase.STABLE, 'AI investment maintains steady growth as algorithms show promise'),
            
            # 2017-2018: AI/Crypto boom peak (Jul 2017 - Dec 2018)
            (26, 104, EconomicPhase.BOOM, 'Tech investors pour billions into AI startups amid automation hype'),
            
            # 2019: Market correction (Jan - Dec 2019)
            (105, 156, EconomicPhase.CORRECTION, 'AI funding cools as investors demand proof of commercial viability'),
            
            # 2020: COVID disruption and early recovery (Jan - Jun 2020)
            (157, 182, EconomicPhase.RECESSION, 'Economic uncertainty hits tech funding as pandemic reshapes priorities'),
            
            # 2020-2021: COVID tech boom (Jul 2020 - Dec 2021)
            (183, 261, EconomicPhase.BOOM, 'Remote work revolution drives massive AI investment surge'),
            
            # 2022: Interest rate correction begins (Jan - Jun 2022)
            (262, 287, EconomicPhase.CORRECTION, 'Rising interest rates cool venture capital enthusiasm'),
            
            # 2022-2023: Tech sector correction (Jul 2022 - Dec 2023)
            (288, 365, EconomicPhase.RECESSION, 'Tech layoffs and funding drought hit AI sector hard'),
            
            # 2024: Recovery begins (Jan - Jun 2024)
            (366, 391, EconomicPhase.RECOVERY, 'AI funding shows signs of recovery as ChatGPT proves commercial potential'),
            
            # 2024-2025: Current AI boom (Jul 2024 - present)
            (392, 600, EconomicPhase.BOOM, 'Generative AI triggers unprecedented investment gold rush'),
        ]
        
        return timeline
    
    def _get_phase_for_turn(self, turn: int) -> EconomicState:
        '''Get economic state for specific turn based on historical timeline.'''
        # Find current phase in historical timeline
        for start_turn, end_turn, phase, headline in self.historical_phases:
            if start_turn <= turn <= end_turn:
                turn_in_phase = turn - start_turn
                phase_duration = end_turn - start_turn + 1
                
                # Calculate funding multiplier with some randomness
                base_multiplier = self._get_base_multiplier(phase)
                multiplier = base_multiplier + self.rng.uniform(-0.1, 0.1, context=f'economic_phase_{turn}')
                
                # Calculate availability threshold modifier
                threshold_modifier = self._get_threshold_modifier(phase)
                
                # Calculate calendar year
                calendar_year = 2017 + (turn // 52)  # 52 weeks per year
                
                return EconomicState(
                    phase=phase,
                    turn_in_phase=turn_in_phase,
                    phase_duration=phase_duration,
                    funding_multiplier=multiplier,
                    availability_threshold=threshold_modifier,
                    news_headline=headline,
                    cycle_year=calendar_year
                )
        
        # If beyond timeline, use cyclical pattern
        return self._generate_future_phase(turn)
    
    def _get_base_multiplier(self, phase: EconomicPhase) -> float:
        '''Get base funding multiplier for economic phase.'''
        multipliers = {
            EconomicPhase.BOOM: 1.6,
            EconomicPhase.STABLE: 1.0,
            EconomicPhase.CORRECTION: 0.7,
            EconomicPhase.RECESSION: 0.4,
            EconomicPhase.RECOVERY: 0.9
        }
        return multipliers[phase]
    
    def _get_threshold_modifier(self, phase: EconomicPhase) -> int:
        '''Get reputation threshold modifier for funding access.'''
        modifiers = {
            EconomicPhase.BOOM: -3,        # Easier access during boom
            EconomicPhase.STABLE: 0,       # Normal requirements
            EconomicPhase.CORRECTION: +2,  # Harder access during correction
            EconomicPhase.RECESSION: +5,   # Much harder during recession
            EconomicPhase.RECOVERY: +1     # Slightly harder during recovery
        }
        return modifiers[phase]
    
    def _generate_future_phase(self, turn: int) -> EconomicState:
        '''Generate economic state for turns beyond historical timeline (post-2025).'''
        # Use simplified cyclical pattern for future
        cycle_length = 80  # ~1.5 year cycles
        position_in_cycle = turn % cycle_length
        
        if position_in_cycle < 20:
            phase = EconomicPhase.BOOM
            headline = 'AI sector experiences renewed growth and investment'
        elif position_in_cycle < 35:
            phase = EconomicPhase.STABLE
            headline = 'AI funding stabilizes as market matures'
        elif position_in_cycle < 50:
            phase = EconomicPhase.CORRECTION
            headline = 'Market correction hits AI sector as valuations adjust'
        elif position_in_cycle < 65:
            phase = EconomicPhase.RECESSION
            headline = 'Economic downturn reduces AI investment appetite'
        else:
            phase = EconomicPhase.RECOVERY
            headline = 'AI sector shows early signs of recovery'
        
        base_multiplier = self._get_base_multiplier(phase)
        multiplier = base_multiplier + self.rng.uniform(-0.15, 0.15, context=f'future_phase_{turn}')
        threshold_modifier = self._get_threshold_modifier(phase)
        calendar_year = 2017 + (turn // 52)
        
        return EconomicState(
            phase=phase,
            turn_in_phase=position_in_cycle,
            phase_duration=cycle_length,
            funding_multiplier=multiplier,
            availability_threshold=threshold_modifier,
            news_headline=headline,
            cycle_year=calendar_year
        )
    
    def update_for_turn(self, turn: int) -> Optional[str]:
        '''
        Update economic state for new turn.
        Returns news headline if phase changed, None otherwise.
        '''
        previous_phase = self.current_state.phase
        self.current_state = self._get_phase_for_turn(turn)
        
        # Return news headline if phase changed
        if previous_phase != self.current_state.phase:
            return self.current_state.news_headline
        
        return None
    
    def get_funding_multiplier(self, funding_source: FundingSource = FundingSource.VENTURE) -> float:
        '''Get current funding multiplier for specific funding source.'''
        base_multiplier = self.current_state.funding_multiplier
        source_multiplier = self.phase_multipliers[self.current_state.phase][funding_source]
        return base_multiplier * source_multiplier
    
    def get_funding_availability_threshold(self) -> int:
        '''Get additional reputation requirement for funding access.'''
        return self.current_state.availability_threshold
    
    def can_access_funding_source(self, funding_source: FundingSource, reputation: int) -> bool:
        '''Check if player can access specific funding source given current conditions.'''
        base_requirements = {
            FundingSource.SEED: 0,      # Always available
            FundingSource.VENTURE: 5,   # Requires some reputation
            FundingSource.CORPORATE: 10, # Requires established reputation  
            FundingSource.GOVERNMENT: 8, # Requires credibility
            FundingSource.REVENUE: 3    # Requires some market presence
        }
        
        required_reputation = base_requirements[funding_source] + self.get_funding_availability_threshold()
        return reputation >= required_reputation
    
    def get_funding_round_info(self) -> Dict[str, any]:
        '''Get information about available funding rounds based on game state.'''
        reputation = self.game_state.reputation
        turn = self.game_state.turn
        
        available_sources = []
        for source in FundingSource:
            if self.can_access_funding_source(source, reputation):
                multiplier = self.get_funding_multiplier(source)
                available_sources.append({
                    'source': source,
                    'multiplier': multiplier,
                    'description': self._get_funding_source_description(source, multiplier)
                })
        
        return {
            'available_sources': available_sources,
            'phase': self.current_state.phase,
            'phase_description': self._get_phase_description(),
            'turns_since_last_funding': turn - self.last_major_funding,
            'calendar_year': self.current_state.cycle_year
        }
    
    def _get_funding_source_description(self, source: FundingSource, multiplier: float) -> str:
        '''Get human-readable description of funding source conditions.'''
        descriptions = {
            FundingSource.SEED: f'Angel/seed funding (x{multiplier:.1f})',
            FundingSource.VENTURE: f'Venture capital (x{multiplier:.1f})',
            FundingSource.CORPORATE: f'Strategic investment (x{multiplier:.1f})',
            FundingSource.GOVERNMENT: f'Government grants (x{multiplier:.1f})',
            FundingSource.REVENUE: f'Customer revenue (x{multiplier:.1f})'
        }
        return descriptions[source]
    
    def _get_phase_description(self) -> str:
        '''Get human-readable description of current economic phase.'''
        descriptions = {
            EconomicPhase.BOOM: 'Market conditions are favorable for AI investment',
            EconomicPhase.STABLE: 'Economic conditions are stable for AI development', 
            EconomicPhase.CORRECTION: 'Market correction is affecting AI funding',
            EconomicPhase.RECESSION: 'Economic downturn is constraining investment',
            EconomicPhase.RECOVERY: 'Market recovery is beginning to boost confidence'
        }
        return descriptions[self.current_state.phase]
    
    def record_funding_round(self, amount: int, source: FundingSource, turn: int):
        '''Record a funding round for narrative tracking.'''
        self.funding_history.append({
            'turn': turn,
            'amount': amount,
            'source': source,
            'phase': self.current_state.phase,
            'multiplier': self.get_funding_multiplier(source)
        })
        
        if amount >= 100:  # Major funding threshold
            self.last_major_funding = turn
    
    def get_emergency_funding_options(self) -> List[Dict[str, any]]:
        '''Get emergency funding options during crisis (to be implemented in future versions).'''
        # Placeholder for future debt/emergency funding system
        # TODO: Implement emergency funding mechanics
        return []
    
    def get_phase_transition_events(self) -> List[Dict[str, any]]:
        '''Get events that should trigger during phase transitions.'''
        phase = self.current_state.phase
        events = []
        
        # Phase-specific events that can occur
        if phase == EconomicPhase.RECESSION:
            events.extend([
                {
                    'name': 'Funding Drought Warning',
                    'description': 'Economic conditions make fundraising extremely difficult',
                    'type': 'warning'
                },
                {
                    'name': 'Emergency Cost Cutting',
                    'description': 'Consider reducing expenses to survive the downturn',
                    'type': 'advice'
                }
            ])
        elif phase == EconomicPhase.BOOM:
            events.extend([
                {
                    'name': 'Funding Opportunity Window', 
                    'description': 'Optimal conditions for raising capital',
                    'type': 'opportunity'
                }
            ])
        
        return events
