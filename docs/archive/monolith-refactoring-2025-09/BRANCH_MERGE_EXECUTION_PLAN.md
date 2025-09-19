# Branch Merge Execution Plan

## Executive Summary
This document provides step-by-step instructions for merging the 3 production-ready branches identified in the repository analysis and cleaning up the development environment.

**Target Branches for Immediate Merge:**
1. `bug-sweep-critical-stability` (PR #300 exists) - UI layout optimization  
2. `hotfix/mac-research-debt-fix` - Critical Mac compatibility fixes
3. `feature/leaderboard-activation-v0.4.1` - Complete party-ready release

## Phase 1: Pre-Merge Validation

### 1.1 Verify Branch Status
```bash
# Check current main branch state
git checkout main
git pull origin main
git status

# Verify ready branches exist and are up to date
git branch -r | grep -E "(bug-sweep-critical-stability|hotfix/mac-research-debt-fix|feature/leaderboard-activation-v0.4.1)"
```

### 1.2 Run Tests on Ready Branches
```bash
# Test each branch before merge
for branch in bug-sweep-critical-stability hotfix/mac-research-debt-fix feature/leaderboard-activation-v0.4.1; do
    echo "Testing branch: $branch"
    git checkout $branch
    git pull origin $branch
    python -m unittest discover tests -v
    if [ $? -ne 0 ]; then
        echo "FAIL: Tests failed on branch $branch"
        exit 1
    fi
done
```

## Phase 2: Systematic Branch Merges

### 2.1 Merge Strategy
- Use fast-forward merge where possible to maintain clean history
- Create merge commits for feature branches to preserve development context
- Merge in priority order: hotfixes first, then features

### 2.2 Merge Execution (ADMIN REQUIRED)

#### Step 1: Merge hotfix/mac-research-debt-fix (CRITICAL)
```bash
git checkout main
git merge --no-ff hotfix/mac-research-debt-fix -m "Merge critical Mac compatibility fixes

- Fix Mac TypeError with verbose naming pattern
- Add GameClock array bounds protection  
- Verify hiring dialog ESC functionality
- 24 new test scenarios (15 type safety + 9 integration)
- Resolves blocking issues for Mac users"
```

#### Step 2: Merge PR #300 (bug-sweep-critical-stability)
```bash
# Option A: Use GitHub UI to merge PR #300 (RECOMMENDED)
# Go to https://github.com/PipFoweraker/pdoom1/pull/300 and click "Merge pull request"

# Option B: Command line merge
git merge --no-ff bug-sweep-critical-stability -m "Merge UI layout optimization hotfix

- Reduce button width from 30% to 25% (17% smaller)
- Reduce button height from 5.5% to 4.5% (18% smaller)
- Reduce button spacing from 1.5% to 0.8% (47% smaller)
- Better space utilization and professional layout
- No logic changes, UI improvements only"
```

#### Step 3: Merge feature/leaderboard-activation-v0.4.1
```bash
git merge --no-ff feature/leaderboard-activation-v0.4.1 -m "Merge complete v0.4.1 party-ready release

- Enhanced leaderboard system with seed-specific competition
- Spectacular game over screen with celebration effects
- Mini leaderboard preview with rank highlighting  
- Context-aware button text and natural flow progression
- Complete party demo functionality"
```

### 2.3 Post-Merge Validation
```bash
# Verify all merges successful
git log --oneline -10

# Run full test suite on merged main
python -m unittest discover tests -v

# Verify game starts correctly
python -c "from src.core.game_state import GameState; gs = GameState('test'); print('Game initializes correctly')"

# Push merged main
git push origin main
```

## Phase 3: Branch Cleanup

### 3.1 Safe Branch Deletion (Local)
```bash
# Delete merged feature branches locally
git branch -d bug-sweep-critical-stability
git branch -d hotfix/mac-research-debt-fix  
git branch -d feature/leaderboard-activation-v0.4.1

# Verify deletion
git branch -a
```

### 3.2 Remote Branch Cleanup (ADMIN REQUIRED)
```bash
# Delete remote branches after successful merge
git push origin --delete bug-sweep-critical-stability
git push origin --delete hotfix/mac-research-debt-fix
git push origin --delete feature/leaderboard-activation-v0.4.1
```

### 3.3 PR Cleanup
- [ ] Close PR #300 (should close automatically after merge)
- [ ] Close PR #304 (this analysis PR) after execution complete
- [ ] Update any related issues with merge status

## Phase 4: Additional Branch Evaluation

### 4.1 Next Priority Branches (Short-term consideration)
Based on the analysis, evaluate these for next merge cycle:

1. **`develop`** - Sound system improvements (HIGH priority UX fix)
2. **`type-annotation-upgrades`** - Website pipeline infrastructure 
3. **`copilot/fix-184`** (PR #217) - Office cat feature (if approved)

### 4.2 Experimental Branch Management
Consider archiving or documenting status of experimental branches:
- `experimental/longtermist-dates`
- `experimental/playground`  
- `dead-code-analysis`

## Phase 5: Environment Validation

### 5.1 Final System Check
```bash
# Verify clean main branch
git checkout main
git status
git log --oneline -5

# Confirm game functionality
python main.py  # Should start without errors

# Verify version consistency
python -c "from src.services.version import get_display_version; print(f'Version: {get_display_version()}')"
```

### 5.2 Documentation Updates
- [ ] Update CHANGELOG.md with merged features
- [ ] Update version numbers if needed
- [ ] Document any new configuration requirements

## Rollback Plan

If any issues arise during merge:

```bash
# Identify last good commit before merges
git log --oneline

# Reset to last good state (DESTRUCTIVE)
git reset --hard <last_good_commit>

# Force push (requires admin)
git push --force origin main
```

## Success Criteria

- [ ] All 3 identified branches successfully merged to main
- [ ] Full test suite passes (507 tests expected)
- [ ] Game starts and functions correctly
- [ ] No merge conflicts or broken dependencies
- [ ] Remote branches cleaned up
- [ ] Development environment is clean and organized

## Emergency Contacts

If issues arise during execution:
- Review original analysis in `BRANCH_STATUS_REPORT.md`
- Check individual branch documentation
- Use rollback plan if critical issues detected

---

**Total Execution Time:** Estimated 15-30 minutes
**Risk Level:** LOW-MEDIUM (all branches pre-validated)
**Dependencies:** Admin git access, Python environment