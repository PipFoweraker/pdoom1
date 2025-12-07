# P(Doom) UI Design Vision

**Date Created**: 2025-10-17
**Status**: Planning / Early Implementation

---

## Design Philosophy

### Core Principles
1. **Function Over Form** - Working buttons and clear feedback trump polish
2. **Ugly is OK** - Deliberately minimal UI during development
3. **UI as Gameplay** - The interface itself upgrades through game progression
4. **Modular Screens** - Swappable views like Civilization IV

### Future Vision
- **Strategic Overview** - X-COM or StarCraft 2 style command center
- **Screen Switching** - Different views for different game aspects
- **Progressive Enhancement** - UI unlocks and upgrades as player progresses
- **Submenu Integration** - Categories expand visually into the interface

---

## Architecture

### Screen Manager System
The UI is built around a **ScreenManager** that can swap between different views:

```
ScreenManager (root)
|-- MainGameScreen (default)
|-- ResearchScreen (future)
|-- EmployeeScreen (future)
|-- SettingsScreen (future)
`-- etc.
```

**Benefits**:
- Easy to add new screens without refactoring
- Clean separation of concerns
- Natural fit for UI upgrades as gameplay mechanics

### Phase 4 MVP (Current)
**Goal**: Prove the Python bridge works with minimal UI

**Components**:
- GameManager singleton (handles Python bridge)
- Simple control panel with test buttons
- Raw text resource display
- Message log for feedback
- No styling, no graphics, pure function

**Test Flow**:
```
1. Click "Init Game"  ->  See resources update
2. Click "Hire Safety Researcher"  ->  See message
3. Click "End Turn"  ->  See turn increment
```

---

## Progressive Enhancement Roadmap

### Phase 5: Basic Screens (1-2 weeks)
- Action selection screen (categorized lists)
- Event popup system
- Turn phase indicator
- Basic resource displays with icons

### Phase 6: Screen System (2-4 weeks)
- Multiple swappable screens
- Navigation menu
- Screen transitions
- Keyboard shortcuts for screen switching

### Phase 7: UI as Gameplay (Future)
- **UI Upgrades as Actions**
  - "Hire UI Designer"  ->  Unlocks better visuals
  - "Install Dashboard Software"  ->  Unlocks new screen
  - "Upgrade Analytics"  ->  Shows more detailed stats

- **Progressive Information Disclosure**
  - Early game: Simple lists, basic info
  - Mid game: Graphs, trends, predictions
  - Late game: Full strategic overview, AI analysis

### Phase 8: Polish (Future)
- X-COM style command center aesthetic
- Animated transitions
- Sound effects and feedback
- Visual themes (can change through gameplay)

---

## Technical Notes

### Godot Scene Structure
```
Main.tscn
|-- GameManager (AutoLoad singleton)
|-- ScreenManager (Control)
|  |-- CurrentScreen (Container)
|  `-- ScreenCache (stores inactive screens)
|-- PersistentUI (Control - always visible)
|  |-- ResourceDisplay
|  |-- TurnCounter
|  `-- MessageLog
`-- DebugOverlay (optional, for development)
```

### Screen Interface
All screens implement a common interface:
```gdscript
func _on_screen_enter():
    # Called when screen becomes active

func _on_screen_exit():
    # Called when switching away

func update_state(game_state: Dictionary):
    # React to game state changes
```

---

## Inspiration & References

### UI Evolution Examples
- **Civilization IV** - Multiple screens (city view, diplomacy, tech tree)
- **X-COM** - Strategic layer vs. tactical layer
- **StarCraft 2** - Command center with different tabs
- **FTL** - Simple but clear information hierarchy

### UI as Gameplay Examples
- **Papers Please** - Interface IS the game
- **Hacknet** - Terminal aesthetic unlocks features
- **Uplink** - Upgrading your interface is core progression

---

## Current Status (Phase 4)

### Completed
- [x] GameManager with Python bridge communication
- [x] Command sending via PowerShell + pipe
- [x] Signal-based architecture for state updates

### In Progress
- [ ] main.tscn with minimal test UI
- [ ] Basic button layout (init, action, end turn)
- [ ] Resource display (text labels)
- [ ] Message log area

### Next Steps
1. Create minimal main.tscn scene
2. Test Python bridge end-to-end
3. Verify turn flow works in UI
4. Document any issues or improvements needed

---

## Development Guidelines

### When Adding UI Features
1. **Function first** - Does it work?
2. **Signals over polling** - Use Godot's signal system
3. **Screen context** - Which screen does this belong to?
4. **Future-proof** - Will this work when UI upgrades are gameplay?

### Avoid Premature Polish
- ERROR Don't spend time on graphics/styling yet
- ERROR Don't worry about animations or transitions
- ERROR Don't implement features that aren't testable yet
- SUCCESS DO focus on working buttons and clear feedback
- SUCCESS DO use placeholder text/colors
- SUCCESS DO document what needs polish later

### When to Polish
Polish happens when:
1. Core gameplay loop is complete and tested
2. All major features are implemented
3. Game is actually playable end-to-end
4. We're ready to add "UI upgrades" as gameplay

---

## Notes & Ideas

### Potential UI Upgrade Mechanics
- **Basic Terminal** (Start)  ->  **Dashboard** (Mid)  ->  **AI Command Center** (Late)
- Unlock graphs, charts, predictions as you hire analysts
- "Dark mode" could be an actual upgrade
- More screen space = more employees to manage visibility

### Accessibility Considerations (Future)
- Keyboard-only navigation
- Screen reader support (Godot has built-in accessibility)
- Colorblind-friendly indicators
- Text scaling options

### Performance Considerations
- Screen caching to avoid recreating UI
- Lazy loading for complex screens
- Efficient state updates (only changed elements)

---

**Last Updated**: 2025-10-17
**Related Docs**:
- [SESSION_HANDOFF_2025-10-16_GODOT_MIGRATION_START.md](SESSION_HANDOFF_2025-10-16_GODOT_MIGRATION_START.md)
- `shared_bridge/turn_architecture.py` (Turn system design)
