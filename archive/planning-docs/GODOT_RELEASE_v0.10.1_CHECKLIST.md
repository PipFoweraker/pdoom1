# Godot v0.10.1 Release Checklist

**Target:** Release tonight (within 11 hours)
**Goal:** First official Godot 4.x release

---

## Pre-Export Checklist

### 1. Godot Project Verification (15 min)
- [ ] Open `godot/project.godot` in Godot 4.x
- [ ] Test game runs without errors
- [ ] Verify main menu works
- [ ] Play through at least 5 turns
- [ ] Check leaderboard functionality
- [ ] Test keyboard shortcuts (Q/W/E/R/A/S/D/F/Z)
- [ ] Verify F3 debug overlay works

### 2. Export Configuration (10 min)
- [ ] Open Project → Export in Godot
- [ ] Verify "Windows Desktop" template exists
- [ ] Check export settings:
  - [ ] Executable name: `PDoom.exe`
  - [ ] Application icon set (if available)
  - [ ] Version set to v0.10.1
- [ ] Check embedded PCK is enabled

### 3. Build Windows Export (5 min)
- [ ] Project → Export → Windows Desktop
- [ ] Export to `builds/windows/v0.10.1/`
- [ ] Creates `PDoom.exe` + data files

### 4. Test Exported Build (15 min)
- [ ] Run `PDoom.exe` from builds folder
- [ ] Verify game launches
- [ ] Test gameplay (full game if possible)
- [ ] Check all features work:
  - [ ] Menu navigation
  - [ ] Game start
  - [ ] Actions work
  - [ ] Sound works
  - [ ] Leaderboard saves
  - [ ] Game end screen

---

## Packaging (15 min)

### 5. Create Release Package
```bash
cd builds/windows/v0.10.1/
# Zip everything
zip -r PDoom-v0.10.1-Windows.zip *
```

**Contents should include:**
- PDoom.exe
- PDoom.pck (if separate)
- Any required DLLs
- README.txt (optional - quick instructions)

### 6. Verify Package
- [ ] Extract zip to new folder
- [ ] Run from extracted folder
- [ ] Confirm it works standalone

---

## GitHub Release (20 min)

### 7. Create Release on GitHub
```bash
gh release create v0.10.1 \
  --title "v0.10.1 - First Godot Release" \
  --notes-file RELEASE_NOTES.txt \
  builds/windows/v0.10.1/PDoom-v0.10.1-Windows.zip
```

**Release Notes Template:**
```markdown
# P(Doom) v0.10.1 - First Godot Release

🎉 **First official Godot 4.x release!**

## Download
- **Windows**: PDoom-v0.10.1-Windows.zip

## What's New
- Complete migration to Godot 4.x engine
- Full UI with menus, settings, and pre-game setup
- Comprehensive leaderboard system with seed filtering
- Turn-based gameplay with event system
- Debug overlay (F3)
- Stray cat adoption event (turn 7)

## Installation
1. Download PDoom-v0.10.1-Windows.zip
2. Extract to any folder
3. Run PDoom.exe
4. Play!

## System Requirements
- Windows 10/11
- 2GB RAM
- 500MB disk space

## Known Issues
- Mac/Linux builds coming soon
- First Godot release - please report bugs!

## Links
- Website: https://pdoom1.com
- Issues: https://github.com/PipFoweraker/pdoom1/issues

Built with Godot 4.x | Made with coffee and existential dread ☕
```

### 8. Tag the Release
```bash
git tag v0.10.1
git push origin v0.10.1
```

---

## Post-Release (15 min)

### 9. Update README
- [ ] Change "builds coming soon" to actual download link
- [ ] Point to v0.10.1 release
- [ ] Update status from "in development" to "available"

### 10. Verify Everything
- [ ] Release appears on GitHub
- [ ] Download link works
- [ ] Downloaded file works
- [ ] README updated

---

## Quick Export Command Reference

```bash
# From Godot editor
Project → Export → Windows Desktop → Export Project

# Or via command line (if configured)
godot --export "Windows Desktop" builds/windows/v0.10.1/PDoom.exe
```

---

## Estimated Total Time: ~90 minutes

- Pre-export: 30 min
- Export & test: 20 min
- Package: 15 min
- GitHub release: 20 min
- Post-release: 15 min
- **Buffer:** 30 min for issues

---

## If Something Goes Wrong

**Export fails:**
- Check Godot export templates are installed (Editor → Manage Export Templates)
- Verify project.godot is not corrupted

**Game crashes on export:**
- Check for missing resources
- Look at Godot output console for errors
- Try debug export first

**Packaging issues:**
- Ensure all dependencies are included
- Check file paths are relative, not absolute

---

## Ready to Execute?

1. Commit current changes first
2. Follow checklist step by step
3. Test thoroughly before releasing
4. Update website after release goes live

**Let's ship it! 🚀**
