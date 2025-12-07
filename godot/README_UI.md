# P(Doom) Godot UI - Quick Reference

## Scene Structure

```
FOLDER godot/
|--- FOLDER scenes/
|   |--- 🎬 welcome.tscn              [Main menu - Start here]
|   |--- 🎬 settings_menu.tscn        [Audio, graphics, gameplay settings]
|   |--- 🎬 pregame_setup.tscn        [Player name, lab name, seed, difficulty]
|   |--- 🎬 player_guide.tscn         [Tutorial and help]
|   |--- 🎬 main.tscn                 [Main game scene]
|   `--- 🎬 end_game_screen.tscn      [Victory/defeat screen]
|
`--- FOLDER scripts/ui/
    |--- 📜 welcome_screen.gd          [Main menu logic]
    |--- 📜 settings_menu.gd           [Settings management]
    |--- 📜 pregame_setup.gd           [Game configuration]
    |--- 📜 player_guide.gd            [Guide display]
    |--- 📜 main_ui.gd                 [In-game UI controller]
    `--- 📜 end_game_screen.gd         [End game display + celebration]
```

## Quick Start Testing

1. **Open Godot project**
   ```
   godot godot/project.godot
   ```

2. **Test Welcome Screen**
   - Set `welcome.tscn` as main scene
   - Press F5 to run
   - Test all 5 buttons:
     - Launch Lab  ->  Main game
     - Custom Seed  ->  Pre-game setup
     - Settings  ->  Settings menu
     - Player Guide  ->  Guide
     - Exit  ->  Quit

3. **Test Each Screen**
   - Use Escape key to navigate back
   - Use arrow keys for navigation
   - Use Enter to select

## Screen Descriptions

### 🎮 Welcome Screen
**Purpose:** Main menu entry point
**Buttons:**
- Launch Lab
- Launch with Custom Seed
- Settings
- Player Guide
- Exit

**Keyboard:**
-  ^  v  or WS: Navigate
- Enter/Space: Select
- 1-5: Direct selection
- Escape: Quit

---

### ⚙ Settings Menu
**Purpose:** Configure game settings
**Sections:**
- Audio (Master volume, SFX volume)
- Graphics (Quality, Fullscreen)
- Gameplay (Difficulty)

**Keyboard:**
- Escape: Back to welcome

**Status:** SUCCESS Complete (needs config persistence)

---

### 🛠 Pre-Game Setup
**Purpose:** Configure new game
**Fields:**
- Player Name (required)
- Lab Name (required, with 🎲 random button)
- Seed (optional, weekly challenge by default)
- Difficulty (Easy/Standard/Hard)

**Validation:**
- Launch button disabled until names entered

**Keyboard:**
- Enter: Launch (when valid)
- Escape: Cancel

**Status:** SUCCESS Complete (needs connection to GameManager)

---

### BOOK Player Guide
**Purpose:** Tutorial and help
**Sections:**
- Game Objective
- Controls
- Key Resources
- Strategy Tips

**Features:**
- Scrollable content
- Color-coded resource explanations
- Keyboard shortcut reference

**Keyboard:**
- Escape: Back to welcome

**Status:** SUCCESS Complete

---

### TARGET Main Game UI
**Purpose:** In-game interface
**Features:**
- Resource display
- Action list (categorized)
- Message log
- Turn phase indicator
- Employee blobs (* * * )

**Keyboard:**
- 1-9: Quick-select actions
- Space/Enter: End turn
- Escape: Init game (if not started)

**Status:** SUCCESS Complete (from Phase 6)

---

### ACHIEVEMENT End Game Screen
**Purpose:** Victory/defeat celebration
**Features:**
- Title with emoji (ACHIEVEMENT/CHECKED/☠)
- Color-coded based on outcome
- Stats display with rank highlighting
- Final resources
- Top 5 leaderboard
- Celebration for new records

**Buttons:**
- Play Again (R key)
- View Full Leaderboard
- Main Menu (Escape key)

**Status:** SUCCESS Complete (enhanced from Phase 6)

---

## Color Scheme Reference

### Background Colors
- Main BG: `#29323A` (Color(0.16, 0.18, 0.22))
- Panel BG: `#1F252E` (Color(0.12, 0.14, 0.18))
- Button Normal: `#335080` (Color(0.2, 0.3, 0.5))
- Button Hover: `#4D80CC` (Color(0.3, 0.5, 0.8))
- Button Focus: `#6699FF` (Color(0.4, 0.6, 1.0))

### Text Colors
- Title: `#DBF0FF` (Color(0.86, 0.94, 1.0))
- Subtitle: `#B3C7DB` (Color(0.7, 0.78, 0.86))
- Section Header: `#66CCFF` (Color(0.4, 0.8, 1.0))
- Body: `#E6E6E6` (Color(0.9, 0.9, 0.9))

