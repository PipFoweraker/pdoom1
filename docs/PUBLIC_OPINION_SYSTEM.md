# Public Opinion & Media System Documentation

## Overview

The Public Opinion & Media System adds dynamic public sentiment tracking and media mechanics to P(Doom). This system provides more nuanced feedback on player actions and creates strategic opportunities for managing public perception.

## Core Components

### Public Opinion Tracking

The system tracks four key metrics on a 0-100 scale:

1. **General Sentiment** (50): Overall public optimism about AI development
2. **Trust in Player** (50): Specific trust in your organization 
3. **AI Safety Awareness** (20): How much the public cares about AI safety
4. **Media Attention** (0): How closely media is watching the AI sector

### Media Stories

Media stories are generated based on:
- Player actions (research breakthroughs, transparency efforts)
- Competitor actions (scandals, achievements)
- Random events (celebrity endorsements, policy discussions)

Each story has:
- **Headline**: Descriptive title
- **Type**: breakthrough, scandal, human_interest, policy, safety_concern, industry_news
- **Duration**: How many turns it stays active
- **Sentiment Impact**: Effect on opinion metrics
- **Attention Level**: Media attention generated

### Opinion Modifiers

Temporary effects that modify opinion over time:
- Applied by actions, events, or media stories
- Have duration (number of turns active)
- Can stack for cumulative effects

## Gameplay Effects

### High Public Trust (70+)
- +20% funding from investors
- -10% regulatory pressure  
- Easier researcher recruitment

### Low Public Trust (30-)
- -30% funding availability
- +20% regulatory pressure
- Competitors can use public concern against you

### High Safety Awareness (70+)
- Safety research generates more reputation
- Capabilities research generates suspicion
- Unlocks "Public Safety Advocate" funding source

### High Media Attention (50+)
- Your actions have amplified public impact
- Increased scrutiny of activities

## Media Actions

Players can actively manage their public image through media actions:

### Press Release ($50k)
- Control narrative around recent developments
- Moderate boost to trust and sentiment
- Duration: 2 turns

### Exclusive Interview (5 reputation, 1 AP)
- High-impact deep dive story
- Significant trust boost (with small risk of backfire)
- Generates its own media story
- Requires: 10+ reputation

### Damage Control ($200k)
- Reduces negative story impact by 50%
- Shortens scandal duration
- Only available when scandal stories are active

### Social Media Campaign ($75k)
- Targeted outreach to improve sentiment
- Good for general sentiment, moderate for trust
- Risk of backlash if overused (multiple campaigns per turn)

### Public Statement ($10k)
- Quick response to current events
- Enhanced effect during high media attention
- Low cost, moderate impact

### Investigative Tip ($100k) 
- Plant negative story about competitor
- Risk of discovery based on reputation
- Discovery causes significant trust loss
- Requires: 20+ reputation

## Natural Dynamics

### Opinion Decay
- Extreme values naturally drift toward neutral (50)
- Media attention decreases over time
- Safety awareness slowly declines without events

### Story Expiration
- Stories automatically expire after their duration
- Expired stories stop affecting opinion
- New stories can override old narratives

### Volatility
- Opinion changes are multiplied by volatility setting (default 1.0)
- High volatility = more dramatic swings
- Can be configured for different game experiences

## Integration Points

### Research Actions
Research with significant reputation gain (2+) can generate media stories:
- Safety research → positive breakthrough stories
- Capabilities research → mixed coverage with safety concerns

### Event System
- Random media events occur each turn
- Competitor actions can generate stories
- External events (policy hearings, celebrity comments) add variety

### Reputation System
- Public opinion complements existing reputation
- Trust in player correlates with but is separate from reputation
- Media stories can affect both systems

## Configuration

The system respects existing game complexity settings:
- **Simple**: Basic reputation system (existing behavior)
- **Standard**: Public opinion tracking, basic media stories
- **Complex**: Full media cycle, player media actions, demographic breakdown

## UI Components

### Public Opinion Panel
- Current metrics with trend indicators
- Color-coded progress bars
- Compact display option for minimal UI

### Media Stories Ticker
- Active stories with remaining duration
- Story type indicators
- Impact preview

### Media Actions Menu
- Available actions based on game state
- Cost and requirement display
- Effect predictions

## Technical Implementation

### Data Structures
- `PublicOpinion`: Core opinion tracking class
- `MediaStory`: Individual media story representation
- `MediaSystem`: Manages actions and story generation
- `OpinionModifier`: Temporary opinion effects

### Serialization
- Full save/load support through dictionary conversion
- History tracking (last 20 turns)
- Active modifiers and stories preserved

### Error Handling
- Graceful fallback when system unavailable
- Validation of opinion values (0-100 clamping)
- Safe access patterns for optional features

## Balancing Notes

### Initial Values
- General sentiment starts neutral (50)
- Trust starts neutral (50), adjusts based on starting reputation
- Safety awareness starts low (20) - public isn't initially concerned
- Media attention starts at zero

### Action Costs
- Press releases are affordable for regular use ($50k)
- Damage control is expensive but powerful ($200k)
- Interview costs reputation (risk/reward)
- Social media is mid-range cost ($75k)

### Story Generation
- Not every action generates stories (prevents spam)
- Significant reputation gains (2+) have story potential
- Random story generation is relatively rare
- Media attention level affects story generation rates

## Future Enhancements

### Demographic Breakdown
- Track opinion by demographic groups
- Different groups respond differently to actions
- Targeted media campaigns for specific demographics

### Regulatory Integration
- Public opinion affects regulatory pressure
- Safety awareness influences regulation speed
- Trust affects regulatory cooperation

### Competitor Strategies
- AI opponents use media actions strategically
- Scandal planting between competitors
- Public relations arms race

### Advanced Media Types
- Investigative journalism series
- Documentary features
- Academic paper coverage
- Social media viral moments

## Development Guidelines

### Adding New Media Actions
1. Define action in `MediaSystem._initialize_media_actions()`
2. Implement effect function
3. Add to main actions list in `actions.py`
4. Test availability conditions

### Creating New Story Types
1. Add to `MediaStoryType` enum
2. Update story generation templates
3. Add UI icons and formatting
4. Test story lifecycle

### Modifying Opinion Effects
1. Update effect calculations in `public_opinion.py`
2. Add to documentation
3. Test edge cases and balance
4. Update UI display logic

This system provides rich strategic depth while maintaining the core gameplay loop of P(Doom), giving players meaningful choices in how they manage their public image alongside their research and safety efforts.