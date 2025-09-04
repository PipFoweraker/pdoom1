# P(Doom) Hotfix Workflow - UI Stability Push

## Current Status: v0.2.1 "Three Column" - Hotfix Candidate

### Quick Version Management

**When you need to bump the version:**

1. **For any UI fix/improvement:**
   ```
   Current: 0.2.1 → Next: 0.2.2
   ```

2. **Update the version:**
   - Edit `src/services/version.py`
   - Change `VERSION_PATCH = 1` to `VERSION_PATCH = 2` 
   - Update `__version__ = "0.2.1"` to `__version__ = "0.2.2"`

3. **Document the change:**
   - Add one line to the development log about what was fixed

---

## System Prompt for AI Assistance

**Copy this when starting a new session:**

```
CONTEXT: P(Doom) v0.2.1 is in active UI stability development. 

The game has a new 3-column layout system and is being prepared for wider playtesting. 
I'm expecting to do frequent hotfixes (0.2.2, 0.2.3, 0.2.4, etc.) over the next few weeks 
as players find UI bugs and installation issues.

VERSION MANAGEMENT:
- Current version: 0.2.1 (hotfix-candidate)
- Auto-increment patch version for any UI fixes
- Target: stable v0.3.0 for distribution

PRIORITY ISSUES TO WATCH FOR:
- Button visibility/overlap problems
- Text overflow in right column  
- Keystroke conflicts
- Game crashes or freezes
- Installation/dependency issues
- Performance problems

When making changes, always:
1. Test the 3-column layout still works
2. Verify buttons are clickable and visible
3. Check keystroke bindings don't conflict
4. Increment version if it's a user-facing fix
```

---

## Expected Hotfix Series

- **v0.2.1** ✓ 3-column layout with keystroke support
- **v0.2.2** → Button sizing and text overflow fixes
- **v0.2.3** → Color differentiation and visibility improvements
- **v0.2.4** → Keystroke binding refinements and input handling
- **v0.2.5** → Performance optimizations and stability
- **v0.3.0** → **MILESTONE: Stable UI release**

---

## Quick Commands

**Test the game:**
```bash
cd "c:\Users\Pip\Documents\Local Code (Upstairs PC)\Pdoom1Folder\pdoom1"
python main.py
```

**Check current version:**
```python
from src.services.version import get_display_version
print(get_display_version())
```

**Typical hotfix workflow:**
1. Player reports UI issue
2. Fix the issue
3. Bump patch version  
4. Test quickly
5. Ship immediately

Remember: UI stability is the priority. Don't let perfect be the enemy of good during this phase!
