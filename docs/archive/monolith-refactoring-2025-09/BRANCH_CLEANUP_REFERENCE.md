# Branch Cleanup Reference

## Summary
After merging the 3 production-ready branches, this reference helps identify which additional branches can be safely closed or archived.

## Branches Merged (To be deleted after merge)
[EMOJI] **READY FOR DELETION after merge:**
1. `bug-sweep-critical-stability` - Merged via PR #300
2. `hotfix/mac-research-debt-fix` - Merged directly  
3. `feature/leaderboard-activation-v0.4.1` - Merged directly

## Active Development Branches (Keep)
[EMOJI] **KEEP - Active development:**
1. `develop` - Sound system improvements (HIGH priority)
2. `type-annotation-upgrades` - Website pipeline infrastructure
3. `stable-alpha` - Strategic planning and development issues
4. `refactor/alpha-stabilization` - Core stability improvements

## Feature Branches (Evaluate)
[WARNING][EMOJI] **EVALUATE for next merge cycle:**
1. `copilot/fix-184` (PR #217) - Office cat feature (draft PR exists)
2. `feature/accessibility-keyboard-navigation` - Accessibility improvements
3. `pdoom1-website` - Website development

## Maintenance Branches (Keep for reference) 
[CHECKLIST] **KEEP - Maintenance and hotfixes:**
1. `hotfix/menu-navigation-fixes` - Menu improvements
2. `hotfix/sound-enabled-by-default` - Sound configuration
3. `refactor/monolith-breakdown` - Code organization
4. `release/staging` - Release preparation

## Experimental Branches (Archive consideration)
[U+1F9EA] **CONSIDER ARCHIVING if inactive:**
1. `experimental/longtermist-dates` - Experimental feature
2. `experimental/playground` - Development sandbox
3. `dead-code-analysis` - Code analysis tools

## Personal/Contributor Branches (Owner decision)
[EMOJI] **OWNER DECISION:**
1. `steven-branch` (PR #218) - Contributor branch
2. `PipFoweraker-patch-1-cat-images` (PR #219) - Asset branch

## Beta/Release Branches (Keep)
[ROCKET] **KEEP - Release management:**
1. `stable-beta` - Beta release branch

## Quick Cleanup Commands

### Delete merged branches locally:
```bash
git branch -d bug-sweep-critical-stability
git branch -d hotfix/mac-research-debt-fix  
git branch -d feature/leaderboard-activation-v0.4.1
```

### Delete merged branches remotely (ADMIN):
```bash
git push origin --delete bug-sweep-critical-stability
git push origin --delete hotfix/mac-research-debt-fix
git push origin --delete feature/leaderboard-activation-v0.4.1
```

### Prune local tracking of deleted remote branches:
```bash
git remote prune origin
```

## Branch Health Status

### [U+1F7E2] HEALTHY (Recent activity, clear purpose)
- `develop` (Sep 11 - Sound system)
- `type-annotation-upgrades` (Sep 14 - Website pipeline)  
- `stable-alpha` (Recent - Strategic planning)

### [U+1F7E1] MODERATE (Some activity, evaluate priority)
- `copilot/fix-184` (Sep 4 - Office cat feature)
- `refactor/alpha-stabilization` (Older but structured)

### [EMOJI] STALE (Consider archiving)
- `experimental/longtermist-dates` (Experimental, unclear status)
- `experimental/playground` (Sandbox, may be obsolete)

## Post-Cleanup Repository State

After cleanup, the repository will have:
- **Clean main branch** with merged production features
- **~15-18 active branches** (down from 21)
- **Clear categorization** of remaining branches
- **Reduced cognitive overhead** for development

## Recommended Next Steps

1. **Immediate (after merge):**
   - Delete merged branches
   - Close related PRs
   - Update documentation

2. **Short-term (next week):**
   - Evaluate `develop` branch for merge
   - Review `copilot/fix-184` PR for approval
   - Consider `type-annotation-upgrades` timeline

3. **Medium-term (next month):**
   - Archive experimental branches if inactive  
   - Consolidate maintenance branches
   - Plan next major feature development

This cleanup strategy maintains development momentum while creating a clean, manageable environment for ongoing work and playtesting.