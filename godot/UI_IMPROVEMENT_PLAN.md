# UI Improvement Plan
_Based on feedback session 2025-10-31_

---

## 🎯 Priority Matrix

### P0 - Critical (Do Now - 2 hours)
1. **Top Bar Layout Redesign** - Reduce clutter, single-line resources
2. **Button Styling** - Apply style guide (smaller, colored, themed)
3. **Submenu Keyboard Shortcuts** - Add 1-4 keys to dialogs

### P1 - High (Next Session - 3 hours)
4. **Employee Personality System** - Port from Python (names, traits, specializations)
5. **Background Images** - Title screen, end screen backgrounds
6. **Enhanced Hiring Dialog** - Multi-tier specialist selection

### P2 - Medium (Future - 4+ hours)
7. **Advanced Layout Options** - Resizable panels, customizable layouts
8. **Animation Polish** - Button hovers, transitions
9. **Sound Effects** - Button clicks, notifications

---

## 📋 Detailed Implementation Plans

### 1. Top Bar Layout Redesign (P0 - 45 min)

**Current Problem:**
- TopBar has title + doom meter + cat = cluttered
- ResourceDisplay is separate row (wastes vertical space)
- Doom meter takes 120x120px in premium real estate

**Proposed Solution:**
```
┌──────────────────────────────────────────────────────────────────────┐
│ P(Doom) | Turn: 5 | Money: $100k | Compute: 50 | Research: 75 |     │
│         | Papers: 3 | Rep: 80 | Doom: 45% ↑2.3 | AP: 3 ●●●○ | 🐱    │
└──────────────────────────────────────────────────────────────────────┘
```

**Implementation:**
1. Merge TopBar + ResourceDisplay into single HBoxContainer
2. Move doom meter to **bottom-right corner** as circular widget (persistent)
3. Show compact doom in top bar: `Doom: 45% ↑2.3` (text + momentum)
4. Cat stays top-right as small icon
5. Use `|` separators for visual grouping

**Files to modify:**
- `scenes/main.tscn` - Restructure TopBar/ResourceDisplay
- `scripts/ui/main_ui.gd` - Update label references

**Benefits:**
- Saves ~100px vertical space
- Cleaner visual hierarchy
- Doom meter still visible but not intrusive

---

### 2. Button Styling (P0 - 45 min)

**Current Problem:**
- Buttons too large and grey
- No visual personality
- Not using style guide colors

**Style Guide Colors (from UI_STYLE_GUIDE.md):**
```gdscript
# Primary colors
STEEL_DARK = Color(0.110, 0.153, 0.188)      # Backgrounds
ELECTRIC_BLUE = Color(0.204, 0.596, 0.859)   # Accents
NEON_MAGENTA = Color(0.929, 0.263, 0.792)    # Highlights
TERMINAL_GREEN = Color(0.196, 0.804, 0.196)  # Success
WARNING_AMBER = Color(0.961, 0.682, 0.251)   # Warnings
```

**Proposed Button Styles:**

```gdscript
# Action Buttons (smaller, themed)
- Normal: STEEL_DARK bg, ELECTRIC_BLUE border (2px)
- Hover: ELECTRIC_BLUE glow (4px), slight scale (1.05x)
- Disabled: 50% opacity, grey

# Cost displays
- AP cost: NEON_MAGENTA
- Money cost: WARNING_AMBER (gold)
- Affordable: TERMINAL_GREEN border
- Unaffordable: RED border, 70% opacity

# Keyboard hints
- [1] prefix: ELECTRIC_BLUE, bold
```

**Implementation:**
1. Update `ThemeManager.create_button()` with new default style
2. Add affordability color-coding
3. Reduce button height from ~40px to ~32px
4. Add subtle hover animations

**Files:**
- `autoload/theme_manager.gd` - Update button style
- `scripts/ui/main_ui.gd` - Apply affordability colors

---

### 3. Submenu Keyboard Shortcuts (P0 - 30 min)

**Current Problem:**
- Hire Staff submenu requires mouse clicks
- Fundraising submenu requires mouse clicks
- Event dialogs require mouse clicks

**Proposed Solution:**
Add 1-4 number keys to all submenu dialogs:

```
┌─────────────────────────────────────────┐
│         Hire Staff                      │
├─────────────────────────────────────────┤
│ [1] Safety Researcher ($60k, 2 AP)      │
│ [2] Capability Researcher ($60k, 2 AP)  │
│ [3] Compute Engineer ($50k, 2 AP)       │
│ [4] Cancel                              │
└─────────────────────────────────────────┘
```

**Implementation:**
1. Add `_input()` handler to submenu dialog creation
2. Map KEY_1-KEY_4 to button presses
3. Add keyboard hint labels to button text
4. Apply to:
   - Hiring submenu (`_show_hiring_submenu()`)
   - Fundraising submenu (`_show_fundraising_submenu()`)
   - Event dialogs (`_show_event_dialog()`)

**Files:**
- `scripts/ui/main_ui.gd` - Add input handlers to dialog creation

**Benefits:**
- Faster gameplay for power users
- Consistent with main action keyboard shortcuts
- Better accessibility

---

### 4. Employee Personality System (P1 - 2 hours)

**Source Material (Python):**
- `src/core/researchers.py` - Full Researcher class
- `src/core/employee_subtypes.py` - Specialization system

**Features to Port:**

**4a. Individual Names**
```gdscript
# From Python: 32 first names, 32 last names = 1024 combinations
const FIRST_NAMES = ["Alex", "Jordan", "Casey", ...]
const LAST_NAMES = ["Chen", "Patel", "Garcia", ...]

func generate_researcher_name() -> String:
    return "%s %s" % [FIRST_NAMES.pick_random(), LAST_NAMES.pick_random()]
```

**4b. Specializations**
```gdscript
enum Specialization { SAFETY, CAPABILITY, COMPUTE_ENGINEERING }

const SPEC_EFFECTS = {
    SAFETY: {
        "doom_reduction_bonus": 0.15,
        "color": Color.GREEN
    },
    CAPABILITY: {
        "research_speed_modifier": 1.25,
        "doom_per_research": 0.05,
        "color": Color.RED
    },
    COMPUTE_ENGINEERING: {
        "compute_bonus": 10,
        "color": Color.BLUE
    }
}
```

**4c. Traits (Positive + Negative)**
```gdscript
const POSITIVE_TRAITS = {
    "workaholic": {
        "name": "Workaholic",
        "productivity_bonus": 0.20,
        "burnout_increase": 2
    },
    "team_player": {
        "name": "Team Player",
        "team_productivity_bonus": 0.10
    },
    "media_savvy": {
        "name": "Media Savvy",
        "reputation_bonus": 1
    }
}

const NEGATIVE_TRAITS = {
    "prima_donna": {
        "name": "Prima Donna",
        "team_productivity_penalty": 0.10
    },
    "leak_prone": {
        "name": "Leak Prone",
        "leak_chance": 0.05
    }
}
```

**4d. Researcher Class**
```gdscript
class Researcher:
    var id: String
    var name: String
    var specialization: int
    var skill_level: int  # 3-8
    var traits: Array[String]
    var salary_expectation: int
    var productivity: float
    var loyalty: int  # 0-100
    var burnout: int  # 0-100
    var turns_employed: int
```

**Implementation Plan:**
1. Create `godot/scripts/core/researcher_system.gd`
2. Port Python Researcher class to GDScript
3. Add to GameState: `var researchers: Array[Researcher] = []`
4. Update hiring dialog to show individual researchers with traits
5. Update employee display to show names + traits

**UI Changes:**
```
Current:  ●●● (just colored blobs)
Proposed: Dr. Alex Chen (Safety, Workaholic) ●
          Jordan Patel (Capability, Media Savvy) ●
          Casey Garcia (Compute, Team Player) ●
```

**Files to create:**
- `godot/scripts/core/researcher_system.gd` (new)

**Files to modify:**
- `godot/scripts/core/game_state.gd` - Add researchers array
- `godot/scripts/ui/main_ui.gd` - Show researcher details
- `godot/scripts/core/actions.gd` - Use researcher system in hiring

**Depth Indicators:**
- Show individual names = future individual management
- Show traits = future personality-based events
- Show specializations = future tech tree depth

---

### 5. Background Images (P1 - 1 hour)

