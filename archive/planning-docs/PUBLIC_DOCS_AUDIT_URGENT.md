# PUBLIC-FACING DOCUMENTATION AUDIT - URGENT

**Date:** 2025-11-03
**Deadline:** 12 hours (traffic trending up)
**Status:** 🔴 CRITICAL INACCURACIES FOUND

---

## 🚨 CRITICAL ISSUES IN README.md

### Issue 1: Wrong Website URL
**Line 58:** `Website: pdoom.org (coming soon)`
- ❌ WRONG: pdoom.org doesn't exist
- ✅ CORRECT: pdoom1.com (LIVE)
- **Impact:** Users can't find the actual website

### Issue 2: Python Instructions for Players
**Line 11:** `Python: pip install -r requirements.txt && python main.py`
- ❌ MISLEADING: Python version is legacy/dev only
- ✅ CORRECT: Players should use Godot version or downloads
- **Impact:** Players get wrong version, bad experience

### Issue 3: "Coming Soon" Status
**Line 58:** Website listed as "coming soon"
- ❌ OUTDATED: Website is already live at pdoom1.com
- **Impact:** Looks unprofessional, undermines credibility

### Issue 4: Version Numbers Unclear
**Lines 65-66:**
- Python version: v0.10.x
- Godot version: v0.5.x
- ❓ **VERIFY:** Are these accurate? What's the ACTUAL current version?

### Issue 5: Quick Start Priority
**Lines 10-12:** Python listed equally with Windows download
- ❌ CONFUSING: Should prioritize Godot/Windows for players
- Python should be for developers only

---

## 📋 FULL README ISSUES BREAKDOWN

### Quick Start Section (Lines 7-12)
```markdown
**Play Now:**
- **Windows**: Download from [Releases](https://github.com/PipFoweraker/pdoom1/releases)
- **Python**: `pip install -r requirements.txt && python main.py`  ❌ DEV ONLY
- **Godot**: Open `godot/project.godot` in Godot 4.x  ❌ DEV ONLY
```

**SHOULD BE:**
```markdown
**Play Now:**
- **Windows**: Download from [Releases](https://github.com/PipFoweraker/pdoom1/releases) ✅
- **Mac/Linux**: [Build instructions](docs/deployment/DEPLOYMENT.md) or Python fallback
- **Developers**: See [Development Setup](docs/developer/SETUP.md)
```

### Python Implementation Section (Lines 50-54)
```markdown
### Python Implementation (Legacy/Stable)
- Command-line gameplay
- Global leaderboard export system
- Privacy-first analytics
- Extensive test coverage
```

**ISSUE:** This makes Python sound like a player option
**SHOULD BE:** Move to developer documentation or clearly mark as "For Development Only"

### Links Section (Lines 56-61)
```markdown
- **Website**: [pdoom.org](https://pdoom.org) *(coming soon)*  ❌ WRONG URL
- **Issues**: [GitHub Issues](...)  ✅
- **Discussions**: [GitHub Discussions](...)  ✅
- **License**: MIT  ✅
```

**FIX:** Update to pdoom1.com, remove "coming soon"

---

## 🔍 PYTHON REFERENCES IN PUBLIC DOCS

### Where Players See Python References

**README.md:**
- Line 11: Quick Start - Python instructions
- Lines 50-54: Python Implementation section
- Line 65: Python version status

**Likely in docs/user-guide/:**
- Installation guide probably mentions Python
- Gameplay guide might reference Python version
- FAQ might have Python-specific answers

**Need to check:**
- [ ] docs/user-guide/INSTALLATION.md
- [ ] docs/user-guide/GAMEPLAY.md
- [ ] docs/user-guide/FAQ.md

---

## ✅ PROPOSED FIXES

### Fix 1: README Quick Start
```markdown
## Quick Start

### For Players

**Download & Play (Recommended):**
- **Windows**: [Download latest release](https://github.com/PipFoweraker/pdoom1/releases)
- **Mac/Linux**: Coming soon (or use [build instructions](docs/deployment/DEPLOYMENT.md))

Visit **[pdoom1.com](https://pdoom1.com)** for news, guides, and community!

### For Developers

See [Development Setup](docs/developer/SETUP.md) for:
- Building from source (Godot 4.x)
- Running tests
- Contributing guidelines
```

### Fix 2: Update Links
```markdown
## Links

- **Website**: [pdoom1.com](https://pdoom1.com) ✨
- **Issues**: [GitHub Issues](https://github.com/PipFoweraker/pdoom1/issues)
- **Discussions**: [GitHub Discussions](https://github.com/PipFoweraker/pdoom1/discussions)
- **License**: MIT
```

### Fix 3: Reframe Python Section
```markdown
## Development

### Current Implementation: Godot 4.x
The game is built in Godot 4.x with full UI, sound, and gameplay features.

**For Players:** Download the compiled version from Releases.
**For Developers:** See [Contributing](docs/developer/CONTRIBUTING.md).

### Legacy Python Version (Development/Testing Only)
A Python/Pygame prototype exists for:
- Automated testing
- Development tools
- Command-line debugging

Not recommended for players. See [Developer Guide](docs/developer/PYTHON_DEV.md).
```

### Fix 4: Status Section
```markdown
## Status

- **Current Version**: v0.10.0 (Godot)  ❓ VERIFY THIS
- **Platform**: Windows (Mac/Linux in development)
- **Development**: Active

Built with Godot 4.x | [Source on GitHub](https://github.com/PipFoweraker/pdoom1)
```

---

## 🎯 ACTION ITEMS (Priority Order)

### URGENT (Next 30 minutes)
1. ✅ Fix website URL: pdoom.org → pdoom1.com
2. ✅ Remove "coming soon" status
3. ✅ Update Quick Start to prioritize player downloads
4. ✅ Move Python to developer-only context

### HIGH PRIORITY (Next 2 hours)
5. Check docs/user-guide/ for Python references
6. Create docs/developer/PYTHON_DEV.md for dev-specific Python info
7. Update version numbers (VERIFY FIRST)
8. Test that Quick Start instructions actually work

### MEDIUM PRIORITY (Next 4 hours)
9. Audit website (pdoom1.com) vs README consistency
10. Move Python implementation details to developer docs
11. Create clear "For Players" vs "For Developers" sections
12. Add prominent website link at top of README

---

## 📊 VERIFICATION NEEDED

Before making changes, please confirm:

1. **Website URL:** Is it pdoom1.com? ✓
2. **Current version:** What's the actual current release version?
3. **Python player experience:** Does `python main.py` work? Should it?
4. **Windows downloads:** Are releases available and working?
5. **What's on pdoom1.com:** Does website match repo info?

---

## 🔄 QUICK WIN CHECKLIST

Changes that take <5 minutes each:

- [ ] Line 58: pdoom.org → pdoom1.com
- [ ] Line 58: Remove "(coming soon)"
- [ ] Line 11: Move Python to "For Developers" section
- [ ] Add prominent website link at top
- [ ] Reorder Quick Start: Downloads first, dev instructions separate
- [ ] Clarify Python = dev/testing only

**Estimated time for all quick wins:** 20-30 minutes

---

## 📝 NEXT STEPS

1. **Review this audit** - Confirm issues and priorities
2. **Verify facts** - Website URL, version numbers, what works
3. **Make fixes** - Start with quick wins
4. **Test** - Verify instructions work
5. **Commit** - Update public-facing docs

Ready to execute when you give the go-ahead!
