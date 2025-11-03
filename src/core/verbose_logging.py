'''
Verbose logging utilities extracted from game_state.py

This module contains all the verbose message formatting functions that create
'old school turn by turn RPG details' style logging for resource changes.
These are pure formatting functions that generate flavorful messages.
'''

from typing import List
from src.services.deterministic_rng import get_rng


def create_verbose_money_message(val: float, reason: str = '', current_money: float = 0) -> List[str]:
    '''Create detailed, flavorful messages for money changes like an RPG combat log.'''
    messages = []
    amount = abs(val)
    
    # Create verbose, flavor-rich messages based on amount and context
    if val > 0:  # Gaining money
        if amount >= 1000:
            if 'funding' in reason.lower() or 'fundrais' in reason.lower():
                messages.append(f'? MAJOR CAPITAL INJECTION: +${amount:.0f}k secured through strategic funding!')
            elif 'revenue' in reason.lower() or 'customer' in reason.lower():
                messages.append(f'? REVENUE WINDFALL: +${amount:.0f}k earned from satisfied customers!')
            elif 'grant' in reason.lower() or 'government' in reason.lower():
                messages.append(f'? GOVERNMENT BACKING: +${amount:.0f}k awarded through official channels!')
            else:
                messages.append(f'? FINANCIAL SUCCESS: +${amount:.0f}k added to your war chest!')
        elif amount >= 100:
            messages.append(f'? Solid gains: +${amount:.0f}k helps strengthen your position')
        else:
            messages.append(f'? Minor income: +${amount:.0f}k trickles into your accounts')
            
    else:  # Spending money
        if amount >= 1000:
            if 'staff' in reason.lower() or 'hir' in reason.lower():
                messages.append(f'? MAJOR EXPANSION: -${amount:.0f}k invested in growing your team!')
            elif 'research' in reason.lower():
                messages.append(f'? RESEARCH INVESTMENT: -${amount:.0f}k allocated to cutting-edge work!')
            elif 'upgrade' in reason.lower() or 'equipment' in reason.lower():
                messages.append(f'? INFRASTRUCTURE UPGRADE: -${amount:.0f}k spent on essential systems!')
            else:
                messages.append(f'? STRATEGIC SPENDING: -${amount:.0f}k deployed for organizational needs')
        elif amount >= 100:
            messages.append(f'? Measured spending: -${amount:.0f}k allocated to operations')
        else:
            messages.append(f'? Minor expense: -${amount:.0f}k spent on day-to-day needs')
    
    # Add flavor text based on remaining balance
    if current_money < 100:
        messages.append('WARNINGWARNING [CASH FLOW ALERT] Reserves running critically low!')
    elif current_money > 10000:
        messages.append('? [FINANCIAL STRENGTH] Substantial reserves provide strategic flexibility')
    
    return messages


def create_verbose_staff_message(val: float, reason: str = '', current_staff: int = 0) -> List[str]:
    '''Create detailed, flavorful messages for staff changes like an RPG party management log.'''
    messages = []
    count = abs(int(val))
    
    if val > 0:  # Hiring staff
        if count >= 5:
            messages.append(f'? HIRING SPREE: +{count} new team members join your growing organization!')
            messages.append('FAST The lab buzzes with fresh energy and ambitious conversations')
        elif count >= 2:
            messages.append(f'? TEAM EXPANSION: +{count} talented individuals strengthen your capabilities')
        else:
            # Single hire with personality
            personality_traits = [
                'eager and ambitious', 'highly skilled', 'experienced veteran', 
                'innovative thinker', 'reliable workhorse', 'creative problem-solver'
            ]
            trait = get_rng().choice(personality_traits, 'verbose_staff_hire')
            messages.append(f'? NEW RECRUIT: A {trait} joins your team (+{count} staff)')
            
        # Add context based on team size
        if current_staff >= 20:
            messages.append('? [MAJOR ORGANIZATION] Your lab now rivals established institutions')
        elif current_staff >= 10:
            messages.append('? [GROWING INFLUENCE] Your expanded team opens new strategic possibilities')
        elif current_staff >= 5:
            messages.append('SETTINGS [SOLID FOUNDATION] A capable core team forms the backbone of your operations')
            
    else:  # Losing staff
        if count >= 5:
            messages.append(f'? MAJOR DOWNSIZING: -{count} team members leave your organization')
            messages.append('? The remaining staff look uncertain about the future')
        elif count >= 2:
            messages.append(f'? STAFF REDUCTION: -{count} people depart, citing various reasons')
        else:
            departure_reasons = [
                'better opportunities elsewhere', 'disagreements over direction',
                'pursuit of higher compensation', 'concerns about project viability',
                'family obligations', 'burnout from intense work'
            ]
            reason_text = get_rng().choice(departure_reasons, 'verbose_staff_departure')
            messages.append(f'? DEPARTURE: One team member leaves due to {reason_text} (-{count} staff)')
    
    return messages


