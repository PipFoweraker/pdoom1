# P(Doom) Player Guide

Welcome to **P(Doom): Bureaucracy Strategy Prototype**!  
A satirical strategy game about managing an AI safety lab while competing against reckless frontier labs.

---

## Quick Setup

1. **Install Python 3.8+** (if not already installed)
2. **Install pygame**: `pip install pygame`
3. **Run the game**: `python main.py`

That's it! The game will open with a main menu.

---

## How to Play

### Your Goal
Survive as long as possible while managing your AI safety lab. Avoid catastrophe (p(Doom) = 100%), keep your team, and outlast the reckless competition.


### Basic Game Loop
1. **Take actions** (left panel) - Click buttons to spend money and affect your lab
2. **Buy upgrades** (right panel) - One-time purchases that give permanent benefits  
3. **End your turn** - Click "END TURN" or press `Space` to see results
4. **Handle events** - Random events will challenge your strategy
5. **Repeat** - Keep going until game over


### Resources to Manage
- **💰 Money**: Spend on actions and upgrades, earn through fundraising
- **👥 Staff**: Your team (costs money each turn, can quit if unpaid)
- **⭐ Reputation**: Affects fundraising and events
- **☢️ p(Doom)**: AI catastrophe risk (game over at 100%)
- **🖥️ Compute**: Powers employee productivity and research
- **📄 Research**: Progress toward publishing papers (boosts reputation)
- **🎯 Competitors**: Track discovered opponents and their progress toward AGI

---

## Controls & Interface

### Main Menu Navigation
| Action | How To |
|--------|--------|
| Navigate options | Arrow keys ↑↓ or mouse |
| Select option | Enter or mouse click |
| Exit | Escape key |

### In-Game Controls
| Action | How To |
|--------|--------|
| Take action | Click action button (left panel) |
| Buy upgrade | Click upgrade button (right panel) |
| End turn | Click "END TURN" or press `Space` |
| View upgrade details | Hover mouse over purchased upgrades (top right) |
| Quit to menu | Press `Esc` |
| Restart after game over | Click anywhere on final score screen |

### Game Modes
- **Weekly Seed**: This week's community challenge (same for everyone)
- **Custom Seed**: Enter your own seed for repeatable scenarios
- **Report Bug**: Submit feedback or issues (privacy-focused)

---

## Competitors & Intelligence

You're not alone in the AI race! Three competing organizations are also racing toward AGI:

### The Competition
- **🏢 TechCorp Labs**: Massive tech corporation with deep pockets and aggressive timelines
- **🏛️ National AI Initiative**: Government-backed program with strong regulatory influence
- **🚀 Frontier Dynamics**: Secretive startup with mysterious funding and rapid development

### Intelligence Gathering

**🕵️ Espionage (Available from start)**
- Cost: $30k, Risk: Moderate
- Discovers new competitors or gathers basic intelligence
- Can reveal progress estimates and general capabilities

**🎯 Scout Opponent (Unlocked after Turn 5)**
- Cost: $50k, Risk: Moderate
- Focused intelligence gathering on specific competitors
- Reveals detailed stats: budget, researchers, lobbyists, compute

### Competitor Intelligence Panel
The competitors panel (between resources and actions) shows:
- **Discovered competitors** and their names/descriptions
- **Progress toward AGI** (0-100%, game over if any reaches 100%)
- **Hidden stats** revealed through successful intelligence operations
- **Recent activities** when competitors make major moves

### Strategy Tips
- **Early scouting** helps prioritize which competitors pose the biggest threat
- **Budget tracking** reveals which competitors can afford rapid expansion  
- **Researcher counts** indicate research capacity and progress speed
- **Progress monitoring** helps predict game-ending scenarios


---

## Screen Layout

**Top Bar:** Your current resources and game info
**Competitors Panel:** Intelligence on discovered opponents (between resources and actions)
**Left Panel:** Available actions you can take this turn  
**Right Panel:** Available upgrades (becomes icons after purchase)
**Bottom Center:** "END TURN" button
**Bottom Left:** Activity log showing recent events


### Activity Log
- Shows events from the current turn only
- Clears automatically when you end your turn  
- Displays action results, random events, and resource changes
- **Enhanced mode** unlocked later: scroll through complete game history

---

## Actions You Can Take

**💰 Fundraise** - Gain money (more effective with higher reputation)
**👥 Grow Community** - Increase reputation, chance to gain staff
**🔬 Safety Research** - Reduce p(Doom), gain reputation (expensive)
**🏛️ Governance Research** - Reduce p(Doom), gain reputation (expensive)  
**🖥️ Buy Compute** - Purchase compute resources for employee productivity
**📈 Hire Staff** - Add team members (cost money each turn)
**🕵️ Espionage** - Learn about competitor progress (risky)
**🎯 Scout Opponent** - Focused intelligence gathering (unlocked turn 5+, risky)

*Each action shows its cost and effects when you hover over it.*

---

## Upgrade Strategy

**🖥️ Computer System** - Makes research more effective
**🪑 Comfy Chairs** - Staff less likely to quit when unpaid
**☁️ Secure Cloud** - Reduces damage from lab breakthrough events
**📊 Accounting Software** - Shows resource changes each turn
**📋 Event Log System** - Unlock scrollable activity history

*Purchased upgrades appear as icons at the top right - hover for details.*

---


## Game Events & Tips


### Random Events to Watch For
- **🔬 Lab Breakthrough** - p(Doom) increases (mitigated by security upgrades)
- **💸 Funding Crisis** - Lose money when resources are tight
- **😔 Staff Burnout** - Staff quit when overworked and underpaid
- **💻 Software Offers** - Special upgrade opportunities

### Winning Strategies

**Early Game (Turns 1-5):**
- Focus on fundraising to build a money buffer
- Hire a couple staff members for stability  
- Buy accounting software if available for better tracking

**Mid Game (Turns 6-15):**
- Invest in research to keep p(Doom) under control
- Build reputation for better fundraising
- Get key upgrades like computer systems and comfy chairs

**Late Game (15+ turns):**
- Balance aggressive research with resource management
- Monitor opponent progress and react accordingly
- Use espionage strategically to plan ahead


**Core Principles:**
- Always keep at least 2 staff (prevents immediate game over)
- Don't let p(Doom) get above 80% without a plan
- Reputation makes fundraising much more effective
- Research is expensive but essential for long-term survival



---

## Game Over Conditions

You lose if any of these happen:
- **☢️ p(Doom) reaches 100%** - Catastrophic AI development
- **👥 All staff quit** - No one left to run the lab
- **🏁 Opponent wins** - Competition reaches 100% progress first

Your score is how many turns you survived. Try to beat your previous best!


---
=======


## Seeds & High Scores

**Weekly Seed**: Everyone gets the same challenge each week - compete with friends!  
**Custom Seed**: Use any text as a seed for repeatable games
**High Scores**: Tracked separately for each seed in `local_highscore.json`

---

## Need Help?

- **Stuck?** Try the in-game "Report Bug" feature to get help
- **Technical issues?** See the [README](README.md) for troubleshooting
- **Want to contribute?** Check the [Developer Guide](DEVELOPERGUIDE.md)

---

**Remember: It's supposed to be hard! You're fighting an uphill battle against reckless AI development. Every turn you survive is a victory. 🎯**