# Mac/Linux Platform Support Issues

**Status:** Ready to create on GitHub
**Priority:** High

## Issue 1: Mac (macOS) Support

**Title:** Add macOS build support for P(Doom)

**Labels:** enhancement, platform, high-priority

**Description:**
```markdown
## Summary
Add native macOS build support for P(Doom).

## Current Status
- Windows builds working via Godot 4.x export
- Mac builds not yet configured

## Requirements
- [ ] Configure Godot export template for macOS
- [ ] Test on macOS (Intel and Apple Silicon if possible)
- [ ] Add to release pipeline
- [ ] Update documentation

## Priority
High - Players are requesting Mac support

## Notes
Godot 4.x supports macOS exports natively, should be straightforward to add.
```

---

## Issue 2: Linux Support

**Title:** Add Linux build support for P(Doom)

**Labels:** enhancement, platform, high-priority

**Description:**
```markdown
## Summary
Add native Linux build support for P(Doom).

## Current Status
- Windows builds working via Godot 4.x export
- Linux builds not yet configured

## Requirements
- [ ] Configure Godot export template for Linux
- [ ] Test on Ubuntu/Debian (most common)
- [ ] Add to release pipeline
- [ ] Update documentation

## Priority
High - Linux users are part of our audience

## Notes
Godot 4.x supports Linux exports natively, should be straightforward to add.
```

---

## Quick Create Commands

```bash
# Create Mac support issue
gh issue create --title "Add macOS build support for P(Doom)" \
  --label "enhancement,platform,high-priority" \
  --body-file MAC_ISSUE.txt

# Create Linux support issue
gh issue create --title "Add Linux build support for P(Doom)" \
  --label "enhancement,platform,high-priority" \
  --body-file LINUX_ISSUE.txt
```

## For README Update

Once issues are created, update README.md line 18:
```markdown
- See [Issue #XXX](link) (Mac) and [Issue #YYY](link) (Linux) - High priority, coming soon!
```