### Status Colors
- Victory: `#33FF33` (Color(0.2, 1.0, 0.2))
- Defeat: `#FF3333` (Color(1.0, 0.2, 0.2))
- Gold Rank: `#FFD700` (Color(1.0, 0.84, 0.0))
- Silver Rank: `#C0C0C0` (Color(0.75, 0.75, 0.75))
- Bronze Rank: `#CC8033` (Color(0.8, 0.5, 0.2))

### Resource Colors
- Money: `#FFFF00` (Yellow)
- Compute: `#00FFFF` (Cyan)
- Research: `#FF00FF` (Purple)
- Papers: `#FFA500` (Orange)
- Reputation: `#0080FF` (Blue)
- Safety: `#00FF00` (Green)
- Capabilities: `#FF0000` (Red)
- Doom: Dynamic (Green < 30, Yellow < 70, Red >= 70)

---

## Common Patterns

### Button Styling
All buttons use the same StyleBox pattern:
- Normal: Dark blue
- Hover: Bright blue
- Pressed: Very dark blue
- Focus: Bright blue with white border

### Navigation Pattern
All screens follow the same pattern:
```gdscript
func _input(event: InputEvent):
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_ESCAPE:
            _on_back_pressed()
```

### Scene Transition Pattern
All navigation uses:
```gdscript
get_tree().change_scene_to_file("res://scenes/TARGET.tscn")
```

---

## Testing Workflow

### Manual Testing Sequence
1. **Start at Welcome**  ->  Test all 5 buttons
2. **Settings Menu**  ->  Adjust all settings, test Apply/Back
3. **Pre-Game Setup**  ->  Try random lab name, test validation
4. **Player Guide**  ->  Scroll through all sections
5. **Main Game**  ->  Play through to end game
6. **End Game**  ->  Test Play Again and Main Menu

### Test Cases
- [ ] Fresh install (no config file)
- [ ] With existing config file
- [ ] Victory ending
- [ ] Defeat ending
- [ ] New record (#1 rank)
- [ ] Keyboard-only navigation
- [ ] Mouse-only navigation
- [ ] Mixed keyboard/mouse
- [ ] Different screen resolutions
- [ ] Fullscreen toggle

---

## Known Issues & Workarounds

### Issue: Settings don't persist
**Status:** Expected (not implemented yet)
**Workaround:** None
**Fix Required:** Create config.cfg system

### Issue: Pre-game config not passed to game
**Status:** Expected (integration pending)
**Workaround:** Game uses defaults
**Fix Required:** Create GameConfig singleton

### Issue: Audio sliders don't affect actual volume
**Status:** Expected (audio system not connected)
**Workaround:** Volume preview works for master
**Fix Required:** Connect to audio buses

### Issue: Full leaderboard shows placeholder
**Status:** Expected (not implemented yet)
**Workaround:** Top 5 shown on end game screen
**Fix Required:** Create dedicated leaderboard scene

---

## Next Development Steps

### Priority 1 (Required for playability)
1. Create `game_config.gd` autoload singleton
2. Connect pre-game setup to GameManager
3. Implement config file persistence
4. Fix audio system integration

### Priority 2 (Polish)
1. Create full leaderboard screen
2. Add screen transition animations
3. Add button hover sound effects
4. Add confirmation dialogs (e.g., "Quit without saving?")

### Priority 3 (Future)
1. Keybinding customization
2. Accessibility options
3. Achievement system
4. Save game slots
5. Profile system with stats tracking

---

## File Size & Performance

**Scene Sizes:**
- `welcome.tscn`: ~6 KB
- `settings_menu.tscn`: ~9 KB
- `pregame_setup.tscn`: ~8 KB
- `player_guide.tscn`: ~10 KB
- `end_game_screen.tscn`: ~4 KB (existing)

**Total UI Code:** ~1,500 lines of GDScript

**Performance:** All screens run at 60 FPS (lightweight UI)

---

## Credits

**Ported from Pygame:**
- Settings menu structure  ->  `src/ui/settings_menus.py`
- Pre-game setup logic  ->  `src/ui/pre_game_settings.py`
- Menu styling  ->  `src/ui/menus.py`
- End game celebration  ->  `src/ui/modular_end_game_menu.py`

**Godot Implementation:**
- All `.tscn` and `.gd` files created fresh for Godot
- Styled to match P(Doom) bureaucracy theme
- Adapted for Godot's node-based UI system

---

## Support & Questions

For issues or questions about the UI:
1. Check `UI_MIGRATION_SUMMARY.md` for detailed documentation
2. Review this README for quick reference
3. Test each screen individually using the Testing Workflow
4. Check console output (`print()` statements throughout)

**Happy testing!** LAUNCH
