# P(Doom) UI Layout Guide
**Version**: v0.10.3+
**Last Updated**: November 17, 2025
**Purpose**: Visual reference for UI layout and design decisions

## Table of Contents
1. [Overview](#overview)
2. [Screen Layout](#screen-layout)
3. [Component Details](#component-details)
4. [Adaptive Layouts](#adaptive-layouts)
5. [Design Philosophy](#design-philosophy)
6. [Contributing](#contributing)

---

## Overview

P(Doom) uses a clean, information-dense UI inspired by StarCraft 2 and X-COM. The layout prioritizes:
- **Clarity**: Important information is always visible
- **Breathing Room**: Negative space prevents visual clutter
- **Consistency**: Similar elements are grouped logically
- **Feedback**: Hover states and color coding provide instant context

---

## Screen Layout

### Main Game Screen (Default State - No Office Cat)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TOP BAR                                                                      │
│ P(Doom) | Turn: 9 | Money: $194,500 | Compute: 250.0 | Research: 0.0 |      │
│ Papers: 0 | Rep: 60 | Doom: 62.1% | AP: 3    [Employees (E)]                 │
├──────────────┬─────────────────────────────────┬────────────────────────────┤
│              │                                 │                            │
│  ACTIONS     │         DOOM METER              │  UPGRADES                  │
│  (Left 22%)  │        (Middle 28%)             │  (Right 50%)               │
│              │                                 │                            │
│  [1] Hire    │    ┌─────────────────────┐     │  Upgrade Computer System   │
│  [2] Purchase│    │   DOOM METER        │     │  Buy Comfy Office Chairs   │
│  [3] Safety  │    │  ┌───────────────┐  │     │  Secure Cloud Provider     │
│  [4] Capability   │  │   ##########  │  │     │  Adopt Office Cat          │
│  [5] Publish │    │  │   ##########  │  │     │                            │
│  [6] Safety  │    │  │   ##########  │  │     │  ACTION QUEUE:             │
│  [7] Write   │    │  │     62.1%     │  │     │  ┌──────┐ ┌──────┐        │
│  [8] Fundraise    │  │               │  │     │  │Reserve│ │      │        │
│  [9] Networking   │  └───────────────┘  │     │  │All AP │ │Remove│        │
│  Team Building    │                     │     │  └──────┘ └──────┘        │
│  ...         │    └─────────────────────┘     │                            │
│              │                                 │  ────────────────────────   │
│              │                                 │  MESSAGE LOG:              │
│              │                                 │  [17.15] Turn Phase: ...   │
│              │                                 │  [17.15] Turn 9 started    │
│              │                                 │  [17.15] Action Points...  │
│              │                                 │  [17.15] 2 event(s)...     │
│              │                                 │  [19.05] EVENT: Talent...  │
└──────────────┴─────────────────────────────────┴────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────────┐
│ INFO BAR (60px height, 2 lines permanent)                                   │
│ [b][cyan]Hire Staff[/cyan][/b] — Hire a new researcher to expand your team  │
│ [gray]├─[/gray] [yellow]Costs:[/yellow] [gold]$25,000[/gold] • [magenta]1AP │
│ [gray]└─[/gray] [lime]✓ READY TO USE[/lime]                                 │
└─────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────────┐
│ BOTTOM BAR                                                                   │
│ [Init Game] [Hire Safety] [Reserve 1AP] [Clear Queue(C)]                    │
│ [Commit Actions(Space)] [Commit Plan(Enter)]                                │
│                                              Phase: action_selection         │
│                                                     [Bug Report (N)]         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### After Office Cat Adoption

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TOP BAR                                                                      │
│ P(Doom) | Turn: 9 | ... | Doom: 62.1% | AP: 3   [🐱] [Employees (E)]       │
│                                                    ^                         │
│                                              Small cat icon                  │
├──────────────┬─────────────────────────────────┬────────────────────────────┤
│              │                                 │                            │
│  ACTIONS     │      OFFICE CAT 🐱              │  UPGRADES                  │
│  (Left 22%)  │     (Middle 28%)                │  (Right 50%)               │
│              │                                 │                            │
│  [1] Hire    │    ┌─────────────────────┐     │  ...same as before...      │
│  [2] Purchase│    │                     │     │                            │
│  [3] Safety  │    │    ┌─────────┐      │     │                            │
│  [4] Capability   │    │  /\_/\  │      │     │                            │
│  [5] Publish │    │    │ ( o.o ) │      │     │                            │
│  [6] Safety  │    │    │  > ^ <  │      │     │                            │
│  [7] Write   │    │    │ /|   |\  │      │     │                            │
│  [8] Fundraise    │    │/_|   |_\ │      │     │                            │
│  [9] Networking   │    └─────────┘      │     │                            │
│  ...         │    │   [Cat sprite]      │     │                            │
│              │    │  (doom-reactive)    │     │                            │
│              │    └─────────────────────┘     │                            │
│              │                                 │                            │
│              │    Doom meter is HIDDEN         │                            │
└──────────────┴─────────────────────────────────┴────────────────────────────┘
```

---

## Component Details

### 1. Top Bar (40px height)
**Purpose**: Display core game state at a glance

**Components**:
- Game title: `P(Doom)` (18px font)
- Resource stats: Turn, Money, Compute, Research, Papers, Rep, Doom, AP (14px font)
- Separators: `|` (gray, 40% opacity)
- Employee button: `[Employees (E)]` (100px width)
- Cat panel: Hidden by default, 40x40px when cat adopted

**Spacing**: 10px between elements

**Color Coding**:
- Default: White text
- Doom: Color shifts from green → yellow → red based on level

### 2. Left Panel - Actions (22% width)
**Purpose**: Primary player interaction - select actions to queue

**Components**:
- Label: "Actions:" (default font)
- Scrollable list of action buttons
- Keyboard shortcuts: [1-9] for first 9 actions

**Button Format**:
```
[#] Action Name (Costs)
Example: [1] Hire Staff ($25,000, 1 AP)
```

**Color Coding** (by category):
- Hiring: Teal tint
- Resources: Purple tint
- Research: Cyan tint
- Management: Orange tint
- Influence: Yellow tint
- Strategic: Red tint
- Funding: Green tint
- Other: Gray

**Affordability**:
- Affordable: Full color, clickable
- Unaffordable: 60% gray, disabled

### 3. Middle Panel - Doom Meter / Office Cat (28% width)
**Purpose**: Visual feedback for primary game state (doom level)

#### Default State (No Cat):
- **Label**: "DOOM METER" (14px, orange #FF9900)
- **Container**: 200x200px panel, centered
- **Visual**: Circular meter showing doom percentage
- **Color**: Green → Yellow → Orange → Red (based on doom)
- **Animation**: Pulsing effect as doom increases

#### After Cat Adoption:
- Doom meter: **HIDDEN**
- Office cat sprite: **VISIBLE** (200x200px, centered)
- Cat behavior: Reacts to doom level changes
  - Low doom (<30%): Happy, content
  - Medium doom (30-70%): Concerned
  - High doom (>70%): Alarmed, stressed

### 4. Right Panel - Upgrades, Queue, Log (50% width)
**Purpose**: Strategic planning and information display

**Subdivisions**:
1. **Upgrades** (45% of right panel height)
   - Scrollable list of one-time purchases
   - Format: `Upgrade Name ($cost)`
   - Purchased upgrades: `✓ Upgrade Name` (green tint, disabled)

2. **Action Queue** (80px height)
   - Shows currently queued actions
   - Each item displays: Name, AP cost, Remove button
   - Empty state: "No actions queued..." (gray text)

3. **Message Log** (35% of right panel height)
   - Scrollable history of game events
   - Timestamped entries
   - Color-coded by event type:
     - System: Gray
     - Success: Lime
     - Warning: Yellow
     - Error: Red
     - Event: Gold
     - Phase: Magenta

### 5. Info Bar (60px height, FIXED 2-line format)
**Purpose**: Context-sensitive action details on hover

**Format** (always 2 lines to prevent UI flicker):
```
Line 1: [b][cyan]Action Name[/cyan][/b] — Description
Line 2: [gray]├─[/gray] [yellow]Costs:[/yellow] [details] • [details]
Line 3: [gray]└─[/gray] [lime/red]Affordability status[/lime/red]
```

**Default State** (no hover):
```
Line 1: Hover over actions to see details...
Line 2: [empty line with space character]
```

**Design Note**: Fixed 2-line height prevents visual jarring when hovering/unhovering.

### 6. Bottom Bar (variable height, ~40px)
**Purpose**: Game flow controls and phase indication

**Left Section** (75% width):
- Control buttons (compressed, 5px spacing):
  - `Init Game` - Start new game
  - `Hire Safety Researcher` - Test action
  - `Reserve 1 AP` - Reserve AP for events
  - `Clear Queue (C)` - Clear all queued actions
  - `Commit Actions (Space)` - Execute with warnings
  - `Commit Plan (Enter)` - Execute without warnings

**Middle Section**:
- Phase label: Shows current turn phase
  - `Phase: TURN_START (Processing...)` - Red
  - `Phase: ACTION_SELECTION (Ready)` - Green
  - `Phase: TURN_END (Executing...)` - Yellow

**Right Section** (110px):
- `Bug Report (N)` button (12px font)

---

## Adaptive Layouts

### Responsive Width Ratios
The UI uses proportional sizing for adaptability:
- Left Panel: 22% (Actions)
- Middle Panel: 28% (Doom Meter / Cat)
- Right Panel: 50% (Upgrades + Queue + Log)

**Design Philosophy**: Ratios ensure consistency across different window sizes.

### State-Based Visibility

| Component | Default (No Cat) | After Cat Adoption |
|-----------|------------------|-------------------|
| Doom Meter (Middle) | ✅ Visible | ❌ Hidden |
| Office Cat (Middle) | ❌ Hidden | ✅ Visible |
| Cat Icon (Top Bar) | ❌ Hidden | ✅ Visible |

---

## Design Philosophy

### StarCraft 2 Inspiration
- **Information Density**: All critical info visible without scrolling
- **Visual Hierarchy**: Size and color guide player attention
- **Consistent Theming**: Similar elements use similar styling

### X-COM Inspiration
- **Strategic Planning**: Queue actions before committing
- **Risk Communication**: Color-coded warnings (doom, affordability)
- **Tactical Feedback**: Detailed hover states

### P(Doom) Specific
- **Doom as Central Mechanic**: Doom meter gets visual prominence
- **Tonal Balance**: Serious themes with light touches (office cat)
- **Progressive Disclosure**: Complexity revealed gradually

---

## Keyboard Shortcuts

### Global
- `1-9`: Select action by index
- `C`: Clear action queue
- `Space`: Commit actions (with warnings)
- `Enter`: Commit plan (no warnings)
- `E`: Employee screen
- `N` or `\`: Bug reporter

### Dialogs
- `Q, W, E, R, A, S, D, F, Z`: Select dialog option (up to 9)
- `ESC`: Close submenu (NOT events)

---

## Contributing

### Proposing UI Changes

When suggesting UI modifications, please provide:

1. **Visual Mockup**: Sketch or screenshot showing proposed change
2. **Rationale**: Why does this improve player experience?
3. **Impact Assessment**:
   - Which components are affected?
   - Does it maintain visual hierarchy?
   - Does it respect negative space?
4. **Accessibility Considerations**:
   - Color contrast
   - Font sizes
   - Keyboard navigation

### UI Change Checklist

- [ ] Maintains 22%/28%/50% width ratio?
- [ ] Preserves 2-line InfoBar height?
- [ ] Respects color-coding conventions?
- [ ] Keyboard shortcuts still work?
- [ ] Tested with/without office cat?
- [ ] No visual flicker or jarring transitions?

---

## Technical Details

### Scene Hierarchy (Godot)
```
Main
└── TabManager
    ├── MainUI (VBoxContainer)
    │   ├── TopBar (HBoxContainer)
    │   ├── ContentArea (HBoxContainer)
    │   │   ├── LeftPanel (VBoxContainer) - Actions
    │   │   ├── MiddlePanel (VBoxContainer) - Doom/Cat
    │   │   └── RightPanel (VBoxContainer) - Upgrades/Queue/Log
    │   ├── InfoBar (PanelContainer)
    │   └── BottomBar (HBoxContainer)
    ├── EmployeeScreen
    ├── GameOverScreen
    └── BugReportPanel
```

### Key Files
- Layout: `godot/scenes/main.tscn`
- Logic: `godot/scripts/ui/main_ui.gd`
- Theme: `godot/scripts/core/theme_manager.gd`
- Colors: `godot/scripts/core/game_config.gd`

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-17 | v0.10.3+ | Major UI reorganization - doom meter to center, spacing compression, office cat swap logic |
| 2024-10-31 | v0.9.0 | Office cat implementation |
| 2024-10-20 | v0.8.0 | Initial UI framework |

---

**Document Maintained By**: Development Team
**Last Reviewed**: 2025-11-17
**Status**: Active - reflects current v0.10.3+ implementation
