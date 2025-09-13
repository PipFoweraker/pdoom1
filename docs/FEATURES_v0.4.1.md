# P(Doom) v0.4.1 Features Reference

## Core Game Systems

### Resource Management
- **Money**: Start with $100k, weekly staff costs $600-800
- **Staff**: Hire researchers, managers, administrators
- **Reputation**: Affects fundraising success and public relations
- **Doom**: Existential risk level (0-100%), game ends at 100%
- **Action Points**: 3 per turn + staff bonuses, limit actions per turn
- **Compute**: Research infrastructure for advanced projects

### Turn-Based Gameplay
- **Turn Structure**: Select actions → End turn → Process events → Repeat
- **Action System**: Each action costs action points and/or money
- **Event System**: Random events each turn affect resources and strategy
- **Opponent AI**: 3 competing labs with hidden progress and strategies

### Economic Model (Bootstrap v0.4.1)
- **Realistic Costs**: Based on actual AI safety researcher salaries
- **Weekly Expenses**: Staff maintenance costs every turn
- **Fundraising**: 4 different funding approaches with risk/reward
- **Moore's Law**: Compute costs decrease 2% per week
- **No Signing Bonuses**: Budget-conscious hiring (startup reality)

## User Interface Features

### Main Game Screen
- **Resource Dashboard**: Live tracking of money, staff, doom, reputation
- **Action Menu**: Categorized actions (Research, Operations, Strategy)
- **Message Log**: Detailed feedback on all actions and events
- **Opponent Intelligence**: Discovered information about competing labs
- **Turn Counter**: Track game progression

### Enhanced Leaderboard System (v0.4.1)
- **Seed-Specific Competition**: Separate leaderboards for each game seed
- **Dual Identity Support**: Player name + lab name for flexibility
- **Rank Visualization**: Gold/silver/bronze coloring for top performers
- **Session Metadata**: Track money, staff, doom, reputation, duration
- **Persistent Storage**: JSON files preserve progress between sessions

### Spectacular Game Over Screen (v0.4.1)
- **Achievement Celebration**: "NEW HIGH SCORE!" with visual effects
- **Mini Leaderboard Preview**: Show top 5 players with highlighting
- **Detailed Statistics**: Final resources, game duration, economic model
- **Natural Flow**: "View Full Leaderboard" prominently displayed
- **Context-Aware Actions**: "Play Again" vs "Launch New Game" buttons

### Audio System (Party-Ready)
- **Sound Effects Enabled**: Audio feedback on by default
- **Action Sounds**: Action point spending, money transactions
- **UI Feedback**: Popup open/close, button confirmation sounds
- **Employee Hiring**: Distinctive "blob" sound for team growth
- **Error Feedback**: Audio cues for invalid actions

## Gameplay Mechanics

### Research System
- **Safety Research**: Reduces doom, slower capability progress
- **Capability Research**: Faster progress, increases doom risk
- **Technical Quality**: Choose between fast/risky vs slow/careful approaches
- **Research Projects**: Multi-turn investments with varying outcomes
- **Technical Debt**: Poor quality research creates future problems

### Staff Management
- **Employee Types**: Researchers, administrators, managers, board members
- **Productive Actions**: Assign staff to ongoing research tasks
- **Hiring Costs**: Realistic salary-based expenses
- **Staff Efficiency**: More staff = more action points per turn

### Strategic Elements
- **Opponent Espionage**: Spend resources to learn about competitors
- **Public Relations**: Manage reputation through media engagement
- **Milestone System**: Unlock new mechanics as lab grows
- **Event Responses**: Handle crises, opportunities, technical failures

### Risk Management
- **Technical Debt Tracking**: Monitor code quality and system reliability
- **Failure Cascades**: Poor technical practices can cause major setbacks
- **Cover-up vs Transparency**: Choose how to handle failures
- **Prevention Systems**: Invest in monitoring and incident response

## Configuration and Settings

### Game Configuration
- **Custom Seeds**: Reproducible games for competitive play
- **Economic Models**: Different starting conditions and cost structures
- **Difficulty Settings**: Adjust event frequency and resource constraints
- **Advanced Settings**: Debug mode, verbose logging, safety levels

### Audio Settings
- **Master Sound Toggle**: Enable/disable all audio
- **Individual Sound Control**: Toggle specific sound effects
- **Volume Control**: Adjust audio levels (when hardware available)

### Privacy Settings
- **Local-First Design**: All data stays on your device
- **Pseudonymous Play**: Compete without revealing personal information
- **Optional Analytics**: Detailed logging is opt-in only
- **Data Control**: Full control over what information is stored

## Technical Implementation

### Save System
- **JSON Storage**: Human-readable configuration and save files
- **Atomic Writes**: Prevent data corruption during save operations
- **Schema Versioning**: Backward compatibility for config updates
- **Configuration Hashing**: Prevent leaderboard conflicts between settings

### Development Tools
- **Comprehensive Testing**: 507+ unit tests covering all systems
- **Type Annotations**: Strong typing for code reliability
- **ASCII Compliance**: Cross-platform compatibility
- **Modular Architecture**: Clear separation between game logic and UI

### Platform Support
- **Python 3.9+**: Modern Python with typing support
- **pygame GUI**: Cross-platform graphics and input
- **Windows/Mac/Linux**: Full cross-platform compatibility
- **Headless Testing**: Automated testing without display requirements

## Competitive Features

### Deterministic Gameplay
- **Seeded Random**: Same seed produces identical game sequence
- **Fair Competition**: Reproducible outcomes for verification
- **Strategy Comparison**: Test different approaches on same scenario

### Leaderboard Competition
- **Seed Isolation**: Each seed has separate competitive ranking
- **Privacy Preservation**: Compete without sharing personal data
- **Progress Tracking**: See improvement across multiple games
- **Achievement Recognition**: Visual celebration for high scores

This feature set represents a complete, polished game ready for party demonstrations and competitive play.
