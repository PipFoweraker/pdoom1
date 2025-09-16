# P(Doom) v0.4.1 Party Demo Guide

## Quick Demo Setup (2 minutes)

### 1. Installation
```bash
git clone https://github.com/PipFoweraker/pdoom1.git
cd pdoom1
pip install -r requirements.txt
python main.py
```

### 2. Party-Ready Features
- **Sound Effects**: Audio enabled by default for engaging interaction
- **Enhanced Leaderboards**: Visual achievement celebration with rankings
- **Spectacular Game Over**: Professional presentation with rank display
- **Dual Identity System**: Players can have separate player/lab names

## Demo Flow (5-10 minutes per player)

### Opening Hook (30 seconds)
> "You're running a scrappy AI safety nonprofit with $100k. Three well-funded labs are racing toward AGI. Can you solve alignment before everyone dies?"

### Core Gameplay Demo (3-5 minutes)
1. **Show Starting Position**: $100k, 2 staff, 25% doom
2. **Demonstrate Actions**: Hire researchers, conduct research, manage budget
3. **Highlight Audio**: Action sounds, hiring "blob" sound, menu interactions
4. **Show Opponents**: Mysterious labs making progress in the background
5. **Economic Pressure**: Weekly staff costs of $600-800, tough decisions

### Achievement Moment (1-2 minutes)
1. **Game Over Scenario**: Let doom reach 100% or run out of money
2. **Spectacular Screen**: Visual celebration if high score achieved
3. **Leaderboard Integration**: Show ranking against other players
4. **Natural Flow**: "View Full Leaderboard" -> "Launch New Game"

### Competitive Hook (1-2 minutes)
1. **Seed-Specific Competition**: "Try the same seed to compare strategies"
2. **Dual Identity**: "Set your player name and lab name separately"
3. **Progress Tracking**: "Play 10 games and watch your skills improve"

## Key Talking Points

### What Makes P(Doom) Special
- **Realistic Economics**: Based on actual AI safety researcher salaries
- **Bootstrap Model**: Scrappy nonprofit vs well-funded competition
- **Deterministic Gameplay**: Same seed = same game for fair competition
- **Privacy-First**: All data stays local, pseudonymous competition

### Technical Highlights
- **Pure Python**: No complex dependencies, easy to modify
- **Turn-Based Strategy**: Think carefully about resource allocation
- **Event System**: Random events add strategic complexity
- **Milestone Progression**: Unlock new mechanics as lab grows

### Educational Value
- **AI Safety Awareness**: Learn about alignment challenges
- **Resource Management**: Understand funding constraints in research
- **Strategic Thinking**: Balance safety research vs capability research
- **Risk Assessment**: Manage technical debt and failure cascades

## Quick Troubleshooting

### Audio Issues
- **No Sound**: Audio requires pygame and numpy - check console for warnings
- **Silent Mode**: Settings -> Audio -> Enable Sound (though default is enabled)

### Performance
- **Slow Start**: First launch initializes config files (normal)
- **Display Issues**: Game requires display - won't work in headless environments

### Gameplay Questions
- **"I ran out of money"**: Try hiring fewer staff, or choose different research focus
- **"Doom is too high"**: Balance capability research with safety research
- **"Opponents winning"**: Use espionage to learn their strategies

## Party Integration Tips

### Multiple Players
- Use different player names to track individual progress
- Compare strategies on the same seed
- Create impromptu tournaments with specific seeds

### Demo Station Setup
- Leave game running at main menu
- Post quick reference card with basic controls
- Have backup laptop in case of crashes

### Conversation Starters
- "What's your AI safety strategy?"
- "Can you beat my 47-turn survival record?"
- "Try seed 'party2024' - I got ranked #3"

## Version History Highlight

**v0.4.1 "Bootstrap Economic Calibration"** - Current party-ready version
- Enhanced leaderboard system with visual celebration
- Sound effects enabled by default
- Spectacular game over screen
- Context-aware user experience

Perfect for demonstrations, competitions, and introducing people to AI safety concepts through engaging gameplay!
