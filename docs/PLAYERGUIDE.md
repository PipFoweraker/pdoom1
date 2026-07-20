# P(DOOM) PLAYER GUIDE

Welcome to P(DOOM): AI SAFETY STRATEGY GAME!
A bootstrap strategy game about managing a scrappy AI safety lab with realistic funding constraints.

**NEW IN v0.11.0: TRAVEL & CONFERENCES!**
- **Academic Conference System**: Submit papers to real-world AI conferences (NeurIPS, ICML, ICLR, etc.)
- **Travel Mechanics**: Realistic travel costs with economy/business/first class options
- **Jet Lag System**: Researchers experience productivity loss after international travel
- **Paper Review Process**: Multi-turn paper submission with acceptance decisions
- **Calendar Integration**: Conferences occur at historically accurate times

**Current Version**: v0.11.0 'Travel & Conferences' - Academic publishing and travel system

**Strategic Challenge**: Experience the real constraints of running an AI safety nonprofit - manage weekly cash flow, make strategic funding decisions, and scale your team efficiently while keeping doom levels low. With extended gameplay, you now have time to build meaningful strategies and recover from setbacks!

## Table of Contents
- [Quick Setup](#quick-setup)
- [New Player Tutorial & Help System](#new-player-tutorial--help-system)
- [How to Play](#how-to-play)
- [Milestone Events & Employee Management](#milestone-events--employee-management)
- [Controls & Interface](#controls--interface)
- [Visual Feedback & UI Transitions](#visual-feedback--ui-transitions)
- [Action Points Strategy](#action-points-strategy)
- [Competitors & Intelligence](#competitors--intelligence)
- [Screen Layout](#screen-layout)
- [Actions You Can Take](#actions-you-can-take)
- [Upgrade Strategy](#upgrade-strategy)
- [Milestone-Driven Special Events](#milestone-driven-special-events)
- [Travel & Academic Conferences](#travel--academic-conferences-v0110) (NEW!)
- [Game Events & Tips](#game-events--tips)
- [Game Over Conditions](#game-over-conditions)
- [Seeds & High Scores](#seeds--high-scores)
- [End-Game Menu](#end-game-menu)
- [Need Help?](#need-help)

**Configuration**: For game customization and settings, see [CONFIG_SYSTEM.md](CONFIG_SYSTEM.md).

---

## Quick Setup

### For Players (Recommended)

1. **Download the game**: Get the latest release from [GitHub Releases](https://github.com/PipFoweraker/pdoom1/releases)
2. **Extract and run**: Double-click `PDoom.exe` (Windows)
3. **Play**: The game will open with the main menu

### For Developers

Building from source or contributing? See [Development Setup](../docs/developer/CONTRIBUTING.md).

**Note:** This game is built with Godot 4.x. The Python/Pygame version is for development only.

---


## New Player Tutorial & Help System

**[TARGET] For First-Time Players:**
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

**Dismissing Help**: Click the x button, press Escape, or press Enter to dismiss help popups.

### Getting Help
- **During Tutorial**: Use `Next` to proceed or `Skip` to exit tutorial
- **Anytime**: Press `H` key to open the Player Guide
- **Main Menu**: Access Player Guide and enhanced settings system
- **Debug Mode**: Press Ctrl+D during gameplay to check UI state (for troubleshooting)
- **Reset Hints**: Press Ctrl+R during gameplay to reset all hints for new players

### Enhanced Settings & Configuration System
P(Doom) features a comprehensive settings system organized into logical categories:

**[EMOJI] Audio Settings:**
- Master sound control and volume adjustment
- Individual sound effect toggles
- Audio feedback preferences

**[GEAR][EMOJI] Game Configuration:**
- Create custom game configurations with different starting resources
- Set custom seeds for reproducible gameplay experiences
- Export/import config + seed packages for community sharing
- Templates: Standard, Hardcore, Sandbox, and Speedrun modes

**[EMOJI] Gameplay Settings:**
- Auto-delegation preferences
- Difficulty modifiers
- Event frequency controls
- Opponent intel display options

**[EMOJI] Accessibility:**
- Visual aid preferences
- Keyboard navigation options
- Text scaling and contrast settings

**[KEYBOARD][EMOJI] Keybindings:**
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
3. **End your turn** - Click 'END TURN' or press `Space` to see results

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
- **[EMOJI] Money**: Spend on actions and upgrades, earn through fundraising
- **[EMOJI] Staff**: Your team (costs money each turn, can quit if unpaid)
- **[EMOJI] Reputation**: Affects fundraising and events
- **[LIGHTNING] Action Points (AP)**: Limit actions per turn (3 AP max, resets each turn)
- **[EMOJI][EMOJI] p(Doom)**: AI catastrophe risk (game over at 100%)
- **[DESKTOP][EMOJI] Compute**: Powers employee productivity and research
- **[EMOJI] Research**: Progress toward publishing papers (boosts reputation, plays celebratory sound)
- **[TARGET] Competitors**: Track discovered opponents and their progress toward AGI

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
- **Effect**: Installs board members, audit risk, 'Search' action unlocked
- **Prevention**: Purchase Accounting Software ($500) beforehand

*For detailed milestone mechanics, see [Milestone-Driven Special Events](#milestone-driven-special-events) below.*

### Employee Types
- **Individual Researchers**: Specialists with unique names, traits, and skills
  - Safety (green dot): Reduce doom through careful research
  - Capabilities (red dot): Fast research but increases doom
  - Interpretability (purple dot): Standard research, special actions
  - Alignment (cyan dot): Reduces doom through alignment work
- **Managers** (yellow dot): Each oversees a team of up to 8 researchers
- **Compute Engineers**: Improve compute efficiency

### Researcher Productivity System
Each researcher generates research and affects doom based on their specialization and traits:

- **Productivity Factors**: Skill level, burnout, and traits affect output
- **Team Bonuses**: team_player trait gives +10% productivity per team player
- **Compute Requirement**: Each productive researcher needs 1 compute unit
- **Management Required**: Unmanaged researchers become unproductive and add doom

**Key Mechanics:**
- Researchers auto-generate research each turn (30% chance per productive researcher)
- Specialization determines doom impact (safety reduces, capabilities increases)
- Burnout accumulates over time, reducing effectiveness
- Traits provide bonuses or penalties (team_player, workaholic, leak_prone, etc.)
- Use Team Building action to reduce burnout across all researchers

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
| Navigate options | Arrow keys ^v or mouse |
| Select option | Enter or mouse click |
| Exit | Escape key |

**[IDEA] Tip**: Keyboard shortcuts are displayed on the left and right sides of the main menu for quick reference.

### In-Game Controls
| Action | How To |
|--------|--------|
| Take action | Click action button (left panel) **OR** press number keys 1-9 |
| Buy upgrade | Click upgrade button (right panel) |
| End turn | Click 'END TURN' or press `Space` |
| View upgrade details | Hover mouse over purchased upgrades (top right) |
| Open Player Guide | Press `H` key anytime |
| Quit to menu | Press `Esc` |
| End-game options | Click anywhere on final score screen to access end-game menu |

**[EMOJI] Keyboard Shortcuts for Actions:**
- **1-9 keys**: Execute actions 1-9 directly (displayed as [1], [2], etc. on action buttons)
- **Audio feedback**: Hear a satisfying sound when spending Action Points
- **Visual feedback**: Watch the AP counter glow when Action Points are spent
- **Achievement feedback**: Celebratory 'Zabinga!' sound when research papers are completed
- **Error handling**: Audio beep after 3 repeated identical errors (easter egg)

### Context Window System (80's Terminal Style)
**[IDEA] Enhanced Help & Information with Retro Flair:**
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
- **[CHECKLIST] Admin Assistants**: High-cost specialists (+1.0 AP each) for maximum action capacity
- **[EMOJI] Research Staff**: Enable delegation of research actions with reduced effectiveness
- **[GEAR][EMOJI] Operations Staff**: Enable delegation of operational tasks, often with lower AP costs
- **[EMOJI] Regular Staff**: Provide base +0.5 AP bonus and general productivity

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
- **AP Counter**: Displayed as 'AP: 2/3' in the top resource bar
- **Glow Effect**: AP counter glows yellow when Action Points are spent
- **Button States**: Action buttons gray out when you lack sufficient AP
- **Cost Display**: Each action shows both money cost and AP cost


### Strategic Tips
[TARGET] **Early Game (3-4 AP)**: Focus on essential actions like fundraising and safety research
[GRAPH] **Growth Phase (5-8 AP)**: Invest in staff hiring to expand action capacity
[LIGHTNING] **Late Game (9+ AP)**: Leverage delegation and specialized staff for complex operations
[EMOJI] **Admin Investment**: Admin assistants are expensive but provide the highest AP return
[EMOJI] **Delegation Planning**: Build research/ops staff for long-term delegation benefits

### Staff Investment Guide
- **Cost-Effective**: Regular staff (60$ for +0.5 AP = 120$ per AP)
- **High-Impact**: Admin assistants (80$ for +1.0 AP = 80$ per AP)
- **Specialized**: Research/Ops staff (70$ for delegation capabilities)
- **Balanced Approach**: Mix of regular staff, 1-2 admins, and specialists based on strategy

---

## Competitors & Intelligence

You're not alone in the AI race! Three competing organizations are also racing toward AGI:

### The Competition
- **[EMOJI] TechCorp Labs**: Massive tech corporation with deep pockets and aggressive timelines
- **[EMOJI][EMOJI] National AI Initiative**: Government-backed program with strong regulatory influence
- **[ROCKET] Frontier Dynamics**: Secretive startup with mysterious funding and rapid development

### Intelligence Gathering

**[EMOJI][EMOJI] Espionage (Available from start)**
- Cost: $30k, Risk: Moderate
- Discovers new competitors or gathers basic intelligence
- Can reveal progress estimates and general capabilities

**[TARGET] Scout Opponent (Unlocked after Turn 5)**
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
**Bottom Center:** 'END TURN' button
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
**[EMOJI] Fundraising Options** - Strategic funding dialog with 4 approaches and risk profiles
**[EMOJI] Research Options** - Unified research menu with Safety, Governance, Rush, and Quality approaches

### Core Actions
**[EMOJI] Grow Community** - Increase reputation, chance to gain staff
**[DESKTOP][EMOJI] Buy Compute** - Purchase compute resources (cost decreases over time via Moore's Law)
**[GRAPH] Hire Staff** - Interactive hiring dialog to select specific employee types (no upfront costs!)
**[EMOJI][EMOJI] Espionage** - Learn about competitor progress (minimal $500 operational cost)
**[TARGET] Scout Opponents** - Focused intelligence gathering (free internet research)

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

**[DESKTOP][EMOJI] Computer System** - Makes research more effective
**[CHAIR] Comfy Chairs** - Staff less likely to quit when unpaid
**[CLOUD][EMOJI] Secure Cloud** - Reduces damage from lab breakthrough events
**[CHART] Accounting Software** - Shows resource changes each turn
**[CHECKLIST] Event Log System** - Unlock scrollable activity history
**[PHONE] Compact Activity Display** - Minimize activity log to save screen space

*Purchased upgrades appear as icons at the top right - hover for details.*

---

## Milestone-Driven Special Events

As your organization grows, you'll unlock new systems and face new challenges through milestone-triggered events:

### Candidate Pool & Hiring System (v0.11.0+)

**Candidate-Based Hiring:**
- **Candidate Pool**: Available candidates appear in your hiring pool over time
- **Pool Size**: Maximum 6 candidates at once
- **Population**: New candidates arrive each turn (30% base chance + bonuses)
- **Starting Candidates**: 2-3 low-skill candidates available at game start
- **Reputation Bonus**: Higher reputation (60+) attracts better candidates more often

**Hiring from the Pool:**
- Each hiring action draws from available candidates of that specialization
- If no matching candidate exists, the hire fails (resources are refunded)
- Candidates have randomized traits, skills, and salary requirements

### Individual Researchers

**Researcher Attributes:**
- **Name**: Unique generated name
- **Specialization**: Safety, Capabilities, Interpretability, or Alignment
- **Skill Level**: 1-10 (affects productivity and research output)
- **Traits**: Positive (team_player, media_savvy) or Negative (leak_prone, burnout_prone)
- **Burnout**: Increases over time, reduces effective productivity

**Specialization Effects:**
- **Safety**: Reduces doom by 0.3 per productive researcher
- **Capabilities**: +25% research speed but adds doom based on researcher
- **Interpretability**: Standard research, unlocks special actions
- **Alignment**: Reduces doom by 0.15 per productive researcher

**Researcher Traits:**
- **team_player**: +10% productivity bonus (stacks with other team players)
- **media_savvy**: +3 reputation when publishing papers
- **workaholic**: +25% productivity
- **safety_conscious**: Extra doom reduction for safety researchers
- **leak_prone**: 1% chance per turn for research leak (+3 doom)
- **burnout_prone**: +50% faster burnout accumulation

### Team Management (8 Per Manager)

**Team Structure:**
- **Team Size**: Researchers auto-form teams of up to 8
- **Manager Requirement**: Each team needs 1 manager to be productive
- **Unmanaged Penalty**: +0.5 doom per unproductive researcher per turn

**Visual Indicators:**
- Colored dots by specialization (green=safety, red=capabilities, purple=interpretability, cyan=alignment)
- Productivity percentage shown
- Fire icon when burnout is high (60+)

**Strategy Tips:**
- Hire a manager before your 9th researcher
- Balance specializations for doom management
- Use Team Building action to reduce burnout (-15 per researcher)
- Watch for poaching events (competitors may steal your staff after turn 20)

### Financial Oversight Milestones (High Spending)

**Board Member Trigger:**
- **Condition**: Spend >$10,000 in a single turn without accounting software
- **Effect**: Board installs 2 Board Members for compliance monitoring
- **Consequences**: Unlocks 'Search' action, begins audit risk accumulation

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


## Travel & Academic Conferences (v0.11.0+)

Your AI safety lab can gain reputation and reduce doom by publishing papers at academic conferences. The travel system introduces realistic costs and jet lag mechanics.

### Conference Calendar

**Major Conferences (High Prestige):**
| Conference | Month | Prestige | Registration |
|-----------|-------|----------|--------------|
| NeurIPS | December | 1.00 | $800 |
| ICML | July | 0.95 | $700 |
| ICLR | May | 0.90 | $600 |
| AAAI | February | 0.85 | $500 |

**Minor Conferences (Lower Barrier):**
| Conference | Month | Prestige | Registration |
|-----------|-------|----------|--------------|
| FAccT | March | 0.70 | $400 |
| AIES | February | 0.65 | $350 |

**Special Programs (Funded):**
- **MATS Program**: Rolling admissions Q1/Q3 - mentorship-focused
- **ILIAD Summer**: June-August - research program
- **Safety Retreat**: November - informal networking

### Paper Submission Process

1. **Submit Paper** (Action: 15 research points, 1 AP)
   - Select a target conference
   - Your paper enters review for 3-5 turns
   - Quality depends on: research invested + researcher skill + traits

2. **Acceptance Decision**
   - Formula: `quality - (prestige × 0.8) + (reputation/100 × 0.15)`
   - Higher prestige conferences are harder to get into
   - Better reputation improves your chances

3. **Attend Conference** (if accepted)
   - Pay travel costs to attend
   - Present your paper for bonus effects
   - Network with other researchers

### Travel Costs

**Location Tiers:**
- **Local** (Tier 1): No travel costs
- **Domestic** (Tier 2): $500 flight + $150/day accommodation
- **International** (Tier 3): $2,500 flight + $300/day accommodation

**Total Cost** = Flight + (Accommodation × Days) + Registration

**Example**: Attending NeurIPS (International, 4 days, $800 reg)
- Economy: $2,500 + ($300 × 4) + $800 = **$4,500**
- Business: $5,000 + ($500 × 4) + $800 = **$7,800**

### Jet Lag System

Traveling researchers experience jet lag that temporarily reduces productivity.

**Severity Levels:**
| Travel Class | Duration | Severity | Productivity Impact |
|-------------|----------|----------|-------------------|
| Economy | 4 turns | High | -40% |
| Business | 3 turns | Medium | -25% |
| First Class | 2 turns | Low | -10% |

**Recovery:**
- Jet lag automatically recovers 1 level per turn
- Severity decreases: High → Medium → Low → None
- Plan important research projects around travel schedules

**Strategic Tips:**
- Send junior researchers to minor conferences (less impact from jet lag)
- Use business/first class for key researchers before major deadlines
- Balance travel opportunities against productivity loss

### Conference Benefits

**Presenting a Paper:**
- Reputation boost based on conference prestige
- Doom reduction from safety-focused papers
- Networking opportunities (future hiring bonuses)

**Attending Without Paper:**
- Smaller reputation gain
- Learn about competitor research
- Build relationships for future collaborations

---

## Game Events & Tips


### Random Events to Watch For
- **[EMOJI] Lab Breakthrough** - p(Doom) increases (mitigated by security upgrades)
- **[EMOJI] Funding Crisis** - Lose money when resources are tight
- **[EMOJI] Staff Burnout** - Staff quit when overworked and underpaid
- **[LAPTOP] Software Offers** - Special upgrade opportunities

### Enhanced Event System (Unlocked Turn 8+)

After turn 8, your organization will unlock advanced event handling capabilities:

**[EMOJI] Popup Events** - Critical situations that pause the game and require immediate attention:
- Overlay appears with detailed information and multiple response options
- Choose from Accept, Defer, Reduce, or Dismiss actions
- Each choice has different consequences and resource impacts

**[U+23F3] Deferred Events** - Strategic event management:
- Defer non-critical events to handle at a better time
- Deferred events appear in the lower-right 'Deferred Events' zone
- Show countdown timers (events auto-execute when expired)
- Strategic deferring allows you to manage multiple crises

**Event Actions Explained:**
- **Accept**: Full event impact (original effect)
- **Defer**: Postpone for up to 3-4 turns (limited uses)
- **Reduce**: Quick response with reduced impact (if available)
- **Dismiss**: Ignore event (may have hidden consequences)

### Winning Strategies

**Early Game (Turns 1-4):**
- Focus on fundraising to build a money buffer
- Hire your first safety researcher to start doom mitigation
- Buy accounting software if available for better tracking

**Mid Game (Turns 5-9):**
- Invest in safety research projects to build reputation
- Expand team to 3-4 staff for more action capacity
- Get key upgrades like computer systems for productivity bonuses

**Late Game (Turns 10-13):**
- Execute multiple research projects for maximum reputation
- Enhanced safety researchers give better doom control
- Monitor opponent progress and react strategically


**Core Principles:**
- Staff loss now configurable - check settings for your challenge level
- With 80% reduced doom progression, you have time for strategic planning
- Safety researchers are 40% more effective - invest in your team
- Extended gameplay allows 2-3 research projects per game for higher scores



---

## Game Over Conditions

You lose if any of these happen:
- **[EMOJI][EMOJI] p(Doom) reaches 100%** - Catastrophic AI development
- **[EMOJI] All staff quit** - No one left to run the lab
- **[EMOJI] Opponent wins** - Competition reaches 100% progress first

Instead of generic 'GAME OVER' messages, you'll receive detailed end game scenarios that explain what led to your defeat and analyze your organization's performance based on how long you survived and what caused the end.

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
- **[EMOJI] Relaunch Game**: Restart with the same seed for another attempt
- **[EMOJI] Main Menu**: Return to the main menu to select new game options
- **[GEAR][EMOJI] Settings**: View game settings and configuration information
- **[SPEECH] Submit Feedback**: Share suggestions and feedback about the game
- **[EMOJI] Submit Bug Request**: Report bugs or technical issues

### Navigation
- **Mouse**: Click any option to select it
- **Keyboard**: Use arrow keys to navigate, Enter to select, Escape for Main Menu
- **Features**: Same bug reporting system as main menu, preserves game statistics

This replaces the old 'click anywhere to restart' behavior, giving you more control over what to do after a game ends.

---

## Need Help?

- **Stuck?** Try the in-game 'Report Bug' feature to get help
- **Technical issues?** See the [README](../README.md) for troubleshooting
- **Want to contribute?** Check the [Developer Guide](DEVELOPERGUIDE.md)
- **Version questions?** See [CHANGELOG.md](../CHANGELOG.md) for release history and known issues

---

**Remember: It's supposed to be hard! You're fighting an uphill battle against reckless AI development. Every turn you survive is a victory. [TARGET]**