**Assets Available:**
```
godot/assets/dump_october_31_2025/
- main office doom chair scene.png
- vibes computer 1.png
- vibes computer 2.png
- zoomed in doom cat.png

godot/assets/images/backgrounds/
- office_scene.png
```

**Screens to Enhance:**

**5a. Welcome Screen**
- Add background: `office_scene.png` with dark overlay (80% opacity)
- Buttons float over background
- Subtle film grain effect

**5b. Game Over Screen**
- Victory: Office scene with green tint + brightness
- Defeat: Office scene with red tint + desaturation
- Stats panel opaque over dimmed background

**5c. Main Game Screen**
- Optional: Subtle office background behind UI panels
- Very desaturated to not distract (10% opacity)

**Implementation:**
1. Add TextureRect backgrounds to scenes
2. Apply ColorRect overlays for tint/dimming
3. Ensure text remains readable (contrast check)
4. Optimize image sizes (compress PNGs)

**Files:**
- `scenes/welcome.tscn` - Add background
- `scenes/ui/game_over_screen.tscn` - Add background
- `scenes/main.tscn` - Optional subtle background

**Performance:**
- Preload textures in autoload
- Use compressed formats
- Target <5MB total for backgrounds

---

### 6. Enhanced Hiring Dialog (P1 - 1.5 hours)

**Current System:**
- Simple dialog with 3 options (Safety/Capability/Compute)
- No specialization depth
- No hiring complexity tiers

**Proposed System (from Python):**

**Tier 1: Small Team (≤3 staff)**
```
Available Roles:
[1] Generalist ($0, 1 AP) - Basic hire
[2] Safety Researcher ($0, 2 AP) - Reduces doom
[3] Capability Researcher ($0, 2 AP) - Faster research, +doom risk
[4] Compute Engineer ($0, 2 AP) - Boosts compute
```

**Tier 2: Growing Org (4-8 staff)**
```
All Tier 1 roles plus:
[5] Security Specialist ($0, 2 AP) - Reduces leak/hack risk
[6] Data Scientist ($0, 2 AP) - Analytics bonus
```

**Tier 3: Large Org (9+ staff)**
```
All previous roles plus:
[7] Manager ($0, 3 AP) - +1 AP per turn
[8] Specialist Researcher ($0, 3 AP) - Unique traits/skills
```

**Each hire shows:**
- Random generated name
- Specialization
- 0-2 random traits (60% have 1 trait)
- Skill level (3-8, visual bars)
- Expected salary range

**Example Dialog:**
```
┌─────────────────────────────────────────────────┐
│  Hire Safety Researcher (Team size: 5)         │
├─────────────────────────────────────────────────┤
│ [1] Dr. Alex Chen                               │
│     Skill: ████░░░░ (6/10)                      │
│     Traits: Workaholic, Safety Conscious        │
│     Salary: $90k/turn                           │
│     Cost: 2 AP                                  │
├─────────────────────────────────────────────────┤
│ [2] Jordan Patel                                │
│     Skill: ██████░░ (7/10)                      │
│     Traits: Media Savvy                         │
│     Salary: $110k/turn                          │
│     Cost: 2 AP                                  │
├─────────────────────────────────────────────────┤
│ [3] Re-roll candidates (1 AP)                   │
│ [4] Cancel                                      │
└─────────────────────────────────────────────────┘
```

**Implementation:**
1. Create `ResearcherGenerator` class in `researcher_system.gd`
2. Modify `_show_hiring_submenu()` to:
   - Check team size for tier
   - Generate 2-3 random candidates per role
   - Show detailed candidate info
   - Allow re-rolling (costs 1 AP)
3. Update `GameManager.hire_staff()` to use researcher system

**Files:**
- `scripts/core/researcher_system.gd` - Generator logic
- `scripts/ui/main_ui.gd` - Enhanced dialog
- `scripts/game_manager.gd` - Integrate with hiring

**Depth Indicators:**
- Skill levels → future training/leveling system
- Traits → future personality events
- Salary expectations → future budget management
- Re-rolling → strategic resource trade-off

---

## 🎨 Visual Style Application

