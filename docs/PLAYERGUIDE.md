# P(DOOM) PLAYER GUIDE

Welcome to P(DOOM): AI SAFETY STRATEGY GAME!  
A bootstrap strategy game about managing a scrappy AI safety lab with realistic funding constraints.

**NEW IN v0.4.0: STRATEGIC MENU REVOLUTION!** 
- **Bootstrap Economic Model**: Weekly staff costs based on realistic AI safety researcher salaries
- **Strategic Fundraising**: Choose from 4 funding approaches with different risk/reward profiles  
- **Menu Consolidation**: Research and funding streamlined into strategic decision dialogs
- **Verbose Activity Logging**: Detailed RPG-style feedback on all actions and outcomes
- **$100k Starting Capital**: Sufficient runway to experiment with different growth strategies

**Current Version**: v0.4.0+hotfix1 "Strategic Menu Revolution" - Major economic rebalancing and menu overhaul

**Bootstrap Challenge**: Experience the real constraints of running an AI safety nonprofit - manage weekly cash flow, make strategic funding decisions, and scale your team efficiently while keeping doom levels low.

## Table of Contents
- [Quick Setup](#quick-setup) (Line 31)
- [New Player Tutorial & Help System](#new-player-tutorial--help-system) (Line 42)
- [How to Play](#how-to-play) (Line 94)
- [Milestone Events & Employee Management](#milestone-events--employee-management) (Line 120)
- [Controls & Interface](#controls--interface) (Line 151)
- [Visual Feedback & UI Transitions](#visual-feedback--ui-transitions) (Line 184)
- [Action Points Strategy](#action-points-strategy) (Line 211)
- [Competitors & Intelligence](#competitors--intelligence) (Line 261)
- [Screen Layout](#screen-layout) (Line 298)
- [Actions You Can Take](#actions-you-can-take) (Line 316)
- [Upgrade Strategy](#upgrade-strategy) (Line 330)
- [Milestone-Driven Special Events](#milestone-driven-special-events) (Line 343)
- [Game Events & Tips](#game-events--tips) (Line 421)
- [Game Over Conditions](#game-over-conditions) (Line 479)
- [Seeds & High Scores](#seeds--high-scores) (Line 489)
- [End-Game Menu](#end-game-menu) (Line 496)
- [Need Help?](#need-help) (Line 513)

**Configuration**: For game customization and settings, see [CONFIG_SYSTEM.md](CONFIG_SYSTEM.md).

---

## Quick Setup

1. **Install Python 3.9+** (if not already installed)
2. **Install pygame**: `pip install pygame`
3. **Run the game**: `python main.py`

That's it! The game will open with a main menu.

---


## New Player Tutorial & Help System

**🎯 For First-Time Players:**
P(Doom) includes a comprehensive tutorial system and Factorio-style hint system to guide new players through the game mechanics.

### Tutorial vs Hints
- **Tutorial**: Interactive step-by-step walkthrough (can be enabled/disabled in New Player Experience)
- **Hints**: Context-sensitive help popups that appear once when you first encounter mechanics (can be toggled in Settings)

### Tutorial Features
- **Interactive Tutorial**: Step-by-step guidance through core game mechanics on your first playthrough
- **Context-Sensitive Help**: Automatic tips when you encounter new mechanics for the first time
- **In-Game Help**: Press `H` at any time to access the Player Guide
- **Skippable**: Tutorial can be dismissed or skipped if you prefer to learn by playing

### Tutorial Coverage
The tutorial walks you through:
1. **Resources**: Understanding money, staff, reputation, Action Points, and p(Doom)
2. **Actions**: Taking actions to manage your lab and spend Action Points
3. **Action Points**: Strategic resource management and staff scaling
4. **Turn Management**: Ending turns and handling events
5. **Events & Milestones**: Random events and growth milestones
6. **Upgrades**: Permanent improvements to your lab

### First-Time Help
Get automatic guidance when you:
- Hire your first staff member (learn about Action Point scaling) - *appears when first attempting to hire beyond starting staff*
- Purchase your first upgrade (understand permanent benefits)
- Run out of Action Points (tips for increasing capacity)
- Reach high p(Doom) levels (warning and safety advice)

**Dismissing Help**: Click the × button, press Escape, or press Enter to dismiss help popups.

### Getting Help
- **During Tutorial**: Use `Next` to proceed or `Skip` to exit tutorial
- **Anytime**: Press `H` key to open the Player Guide
- **Main Menu**: Access Player Guide and enhanced settings system
- **Debug Mode**: Press Ctrl+D during gameplay to check UI state (for troubleshooting)
- **Reset Hints**: Press Ctrl+R during gameplay to reset all hints for new players

### Enhanced Settings & Configuration System
P(Doom) features a comprehensive settings system organized into logical categories:

**🔊 Audio Settings:**
- Master sound control and volume adjustment
- Individual sound effect toggles
- Audio feedback preferences

**⚙️ Game Configuration:**
- Create custom game configurations with different starting resources
- Set custom seeds for reproducible gameplay experiences
- Export/import config + seed packages for community sharing
- Templates: Standard, Hardcore, Sandbox, and Speedrun modes

**🎮 Gameplay Settings:**
- Auto-delegation preferences
- Difficulty modifiers
- Event frequency controls
- Opponent intel display options

**♿ Accessibility:**
- Visual aid preferences
- Keyboard navigation options
- Text scaling and contrast settings

**⌨️ Keybindings:**
- Customize keyboard shortcuts
- Review all available hotkeys

**Community Features:**
- Share config + seed combinations for challenges
- Import community-created configurations
- Export your setup for others to try

### User Interface & Accessibility
P(Doom) features an enhanced UI system designed for accessibility and clear visual feedback:

- **Visual Feedback**: Buttons provide clear visual states (normal, hover, pressed, disabled)
- **Keyboard Navigation**: Use Tab to navigate menus, Enter/Space to select, Escape to go back
- **Enhanced Tooltips**: Hover over actions and upgrades for detailed cost and availability information
- **Achievement Sound Effects**: Celebratory 'Zabinga!' sound when research papers are completed
- **Error Feedback**: Audio beep plays after three repeated identical errors (easter egg)
- **Responsive Design**: UI adapts to different screen sizes and window resizing
- **Low-Poly Aesthetic**: Clean, retro-inspired visual design with modern accessibility features

**Accessibility Features:**
- Focus indicators for keyboard navigation (yellow rings)
- Scalable text support for readability
- High contrast options for better visibility
- Audio feedback for important events
- Comprehensive keyboard navigation support


---

## How to Play

### Your Goal
Survive as long as possible while managing your AI safety lab. Avoid catastrophe (p(Doom) = 100%), keep your team, and outlast the reckless competition.


### Basic Game Loop
1. **Take actions** (left panel) - Click buttons to spend money and affect your lab
2. **Buy upgrades** (right panel) - One-time purchases that give permanent benefits  
3. **End your turn** - Click "END TURN" or press `Space` to see results

### Keyboard Controls & Debug Features
- **Space**: End turn (always available, even during tutorials)
- **H**: Open Player Guide overlay
- **Number keys (1-9)**: Execute actions by keyboard shortcut
- **Tab/Arrows**: Navigate menus
- **Enter/Space**: Confirm selections
- **Escape**: Go back/cancel (multiple presses access quit menu)

#### Debug & Recovery Controls
- **Ctrl+D**: Display UI state debug information
- **Ctrl+E**: Emergency clear stuck popup events
- **Ctrl+R**: Reset all hints for new players
- **[**: Take screenshot (saved to screenshots/ folder)
4. **Handle events** - Random events will challenge your strategy
5. **Repeat** - Keep going until game over


### Resources to Manage
- **💰 Money**: Spend on actions and upgrades, earn through fundraising
- **👥 Staff**: Your team (costs money each turn, can quit if unpaid)
- **⭐ Reputation**: Affects fundraising and events
- **⚡ Action Points (AP)**: Limit actions per turn (3 AP max, resets each turn)
- **☢️ p(Doom)**: AI catastrophe risk (game over at 100%)
- **🖥️ Compute**: Powers employee productivity and research
- **📄 Research**: Progress toward publishing papers (boosts reputation, plays celebratory sound)
- **🎯 Competitors**: Track discovered opponents and their progress toward AGI

---

## Bootstrap Economics & Cash Flow Management

**P(Doom) v0.4.0+ features a realistic bootstrap AI safety lab economic model:**

### Weekly Staff Costs
- **First Employee**: $600/week (~$31k annually) - Junior research assistant level
- **Additional Staff**: $800/week each (~$42k annually) - Growing overhead costs
- **5-Person Team**: ~$4,000/week total maintenance costs
- **Strategic Pressure**: Creates real 2-3 week funding planning cycles

### Fundraising Strategy (NEW!)
Access **Fundraising Options** action to choose from 4 strategic approaches:
- **Fundraise Small**: $5-10k (covers 2-3 weeks, low risk)
- **Fundraise Big**: $15-25k (provides 4-6 weeks runway, higher risk)  
- **Borrow Money**: Immediate cash with future debt obligations
- **Alternative Funding**: Grants/partnerships (unlocked with milestones)

### Zero-Cost Operations
Bootstrap approach means many actions are now free:
- **Hiring**: No signing bonuses for nonprofit (staff costs come from weekly maintenance)
- **Scout Opponents**: Free internet research and public information gathering
- **Media/PR**: Self-funded social media and blog outreach  
- **Research**: Reduced from $40k to $3k per week (still significant for small labs)

### Moore's Law Advantage
- **Compute Costs**: Decrease 2% each week (realistic technology improvement)
- **Strategic Planning**: Early compute purchases become cheaper over time
- **Scaling Benefits**: Late-game projects benefit from accumulated cost reductions

---

## Milestone Events & Employee Management

As your organization grows, you'll encounter special milestone events:

### Manager System (9+ Employees)
- **Trigger**: Unlocks at 9 employees, hire managers for $90 (1.5x normal cost)
- **Rules**: Employees beyond 9 need management or become unproductive
- **Visual**: Managers = green blobs, unmanaged = red slash overlay

### Board Compliance (>$10K Spending)  
- **Trigger**: Spend >$10K without Accounting Software
- **Effect**: Installs board members, audit risk, "Search" action unlocked
- **Prevention**: Purchase Accounting Software ($500) beforehand

*For detailed milestone mechanics, see [Milestone-Driven Special Events](#milestone-driven-special-events) below.*

### Employee Types
- **Regular Employees** (blue): Your standard workforce
- **Managers** (green with crown): Supervise clusters of employees  
- **Board Members** (purple with briefcase): Ensure regulatory compliance

### Employee Productive Actions
Each employee performs specialized productive actions when requirements are met, providing passive bonuses appropriate to their role:

- **Research Staff**: Focus on literature review, data collection, and advanced algorithm development
- **Security Engineers**: Conduct security auditing, threat modeling, and incident response
- **Operations Staff**: Optimize infrastructure, monitor systems, and maintain documentation  
- **Administrative Staff**: Streamline processes, manage stakeholder relations, and ensure compliance
- **Managers**: Handle strategic planning, team coordination, and resource allocation

**Key Mechanics:**
- Employees automatically perform their selected productive action each game tick (no cost)
- Actions require sufficient compute, reputation, or organizational resources to activate
- Active actions provide multiplicative effectiveness bonuses (typically +6% to +18%)
- Failed requirements result in reduced effectiveness until conditions improve
- Actions can be changed at any time (future UI feature planned)

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

**💡 Tip**: Keyboard shortcuts are displayed on the left and right sides of the main menu for quick reference.

### In-Game Controls
| Action | How To |
|--------|--------|
| Take action | Click action button (left panel) **OR** press number keys 1-9 |
| Buy upgrade | Click upgrade button (right panel) |
| End turn | Click "END TURN" or press `Space` |
| View upgrade details | Hover mouse over purchased upgrades (top right) |
| Open Player Guide | Press `H` key anytime |
| Quit to menu | Press `Esc` |
| End-game options | Click anywhere on final score screen to access end-game menu |

**🎹 Keyboard Shortcuts for Actions:**
- **1-9 keys**: Execute actions 1-9 directly (displayed as [1], [2], etc. on action buttons)
- **Audio feedback**: Hear a satisfying sound when spending Action Points
- **Visual feedback**: Watch the AP counter glow when Action Points are spent  
- **Achievement feedback**: Celebratory 'Zabinga!' sound when research papers are completed
- **Error handling**: Audio beep after 3 repeated identical errors (easter egg)

### Context Window System (80's Terminal Style)
**💡 Enhanced Help & Information with Retro Flair:**
- **Hover Information**: Move mouse over any UI element to see detailed context information
- **DOS-Style Window**: Appears at bottom of screen (8-10% height) with distinctive 80's techno-green aesthetic
- **ALL CAPS Display**: Information shown in terminal-style ALL CAPS text using Courier font
- **Minimize/Maximize**: Click the (-/+) button to toggle context window size
- **Smart Content**: Shows costs, requirements, effects, and availability status
- **Clean Interface**: Only unlocked actions are shown, reducing visual clutter
- **Progressive Disclosure**: Information appears when needed, stays out of the way otherwise

**Retro Styling:**
- **Colors**: Bright techno-green text on dark green background for authentic 80's terminal feel
- **Typography**: Monospace Courier font in ALL CAPS for DOS authenticity
- **Layout**: Horizontal information layout optimized for the thin terminal window

**What You'll See:**
- **Action Details**: Full descriptions, AP/money costs, delegation options, requirements (in ALL CAPS)
- **Resource Information**: Current values, explanations, and how they're used
- **Upgrade Information**: Effects, costs, unlock requirements, and benefits
- **Filtered Actions**: Only available/unlocked actions appear in the interface
- **Smart Mapping**: Proper click handling for filtered action lists

### Game Modes
- **Weekly Seed**: This week's community challenge (same for everyone)
- **Custom Seed**: Enter your own seed for repeatable scenarios
- **Report Bug**: Submit feedback or issues (privacy-focused)

---

## Visual Feedback & UI Transitions

The game provides rich visual feedback to help you understand how your actions affect the game state:

### Upgrade Transitions
When you purchase upgrades, they don't just disappear - they smoothly animate from their button location to become icons at the top right:

- **Smooth Animation**: Upgrades follow a curved arc path over 1 second
- **Visual Trail**: Green trail points create motion blur effect during the transition  
- **Glow Highlight**: The destination icon location pulses with a green glow
- **Clear Feedback**: You can see exactly where your purchased upgrade ends up

### Other Visual Feedback
- **Action Points**: AP counter glows yellow when spent, showing strategic impact
- **Cash Flow**: Balance changes appear when accounting software is purchased
- **Employee Animations**: Staff blobs animate in from the side when hired
- **UI State Changes**: All UI state changes include visual transitions for clarity

### Why Visual Feedback Matters
These animations aren't just decoration - they serve important gameplay functions:
- **Clarity**: See where UI elements go when they change state
- **Feedback**: Immediate confirmation of successful actions
- **Understanding**: Visual cues help you learn the interface faster
- **Satisfaction**: Smooth animations make interactions feel responsive

---

## Action Points Strategy

The Action Points (AP) system creates strategic depth through resource management and staff scaling.

### How Action Points Work
- **Base AP**: You start with 3 Action Points per turn
- **Staff Scaling**: Regular staff provide +0.5 AP each (hire more for higher capacity)
- **Admin Assistants**: Specialized staff providing +1.0 AP each (expensive but powerful)
- **Turn Reset**: AP automatically resets to calculated maximum each turn
- **Dynamic Scaling**: Your max AP grows as you hire staff (3 + staff*0.5 + admin*1.0)

### Staff Types & AP Bonuses
- **📋 Admin Assistants**: High-cost specialists (+1.0 AP each) for maximum action capacity
- **🔬 Research Staff**: Enable delegation of research actions with reduced effectiveness
- **⚙️ Operations Staff**: Enable delegation of operational tasks, often with lower AP costs
- **👥 Regular Staff**: Provide base +0.5 AP bonus and general productivity

### Delegation System
**Research Delegation:**
- Safety Research and Governance Research can be delegated to research staff
- Requires 2+ research staff, maintains same AP cost, but 80% effectiveness
- Good for managing multiple priorities when you have the staff

**Operations Delegation:**
- Buy Compute can be delegated to operations staff for routine procurement
- Requires 1+ operations staff, costs 0 AP when delegated, full effectiveness
- Automatically delegated when beneficial (lower AP cost)

### Visual Indicators
- **AP Counter**: Displayed as "AP: 2/3" in the top resource bar
- **Glow Effect**: AP counter glows yellow when Action Points are spent
- **Button States**: Action buttons gray out when you lack sufficient AP
- **Cost Display**: Each action shows both money cost and AP cost


### Strategic Tips
🎯 **Early Game (3-4 AP)**: Focus on essential actions like fundraising and safety research  
📈 **Growth Phase (5-8 AP)**: Invest in staff hiring to expand action capacity  
⚡ **Late Game (9+ AP)**: Leverage delegation and specialized staff for complex operations  
💼 **Admin Investment**: Admin assistants are expensive but provide the highest AP return  
🔄 **Delegation Planning**: Build research/ops staff for long-term delegation benefits  

### Staff Investment Guide
- **Cost-Effective**: Regular staff (60$ for +0.5 AP = 120$ per AP)
- **High-Impact**: Admin assistants (80$ for +1.0 AP = 80$ per AP) 
- **Specialized**: Research/Ops staff (70$ for delegation capabilities)
- **Balanced Approach**: Mix of regular staff, 1-2 admins, and specialists based on strategy

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
**Left Panel:** Available unlocked actions (filtered to show only what you can currently access)
**Right Panel:** Available upgrades (becomes icons after purchase)
**Bottom Context Window:** Retro 80's-style terminal showing detailed information (8-10% of screen height)
**Bottom Center:** "END TURN" button
**Bottom Left:** Activity log showing recent events

### Context Window (Bottom Terminal)
- **Retro Design**: 80's techno-green styling with DOS-style ALL CAPS text
- **Smart Information**: Shows detailed info about hovered actions, upgrades, or resources
- **Minimizable**: Click (-/+) button to collapse/expand
- **Always Visible**: Persistent information display in non-tutorial mode

### Activity Log
- Shows events from the current turn only
- Clears automatically when you end your turn  
- Displays action results, random events, and resource changes
- **Enhanced mode** unlocked later: scroll through complete game history

### Action Filtering
- **Clean Interface**: Only shows actions that are currently unlocked/available
- **Dynamic Layout**: Action buttons adjust based on number of available options
- **No Clutter**: Locked actions are hidden until requirements are met

---

## Actions You Can Take

### Strategic Menu Actions (NEW!)
**💰 Fundraising Options** - Strategic funding dialog with 4 approaches and risk profiles
**� Research Options** - Unified research menu with Safety, Governance, Rush, and Quality approaches

### Core Actions
**👥 Grow Community** - Increase reputation, chance to gain staff
**🖥️ Buy Compute** - Purchase compute resources (cost decreases over time via Moore's Law)
**📈 Hire Staff** - Interactive hiring dialog to select specific employee types (no upfront costs!)
**🕵️ Espionage** - Learn about competitor progress (minimal $500 operational cost)
**🎯 Scout Opponents** - Focused intelligence gathering (free internet research)

### Strategic Dialogs (v0.4.0+)
Both **Fundraising Options** and **Research Options** now open strategic choice menus:
- **Multiple Approaches**: Each with different risk/reward trade-offs
- **Strategic Planning**: Choose based on current game state and needs
- **Immediate Execution**: Select an option to execute it immediately
- **Progressive Unlocks**: More options become available as you grow

### Bootstrap Operations
Many actions are now **zero-cost** reflecting the bootstrap nonprofit model:
- **Press Releases**: Self-funded social media and blog outreach
- **Social Media Campaigns**: Organic reach and community engagement  
- **Public Statements**: Blog posts and community communications
- **Hiring**: No signing bonuses (weekly maintenance covers all staff costs)

*Each action shows its cost and effects in the context window when you hover over it.*

---

## Upgrade Strategy

**🖥️ Computer System** - Makes research more effective
**🪑 Comfy Chairs** - Staff less likely to quit when unpaid
**☁️ Secure Cloud** - Reduces damage from lab breakthrough events
**📊 Accounting Software** - Shows resource changes each turn
**📋 Event Log System** - Unlock scrollable activity history
**📱 Compact Activity Display** - Minimize activity log to save screen space

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

### Compact Activity Display Upgrade

**Purchase Effects:**
- **Cost**: $150 (visible in right-panel upgrades)
- **Minimize Button**: Adds minimize (-) button to activity log header
- **Space Saving**: Minimized log shows only title bar with expand (+) button
- **Visual Enhancement**: Improved screen space utilization for streamlined UI

**When to Buy:**
- When screen space is limited or cluttered
- After unlocking scrollable event log (turn 5+)
- For cleaner, more focused gameplay experience
- Early-to-mid game for UI optimization

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

Instead of generic "GAME OVER" messages, you'll receive detailed end game scenarios that explain what led to your defeat and analyze your organization's performance based on how long you survived and what caused the end.

Your score is how many turns you survived. Try to beat your previous best!


---
=======


## Seeds & High Scores

**Weekly Seed**: Everyone gets the same challenge each week - compete with friends!  
**Custom Seed**: Use any text as a seed for repeatable games
**High Scores**: Tracked separately for each seed in `local_highscore.json`

---

## End-Game Menu

When your game ends, you'll see your final statistics followed by an **End-Game Menu** with several options:

### Menu Options
- **🔄 Relaunch Game**: Restart with the same seed for another attempt
- **🏠 Main Menu**: Return to the main menu to select new game options
- **⚙️ Settings**: View game settings and configuration information  
- **💬 Submit Feedback**: Share suggestions and feedback about the game
- **🐛 Submit Bug Request**: Report bugs or technical issues

### Navigation
- **Mouse**: Click any option to select it
- **Keyboard**: Use arrow keys to navigate, Enter to select, Escape for Main Menu
- **Features**: Same bug reporting system as main menu, preserves game statistics

This replaces the old "click anywhere to restart" behavior, giving you more control over what to do after a game ends.

---

## Need Help?

- **Stuck?** Try the in-game "Report Bug" feature to get help
- **Technical issues?** See the [README](../README.md) for troubleshooting  
- **Want to contribute?** Check the [Developer Guide](DEVELOPERGUIDE.md)
- **Version questions?** See [CHANGELOG.md](../CHANGELOG.md) for release history and known issues

---

**Remember: It's supposed to be hard! You're fighting an uphill battle against reckless AI development. Every turn you survive is a victory. 🎯**