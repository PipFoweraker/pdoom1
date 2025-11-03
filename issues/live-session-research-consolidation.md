# LIVE SESSION: Consolidated Research Actions

## Issue Summary
Combine 'Safety Research' and 'Governance Research' into a single 'Research' action with submenu options, including quality trade-offs and strategic choices.

## Current State
- Safety Research and Governance Research are separate actions
- Limited strategic depth in research choices
- Quality trade-offs exist but could be more prominent in player decision-making

## Proposed Research Menu Structure

### 1. Safety Research
- **Description**: 'Reduce AI risk through technical safety research'
- **Mechanics**: Doom reduction, reputation gain, existing quality system
- **Focus**: Technical alignment, safety techniques

### 2. Governance Research  
- **Description**: 'Policy and governance approaches to AI safety'
- **Mechanics**: Different balance of doom/reputation/political influence
- **Focus**: Regulatory frameworks, policy development

### 3. Quick Research
- **Description**: 'Fast research with lower quality standards'
- **Mechanics**: Lower cost, faster results, quality debt accumulation
- **Trade-off**: Speed vs long-term research debt

### 4. Thorough Research
- **Description**: 'High-quality research with rigorous standards'  
- **Mechanics**: Higher cost, better results, builds research reputation
- **Trade-off**: Cost vs quality and long-term benefits

### 5. Collaborative Research
- **Description**: 'Partner with other labs for shared research'
- **Mechanics**: Cost sharing, relationship building, knowledge exchange
- **Trade-off**: Shared benefits vs independent control

## Strategic Benefits
- **Research Strategy**: Players choose between speed, quality, focus
- **Quality Trade-offs**: Make research quality system more prominent
- **Resource Management**: Different cost/benefit profiles  
- **Long-term Planning**: Quality debt vs research reputation decisions

## Integration with Existing Systems
- **Research Quality System**: Prominently feature existing quality mechanics
- **Economic Cycles**: Research funding affected by market conditions
- **Technical Debt**: Connect research quality to technical failure systems
- **Reputation**: Different research types affect reputation differently

## Implementation Architecture

### Menu Structure
```python
def get_research_submenu_options(game_state):
    options = []
    
    # Core research types - always available
    options.append({
        'name': 'Safety Research',
        'desc': f'Technical AI safety research {get_quality_description_suffix(gs)}',
        'action': 'safety_research'
    })
    
    options.append({
        'name': 'Governance Research', 
        'desc': f'Policy and governance research {get_quality_description_suffix(gs)}',
        'action': 'governance_research'
    })
    
    # Quality-based variations
    if game_state.money >= 60:  # Can afford thorough research
        options.append({
            'name': 'Thorough Research',
            'desc': 'High-quality research (higher cost, better results)',
            'action': 'thorough_research'
        })
    
    if game_state.turn >= 5:  # Unlocked after establishing lab
        options.append({
            'name': 'Quick Research',
            'desc': 'Fast research (lower cost, quality debt risk)', 
            'action': 'quick_research'
        })
    
    # Advanced options
    if hasattr(game_state, 'collaboration_unlocked'):
        options.append({
            'name': 'Collaborative Research',
            'desc': 'Partner research (shared costs and benefits)',
            'action': 'collaborative_research'
        })
    
    return options
```

## Priority
**MEDIUM** - Live session enhancement 

## Files to Modify  
- `src/core/actions.py` (consolidate and expand research actions)
- `src/core/research_quality.py` (enhance quality feedback)
- UI files (add research submenu interface)

## Acceptance Criteria
- [ ] Single 'Research' action opens submenu
- [ ] 4+ research options with distinct strategies  
- [ ] Quality trade-offs prominently featured
- [ ] Integration with existing research quality system
- [ ] Strategic choices feel meaningful
- [ ] Maintains game balance

## Labels
`enhancement`, `game-mechanics`, `live-session`, `research-system`
