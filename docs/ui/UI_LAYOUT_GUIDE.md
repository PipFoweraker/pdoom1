# P(Doom) UI Layout Guide

**Version:** 0.10.7
**Date:** 2025-11-26
**Purpose:** Comprehensive reference for UI zones to prevent layout confusion in future updates

---

## Overview

The P(Doom) UI follows a classic RTS-inspired layout with distinct, purpose-driven zones. This document provides a complete reference to prevent the UI layout issues we experienced during development.

## Visual Zone Map

```
+--------------------------------------------------------------------------+
| TOP BAR - Resource Display                                     [E]    |
| Turn | Money | Compute | Research | Papers | Rep | AP         Employees|
|-----------+-------------------------------------+-----------------------|
|          |                                     |                      |
|  LEFT    |         MIDDLE PANEL                |    RIGHT PANEL       |
|  PANEL   |                                     |                      |
|          |  +---------------------------+        |  Upgrades:           |
| Actions: |  |   [ORANGE] P(DOOM)      |        |  [upgrade list]      |
|          |  `---------------------------`        |                      |
| [1] Act1 |                                     |                      |
| [2] Act2 |  +--------+  +----------+              |  Action Queue:       |
| [3] Act3 |  |GREEN |  | BLUE   |              |  [queued actions]    |
| [4] Act4 |  | CAT  |  | 58.5%  |              |                      |
| [5] Act5 |  |      |  |----------|              |                      |
| [6] Act6 |  |IMAGE |  |PURPLE  |              |  Message Log:        |
| [7] Act7 |  |      |  | DOOM   |              |  [game messages]     |
| [8] Act8 |  |      |  | METER  |              |                      |
| [9] Act9 |  `--------`  `----------`              |                      |
|          |                                     |                      |
|-----------+-------------------------------------+-----------------------|
| INFO BAR - Hover over actions to see details...                       |
|--------------------------------------------------------------------------|
| [Init] [Hire SR] [Reserve AP] [Clear] [Actions] [Plan]  Phase: ...  [N]|
`--------------------------------------------------------------------------`
```

---

## Zone Breakdown