### Color Palette Usage
```gdscript
# Apply consistently across all UI elements

# Backgrounds
- Main panels: STEEL_DARK (0.110, 0.153, 0.188)
- Overlays: STEEL_DARK at 90% opacity
- Dialogs: STEEL_DARK with ELECTRIC_BLUE border

# Text
- Primary: WHITE (1.0, 1.0, 1.0)
- Secondary: STEEL_LIGHT (0.7, 0.7, 0.8)
- Disabled: STEEL_MEDIUM (0.4, 0.4, 0.5)

# Resources
- Money: WARNING_AMBER (gold #F5AE40)
- Compute: ELECTRIC_BLUE (#34A8DB)
- Research: NEON_MAGENTA (#ED4
3CA)
- Doom: RED → ORANGE → YELLOW → GREEN (gradient)
- AP: NEON_MAGENTA (bright)
- Reputation: ORANGE

# Indicators
- Success: TERMINAL_GREEN (#32CD32)
- Warning: WARNING_AMBER
- Error: ALERT_RED (#FF4444)
- Info: ELECTRIC_BLUE

# Researcher Types
- Safety: GREEN
- Capability: RED
- Compute: BLUE
- Admin: YELLOW
```

---

## 📐 Layout Specifications

### Top Bar (Single Line)
```
Height: 40px
Padding: 8px horizontal, 4px vertical
Font: 14px, monospace preferred
Separator: " | " (pipe with spaces)
```

### Resource Display
```
Format: Label: Value
Money: $123k (show k for thousands)
Compute/Research: One decimal (45.3)
Papers: Integer (5)
AP: Integer + blob display (3 ●●●○)
Doom: Percentage + momentum (45.2% ↑2.3)
```

### Action Buttons
```
Height: 32px (was 40px)
Padding: 6px vertical, 10px horizontal
Font: 12px
Border: 2px ELECTRIC_BLUE
Border Radius: 4px
Hover: scale(1.02), glow 4px
```

### Keyboard Hints
```
Format: [N] Action Name (costs)
[N]: ELECTRIC_BLUE, bold
Costs: WARNING_AMBER (money), NEON_MAGENTA (AP)
```

---

## ⚡ Performance Targets

### Load Times
- Welcome screen: <100ms
- Main game init: <500ms
- Scene transitions: <200ms

### Runtime
- UI updates: <16ms (60fps)
- Button hover: <5ms
- Dialog open: <100ms

### Memory
- Background images: <5MB total
- UI textures: <2MB
- Total runtime: <100MB

---

## 🧪 Testing Checklist

### Before Committing Each Change:
- [ ] Run `run_tests.bat` (all tests pass)
- [ ] Launch game (F5) - no console errors
- [ ] Test changed feature works
- [ ] Test keyboard shortcuts work
- [ ] Check visual appearance at 1920x1080
- [ ] Check visual appearance at 1280x720 (min supported)
- [ ] Take screenshot for dev blog

### Full UI Polish Test:
- [ ] All buttons clickable and keyboard-accessible
- [ ] All colors match style guide
- [ ] All text readable (contrast ≥4.5:1)
- [ ] No layout overflow at min resolution
- [ ] Info bar updates correctly
- [ ] Doom meter visible and updates
- [ ] Game over screen shows properly

---

## 📅 Implementation Timeline

### Session 1 (This Session - 2 hours)
- ✅ Window maximization (done)
- 🔲 Top bar redesign (45 min)
- 🔲 Button styling (45 min)
- 🔲 Submenu keyboard shortcuts (30 min)

### Session 2 (Next - 3 hours)
- Researcher system port (2 hours)
- Background images (45 min)
- Enhanced hiring dialog (shell only - 15 min)

### Session 3 (Future - 2 hours)
- Complete hiring dialog with candidates
- Animation polish
- Sound effects (if time)

---

## 🎯 Success Metrics

### Player Experience:
- "UI feels clean and professional"
- "I can navigate entirely by keyboard"
- "Resources are easy to read at a glance"
- "Hiring feels deep and strategic"

### Technical:
- Zero console errors on launch
- All GUT tests passing
- <200ms scene load times
- 60fps steady during gameplay

### Visual:
- Consistent color palette throughout
- No cluttered screens
- Clear visual hierarchy
- Professional polish level

---

_This plan integrates all feedback from the 2025-10-31 session. Implement in priority order (P0 → P1 → P2)._
