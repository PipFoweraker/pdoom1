# P(Doom) Quick Reference Card

## [EMOJI] GAME CONCEPT
**You run a scrappy AI safety nonprofit ($100k budget) racing against 3 well-funded labs to solve alignment before everyone dies.**

## [LIGHTNING] QUICK START

**For Players:**
- Download from [Releases](https://github.com/PipFoweraker/pdoom1/releases) (Windows)
- Extract and run `PDoom.exe`
- Visit [pdoom1.com](https://pdoom1.com) for guides!

**For Developers:**
```bash
git clone https://github.com/PipFoweraker/pdoom1.git
cd pdoom1
# See docs/developer/CONTRIBUTING.md for setup
```

## [CHART] RESOURCES TO WATCH
- **Money**: $100k start, $600-800/week staff costs
- **Doom**: 0-100% existential risk (game ends at 100%)
- **Staff**: More staff = more actions per turn
- **Action Points**: 3/turn + staff bonuses

## [TARGET] BASIC STRATEGY
1. **Hire Smart**: Balance researchers vs admin staff
2. **Research Focus**: Safety research reduces doom, capability research increases progress
3. **Manage Cash Flow**: Don't run out of money!
4. **Watch Opponents**: Use espionage to learn their strategies

## [KEYBOARD][EMOJI] CONTROLS
- **Mouse**: Click any button or menu item
- **Keyboard**: Hotkeys shown on buttons [H], [R], [1], etc.
- **Navigation**: Arrow keys, Enter/Space to select
- **Quick Actions**: Numbers 1-9 for common actions

## [TROPHY] COMPETITIVE FEATURES
- **Leaderboards**: Each seed has its own ranking
- **High Scores**: Spectacular celebration for achievements
- **Fair Play**: Same seed = identical game for strategy comparison
- **Progress Tracking**: See improvement across multiple games

## [EMOJI] AUDIO CUES
- **Action Sounds**: Feedback for spending action points
- **Hiring**: 'Blob' sound when adding team members
- **UI Feedback**: Popup sounds for professional feel
- **Achievement**: Special sounds for reaching milestones

## [EMOJI] PARTY DEMO TIPS

### For Demo Hosts
- Game takes 5-10 minutes per person
- Leave at main menu between players
- Suggest interesting seeds: 'party2024', 'demo', 'challenge'
- Point out the leaderboard for competition

### For Players
- **First Time**: Try tutorial or just jump in
- **Strategy**: Balance safety vs capability research
- **Competition**: Note your rank and try to beat others
- **Different Approaches**: Conservative vs aggressive growth

## [EMOJI] QUICK TROUBLESHOOTING
- **No Sound**: Check that speakers/headphones are connected
- **Slow Performance**: Close other applications
- **Game Too Hard**: Try hiring fewer staff initially
- **Game Too Easy**: Focus more on capability research (increases doom)

## [IDEA] CONVERSATION STARTERS
- 'What's your AI safety strategy?'
- 'Can you survive longer than 47 turns?'
- 'Try seed 'challenge' - I got ranked #5!'
- 'Should AI labs prioritize safety or capability research?'

## [TERMINAL] DEVELOPER COMMANDS
```bash
# Health monitoring
python scripts/project_health.py              # Check project health
python scripts/health_tracker.py --show-trends # View health history
python scripts/ci_health_integration.py --gate-check # CI/CD health gate

# Testing & validation
python -m unittest discover tests -v          # Run full test suite
python scripts/enforce_standards.py --check-all # Standards validation
```

---
**P(Doom) v0.4.1** - Turn-based AI safety strategy * Educational gameplay * Competitive leaderboards * Party-ready demonstrations
