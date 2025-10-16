# Godot Migration Documentation Plan

**Date**: 2025-10-17
**Context**: Phase 4 MVP Complete, Planning Phase 5+
**Builds On**: [DOCUMENTATION_REORGANIZATION_2025-09-28.md](DOCUMENTATION_REORGANIZATION_2025-09-28.md)

---

## Quick Wins for This Session

### 1. Organize Godot Docs (10 min)
```bash
# Move UI vision to Godot directory
mv docs/UI_DESIGN_VISION.md godot/

# Create phase tracker
touch docs/current/GODOT_MIGRATION_TRACKER.md
```

**Result**: Godot docs consolidated, progress visible

### 2. Archive October Sessions (5 min)
```bash
mkdir -p docs/archive/session-handoffs/2025-10
mv docs/SESSION_*.md docs/archive/session-handoffs/2025-10/
```

**Result**: Clean docs/ root, sessions archived

### 3. Update Index (5 min)
Add to [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md):
- Godot migration section
- Link to godot/ README
- October 2025 archive location

---

## Godot Documentation Structure

### Current (Phase 4)
```
godot/
├─ README.md          # Overview + quick start ✅
├─ SETUP.md           # Installation guide ✅
└─ project.godot      # Godot project file
```

### Proposed (Phase 5+)
```
godot/
├─ README.md                    # Overview + quick start
├─ SETUP.md                     # Installation
├─ UI_DESIGN_VISION.md          # Moved from docs/
├─ ARCHITECTURE.md              # How bridge works (NEW)
├─ TROUBLESHOOTING.md           # Common issues (NEW)
└─ docs/                        # Godot-specific deep dives
   ├─ BRIDGE_PROTOCOL.md        # JSON API reference
   ├─ SCENE_STRUCTURE.md        # Scene organization
   └─ PHASE_HISTORY.md          # Migration phases log
```

**Rationale**:
- Keep godot/ lightweight (5-7 files max)
- Deep technical docs in godot/docs/
- Main project docs/ stays for cross-cutting concerns

---

## Pygame Deprecation Strategy

### Option A: In-Place Deprecation (Recommended)
```
pygame/
├─ DEPRECATED.md        # "Don't use this, use Godot instead"
├─ *.py files           # Leave as-is (broken but documented)
└─ (everything else)
```

**Pros**: Simple, clear signal, preserves git history
**Cons**: Broken code still in main codebase

### Option B: Archive to docs/
```
docs/archive/pygame-deprecated-2025-10/
├─ DEPRECATION_NOTICE.md
├─ pygame/ (entire directory moved)
└─ MIGRATION_NOTES.md
```

**Pros**: Cleaner main directory
**Cons**: Loses file history context, more disruptive

**Decision**: Use Option A for now, consider Option B after Godot reaches feature parity.

---

## Current Documentation Tracker

### Active Documents (Touch Monthly)
- `docs/current/GODOT_MIGRATION_TRACKER.md` (NEW)
- `docs/development-sessions/2025-10/` (sessions this month)
- `godot/README.md` (as phases progress)

### Stable References (Touch Quarterly)
- `DEVELOPERGUIDE.md`
- `process/CONTRIBUTING.md`
- `WORKFLOW_JJ_GITHUB_CLAUDE.md`

### Archive Triggers
- Session handoffs → After next session starts
- Investigation logs → After issue closed + 7 days
- Phase completion docs → When next phase starts

---

## Tools to Build (Prioritized)

### Priority 1: Archive Helper Script
```bash
#!/bin/bash
# tools/archive-session.sh
# Usage: ./tools/archive-session.sh SESSION_HANDOFF_2025-10-16.md

FILE=$1
MONTH=$(echo $FILE | grep -oP '\d{4}-\d{2}')
DEST="docs/archive/session-handoffs/$MONTH/"

mkdir -p "$DEST"
mv "$FILE" "$DEST"
echo "Archived $FILE to $DEST"
```

**Why First**: We create 2-3 session handoffs per week, this saves time