### 1. TOP BAR (Resource Display)
**File:** [main.tscn:42-131](../godot/scenes/main.tscn#L42-L131)
**Script:** [main_ui.gd:5-11](../godot/scripts/ui/main_ui.gd#L5-L11)

**Purpose:** Display all game resources and current turn in a single horizontal line

**Elements (left to right):**
- **P(Doom)** - Game title
- **Turn: N** - Current turn number
- **Money: $N** - Available money
- **Compute: N** - Computing resources
- **Research: N** - Research points
- **Papers: N** - Published papers
- **Rep: N** - Reputation score
- **AP: N** - Action Points (shows reserved AP with colored indicators)
- **[Employees (E)]** - Button to open employee management screen

**Layout Properties:**
- Container: HBoxContainer
- Separation: 10px between elements
- Font size: 14px (resources), 18px (title)
- Separators: Gray vertical bars (|) with modulate Color(0.4, 0.4, 0.5, 1)

**Important Notes:**
- Doom percentage was **removed** from top bar (previously displayed as "Doom: N%")
- Now shown in middle panel as part of 4-zone core UI
- DO NOT add doom back to top bar - it creates visual clutter

---

### 2. LEFT PANEL (Actions)
**File:** [main.tscn:140-176](../godot/scenes/main.tscn#L140-L176)
**Script:** [main_ui.gd:14](../godot/scripts/ui/main_ui.gd#L14)

**Purpose:** Display all available actions player can queue

**Structure:**
- **Label:** "Actions:" header
- **ScrollContainer:** Scrollable list of action buttons
- **VBoxContainer (ActionsList):** Vertical list of dynamically generated action buttons

**Action Button Properties:**
- Keyboard shortcuts: 1-9 for first 9 actions
- Display format: `[N] Action Name`
- Color coding by affordability:
  - Can afford: Full color
  - Cannot afford: Dimmed (modulate 0.6)
- Hover behavior: Updates InfoBar with action details
- Click behavior: Adds action to queue (right panel)

**Size:**
- stretch_ratio: 0.22 (22% of ContentArea width)
- Buttons: SIZE_FILL horizontally, custom_minimum_size for consistent height

**Important Notes:**
- This panel is independent and should NOT be affected by middle panel changes
- Has its own dedicated space - plenty of screen real estate
- Keep action list clutter-free by using submenus for related actions

---

### 3. MIDDLE PANEL (Core 4-Zone Display)
**File:** [main.tscn:178-237](../godot/scenes/main.tscn#L178-L237)
**Script:** [main_ui.gd:26-27, 31](../godot/scripts/ui/main_ui.gd#L26-L27)

**Purpose:** Central focal point showing doom status or office cat

**THIS IS THE CRITICAL ZONE - READ CAREFULLY!**

#### Overall Structure:
```
MiddlePanel (VBoxContainer, alignment = 2 = bottom aligned)
|--- TitleZone (CenterContainer)
|   `--- TitleLabel: "P(DOOM)"
`--- CoreZone (HBoxContainer, separation = 0)
    |--- CatZone (CenterContainer)
    |   `--- OfficeCat (instance)
    `--- RightZones (VBoxContainer, separation = 0)
        |--- NumericDoomZone (CenterContainer)
        |   `--- NumericDoomLabel: "58.5%"
        `--- DoomMeterZone (CenterContainer)
            `--- DoomMeterPanel (PanelContainer, 140x140)
                `--- MarginContainer (2px margins)
                    `--- DoomMeter (instance)
```

#### The 4 Zones (Color-Coded):

**🟠 ORANGE ZONE - Title**
- **Element:** TitleLabel
- **Text:** "P(DOOM)"
- **Font Size:** 24px
- **Color:** Color(1.0, 0.6, 0.0, 1) - Orange
- **Purpose:** Game title / branding
- **File Reference:** [main.tscn:187-192](../godot/scenes/main.tscn#L187-L192)

**🟢 GREEN ZONE - Office Cat**
- **Element:** OfficeCat (instanced scene)
- **Size:** 196x245 (reduced from 280x350)
- **Cat Panel:** 179x179 (reduced from 256x256)
- **Visibility:** Hidden by default, shown when `state.has_cat == true`
- **Purpose:** Display contributor cat images with doom-level variants
- **File Reference:** [main.tscn:198-204](../godot/scenes/main.tscn#L198-L204)
- **Scene File:** [office_cat.tscn](../godot/scenes/ui/office_cat.tscn)
- **Script:** [office_cat.gd](../godot/scripts/ui/office_cat.gd)

**🔵 BLUE ZONE - Numeric Doom**
- **Element:** NumericDoomLabel
- **Font Size:** 18px (reduced from 20px)
- **Color:** Dynamic via ThemeManager.get_doom_color(doom)
  - Low doom (0-30%): Green
  - Medium doom (30-60%): Yellow/Orange
  - High doom (60%+): Red
- **Purpose:** Display exact doom percentage as text
- **File Reference:** [main.tscn:211-219](../godot/scenes/main.tscn#L211-L219)

**🟣 PURPLE ZONE - Doom Meter (Visual)**
- **Element:** DoomMeter (instanced scene)
- **Size:** 140x140 (reduced from 150x150)
- **Margins:** 2px (reduced from 8px)
- **Purpose:** Visual doom meter with momentum indicator
- **File Reference:** [main.tscn:221-237](../godot/scenes/main.tscn#L221-L237)
- **Scene File:** [doom_meter.tscn](../godot/scenes/ui/doom_meter.tscn)
- **Script:** [doom_meter.gd](../godot/scripts/ui/doom_meter.gd)

#### Critical Spacing Rules:

**THESE SPACINGS MUST BE MAINTAINED:**
- **CoreZone separation:** 0px (NO SPACE between cat and doom zones)
- **RightZones separation:** 0px (NO SPACE between numeric doom and meter)
- **DoomMeterPanel margins:** 2px all sides (minimal padding)

**Why Zero Spacing?**
The 4 zones are designed to be a **tightly clustered cohesive unit**, like the HUD in classic RTS games (StarCraft, X-COM). Any spacing makes it feel scattered and disconnected.

#### Size Relationships:

**Proportions (after 2025-11-17 adjustments):**
- Cat: 179x179 image + label ≈ 196x245 total
- Doom Meter: 140x140 + 4px margin = 144x144 total
- Numeric Doom: 18px font (single line)

**The cat is intentionally larger** - it's a reward for player engagement (adopting the cat). The doom meter is smaller to balance the visual weight.

#### Middle Panel Sizing:
- **stretch_ratio:** 0.28 (28% of ContentArea width)
- **alignment:** 2 (BOTTOM) - anchors content to bottom like RTS resource indicators

---

### 4. RIGHT PANEL (Upgrades, Queue, Message Log)
**File:** [main.tscn:239-275](../godot/scenes/main.tscn#L239-L275)
**Script:** [main_ui.gd:15-18](../godot/scripts/ui/main_ui.gd#L15-L18)

**Purpose:** Display upgrades, action queue, and game messages

**Structure (top to bottom):**

**4a. Upgrades Section**
- **Label:** "Upgrades:"
- **ScrollContainer:** Scrollable upgrade list
- **size_flags_stretch_ratio:** 0.45 (45% of panel height)
- **Purpose:** Show available upgrades player can purchase

**4b. Action Queue**
- **Label:** "Action Queue:"
- **PanelContainer:** Displays queued actions
- **custom_minimum_size:** Vector2(0, 80)
- **Purpose:** Show actions player has queued for next turn
- **Hint Text:** "No actions queued..." (when empty, gray)

**4c. Message Log**
- **Label:** "Message Log:"
- **ScrollContainer:** Auto-scrolling message area
- **RichTextLabel:** BBCode-enabled log
- **size_flags_stretch_ratio:** 0.35 (35% of panel height)
- **Purpose:** Display game events, actions, and feedback
- **Properties:**
  - bbcode_enabled: true
  - fit_content: true
  - scroll_following: true (auto-scrolls to bottom)

**Size:**
- **stretch_ratio:** 0.5 (50% of ContentArea width)

---

### 5. INFO BAR (Action Details)
**File:** [main.tscn:279-297](../godot/scenes/main.tscn#L279-L297)
**Script:** [main_ui.gd:16](../godot/scripts/ui/main_ui.gd#L16)

**Purpose:** Display detailed information when hovering over actions/upgrades

**Properties:**
- **Container:** PanelContainer with MarginContainer (10px margins)
- **Size:** custom_minimum_size Vector2(0, 60) - 2 lines tall to prevent flicker
- **Text:** RichTextLabel (BBCode enabled)
- **Default Text:** "Hover over actions to see details..."
- **Behavior:**
  - Shows action name, description, costs, effects on hover
  - Returns to default when not hovering
  - Permanently 2 lines tall to prevent UI shifting

**Important:**
- Height is FIXED at 60px to prevent visual jarring
- "No costs" text added for actions without costs (maintains 2-line format)
- Inspired by StarCraft 2 / X-COM info panels

---

### 6. BOTTOM BAR (Controls and Phase)
**File:** [main.tscn:298-370](../godot/scenes/main.tscn#L298-L370)
**Script:** [main_ui.gd:20-25](../godot/scripts/ui/main_ui.gd#L20-L25)

**Purpose:** Game control buttons and phase indicator

**Structure:**

**6a. Control Buttons (Left Side)**
- **Container:** HBoxContainer, separation = 3px (compressed)
- **Buttons (all 12px font):**
  - **Init** - Initialize game
  - **Hire SR** - Test action (hire safety researcher)
  - **Reserve AP** - Reserve 1 AP for next turn
  - **Clear (C)** - Clear action queue
  - **Actions (Space)** - Commit queued actions
  - **Plan (Enter)** - Commit plan and reserve remaining AP

**Button Compression (2025-11-17):**
- Text shortened for compactness (e.g., "Init Game"  ->  "Init")
- Font size reduced to 12px
- Separation reduced to 3px
- Removed expand flag - buttons stay compact on left side

**6b. Phase Label (Center)**
- **Container:** RichTextLabel (BBCode enabled)
- **size_flags_horizontal:** 3 (expands to fill space)
- **Text:** "[color=white]Phase: Not Started[/color]"
- **Purpose:** Show current game phase (TURN_START, ACTION_SELECTION, etc.)

**6c. Bug Report Button (Right)**
- **Size:** custom_minimum_size Vector2(110, 0)
- **Text:** "Bug Report (N)"
- **Font Size:** 12px
- **Keyboard:** N key to open

---

## File Reference Table

| Zone | Scene File | Script File | Lines in main.tscn |
|------|-----------|-------------|-------------------|
| Top Bar | main.tscn | main_ui.gd | 42-131 |
| Left Panel | main.tscn | main_ui.gd | 140-176 |
| **Middle Panel** | main.tscn | main_ui.gd | 178-237 |
| ∟ Orange (Title) | main.tscn | main_ui.gd | 184-192 |
| ∟ Green (Cat) | office_cat.tscn | office_cat.gd | 198-204 |
| ∟ Blue (Numeric) | main.tscn | main_ui.gd | 211-219 |
| ∟ Purple (Meter) | doom_meter.tscn | doom_meter.gd | 221-237 |
| Right Panel | main.tscn | main_ui.gd | 239-275 |
| Info Bar | main.tscn | main_ui.gd | 279-297 |
| Bottom Bar | main.tscn | main_ui.gd | 298-370 |

---

## Layout Mathematics

### ContentArea Width Distribution (HBoxContainer):
```
Total ContentArea = 100%

|-- LeftPanel:   30% (stretch_ratio 0.3)  [UPDATED v0.10.7]
|-- MiddlePanel: 30% (stretch_ratio 0.3)  [UPDATED v0.10.7]
`-- RightPanel:  40% (stretch_ratio 0.4)  [UPDATED v0.10.7]
```

**Note:** Percentages updated in v0.10.7 for better balance and space utilization.

### Right Panel Height Distribution (VBoxContainer):
```
Total RightPanel = 100%

|-- UpgradesScroll: 45% (stretch_ratio 0.45)
|-- QueuePanel:     Responsive (size_flags_vertical = 0)  [UPDATED v0.10.7]
`-- MessageScroll:  35% (stretch_ratio 0.35)
```

### Responsive Sizing Philosophy (v0.10.7):

**All layout elements now use percentage-based sizing instead of fixed pixels.**

| Element | Old (Fixed Pixels) | New (Responsive) |
|---------|-------------------|------------------|
| LeftPanel | custom_minimum_size: Vector2(80, 0) | size_flags_stretch_ratio: 0.3 |
| MiddlePanel | size_flags_stretch_ratio: 0.28 | size_flags_stretch_ratio: 0.3 |
| RightPanel | size_flags_stretch_ratio: 0.5 | size_flags_stretch_ratio: 0.4 |
| TopBar | custom_minimum_size: Vector2(0, 40) | (removed - responsive height) |
| InfoBar | custom_minimum_size: Vector2(0, 80) | size_flags_vertical: 0 |
| QueuePanel | custom_minimum_size: Vector2(0, 80) | size_flags_vertical: 0 |
| DoomMeterPanel | custom_minimum_size: Vector2(140, 140) | size_flags: 4 (shrink center) |
| EndTurnButton | custom_minimum_size: Vector2(180, 42) | size_flags_horizontal: 3 (fill) |

**Benefits:**
- Layout responds naturally to window resizing
- Better space utilization across different screen sizes
- More consistent with modern UI design patterns
- Easier to maintain (no magic pixel numbers)

---

## Common Mistakes to Avoid

### ERROR DON'T:
1. **Add doom back to top bar** - It was intentionally removed for clarity
2. **Add spacing to CoreZone or RightZones** - Zones must be tightly clustered
3. **Increase cat size** - It's already been reduced 30% for balance
4. **Make InfoBar single-line** - Fixed 2-line height prevents UI flicker
5. **Expand control buttons** - They've been compressed for better space usage
6. **Modify middle panel alignment** - Bottom alignment is intentional (RTS style)

### SUCCESS DO:
1. **Keep 4 zones tightly clustered** - They're a cohesive unit
2. **Maintain zero spacing** between CoreZone elements
3. **Use color-coding** when discussing zones (Orange/Green/Blue/Purple)
4. **Reference this doc** before making UI changes
5. **Test with cat both shown and hidden** - visibility changes affect layout
6. **Preserve button compression** - Bottom bar should stay compact

---

## UI Design Philosophy

### Inspiration Sources:
- **Classic DOOM (1993)** - Status bar at bottom with health/armor/ammo
- **StarCraft 2** - Resource bar at top, command area at bottom
- **X-COM** - Action points, info panels, clear resource indicators
- **RTS Games** - Fixed UI zones that don't shift during gameplay

### Core Principles:
1. **Clarity** - Each zone has one clear purpose
2. **Stability** - UI elements don't shift or resize during gameplay
3. **Accessibility** - Keyboard shortcuts for all major actions
4. **Feedback** - Hover states, info bar, message log provide context
5. **Minimalism** - Only essential information visible at all times

---

## Event Dialog System

**File:** [main_ui.gd:45-47, 1138-1367](../godot/scripts/ui/main_ui.gd)

**Critical Fix (2025-11-17):** Sequential event queue system

**Problem:** When multiple events triggered in same turn, dialogs stacked and keyboard input routed to wrong dialog.

**Solution:** Event queue system
- Events added to `event_queue: Array[Dictionary]`
- Only one event dialog shown at a time
- After resolving event, next event automatically shown
- Flag `is_showing_event: bool` prevents simultaneous dialogs

**Keyboard Shortcuts:**
- **Q/W/E/R/A/S/D/F/Z** - Select event choices (up to 9 options)
- **ESC** - Does NOT close event dialogs (by design, per issue #452)

**Important:**
- Event dialogs use forest green background Color(0.15, 0.25, 0.15)
- All dialogs have z_index = 1000 for overlay
- Dialogs are added to TabManager (not MainUI) to overlay everything

---

## Keyboard Shortcuts Reference

### Action Shortcuts:
- **1-9** - Queue actions 1-9 from left panel
- **Space** - Commit queued actions
- **Enter** - Commit plan (reserve remaining AP)
- **C** - Clear action queue
- **E** - Open employee screen

### Dialog Shortcuts:
- **Q/W/E/R/A/S/D/F/Z** - Select dialog options (events, hiring, etc.)
- **ESC** - Close submenu dialogs (NOT event dialogs)

### System Shortcuts:
- **N** or **Backslash (\\)** - Open/close bug report panel
- **F3** - Toggle debug overlay (if enabled)

---

## Future UI Additions

When adding new UI elements, follow these guidelines:

### Adding to Top Bar:
- SUCCESS New resources (e.g., "Influence", "Tech Level")
- ERROR Dynamic text that changes frequently (use message log instead)
- ERROR Doom percentage (it's in middle panel now)

### Adding to Left Panel:
- SUCCESS New actions (auto-managed by GameActions)
- SUCCESS Submenus for related actions (e.g., hiring submenu)
- ERROR Static information (use info bar)

### Adding to Middle Panel:
- WARNING **EXTREME CAUTION** - This is the visual centerpiece
- SUCCESS Alternative displays that swap with cat/doom (e.g., future features)
- ERROR Additional permanent elements (it's already 4 zones)

### Adding to Right Panel:
- SUCCESS New upgrade types (auto-managed by GameUpgrades)
- SUCCESS Additional info sections (ensure proper spacing)
- ERROR Action queue modifications (format is intentional)

### Adding to Info Bar:
- SUCCESS Enhanced action/upgrade descriptions
- ERROR Permanent text (it's for hover details only)
- ERROR Height changes (fixed 60px to prevent flicker)

### Adding to Bottom Bar:
- SUCCESS Essential control buttons (keep text short!)
- WARNING Phase info additions (use BBCode, keep concise)
- ERROR Expanding buttons (compression is intentional)

---

## Testing Checklist

When making UI changes, test these scenarios:

### Visual Tests:
- [ ] All 4 middle zones visible and tightly clustered
- [ ] Cat displays correctly when adopted (green zone)
- [ ] Doom meter animates smoothly (purple zone)
- [ ] Numeric doom updates and color-codes correctly (blue zone)
- [ ] P(DOOM) title visible (orange zone)
- [ ] Top bar resources all visible, no overflow
- [ ] Bottom bar buttons readable and compact

### Interaction Tests:
- [ ] Hover over actions updates info bar
- [ ] Info bar doesn't cause UI shifting (60px height)
- [ ] Action buttons 1-9 work correctly
- [ ] Space/Enter commit buttons function
- [ ] Employee screen opens with E key
- [ ] Bug report opens with N key

### Event Tests:
- [ ] Single event displays correctly
- [ ] Multiple events queue and show sequentially
- [ ] Q/W/E shortcuts work for all visible event options
- [ ] ESC does NOT close event dialogs
- [ ] Event resolution shows next queued event

### Edge Cases:
- [ ] Window resize (all zones scale properly)
- [ ] Long action names (buttons don't overflow)
- [ ] Many queued actions (queue panel scrollable if needed)
- [ ] Long message log (auto-scrolls, doesn't break layout)
- [ ] Cat + doom meter swap (visibility transitions smooth)

---

## Version History

### v0.10.7 (2025-11-26) - Responsive Layout Redesign
- **Converted all fixed-pixel sizing to percentage-based responsive layout**
- Updated ContentArea panel ratios: Left 22% -> 30%, Middle 28% -> 30%, Right 50% -> 40%
- Removed custom_minimum_size from TopBar, InfoBar, QueuePanel, DoomMeterPanel, EndTurnButton
- Layout now responds naturally to window resizing
- Better space utilization and balance across all panels
- Completes Issue #434 (UI Layout Redesign)

### v0.10.3 (2025-11-17) - UI Polish & Event Fix
- Fixed event dialog queue system (sequential presentation)
- Reduced cat size by 30% (280x350  ->  196x245)
- Removed all spacing between central zones (CoreZone: 10 -> 0, RightZones: 5 -> 0)
- Reduced doom meter size (150x150  ->  140x140)
- Reduced numeric doom font (20px  ->  18px)
- Compressed bottom control buttons (separation 5 -> 3, font 14 -> 12, text shortened)
- Created comprehensive UI zone documentation (this file)

### v0.10.2 (2025-11-16) - Middle Panel Restructure
- Restructured MiddlePanel into 4-zone layout (Orange/Green/Blue/Purple)
- Removed doom from top bar (moved to middle panel)
- Updated main_ui.gd references for new node paths
- Fixed office cat positioning issue (layout_mode 3 -> 2)

### Previous Versions:
- See [CHANGES_COMPLETED.md](../ui_changes_20251117/CHANGES_COMPLETED.md) for full history

---

## Contact / Questions

**This document should be the single source of truth for UI layout.**

If you're making UI changes and find this doc unclear or incorrect:
1. Update this document with corrections
2. Add clarifications for future developers
3. Include screenshots if helpful
4. Reference specific line numbers in scene/script files

**Remember:** The UI is a carefully balanced ecosystem. Small changes can have cascading effects. When in doubt, consult this guide!

---

*Generated with Claude Code - 2025-11-17*
