# Missing Core Features from Pygame Version

## Overview
Track parity between Godot and pygame versions, plus new feature ideas that would enhance gameplay.

## Admin Mode Features
The `]` keybind is configured for admin mode, but functionality is not yet implemented.

### Proposed Admin Features
- [ ] **Skip to Turn N** - Jump to specific turn for testing
- [ ] **Set Resource Values** - Directly edit money/compute/research
- [ ] **Trigger Specific Events** - Force events to fire for testing
- [ ] **Toggle God Mode** - Prevent game over conditions
- [ ] **Save State Management** - Save/load arbitrary game states
- [ ] **Event Browser** - View and trigger all events on demand
- [ ] **Researcher Editor** - Add/edit/remove researchers with custom stats

### Implementation Notes
```gdscript
# Hook is already in KeybindManager
KeybindManager.admin_mode_toggled.connect(_on_admin_mode_activated)

# Could create admin_panel.tscn with all debug tools
# Similar to debug_overlay but more powerful
```

## Additional Events & Random Encounters

### Missing pygame Events
- [ ] Audit pygame events vs Godot events
- [ ] Port missing events
- [ ] Add event probability tuning

### New Event Ideas
- [ ] **Rival Lab Poaching** - Attempt to steal your researchers
- [ ] **Funding Crisis** - Emergency money decisions
- [ ] **Breakthrough Discovery** - Random research spike
- [ ] **Conference Opportunities** - Trade money for reputation boost
- [ ] **Equipment Failure** - Compute goes down temporarily
- [ ] **Whistleblower** - Moral/ethical dilemmas
- [ ] **Media Attention** - Double-edged publicity
- [ ] **Government Inquiry** - Reputation/funding investigation

## Researcher Visuals

### Current State
- Researchers are data-only (no visuals)
- Names and stats displayed in text

### Proposed Features
- [ ] **Researcher Portraits** - 256x256 character art
  - Generic portraits by specialization (safety, capabilities, interpretability, alignment)
  - Could use AI-generated art as placeholders
  - Asset path: `godot/assets/images/characters/researcher_*.png`

- [ ] **Researcher Panel** - Dedicated UI for managing team
  - Grid or list view
  - Click to see details (traits, productivity, burnout)
  - Visual burnout/loyalty indicators
  - Hire/fire actions

- [ ] **Trait Icons** - Small icons for researcher traits
  - "Workaholic", "Brilliant", "Pessimist", etc.
  - Asset path: `godot/assets/icons/traits/*.png`

### Implementation Plan
```gdscript
# Add to ThemeManager assets
"researcher_safety": "res://assets/images/characters/researcher_safety.png",
"researcher_capabilities": "res://assets/images/characters/researcher_capabilities.png",

# Create researcher_panel.tscn
# Display researchers in a grid with portraits + stats
```

## Doom Meter Visualization

### Current State
- Doom shows as text percentage
- Color changes based on threshold (via ThemeManager)

### Proposed Enhancements
- [ ] **Visual Doom Meter** - Progress bar or gauge
  - Fill color changes (green → yellow → orange → red)
  - Optional: Animated pulsing at high doom
  - Could use a circular gauge (Doomsday Clock aesthetic)

- [ ] **Doom History Graph** - Track doom over time
  - Line chart showing doom % per turn
  - Helps players understand their trajectory
  - Could overlay events on graph

- [ ] **Momentum Indicators** - Show doom delta per turn
  - "+2.5% this turn" in red/green
  - Arrow indicators (↑ ↓)

### Asset Needs
```
godot/assets/icons/doom_meter_fill.png
godot/assets/icons/doom_meter_bg.png
godot/assets/icons/arrow_up.png
godot/assets/icons/arrow_down.png
```

## Cat Features Expansion
Our "only drawcard" deserves more love!

- [ ] **Cat Moods** - Visual states based on doom
  - Happy cat (low doom)
  - Nervous cat (medium doom)
  - Panicking cat (high doom)
  - Multiple sprites or sprite sheet

- [ ] **Cat Interactions** - Click the cat for bonus
  - Pet the cat for +1 morale (once per turn)
  - Cat brings you a "gift" (random small bonus)
  - Cat walks across keyboard (humorous message log entry)

- [ ] **Custom Cat Photos** - User-uploaded cat images
  - "Far future state" - mentioned in previous session
  - Upload photo → convert to pixel art or apply filter
  - Store in `user://custom_cats/`
  - "Doominess conversion" algorithm (brightness/contrast to doom correlation?)

### Asset Needs
```
godot/assets/images/misc/cat_happy.png
godot/assets/images/misc/cat_nervous.png
godot/assets/images/misc/cat_panic.png
```

## Miscellaneous Quality-of-Life

- [ ] **Tutorial Mode** - First-time player guidance
- [ ] **Tooltips** - Hover info for all UI elements
- [ ] **Action Preview** - "This will cost X, give Y" before confirming
- [ ] **Undo Last Action** - Optional easy mode feature
- [ ] **Action Queue** - Plan multiple actions, execute on End Turn
- [ ] **Researcher Specialization Tooltips** - Explain what each type does
- [ ] **Event History** - Review past events and choices made
- [ ] **Achievements** - Steam-ready achievement system
- [ ] **Daily Challenge Seeds** - Predetermined seed of the day

## Testing Infrastructure Needs
While implementing these features:
- Unit tests for new event triggers
- Integration tests for admin mode
- Visual regression tests for UI changes
- Performance tests for doom meter animations

## Priority Ranking
1. **High**: Admin mode (testing enabler), Doom meter visualization
2. **Medium**: Researcher visuals, Additional events
3. **Low**: Cat expansion, QoL features
4. **Future**: Custom cat photos, Achievements

## Related Issues
- #365 - Cat event (completed)
- #291 - Leaderboard (completed)
- [Add new issues as created]

## Labels
`enhancement`, `feature`, `backlog`, `ui`, `gameplay`