### Priority 2: Documentation Health Check
```python
# tools/doc-health.py
"""
Checks:
- Root .md files (should only be README, CHANGELOG)
- Broken links in docs/
- Outdated dates (>90 days since update)
"""
```

**Why Second**: Prevents documentation debt from accumulating

### Priority 3: Phase Tracker Generator
```python
# tools/update-phase-tracker.py
"""
Scans:
- godot/scenes/*.tscn (what's built)
- godot/scripts/*.gd (what's implemented)
- GitHub issues with "godot" label

Generates:
- docs/current/GODOT_MIGRATION_TRACKER.md
- Progress bars, completion %, next priorities
"""
```

**Why Third**: Automates status updates, keeps docs current

---

## GitHub Issues Integration

### Issue Labels
- `godot-migration` - Godot-specific work
- `pygame-deprecated` - Pygame bugs we won't fix
- `documentation` - Doc improvements

### Issue Templates
Consider adding:
- `.github/ISSUE_TEMPLATE/godot-feature.md`
- Links to godot/ARCHITECTURE.md
- Phase tracker reference

###

 Closing Pygame Issues
```bash
gh issue close 390 -c "Pygame UI deprecated. See Godot migration: #[NEW_ISSUE]"
gh issue close 257 -c "Pygame UI deprecated. UI will be rebuilt in Godot."
```

---

## Next Steps (This Session)

### Immediate (15 min total)

1. **Move UI_DESIGN_VISION.md** (2 min)
   ```bash
   git mv docs/UI_DESIGN_VISION.md godot/
   ```

2. **Create Phase Tracker** (5 min)
   ```bash
   # Create docs/current/GODOT_MIGRATION_TRACKER.md
   # Content: Phase 1-4 status, Phase 5 priorities
   ```

3. **Archive Session Handoffs** (3 min)
   ```bash
   mkdir -p docs/archive/session-handoffs/2025-10
   mv docs/SESSION_HANDOFF_2025-10-16_*.md docs/archive/session-handoffs/2025-10/
   mv docs/SESSION_SUMMARY_2025-10-17_*.md docs/archive/session-handoffs/2025-10/
   ```

4. **Update GitHub Issues** (5 min)
   - Close #390, #257 as "wontfix" with Godot migration note
   - Create "Godot Phase 5" issue
   - Optional: Create "Documentation Tooling" issue

### Future Sessions

- **Phase 5 Start**: Create godot/ARCHITECTURE.md
- **Mid-Phase 5**: Add godot/TROUBLESHOOTING.md
- **Phase 5 Complete**: Build tools/archive-session.sh
- **Phase 6+**: Consider automated phase tracker

---

## Success Criteria

### This Session
- [ ] UI_DESIGN_VISION.md in godot/ directory
- [ ] Phase tracker created
- [ ] October session handoffs archived
- [ ] GitHub issues updated

### Next Month
- [ ] All October sessions archived
- [ ] Godot docs consolidated
- [ ] At least one automation script created
- [ ] Documentation index reflects current state

### Long Term
- [ ] Pygame fully deprecated or archived
- [ ] Godot documentation comprehensive
- [ ] Automated health checks in CI
- [ ] Monthly archive runs automated

---

## Notes & Observations

### What's Working
- September's reorganization pattern is solid
- Investigation workspaces are great for complex issues
- Archive by date/topic makes sense

### What Needs Attention
- Root directory accumulates files again (need automation)
- Session handoffs should auto-archive after 30 days
- Need "current status" view for quick context

### Future Considerations
- When to split pygame code out entirely?
- Should godot/ be a separate repo eventually?
- Documentation site generation (MkDocs, Docusaurus)?

---

**Status**: Planning Complete
**Next**: Execute immediate actions (15 min)
**Then**: Update GitHub issues
**Finally**: Commit and archive this session

---

*Related Docs*:
- [DOCUMENTATION_REORGANIZATION_2025-09-28.md](DOCUMENTATION_REORGANIZATION_2025-09-28.md)
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- [godot/README.md](../godot/README.md)