def create_verbose_reputation_message(val: float, reason: str = '', current_rep: int = 0) -> List[str]:
    '''Create detailed, flavorful messages for reputation changes.'''
    messages = []
    amount = abs(val)
    
    if val > 0:  # Gaining reputation
        if amount >= 10:
            messages.append(f'STAR MAJOR RECOGNITION: +{amount} reputation from outstanding achievements!')
            messages.append('? Industry publications take notice of your groundbreaking work')
        elif amount >= 5:
            messages.append(f'STAR SOLID PROGRESS: +{amount} reputation as your work gains recognition')
        else:
            messages.append(f'? Steady improvement: +{amount} reputation from consistent performance')
            
        # Add context based on reputation level
        if current_rep >= 80:
            messages.append('SHINE [INDUSTRY LEADER] Your reputation precedes you in all professional circles')
        elif current_rep >= 60:
            messages.append('? [WELL REGARDED] Your organization is widely respected in the field')
        elif current_rep >= 40:
            messages.append('GROWTH [RISING STAR] Your growing reputation opens new doors')
            
    else:  # Losing reputation
        if amount >= 10:
            messages.append(f'? REPUTATION CRISIS: -{amount} reputation from serious setbacks!')
            messages.append('? Negative coverage spreads across industry media')
        elif amount >= 5:
            messages.append(f'? SETBACK: -{amount} reputation from concerning developments')
        else:
            messages.append(f'? Minor concerns: -{amount} reputation from small issues')
            
        # Add warnings based on low reputation
        if current_rep <= 20:
            messages.append('WARNING [CREDIBILITY CRISIS] Your reputation makes future partnerships difficult')
        elif current_rep <= 40:
            messages.append('? [REPUTATION CONCERNS] Stakeholders express growing doubts')
    
    return messages


def create_verbose_compute_message(val: float, reason: str = '', current_compute: int = 0) -> List[str]:
    '''Create detailed, flavorful messages for compute resource changes.'''
    messages = []
    amount = abs(val)
    
    if val > 0:  # Gaining compute
        if amount >= 100:
            messages.append(f'? MASSIVE COMPUTE BOOST: +{amount} units of computational power!')
            messages.append('FAST Your researchers celebrate the expanded capabilities')
        elif amount >= 50:
            messages.append(f'CODE SIGNIFICANT UPGRADE: +{amount} compute units enhance your capabilities')
        else:
            messages.append(f'SETTINGS System improvement: +{amount} compute units added to your resources')
            
        # Add context based on compute level
        if current_compute >= 1000:
            messages.append('LAUNCH [SUPERCOMPUTING] Your computational resources rival major tech companies')
        elif current_compute >= 500:
            messages.append('? [HIGH PERFORMANCE] Substantial compute power accelerates all research')
        elif current_compute >= 100:
            messages.append('FAST [SOLID FOUNDATION] Reliable computational resources support steady progress')
            
    else:  # Using/losing compute
        if amount >= 100:
            messages.append(f'? INTENSIVE COMPUTATION: -{amount} compute units consumed by major calculations')
        elif amount >= 50:
            messages.append(f'CODE HEAVY PROCESSING: -{amount} compute units used for complex analysis')
        else:
            messages.append(f'SETTINGS Standard usage: -{amount} compute units consumed by routine operations')
    
    return messages


def create_verbose_research_message(research_type: str, doom_reduction: int, rep_gain: int) -> List[str]:
    '''Create detailed messages for research progress with specific outcomes.'''
    messages = []
    
    if research_type.lower() == 'safety':
        messages.append(f'? SAFETY BREAKTHROUGH: Research reduces existential risk by {doom_reduction} points!')
        messages.append(f'CHART Reputation grows by {rep_gain} as the community recognizes your responsible approach')
        messages.append('TARGET Your commitment to safety research sets a positive example for the field')
    elif research_type.lower() == 'capabilities':
        messages.append(f'LAUNCH CAPABILITIES ADVANCE: Significant progress in AI systems development!')
        messages.append(f'GROWTH Reputation increases by {rep_gain} from impressive technical achievements')
        if doom_reduction < 0:  # Capabilities research might increase doom
            messages.append(f'WARNING However, rapid capability advances may increase long-term risks')
    else:
        messages.append(f'? RESEARCH PROGRESS: {research_type} research yields valuable insights')
        messages.append(f'CHART Academic standing improves by {rep_gain} reputation points')
        if doom_reduction > 0:
            messages.append(f'? This work contributes to reducing existential risk by {doom_reduction}')
    
    return messages
