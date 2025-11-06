# Release Checklist - v0.10.1

**Target:** First official Godot 4.x release with major UX improvements
**Time Budget:** 2-3 hours for export, test, package, release

---

## Pre-Export Checklist (10 min)

### Code Quality
- [x] All Tier 1 tasks complete (UX, warnings, validation)
- [x] All Tier 2 tasks complete (description, warnings, queue buttons)
- [ ] All commits pushed to main branch
- [ ] Zero GDScript warnings in Godot editor

### Version Verification
- [ ] CHANGELOG.md updated with v0.10.1 changes
- [ ] README.md accurate (no false promises about features)
- [ ] project.godot version consistent

### Testing in Editor
- [ ] Game runs without errors in Godot
- [ ] All keyboard shortcuts work (1-9, C, Space)
- [ ] Queue actions → AP counter updates correctly
- [ ] Remove button on queue items works
- [ ] Clear Queue (C) works
- [ ] Commit Actions only enabled when queue not empty
- [ ] Danger warnings show when doom/rep in danger zones

---

## Export Process (15 min)

### Godot Export
1. **Open Godot** (if not already open)
2. **Project → Export...**
3. **Select "Windows Desktop"** preset
4. **Export to:** `builds/windows/v0.10.1/PDoom.exe`
5. **Wait for export** (~30 seconds)

### Files Created
- `PDoom.exe` - Main executable (~91MB)
- `PDoom.pck` - Game data (~19MB)
- `PDoom.console.exe` - Debug version (optional, ~49KB)

### Quick Smoke Test
- [ ] Run `builds/windows/v0.10.1/PDoom.exe`
- [ ] Game launches without errors
- [ ] Can start game and queue actions
- [ ] Basic gameplay works

---

## Testing Exported Build (30 min)

### Core Gameplay Test
- [ ] **Init game** - Starts on Turn 1
- [ ] **Queue 2 actions** - AP: 3 (1 free, 2 queued) shows
- [ ] **Press C** - Queue clears, AP refunded
- [ ] **Queue 3 actions** - AP: 3 (0 free, 3 queued) RED
- [ ] **Try queue 4th** - Error: Not enough AP
- [ ] **Click remove button on queue item** - Action removed, AP refunded
- [ ] **Press Space/Enter** - Turn commits

### Warning System Test
- [ ] Get doom above 70% - Warning shows before commit
- [ ] Get reputation below 30 - Warning shows before commit
- [ ] Money below $20k - Warning shows

### UI Test
- [ ] All keyboard shortcuts work
- [ ] Buttons enable/disable correctly
- [ ] Queue display updates properly
- [ ] Message log shows colored messages
- [ ] No visual glitches

### Edge Cases
- [ ] Can't commit with empty queue
- [ ] Can't overcommit AP
- [ ] Clear queue works at any point
- [ ] Remove individual actions works

---

## Packaging (10 min)

### Create Release Package
Run: `bash package_release.sh`

This creates: `PDoom-v0.10.1-Windows.zip` containing:
- PDoom.exe
- PDoom.pck
- README.txt (quick start guide)
- CHANGELOG.txt (v0.10.1 changes)

### Verify Package
- [ ] Zip file exists (~110MB)
- [ ] Extract to temp folder
- [ ] Run PDoom.exe from extracted folder
- [ ] Game works without issues

---

## GitHub Release (20 min)

### Pre-Release
- [ ] All commits pushed to `main`
- [ ] All tests passed
- [ ] Package verified

### Create Release
Run: `bash create_github_release.sh`

Or manually:
```bash
gh release create v0.10.1 \
  --title "v0.10.1 - UX Improvements & Public Release" \
  --notes-file RELEASE_NOTES_v0.10.1.md \
  PDoom-v0.10.1-Windows.zip
```

### Verify Release
- [ ] Release visible on GitHub
- [ ] Download link works
- [ ] Release notes correct
- [ ] Tagged correctly as v0.10.1

---

## Post-Release (15 min)

### Update README
- [ ] Change "Windows builds coming soon" to actual download link
- [ ] Update Quick Start section with release link
- [ ] Commit and push

### Close Issues
- [ ] Close #435 (GDScript warnings) ✅
- [ ] Close #431 (Game description) ✅
- [ ] Close #389 (AP validation) with explanation ✅

### Announcements (Optional)
- [ ] Update pdoom1.com website
- [ ] Post on social media (if applicable)
- [ ] Notify community

---

## Rollback Plan (If Issues Found)

If critical bugs discovered after release:

1. **Mark release as "Pre-release"** on GitHub
2. **Create hotfix branch** from main
3. **Fix critical bugs**
4. **Test thoroughly**
5. **Release v0.10.2** with fixes

---

## Success Criteria

**Minimum (Must Have):**
- ✅ Game exports successfully
- ✅ Basic gameplay works in exported build
- ✅ AP tracking works correctly
- ✅ No critical bugs

**Good (Should Have):**
- ✅ All UX improvements working
- ✅ GitHub release created
- ✅ README updated with download link

**Excellent (Nice to Have):**
- ✅ Zero known bugs
- ✅ Polished user experience
- ✅ Website updated
- ✅ Community notified

---

## Time Tracking

| Phase | Planned | Actual | Notes |
|-------|---------|--------|-------|
| Pre-Export | 10min | ___ | |
| Export | 15min | ___ | |
| Testing | 30min | ___ | |
| Packaging | 10min | ___ | |
| GitHub Release | 20min | ___ | |
| Post-Release | 15min | ___ | |
| **Total** | **100min** | ___ | |

---

## Notes

Add any issues found during testing here:

-

---

**Ready to proceed? Run the test checklist, then execute the scripts below!**
