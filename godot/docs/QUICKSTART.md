# P(Doom) - Godot Version Quick Start

**New Godot Engine Version** - Beta Testing Ready! 🚀

---

## What's New?

The game has been migrated to **Godot Engine 4.5** for better performance, reliability, and future development. This is a fresh start with the same great gameplay!

### Why Godot?
- ✅ More stable and performant
- ✅ Cleaner architecture
- ✅ Better cross-platform support
- ✅ Easier to develop and maintain
- ✅ No more pygame corruption issues!

---

## Quick Start (2 Minutes)

### Option 1: Using Project-Local Godot (Recommended)

The Godot engine is already downloaded in `tools/godot/`!

**Windows**:
```bash
# From project root:
cd godot
..\tools\godot\Godot_v4.5-stable_win64.exe project.godot
```

**That's it!** The game will launch.

### Option 2: System-Wide Godot Install

If you prefer system-wide installation:

```bash
# Install via WinGet
winget install GodotEngine.GodotEngine

# Run from project
cd godot
godot project.godot
```

---

## How to Play

1. **Click "Init Game"** - Starts a new game
2. **Select Actions** - Click action buttons (grayed out = can't afford)
3. **Click "End Turn"** - Executes your selected actions
4. **Watch Events** - Popups appear for important events
5. **Repeat** - Keep playing until victory or doom!

### UI Guide

**Top Bar**:
- **Turn Number** - Current turn
- **Money** - Your funds ($)
- **Compute** - Computing power
- **Safety** - AI safety research level

**Left Panel** - Available Actions:
- Green buttons = You can afford these
- Gray buttons = Too expensive right now
- Hover for details (cost, description)

**Right Panel** - Message Log:
- Color-coded messages
- Turn history
- Action results
- Events and warnings

**Bottom Bar**:
- **Phase Indicator** - Current turn phase
  - 🟢 GREEN = Action Selection (your turn!)
  - 🔴 RED = Turn Start (processing...)
  - 🟡 YELLOW = Turn End (executing...)

---

## Game Flow

```
1. ACTION SELECTION (Your Turn)
   ↓ Select actions you want
   ↓ Click "End Turn"

2. TURN END (Processing)
   ↓ Actions execute
   ↓ Resources update

3. TURN START (New Turn Begins)
   ↓ Events may trigger
   ↓ Back to Action Selection
```

The game **auto-advances** between phases - just select actions and click "End Turn"!

---

## Beta Testing Focus

### What to Test:

1. **Play 10-20 turns** - Does it crash? Any bugs?
2. **Try different actions** - Do they all work?
3. **Test events** - Do popups appear correctly?
4. **Check affordability** - Are costs calculated correctly?
5. **Game over/victory** - Does the game end properly?

### Known Limitations (Phase 5 MVP):

- ❌ No multiple screens yet (research, employees, etc.)
- ❌ No save/load
- ❌ No settings menu
- ❌ No graphics/styling (functional only)
- ❌ No sound
- ⏳ Limited action set (core actions only)

### What Works:

- ✅ Full turn system
- ✅ Dynamic action loading
- ✅ Event popups
- ✅ Resource management
- ✅ Action queueing
- ✅ Affordability checking
- ✅ Game over/victory detection
- ✅ Auto-advancing turn flow

---

## Troubleshooting

### Game Won't Start

**Check Python**:
```bash
python --version
# Should show Python 3.11+
```

The Godot UI communicates with a Python backend. Make sure Python is in your PATH.

### Actions Don't Appear

Check the message log for errors. The bridge may have failed to connect.

### Godot Not Found

If using system install:
```bash
# Windows
where godot

# If not found:
winget install GodotEngine.GodotEngine
```

### Still Having Issues?

1. Check the **message log** (right panel) for error messages
2. Look for Python errors in Godot's console output
3. Report bugs with:
   - What you did
   - What happened
   - What the message log shows
   - Screenshots if possible

---

## Feedback Wanted!

### Critical Questions:

1. **Stability** - Any crashes? When?
2. **Gameplay** - Is the flow smooth? Confusing?
3. **UI/UX** - Is it clear what to do? What's missing?
4. **Actions** - Which actions feel broken/overpowered/useless?
5. **Events** - Do events work? Are they interesting?
6. **Performance** - Any lag or slowness?

### Report Issues:

- GitHub Issues: https://github.com/PipFoweraker/pdoom1/issues
- Or just tell me directly!

---

## Technical Details

### Architecture

```
Godot UI (GDScript)
    ↓ PowerShell Pipes
Python Bridge (bridge_server.py)
    ↓ Game Logic
Shared Game Logic (Python)
```

### Files:

- `godot/` - Godot project
- `godot/scenes/main.tscn` - Main UI scene
- `godot/scripts/` - GDScript code
- `shared_bridge/` - Python bridge server
- `src/` - Shared game logic (old pygame code)

### For Developers:

See `godot/README.md` and `godot/SETUP.md` for detailed architecture and setup info.

---

## What's Next?

After beta testing feedback, we'll add:

- 📊 Multiple screens (research, employees, upgrades)
- 🎨 Proper UI styling and graphics
- 💾 Save/load system
- ⚙️ Settings menu
- 🔊 Sound effects and music
- 📈 More actions and events
- 🏆 Victory conditions and scoring

---

## Legacy Python Version

The old pygame version is still available but deprecated:

```bash
# Not recommended - has known issues
cd pygame
python main.py
```

**Please test the Godot version instead!** 🙏

---

**Version**: Phase 5 MVP (2025-10-30)
**Status**: Beta Testing Ready
**Engine**: Godot 4.5 + Python 3.11

🤖 Happy testing! May your P(Doom) remain low! 🤖

---

_Generated with [Claude Code](https://claude.com/claude-code)_
