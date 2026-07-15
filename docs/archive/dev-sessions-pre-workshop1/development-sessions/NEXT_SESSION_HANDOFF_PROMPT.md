# Next Session Handoff Prompt

## Context for Next Chat Session

### Mission Status: Enhanced Personnel System Complete

**MAJOR ACHIEVEMENT**: Implemented Issue #197 - Enhanced Personnel System with individual researchers, candidate pool, traits, and team management.

**PREVIOUS ACHIEVEMENT**: Generated 91 custom game icons through AI asset pipeline (~$12 for 145 images).

### Current State (Ready for Handoff)

**Working Branch**: `main`
**Personnel System**: Complete - individual researchers with traits, burnout, skills
**Candidate Pool**: Implemented - 6-slot pool that populates slowly each turn
**Asset Pipeline**: Complete and production-ready
**Icons Available**: 91 assets in `godot/assets/icons/`

### Primary Missions

**Mission 1: Candidate Pool UI**
- Show available candidates in hiring menu before player selects
- Display candidate traits, skills, and specialization
- Let player choose which specific candidate to hire

**Mission 2: Integrate Icons into UI**
- Replace placeholder/text-based UI elements with generated icons
- Start with highest-impact, most-visible elements
- Reference: `docs/ui/UI_LAYOUT_GUIDE.md`

### Key Files to Focus On

1. **Asset Inventory**:
   - Icons: `godot/assets/icons/` (organized by category)
   - YAML definition: `art_prompts/ui_icons.yaml`

2. **UI Implementation Files**:
   ```
   godot/scenes/main.tscn          # Main game layout
   godot/scripts/ui/main_ui.gd     # Main UI logic
   godot/scripts/ui/tab_manager.gd # Screen management
   ```

3. **Asset Categories Available**:
   - `main_navigation/` - Home, Research, Employees, etc.
   - `actions/` - Hire, Build, Safety, Capability research
   - `upgrades/` - Compute, Cloud, Office improvements
   - `resources/` - Money, Compute, Data, Power, Space
   - `indicators/` - Risk, Alert, Status levels

### Technical Foundation

```python
# Asset pipeline tools (working correctly)
tools/assets/generate_images.py    # OpenAI API image generation
tools/assets/select_assets.py      # Interactive variant selection
tools/assets/promote_assets.py     # Copy to game assets directory

# YAML as single source of truth
art_prompts/ui_icons.yaml          # All 91 asset definitions
```

### Documentation Created

- **Pipeline Guide**: `docs/ASSET_GENERATION_PIPELINE.md`
- **Dev Blog Entry**: `docs/devblog/entries/2025-11-18-building-an-ai-asset-generation-pipeline.md`
- **UI Layout Reference**: `docs/ui/UI_LAYOUT_GUIDE.md`

### Next Session Action Plan

1. **Identify first integration target**: Pick highest-impact UI element
2. **Create icon texture resources**: Set up Godot import for icon files
3. **Update UI scenes**: Replace placeholders with actual icons
4. **Test visual consistency**: Ensure icons match StarCraft 2/XCOM aesthetic
5. **Iterate**: Continue with remaining UI elements

### Architecture Insights

**Icon Naming Convention**: `{asset_id}_{size}.png`
- Example: `ui_home_hq_128.png`, `action_hire_256.png`

**Category Structure** (in `godot/assets/icons/`):
```
main_navigation/   # Tab/screen icons
actions/           # Left panel action buttons
upgrades/          # Right panel upgrade buttons
resources/         # Top bar resource indicators
indicators/        # Status and alert icons
decorative/        # UI frames and dividers
```

### Success Metrics to Achieve

**Personnel System (Done)**:
- [x] Individual researchers with traits, skills, burnout
- [x] Candidate pool populates slowly over time
- [x] Hiring from pool with resource refunds on failure
- [x] Team management (8 per manager)
- [x] Poaching events (4% chance after turn 20)
- [x] Traits active (team_player, media_savvy, leak_prone, etc.)

**UI Integration (Pending)**:
- [ ] Candidate pool displayed in hiring menu
- [ ] Main navigation tabs using icon assets
- [ ] Action buttons showing contextual icons
- [ ] Resource indicators with visual representations

### Files Modified This Session

```
# Core Game Systems (Personnel #197)
godot/scripts/core/turn_manager.gd   # Individual researcher productivity
godot/scripts/core/actions.gd        # Pool-based hiring with refunds
godot/scripts/core/events.gd         # Poaching event + threshold conditions
godot/scripts/core/game_state.gd     # Candidate pool management

# UI Updates
godot/scripts/ui/main_ui.gd          # Employee roster display
godot/scripts/ui/tab_manager.gd      # Disabled E key shortcut
godot/autoload/keybind_manager.gd    # Disabled employee_tab binding
godot/scenes/main.tscn               # Added EmployeeRosterZone

# Documentation
docs/game-design/PERSONNEL_BALANCING_NOTES.md  # Tuning values
docs/PLAYERGUIDE.md                   # Player-facing docs
docs/DEVELOPERGUIDE.md                # Developer architecture
docs/QUICK_REFERENCE.md               # Quick reference card
README.md                             # Gameplay description
```

### Ready to Continue

**Personnel System**: Complete, needs playtesting for balance tuning
**UI Work**: Candidate pool needs UI to show available hires before selection
**Icon Integration**: Ready to begin replacing placeholders with generated assets

**Branch Status**: All commits made
**Next Focus**: Candidate pool UI, then icon integration
**Reference Docs**:
- Balancing: `docs/game-design/PERSONNEL_BALANCING_NOTES.md`
- Pipeline: `docs/ASSET_GENERATION_PIPELINE.md`

### Quick Reference

```bash
# View available icons
ls godot/assets/icons/

# Check YAML for specific asset
grep -A 5 "ui_home_hq" art_prompts/ui_icons.yaml

# Regenerate or add variants if needed
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml --ids ui_home_hq --variants 2
python tools/assets/select_assets.py --file art_prompts/ui_icons.yaml --gallery generated
python tools/assets/promote_assets.py --file art_prompts/ui_icons.yaml --status selected
```
