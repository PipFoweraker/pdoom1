# P(Doom) v0.10.1 - UX Improvements & First Public Release

**Release Date:** 2025-11-03
**Platform:** Windows 10/11 (64-bit)
**Engine:** Godot 4.5.1

---

## 🎉 First Official Godot Release!

This is the first official release of P(Doom) built with Godot 4.x! The Python/Pygame version (v0.1.0) is now deprecated for players.

---

## ✨ Major Features

### Critical Fixes
- **🔧 Action Point Tracking Fixed** - Players can no longer overcommit AP beyond their available points
- **🔧 Queue Management** - Clear Queue button now works correctly with case-insensitive phase checking
- **🔧 AP Display** - Shows remaining AP: "AP: 3 (1 free, 2 queued)" with color coding

### UX Improvements
- **✅ Visual Queue Controls** - Each queued action has a "✕ Remove" button
- **✅ Danger Warnings** - Alerts when doom >70%, reputation <30, or money <$20k before committing turn
- **✅ Better Button States** - Commit Actions button disabled when queue is empty
- **✅ Keyboard Shortcuts** - C to clear queue, Space/Enter to commit
- **✅ Color-Coded AP** - Green (available), Yellow (low), Red (depleted)

### Polish
- **📝 Professional Description** - "Strategic simulation" tone replacing "satirical"
- **🧹 Code Quality** - Zero GDScript warnings, clean codebase
- **📚 Organized Docs** - 20 files moved into logical structure

---

## 🎮 Quick Start

### Windows Users
1. Download `PDoom-v0.10.1-Windows.zip`
2. Extract to a folder
3. Run `PDoom.exe`
4. Play!

### System Requirements
- **OS:** Windows 10/11 (64-bit)
- **RAM:** 2GB minimum
- **Disk:** 150MB free space
- **Display:** 1280x720 or higher

---

## 🎯 How to Play

### Goal
Manage an AI safety lab and reach turn 100 with P(Doom) at 0% while staying funded.

### Controls
- **1-9:** Select actions from the menu
- **C:** Clear action queue
- **Space/Enter:** Commit queued actions and end turn
- **ESC:** Pause/Menu

### Core Mechanics
1. **Queue Actions** - Select 1-3 actions per turn (uses Action Points)
2. **Manage Resources** - Balance money, compute, research, and reputation
3. **Watch Doom** - Your choices affect P(Doom) - keep it low!
4. **React to Events** - Random events require strategic responses
5. **Compete** - Rival labs advance AI capabilities

---

## 📋 Full Changelog

### Fixed
- **CRITICAL:** Action overcommitment bug - AP validation now checks remaining AP
- **CRITICAL:** Clear Queue button always disabled - Fixed case-sensitive phase check
- **CRITICAL:** Committed AP not tracked - Now properly increments when queuing
- GDScript warnings - Renamed shadowing variables, prefixed unused vars

### Changed
- Button text: "End Turn" → "Commit Actions (Space)"
- AP display: Now shows "AP: 3 (X free, Y queued)"
- Game description: "Satirical" → "Strategic simulation"
- Keyboard shortcut: X → C for clear queue (avoids conflicts)

### Added
- **Clear Queue button** with C keyboard shortcut
- **Remove buttons** on individual queue items
- **Danger warnings** before committing risky turns
- **Color-coded AP counter** (green/yellow/red)
- **Better error messages** with actionable suggestions

### Technical
- Fixed GUT addon compatibility with Godot 4.5.1
- Added remove_queued_action() function to GameManager
- Improved button state management
- Case-insensitive phase checking

---

## 🐛 Known Issues

### Non-Critical
- Mac/Linux builds not available yet (high priority for v0.11.0)
- Some advanced keyboard navigation not implemented (#423)

### Workarounds
- If game doesn't start: Right-click PDoom.exe → Properties → Unblock → Apply

---

## 📚 Resources

- **Website:** [pdoom1.com](https://pdoom1.com)
- **GitHub:** [PipFoweraker/pdoom1](https://github.com/PipFoweraker/pdoom1)
- **Player Guide:** [docs/PLAYERGUIDE.md](https://github.com/PipFoweraker/pdoom1/blob/main/docs/PLAYERGUIDE.md)
- **Report Bugs:** [GitHub Issues](https://github.com/PipFoweraker/pdoom1/issues)

---

## 🙏 Credits

**Game Design & Development:** Pip Foweraker
**AI Assistant:** Claude (Anthropic) - Code generation and testing
**Engine:** Godot 4.5.1
**Inspiration:** AI Safety community, Manifold Markets

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🔜 What's Next (v0.11.0)?

- Mac/Linux builds
- Universal keyboard navigation (#423)
- Employee management screen (#430)
- More polish and QoL improvements

---

**Enjoy the game! If you encounter issues, please report them on GitHub.**

🌐 Visit [pdoom1.com](https://pdoom1.com) for guides and community discussions!
