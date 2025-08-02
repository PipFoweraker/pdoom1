# P(Doom) Player Guide

Welcome to **P(Doom): Bureaucracy Strategy Game**!  
A satirical strategy game about managing an AI safety lab while competing against reckless frontier labs.

**Version Information**: Check the game window title or see [CHANGELOG.md](CHANGELOG.md) for current version and recent changes.

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
- **⚡ Action Points (AP)**: Limit actions per turn (3 AP max, resets each turn)
- **☢️ p(Doom)**: AI catastrophe risk (game over at 100%)
- **🖥️ Compute**: Powers employee productivity and research
- **📄 Research**: Progress toward publishing papers (boosts reputation)
- **🎯 Competitors**: Track discovered opponents and their progress toward AGI

---

## Milestone Events & Employee Management

As your organization grows, you'll encounter special milestone events that change how your lab operates:

### Manager System (9th Employee Milestone)
- **Trigger**: Special event triggers when you reach 9 employees for the first time
- **Effect**: 
  - Unlocks the "Hire Manager" action (costs $90, 1.5x normal staff cost)
  - Provides notification about management requirements
  - Manager milestone achieved when first manager is hired
- **Management Rules**:
  - First 9 employees work productively without management
  - Employees beyond 9 require management or become unproductive (red slash overlay)
  - Each Manager can oversee 9 additional employees
  - Plan ahead: hire a Manager for every ~18 employees total

### Board Member Compliance (Spending Threshold)
- **Trigger**: Spending more than $10,000 in a single turn without Accounting Software
- **Effect**: 
  - Installs 2 Board Members automatically for compliance monitoring
  - Audit risk begins accumulating with reputation penalties over time
  - "Search" action becomes available (20% success rate, costs $25 and 1 AP)
  - Accumulating penalties: reputation loss and financial fines for non-compliance
- **Prevention**: Purchase Accounting Software upgrade ($500) to prevent this milestone

### Employee Types
- **Regular Employees** (blue): Your standard workforce
- **Managers** (green with crown): Supervise clusters of employees  
- **Board Members** (purple with briefcase): Ensure regulatory compliance

### Cash Flow UI
- **Unlocked by**: Purchasing the Accounting Software upgrade ($500)
- **Features**: 
  - Real-time balance change indicators (green for income, red for expenses)
  - Displays the last money change amount next to your current balance
  - Prevents the board member spending threshold milestone
  - Essential for avoiding compliance oversight in large organizations

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

## Action Points Strategy

The Action Points (AP) system adds strategic depth by limiting your actions each turn.

### How Action Points Work
- **Starting AP**: You begin each turn with 3 Action Points
- **Action Costs**: Each action costs 1 AP (shown on action buttons)
- **Strategic Choices**: With limited AP, choose your most important actions first
- **Turn Reset**: AP automatically resets to 3 at the start of each new turn

### Visual Indicators
- **AP Counter**: Displayed as "AP: 2/3" in the top resource bar
- **Glow Effect**: AP counter glows yellow when you spend points
- **Button States**: Action buttons gray out when you lack sufficient AP
- **Cost Display**: Each action shows both money cost and AP cost

### Strategic Tips
🎯 **Prioritize Critical Actions**: Use AP on actions that directly address immediate threats  
💡 **Plan Ahead**: Consider saving AP for emergency responses to events  
⚖️ **Balance Resources**: Don't spend all AP early - keep some flexibility  
🔄 **Turn Efficiency**: Use all 3 AP each turn for maximum impact  

### Action Efficiency Guide
- **Free Actions**: Fundraise (0 money, 1 AP) - great early game
- **High Impact**: Safety Research (40 money, 1 AP) - reduces doom effectively  
- **Long-term**: Hire Staff (60 money, 1 AP) - builds capacity
- **Intelligence**: Espionage/Scout (30-50 money, 1 AP) - knowledge is power

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

## Milestone-Driven Special Events

As your organization grows, you'll unlock new systems and face new challenges through milestone-triggered events:

### Management Milestones (9+ Employees)

**Hire Manager Action:**
- **Unlock Condition**: Available when you have 9+ employees
- **Cost**: 1.5x normal hiring cost ($90 vs $60)
- **Effect**: Adds a manager who can oversee up to 9 employees

**Static Management Effects:**
- **Team Clusters**: Each manager handles up to 9 employees effectively
- **Unmanaged Penalty**: Employees beyond 9 without a manager become unproductive
- **Visual Indicators**: 
  - Managers appear as **green blobs**
  - Unmanaged employees show **red slash overlay**
  - Normal employees remain **blue blobs**

**Strategy Tips:**
- Plan manager hiring before reaching 10+ employees
- Multiple managers create separate team clusters
- Unmanaged employees still consume resources but contribute nothing

### Financial Oversight Milestones (High Spending)

**Board Member Trigger:**
- **Condition**: Spend >$10,000 in a single turn without accounting software
- **Effect**: Board installs 2 Board Members for compliance monitoring
- **Consequences**: Unlocks "Search" action, begins audit risk accumulation

**Board Search Action:**
- **Unlock**: Available when board members are active
- **Success Rate**: 20% chance of positive outcomes
- **Benefits**: Compliance improvements, cost savings, process efficiency
- **Risk Reduction**: Successful searches reduce audit risk levels

**Audit Risk System:**
- **Accumulation**: Risk increases each turn while board members are active
- **Penalties**: Reputation loss (>5 risk), financial fines (>10 risk)
- **Mitigation**: Successful searches or purchasing accounting software

### Accounting Software Upgrade

**Purchase Effects:**
- **Cost**: $500 (visible in right-panel upgrades)
- **Cash Flow UI**: Shows balance changes (+$500, -$200) next to money display
- **Compliance Protection**: Prevents board member milestone trigger
- **Strategic Value**: Essential for high-spending strategies

**When to Buy:**
- Before planning expensive expansion (>$10K spending)
- Early game if you anticipate scaling quickly
- As insurance against audit penalties

---


## Game Events & Tips


### Random Events to Watch For
- **🔬 Lab Breakthrough** - p(Doom) increases (mitigated by security upgrades)
- **💸 Funding Crisis** - Lose money when resources are tight
- **😔 Staff Burnout** - Staff quit when overworked and underpaid
- **💻 Software Offers** - Special upgrade opportunities

### Enhanced Event System (Unlocked Turn 8+)

After turn 8, your organization will unlock advanced event handling capabilities:

**🚨 Popup Events** - Critical situations that pause the game and require immediate attention:
- Overlay appears with detailed information and multiple response options
- Choose from Accept, Defer, Reduce, or Dismiss actions
- Each choice has different consequences and resource impacts

**⏳ Deferred Events** - Strategic event management:
- Defer non-critical events to handle at a better time
- Deferred events appear in the lower-right "Deferred Events" zone
- Show countdown timers (events auto-execute when expired)
- Strategic deferring allows you to manage multiple crises

**Event Actions Explained:**
- **Accept**: Full event impact (original effect)
- **Defer**: Postpone for up to 3-4 turns (limited uses)
- **Reduce**: Quick response with reduced impact (if available)
- **Dismiss**: Ignore event (may have hidden consequences)

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
- **Version questions?** See [CHANGELOG.md](CHANGELOG.md) for release history and known issues

---

**Remember: It's supposed to be hard! You're fighting an uphill battle against reckless AI development. Every turn you survive is a victory. 🎯**